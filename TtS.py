import pickle
from pydub import AudioSegment
import os

VOLUME = 70
VOICE = "ScanSoft Daniel_Full_22kHz"

os.system(f"balcon -n \"{VOICE}\" -t \"r slash ask reddit by Robottainment\" -v {VOLUME} -w \"intro.wav\"")
music = AudioSegment.from_mp3("music/chilltrack1.mp3")
music -= 25
music = music
audio = AudioSegment.from_wav("intro.wav")
tvsound = AudioSegment.from_mp3("sounds/tvsound.mp3")
tvsound -= 20
silence = AudioSegment.from_mp3("sounds/silence.mp3")
audio += silence
with open("ablzuq_28_3_2020.pkl","rb") as f:
    x = pickle.load(f)
    print(x)
    for i, val in enumerate(x):
        if val == 1:
            #playsound.playsound("tvsound.mp3")
            audio = audio + tvsound
        elif val == 2:
            #playsound.playsound("silence.mp3")
            audio = audio + silence
        else:
            #tts = gTTS(text=val, lang='en')
            os.system(f"balcon -n \"{VOICE}\" -t \"{val}\" -v {VOLUME} -w \"files/{i}.wav\"")
            #tts.save(f"files/{i}.mp3")
            #playsound.playsound(f"{i}.mp3")
            s = AudioSegment.from_wav(f"files/{i}.wav")
            audio = audio + s
audio = audio.overlay(music, times=300)
audio.export("full_audio_DANIEL.mp3", format="mp3")