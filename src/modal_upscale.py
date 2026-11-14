"""(Copied from clarencechien/theplaybillv2 scripts/modal-upscale.py; adds a batch entrypoint.)
AI-upscale the 720p storybook films to 1080p on a Modal GPU — same footage, sharper.

  MODAL_TOKEN_ID=... MODAL_TOKEN_SECRET=... modal run scripts/modal-upscale.py --src in.mp4 --dst out.mp4

Real-ESRGAN's anime-video model (realesr-animevideov3), frame by frame, then x264 CRF 24
with faststart and no audio. Nothing of the site and no key is baked into the image.

Not yet run end to end: the cloud session that wrote it sits behind a proxy that cannot
carry gRPC, which is Modal's protocol, so it must be started from a machine with normal
network access. The same pipeline was verified frame by frame on CPU there.
"""
import subprocess
import modal

WEIGHTS = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-animevideov3.pth'
# torch + OpenCV only: basicsr's setup.py no longer builds cleanly, and the compact
# network that realesr-animevideov3 uses is twenty lines (see SRVGGNetCompact below).
image = (
    modal.Image.debian_slim(python_version='3.11')
    .apt_install('ffmpeg', 'libgl1', 'libglib2.0-0', 'curl')
    .pip_install('torch==2.5.1', 'opencv-python-headless', 'numpy<2')
    .run_commands(f'curl -sSL -o /root/realesr-animevideov3.pth {WEIGHTS}')
)
app = modal.App('playbill-upscale', image=image)


def build_net(torch):
    """Real-ESRGAN's SRVGGNetCompact (num_feat 64, num_conv 16, upscale 4, PReLU), as in basicsr."""
    nn = torch.nn

    class SRVGGNetCompact(nn.Module):
        def __init__(self, num_feat=64, num_conv=16, upscale=4):
            super().__init__()
            self.upscale = upscale
            self.body = nn.ModuleList([nn.Conv2d(3, num_feat, 3, 1, 1), nn.PReLU(num_parameters=num_feat)])
            for _ in range(num_conv):
                self.body.append(nn.Conv2d(num_feat, num_feat, 3, 1, 1))
                self.body.append(nn.PReLU(num_parameters=num_feat))
            self.body.append(nn.Conv2d(num_feat, 3 * upscale * upscale, 3, 1, 1))
            self.upsampler = nn.PixelShuffle(upscale)

        def forward(self, x):
            out = x
            for layer in self.body:
                out = layer(out)
            out = self.upsampler(out)
            return out + torch.nn.functional.interpolate(x, scale_factor=self.upscale, mode='nearest')

    return SRVGGNetCompact()


def load_upscaler(torch, device, half):
    net = build_net(torch)
    state = torch.load('/root/realesr-animevideov3.pth' if device.type == 'cuda' else WEIGHTS_LOCAL, map_location='cpu')
    net.load_state_dict(state.get('params_ema', state.get('params', state)), strict=True)
    net = net.eval().to(device)
    if half:
        net = net.half()

    def enhance(img_bgr, outscale):
        import cv2, numpy as np
        x = torch.from_numpy(img_bgr[:, :, ::-1].astype(np.float32) / 255.0).permute(2, 0, 1).unsqueeze(0).to(device)
        if half:
            x = x.half()
        with torch.no_grad():
            y = net(x)
        y = y.float().clamp_(0, 1).squeeze(0).permute(1, 2, 0).cpu().numpy()[:, :, ::-1]
        y = (y * 255.0).round().astype(np.uint8)
        h, w = img_bgr.shape[:2]
        return cv2.resize(y, (int(round(w * outscale)), int(round(h * outscale))), interpolation=cv2.INTER_LANCZOS4)

    return enhance


WEIGHTS_LOCAL = 'realesr-animevideov3.pth'


@app.function(gpu='T4', timeout=3600)
def upscale(src: bytes, height: int = 1080, crf: int = 24) -> bytes:
    import time, cv2, torch
    print('cuda:', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '-', flush=True)
    open('/tmp/in.mp4', 'wb').write(src)
    cap = cv2.VideoCapture('/tmp/in.mp4')
    fps = cap.get(cv2.CAP_PROP_FPS) or 24
    w, h, n = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)), int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    scale = height / h
    ow, oh = int(round(w * scale / 2)) * 2, height
    print(f'{w}x{h} @ {fps:.3f} fps, {n} frames -> {ow}x{oh}', flush=True)
    enhance = load_upscaler(torch, torch.device('cuda'), half=True)
    enc = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{ow}x{oh}', '-r', f'{fps:.3f}', '-i', '-',
                            '-an', '-c:v', 'libx264', '-preset', 'slow', '-crf', str(crf), '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', '/tmp/out.mp4'], stdin=subprocess.PIPE)
    t0, i = time.time(), 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        out = enhance(frame, scale)
        if out.shape[1] != ow or out.shape[0] != oh:
            out = cv2.resize(out, (ow, oh), interpolation=cv2.INTER_LANCZOS4)
        enc.stdin.write(out.tobytes()); i += 1
        if i % 60 == 0:
            print(f'{i}/{n} frames, {(time.time() - t0) / i:.2f}s/frame', flush=True)
    enc.stdin.close(); enc.wait()
    print(f'done: {i} frames in {time.time() - t0:.0f}s', flush=True)
    return open('/tmp/out.mp4', 'rb').read()


@app.local_entrypoint()
def main(src: str, dst: str, height: int = 1080, crf: int = 24):
    out = upscale.remote(open(src, 'rb').read(), height, crf)
    open(dst, 'wb').write(out)
    print('saved', dst, len(out), 'bytes')


@app.local_entrypoint()
def batch(src_dir: str, dst_dir: str, height: int = 1080, crf: int = 16):
    """Upscale every NN.mp4 in src_dir in parallel (one T4 per file) into dst_dir."""
    import glob, os
    files = sorted(glob.glob(os.path.join(src_dir, "[0-9][0-9].mp4")))
    os.makedirs(dst_dir, exist_ok=True)
    args = [(open(f, "rb").read(), height, crf) for f in files]
    for f, out in zip(files, upscale.starmap(args)):
        dst = os.path.join(dst_dir, os.path.basename(f)); open(dst, "wb").write(out); print("saved", dst, len(out), "bytes", flush=True)
