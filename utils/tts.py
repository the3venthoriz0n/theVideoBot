import pyttsx3, sys
sys.path.append('venv\Lib')
import edge_tts
import asyncio

def text_to_speech(text):

    # Initialize the pyttsx3 engine
    #engine = pyttsx3.init()

    # Set properties for the engine
    #engine.setProperty('rate', 165)  # Speed of speech in words per minute
    #voices = engine.getProperty('voices')
    #engine.setProperty('voice', voices[1].id)  # 1 is female voice 0 is a bro


    TEXT = text

    VOICE = "en-GB-SoniaNeural" #soft spoken UK
    #VOICE = "en-US-SteffanNeural" #soft spoken chill US bro
    #VOICE = "uk-UA-PolinaNeural" #Russian accent chick
    #VOICE = "zh-CN-XiaoxiaoNeural" #try this voice


    OUTPUT_FILE = "audio/ttsOut.mp3"

    #edge-tts --rate=-50% --text "Hello, world!" --write-media hello_with_rate_halved.mp3

    async def _main() -> None:
        communicate = edge_tts.Communicate(TEXT, VOICE)
        await communicate.save(OUTPUT_FILE)

    #if name == "main":
    asyncio.get_event_loop().run_until_complete(_main())

    # Convert text to speech using pyttsx3 and save as WAV file
    #text = text #set input as the text
    #engine.save_to_file(text, 'audio/ttsOut.wav')
    #engine.runAndWait()

#text_to_speech("HELLO THERE")
