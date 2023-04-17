import os
import sys
import importlib

sys.path.append(r'C:\Users\torr6\anaconda3\tortoise-tts')


from tortoise.api import TextToSpeech

def generate_tts(text):
    tts = TextToSpeech()
    audio = tts.synthesize(text)
    audio.save("output.wav")