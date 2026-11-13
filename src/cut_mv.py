"""Cut a lyric micro-MV: pieces timed to song positions, crossfades, song audio, burned-in lyrics (ASS).
usage: python3 src/cut_mv.py prompts/wedding/mv-edl.yaml review/wedding/mv/mv-720p.mp4 [--height 720] [--no-subs]"""
import argparse, glob, json, os, subprocess, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser(); ap.add_argument("edl"); ap.add_argument("out"); ap.add_argument("--height", type=int, default=720)
ap.add_argument("--no-subs", action="store_true"); ap.add_argument("--src-height", type=int, default=0, help="use upscaled sources video_<h>p.mp4 if present")
a = ap.parse_args()
e = yaml.safe_load(open(os.path.join(ROOT, a.edl))); X = e["xfade"]; H = a.height; W = H * 16 // 9
s_in, s_out = e["song_in"], e["song_out"]; total = s_out - s_in
tmp = os.path.join(ROOT, "runs", "mv-pieces"); os.makedirs(tmp, exist_ok=True)
def src(exp, vid):
    m = [p for p in sorted(glob.glob(os.path.join(ROOT, "runs", exp, f"*-{vid}-r*", "meta.json")), key=os.path.getmtime) if "error" not in json.load(open(p))][-1]
    d = os.path.dirname(m); up = os.path.join(d, f"video_{a.src_height}p.mp4")
    return (up if a.src_height and os.path.exists(up) else os.path.join(d, "video.mp4")), json.load(open(m))["ffprobe"]["duration_s"]
P = e["pieces"]; files, durs, xs = [], [], []
for i, p in enumerate(P):
    end = P[i + 1]["at"] if i + 1 < len(P) else s_out
    x = p.get("xfade", X) if i + 1 < len(P) else 0
    dur = end - p["at"] + x
    out = os.path.join(tmp, f"{i:02d}.mp4")
    norm = f"scale={W}:{H}:flags=lanczos,fps=24,format=yuv420p,setsar=1"
    if "split" in p:
        ins = []
        for q in p["split"]:
            f, L = src(q["exp"], q["id"]); st = min(q["in"], max(0, L - dur)); ins += ["-ss", f"{st:.3f}", "-t", f"{dur:.3f}", "-i", f]
        fc = (f"[0:v]scale={W}:{H},crop={W//2}:{H}:{W//4}:0[l];[1:v]scale={W}:{H},crop={W//2}:{H}:{W//4}:0[r];"
              f"[l][r]hstack=inputs=2,drawbox=x={W//2-1}:y=0:w=2:h={H}:color=white@0.85:t=fill,fps=24,format=yuv420p,setsar=1[v]")
        subprocess.run(["ffmpeg", "-y", "-v", "error"] + ins + ["-filter_complex", fc, "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", out], check=True)
    else:
        f, L = src(p["exp"], p["id"]); st = p["in"]
        if st + dur > L - 0.01:
            print(f"  piece {i} {p['id']}: {st}+{dur:.2f} > {L:.2f}, shifting in-point"); st = max(0, L - 0.01 - dur)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{st:.3f}", "-t", f"{dur:.3f}", "-i", f, "-vf", norm, "-an",
                        "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", out], check=True)
    files.append(out); durs.append(dur); xs.append(x)
# video chain
args = []
for f in files: args += ["-i", f]
fc, lv, t = [], "[0:v]", durs[0]
for k in range(1, len(files)):
    x = xs[k - 1]; t -= x
    fc.append(f"{lv}[{k}:v]xfade=transition=fade:duration={x}:offset={t:.3f}[v{k}]"); lv = f"[v{k}]"; t += durs[k]
# lyrics
subs = os.path.join(tmp, "lyrics.ass")
if not a.no_subs:
    song = json.load(open(e["lyrics"])); L = song["lines"]; fs_zh, fs_jp = round(H * 0.050), round(H * 0.032)
    def ts(x):
        x = max(0, x); return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"
    ev = []
    for i, l in enumerate(L):
        st = l["t"] - s_in; en = (L[i + 1]["t"] if i + 1 < len(L) else l["t"] + 3.0) - s_in - 0.15
        if en <= 0 or st >= total: continue
        st, en = max(st, 0.2), min(en, total - 0.3)
        jp = l["jp"].replace("　", " "); zh = l["zh"]
        text = (f"{{\\fs{fs_jp}\\c&H00E8F4FF&}}{jp}\\N{{\\fs{fs_zh}\\c&H00FFFFFF&}}{zh}" if zh and zh != jp else f"{{\\fs{fs_zh}}}{jp}")
        ev.append(f"Dialogue: 0,{ts(st)},{ts(en)},Lyric,,0,0,0,,{{\\fad(250,250)}}{text}")
    ev.insert(0, f"Dialogue: 0,{ts(0.6)},{ts(3.2)},Title,,0,0,0,,{{\\fad(400,400)}}水果蛋糕之戀\\N{{\\fs{fs_jp}}}Fruit Cake Love")
    open(subs, "w").write(f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Lyric,LyricSerif,{fs_zh},&H00FFFFFF,&H00FFFFFF,&H00402818,&H96000000,0,0,0,0,100,100,1,0,1,{max(2, H // 300)},{max(1, H // 360)},2,{W // 12},{W // 12},{round(H * 0.06)},1
Style: Title,LyricSerif,{round(H * 0.075)},&H00FFFFFF,&H00FFFFFF,&H00402818,&H96000000,0,0,0,0,100,100,2,0,1,{max(2, H // 240)},{max(1, H // 300)},5,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""" + "\n".join(ev) + "\n")
    fc.append(f"{lv}ass={subs}:fontsdir=/root/.fonts[vs]"); lv = "[vs]"
fc.append(f"{lv}fade=t=in:st=0:d=0.8,fade=t=out:st={total - 2.5:.3f}:d=2.5[vout]")
k = len(files)
fc.append(f"[{k}:a]atrim=start={s_in}:end={s_out},asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.6,afade=t=out:st={total - 3.0:.3f}:d=3.0[aout]")
os.makedirs(os.path.dirname(os.path.join(ROOT, a.out)), exist_ok=True)
subprocess.run(["ffmpeg", "-y", "-v", "error"] + args + ["-i", e["song"], "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
                "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", os.path.join(ROOT, a.out)], check=True)
print(f"{len(files)} pieces, video {t:.1f}s, song {total:.1f}s -> {a.out}")
