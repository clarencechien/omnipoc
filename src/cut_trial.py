"""Cut the trial from an edit list: trim clean pieces, normalise, join with crossfades, fade in/out.
usage: python3 src/cut_trial.py prompts/wedding/trial-edl.yaml review/wedding/trial/trial-cut.mp4"""
import glob, json, os, subprocess, sys, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
edl, out = sys.argv[1], sys.argv[2]
e = yaml.safe_load(open(os.path.join(ROOT, edl))); X = e["xfade"]
tmp = os.path.join(ROOT, "runs", "trial-pieces"); os.makedirs(tmp, exist_ok=True)
pieces = []
for i, p in enumerate(e["pieces"]):
    metas = [m for m in sorted(glob.glob(os.path.join(ROOT, "runs", p["exp"], f"*-{p['id']}-r*", "meta.json")), key=os.path.getmtime) if "error" not in json.load(open(m))]
    src = os.path.join(os.path.dirname(metas[-1]), "video.mp4")
    dst = os.path.join(tmp, f"{i:02d}.mp4")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", str(p["in"]), "-to", str(p["out"]), "-i", src,
                    "-vf", "scale=1280:720,fps=24,format=yuv420p,setsar=1", "-af", "aresample=48000,aformat=channel_layouts=stereo",
                    "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-c:a", "aac", "-b:a", "160k", dst], check=True)
    pieces.append((dst, p["out"] - p["in"], p.get("xfade", X)))
args, fv, fa, t = [], [], [], 0.0
for f, _, _ in pieces: args += ["-i", f]
lv, la = "[0:v]", "[0:a]"; t = pieces[0][1]
for k in range(1, len(pieces)):
    x = pieces[k][2]; t -= x
    fv.append(f"{lv}[{k}:v]xfade=transition=fade:duration={x}:offset={t:.3f}[v{k}]"); lv = f"[v{k}]"
    fa.append(f"{la}[{k}:a]acrossfade=d={x}[a{k}]"); la = f"[a{k}]"
    t += pieces[k][1]
fv.append(f"{lv}fade=t=in:st=0:d=0.8,fade=t=out:st={t-1.2:.3f}:d=1.2[vout]")
fa.append(f"{la}afade=t=in:st=0:d=0.8,afade=t=out:st={t-1.2:.3f}:d=1.2[aout]")
subprocess.run(["ffmpeg", "-y", "-v", "error"] + args + ["-filter_complex", ";".join(fv + fa), "-map", "[vout]", "-map", "[aout]",
                "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", os.path.join(ROOT, out)], check=True)
print(f"{len(pieces)} pieces, {t:.1f}s -> {out}")
