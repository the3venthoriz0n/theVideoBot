# Add text to speech code here

from pydub import AudioSegment
import pyttsx3

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1)
    engine.setProperty('voice', engine.getProperty('voices')[0].id)
    engine.save_to_file(text, 'output.mp3')
    engine.runAndWait()
    audio = AudioSegment.from_file("output.mp3", format="mp3")
    audio.export("output.mp3", format="mp3")

text = "This is a test of the text to speech system"
text_to_speech(text)
