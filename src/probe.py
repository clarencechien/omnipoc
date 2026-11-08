import json, subprocess
def ffprobe(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
        "format=duration,size:stream=codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels",
        "-of", "json", path], capture_output=True, text=True, check=True).stdout
    d = json.loads(out)
    v = next((s for s in d["streams"] if s["codec_type"] == "video" and s["codec_name"] != "mjpeg"), {})
    a = next((s for s in d["streams"] if s["codec_type"] == "audio"), None)
    return {"duration_s": round(float(d["format"]["duration"]), 3), "size_bytes": int(d["format"]["size"]),
            "width": v.get("width"), "height": v.get("height"), "fps": v.get("r_frame_rate"), "vcodec": v.get("codec_name"),
            "audio": bool(a), "acodec": a.get("codec_name") if a else None, "channels": a.get("channels") if a else None}
