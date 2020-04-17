import pickle, os, random
from pydub import AudioSegment


def create_audio(filepath, ID):
    VOLUME = 70
    VOICE = "ScanSoft Daniel_Full_22kHz"
    os.system(f"balcon -n \"{VOICE}\" -t \"r slash ask reddit by Robotainment\" -v {VOLUME} -w \"intro.wav\"")
    music = random.choice(os.listdir("music/"))
    music = AudioSegment.from_mp3(f"music/{music}")
    music -= 25
    music = music
    audio = AudioSegment.from_wav("intro.wav")
    tvsound = AudioSegment.from_mp3("sounds/tvsound.mp3")
    tvsound -= 20
    silence = AudioSegment.from_mp3("sounds/silence.mp3")
    audio += silence
    with open(filepath, "rb") as f:
        x = pickle.load(f)
        print(x)
        for i, val in enumerate(x):
            print(f"Processing file {i+1} out of {len(x)}..")
            if val == 1:
                audio = audio + tvsound
            elif val == 2:
                audio = audio + silence
            else:
                os.system(f"balcon -n \"{VOICE}\" -t \"{val}\" -v {VOLUME} -w \"files/{i}.wav\"")
                s = AudioSegment.from_wav(f"files/{i}.wav")
                os.remove(f"files/{i}.wav")
                audio = audio + s
    audio += tvsound
    os.system(f"balcon -n \"{VOICE}\" -t \"Like and subscribe for good luck, you handsome gentleman.   AY....\" -v {VOLUME} -w \"outro.wav\"")
    outro = AudioSegment.from_wav("outro.wav")
    audio += outro
    audio = audio.overlay(music, times=300)
    audio.export(f"audio_files/{ID}.mp3", format="mp3")
    return f"audio_files/{ID}.mp3"
