import pickle, os, random
from pydub import AudioSegment
from pydub.exceptions import CouldntDecodeError
from PIL import Image
from Redditscraper import AudioType

def _put_img(path, savepath):
    background = Image.open("resources/images/background.jpg")
    bg_w, bg_h = background.size
    img = Image.open(path, "r")
    img_w, img_h = img.size
    scaling_fac = 1 if (img_w*1.3 >= bg_w or img_h*1.3 >= bg_h) else 1.3
    new_w_fac = bg_w / (scaling_fac*img_w)
    new_h_fac = bg_h / (scaling_fac*img_h)
    fac = min([new_h_fac, new_w_fac])
    img = img.resize((int(img_w * fac), int(img_h * fac)))
    img_w, img_h = img.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(img, offset)
    background.save(savepath)


class VideoSetup:
    def __init__(self, tv_vol_decr, music_vol_decr, voice_vol):
        self.voice_vol = voice_vol
        self.tv_sound = AudioSegment.from_mp3("resources/sounds/tvsound.mp3")[:750]
        self.tv_sound -= tv_vol_decr
        self.music = random.choice(os.listdir("resources/music/"))
        self.music = AudioSegment.from_mp3(f"resources/music/{self.music}")
        self.music -= music_vol_decr
        self.voice = "ScanSoft Daniel_Full_22kHz"
        self.silence = AudioSegment.from_mp3("resources/sounds/silence.mp3")

    def create_video(self, file_path, ID):
        concat = open("script.ffconcat", "w")
        concat.write("ffconcat version 1.0\n")
        audio = self._create_audio("r slash ask reddit by Rbotainment")
        audio += self.silence
        concat.write(f"file resources/images/outro.png\nduration {round(len(audio) / 1000, 2)}\n")
        with open(file_path, "rb") as f:
            x = pickle.load(f)
            print(x)
            for i, val in enumerate(x):
                print(f"Processing file {i + 1} out of {len(x)}..")
                audio += self.create_audio_img(val, concat)
        audio += self.tv_sound
        concat.write(f"file resources/images/tv.png\nduration {round(len(self.tv_sound) / 1000, 2)}\n")
        outro = self._create_audio("Like and subscribe for good luck, you handsome gentleman.   ....")
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
        if val[0] == AudioType.TVSOUND:
            concat.write(f"file resources/images/tv.png\nduration {round(len(self.tv_sound) / 1000, 2)}\n")
            return self.tv_sound
        elif val[0] == AudioType.SILENCE:
            return self.silence[:1]
        else:
            s = self._create_audio(val[1])
            img_path = f"tmp/images/{val[0]}.png"
            _put_img(f"tmp/screenshots/{val[0]}.png", img_path)
            concat.write(f"file {img_path}\nduration {round((len(s)) / 1000, 2)}\n")
            return s

    def _cleanup(self):
        for img in os.listdir("tmp/images/"):
            os.remove(f"tmp/images/{img}")
        for img in os.listdir("tmp/screenshots/"):
            os.remove(f"tmp/screenshots/{img}")

    def _create_audio(self, text):
        try:
            os.system(f"balcon -n \"{self.voice}\" -t \"{text}\" -v {self.voice_vol} -w \"tmp/audio_files/tmp.wav\"")
            s = AudioSegment.from_wav("tmp/audio_files/tmp.wav")
            os.remove("tmp/audio_files/tmp.wav")
        except CouldntDecodeError:
            return self._create_audio(text)  # simply retrying to decode works fine
        return s
