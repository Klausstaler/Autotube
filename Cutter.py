import os
from pydub import AudioSegment


def create_vid(audiopath):
    audio = AudioSegment.from_mp3(audiopath)
    os.system(
        f"ffmpeg -ss 0 -i cozy-hut-ambience-light-rain-sound-with-warm-fireplace.mp4 -t {len(audio) // 1000 + 1} -c copy videos/out.mp4")
    new_path = audiopath.split("/")[-1].split(".")[0]
    os.system(f"ffmpeg -i videos/out.mp4 -i {audiopath} -c:v copy -map 0:v:0 -map 1:a:0 videos/{new_path}.mp4")
    os.remove("videos\out.mp4")
    return f"videos/{new_path}.mp4"