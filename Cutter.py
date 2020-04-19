import pickle, os, random
from pydub import AudioSegment
from PIL import Image

s = "https://superuser.com/questions/617392/ffmpeg-image-sequence-with-various-durations"


# ffmpeg -i script.ffconcat -i audio_files/test.mp3 -c:a copy -c:v libx264 -pix_fmt yuv420p -vf fps=25 out.mp4

def _put_img(path, savepath):
    background = Image.open("resources/images/background.jpg")
    bg_w, bg_h = background.size
    img = Image.open(path, "r")
    img_w, img_h = img.size
    new_w_fac = bg_w / (1.5 * img_w)
    new_h_fac = bg_h / (1.5 * img_h)
    fac = max(min([new_h_fac, new_w_fac]), 1)
    print(fac)
    img = img.resize((int(img_w * fac), int(img_h * fac)))
    img_w, img_h = img.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(img, offset)
    background.save(savepath)


class VideoSetup:
    def __init__(self, tv_vol_decr, music_vol_decr, voice_vol):
        self.voice_vol = voice_vol
        self.tvsound = AudioSegment.from_mp3("resources/sounds/tvsound.mp3")[:750]
        self.tvsound -= tv_vol_decr
        self.music = random.choice(os.listdir("resources/music/"))
        self.music = AudioSegment.from_mp3(f"resources/music/{self.music}")
        self.music -= music_vol_decr
        self.voice = "ScanSoft Daniel_Full_22kHz"
        self.silence = AudioSegment.from_mp3("resources/sounds/silence.mp3")

    def create_video(self, file_path, ID):
        concat = open("script.ffconcat", "w")
        concat.write("ffconcat version 1.0\n")
        os.system(
            f"balcon -n \"{self.voice}\" -t \"r slash ask reddit by Robotainment\" -v {self.voice_vol} -w \"tmp/audio_files/0.wav\"")
        audio = AudioSegment.from_wav("tmp/audio_files/0.wav")
        os.remove("tmp/audio_files/0.wav")
        audio += self.silence
        concat.write(f"file resources/images/outro.png\nduration {round(len(audio) / 1000, 2)}\n")
        with open(file_path, "rb") as f:
            x = pickle.load(f)
            print(x)
            for i, val in enumerate(x):
                print(f"Processing file {i + 1} out of {len(x)}..")
                audio += self.create_audio_img(val, concat)
        audio += self.tvsound
        concat.write(f"file resources/images/tv.png\nduration {round(len(self.tvsound) / 1000, 2)}\n")
        os.system(
            f"balcon -n \"{self.voice}\" -t \"Like and subscribe for good luck, you handsome gentleman.   ....\" -v {self.voice_vol} -w \"tmp/audio_files/outro.wav\"")
        outro = AudioSegment.from_wav("tmp/audio_files/outro.wav")
        os.remove("tmp/audio_files/outro.wav")
        audio += outro
        concat.write(f"file resources/images/outro.png\nduration {round(len(outro) / 1000, 2)}\n")
        concat.close()
        audio = audio.overlay(self.music, times=300)
        audio.export(f"tmp/audio_files/{ID}.mp3", format="mp3")
        os.system(
            f"ffmpeg -i script.ffconcat -i tmp/audio_files/{ID}.mp3 -c:a copy -c:v libx264 -pix_fmt yuv420p -vf fps=25 videos/{ID}.mp4")
        os.remove(f"tmp/audio_files/{ID}.mp3")
        os.remove("script.ffconcat")
        #self._cleanup()
        return f"videos/{ID}.mp4"

    def create_audio_img(self, val, concat):
        if val[0] == -1:
            concat.write(f"file resources/images/tv.png\nduration {round(len(self.tvsound) / 1000, 2)}\n")
            return self.tvsound
        elif val[0] == -2:
            return self.silence[:1]
        else:
            os.system(f"balcon -n \"{self.voice}\" -t \"{val[1]}\" -v {self.voice_vol} -w \"tmp/audio_files/tmp.wav\"")
            s = AudioSegment.from_wav("tmp/audio_files/tmp.wav")
            os.remove("tmp/audio_files/tmp.wav")
            _put_img(f"tmp/screenshots/{val[0]}.png", f"tmp/images/{val[0]}.png")
            concat.write(f"file tmp/images/{val[0]}.png\nduration {round((len(s)) / 1000, 2)}\n")
            return s

    def _cleanup(self):
        for img in os.listdir("tmp/images/"):
            os.remove(f"tmp/images/{img}")
        for img in os.listdir("tmp/screenshots/"):
            os.remove(f"tmp/screenshots/{img}")
