import torchvision.io as io


def mute(f: str, out: str) -> None:
    video = io.read_video(f)
    fps = video[2]["video_fps"]
    print(f)
    print(out)
    io.write_video(video_array=video[0], filename=out, fps=fps)
