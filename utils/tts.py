import pyttsx3


def text_to_speech(text):

    # Initialize the pyttsx3 engine
    engine = pyttsx3.init()

    # Set properties for the engine
    engine.setProperty('rate', 150)  # Speed of speech in words per minute
    engine.setProperty('volume', 1)  # Volume level between 0 and 1

    # Convert text to speech using pyttsx3 and save as WAV file
    text = text #set input as the text
    engine.save_to_file(text, 'audio/ttsOut.mp3')
    engine.runAndWait()

