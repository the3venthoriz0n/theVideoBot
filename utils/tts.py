import pyttsx3, sys
sys.path.append('venv\Lib')


def text_to_speech(text):

    # Initialize the pyttsx3 engine
    engine = pyttsx3.init()

    # Set properties for the engine
    engine.setProperty('rate', 185)  # Speed of speech in words per minute
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # 1 is female voice 0 is a bro

    # Convert text to speech using pyttsx3 and save as WAV file
    text = text #set input as the text
    engine.save_to_file(text, 'audio/ttsOut.wav')
    engine.runAndWait()

#text_to_speech("HELLO SLUT")