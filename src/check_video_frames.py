"""Extract frames (1 s, middle, last second) from generated videos and run the look check on them.

usage: python3 src/check_video_frames.py --exp W2 [--spec prompts/wedding/videos-test.yaml]
Finds the newest successful run of each spec id under runs/<exp>/, writes frames next to the video,
builds prompts/wedding/look-check-<exp>.yaml and calls src/check_look.py on it.
"""
import argparse, glob, json, os, subprocess, sys, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def who_from_refs(refs):
    w = []
    for r in refs:
        if r.endswith("she-sheet.jpg"): w.append("she")
        elif r.endswith("he-sheet.jpg"): w.append("he")
        elif "playbill-couple" in r: w.append("wed")
    return w

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--exp", required=True)
    ap.add_argument("--spec", default="prompts/wedding/videos-test.yaml"); a = ap.parse_args()
    spec = yaml.safe_load(open(os.path.join(ROOT, a.spec)))["videos"]
    items = []
    for v in spec:
        metas = sorted(glob.glob(os.path.join(ROOT, "runs", a.exp, f"*-{v['id']}-r*", "meta.json")), key=os.path.getmtime)
        metas = [m for m in metas if "error" not in json.load(open(m))]
        if not metas:
            print(f"no successful run for {v['id']}"); continue
        d = os.path.dirname(metas[-1]); video = os.path.join(d, "video.mp4")
        dur = json.load(open(metas[-1]))["ffprobe"]["duration_s"]
        for tag, t in (("start", 1.0), ("mid", dur / 2), ("end", max(dur - 1.0, 0))):
            out = os.path.join(d, f"frame-{tag}.jpg")
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", "-q:v", "2", out], check=True)
            items.append({"id": f"{v['id']}@{tag}", "path": os.path.relpath(out, ROOT), "who": who_from_refs(v["refs"])})
    man = os.path.join(ROOT, "prompts", "wedding", f"look-check-{a.exp}.yaml")
    yaml.safe_dump({"items": items}, open(man, "w"), allow_unicode=True, sort_keys=False, width=1000)
    subprocess.run([sys.executable, os.path.join(ROOT, "src", "check_look.py"), "--exp", "WC", "--manifest", os.path.relpath(man, ROOT)], cwd=ROOT, check=True)

if __name__ == "__main__":
    main()
