import pyttsx3, sys, re, time
#import tortoise

def text_to_speech(text):

    # Initialize the pyttsx3 engine
    engine = pyttsx3.init()

    # Set properties for the engine
    engine.setProperty('rate', 172)  # Speed of speech in words per minute
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # 1 is female voice 0 is a bro

    # Convert text to speech using pyttsx3 and save as WAV file
    text = text #set input as the text
    engine.save_to_file(text, 'audio/ttsOut.wav')
    engine.runAndWait()


# def tortoise():

#     # Initialize the Tortoise object
#     tortoise = Tortoise()

#     # Set the voice and language
#     tortoise.voice = "Microsoft Zira Desktop - English (United States)"
#     tortoise.language = "en-US"

#     # Convert text to speech
#     tortoise.say("Hello, world!")

#     # Release the resources
#     tortoise.close()