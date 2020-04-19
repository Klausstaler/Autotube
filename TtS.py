import pickle, os, random
from pydub import AudioSegment
from PIL import Image

s = "https://superuser.com/questions/617392/ffmpeg-image-sequence-with-various-durations"
# ffmpeg -i script.ffconcat -i audio_files/test.mp3 -c:a copy -c:v libx264 -pix_fmt yuv420p -vf fps=25 out.mp4

tvsound = AudioSegment.from_mp3("resources/sounds/tvsound.mp3")
tvsound -= 20
tvsound = tvsound[:750]
silence = AudioSegment.from_mp3("resources/sounds/silence.mp3")
VOLUME = 70
VOICE = "ScanSoft Daniel_Full_22kHz"


def create_video(filepath, ID):
    os.system(f"balcon -n \"{VOICE}\" -t \"r slash ask reddit by Robotainment\" -v {VOLUME} -w \"files/0.wav\"")
    concat = open("script.ffconcat", "w")
    concat.write("ffconcat version 1.0\n")
    music = random.choice(os.listdir("resources/music/"))
    music = AudioSegment.from_mp3(f"resources/music/{music}")
    music -= 25
    audio = AudioSegment.from_wav("files/0.wav")
    audio += silence
    concat.write(f"file resources/images/outro.png\nduration {round(len(audio) / 1000, 2)}\n")
    with open(filepath, "rb") as f:
        x = pickle.load(f)
        print(x)
        for i, val in enumerate(x):
            print(f"Processing file {i + 1} out of {len(x)}..")
            audio += create_audio_img(val, concat)
    audio += tvsound
    concat.write(f"file resources/images/tv.png\nduration {round(len(tvsound) / 1000, 2)}\n")
    os.system(
        f"balcon -n \"{VOICE}\" -t \"Like and subscribe for good luck, you handsome gentleman.   ....\" -v {VOLUME} -w \"outro.wav\"")
    outro = AudioSegment.from_wav("outro.wav")
    audio += outro
    concat.write(f"file resources/images/outro.png\nduration {round(len(outro) / 1000, 2)}\n")
    concat.close()
    audio = audio.overlay(music, times=300)
    audio.export(f"audio_files/{ID}.mp3", format="mp3")
    os.system(
        f"ffmpeg -i script.ffconcat -i audio_files/{ID}.mp3 -c:a copy -c:v libx264 -pix_fmt yuv420p -vf fps=25 videos/{ID}.mp4")
    os.remove(f"audio_files/{ID}.mp3")
    os.remove("script.ffconcat")
    return f"videos/{ID}.mp4"


def create_audio_img(val, concat):
    if val[0] == -1:
        concat.write(f"file resources/images/tv.png\nduration {round(len(tvsound) / 1000, 2)}\n")
        return tvsound
    elif val[0] == -2:
        return silence
    else:
        os.system(f"balcon -n \"{VOICE}\" -t \"{val[1]}\" -v {VOLUME} -w \"files/temp.wav\"")
        s = AudioSegment.from_wav("files/temp.wav")
        os.remove("files/temp.wav")
        put_img(f"screenshots/{val[0]}.png", f"images/{val[0]}.png")
        concat.write(f"file images/{val[0]}.png\nduration {round((len(s)) / 1000, 2)}\n")
        return s


def put_img(path, savepath):
    background = Image.open("resources/images/background.jpg")
    bg_w, bg_h = background.size
    img = Image.open(path, "r")
    img_w, img_h = img.size
    new_w_fac = bg_w/(2*img_w)
    new_h_fac = bg_h/(2*img_h)
    fac = min([new_h_fac, new_w_fac,1])
    print(fac)
    img = img.resize((int(img_w*fac), int(img_h*fac)))
    img_w, img_h = img.size
    offset = ((bg_w - img_w) // 2, (bg_h - img_h) // 2)
    background.paste(img, offset)
    background.save(savepath)
