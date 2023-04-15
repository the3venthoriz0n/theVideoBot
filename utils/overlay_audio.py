from pydub import AudioSegment
from utils.video_generator import *
from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import random,os


def format_duration(duration):  # Format a messy duration into H:M:S
    hours = int(duration / 3600)
    minutes = int((duration % 3600) / 60)
    seconds = int(duration % 60)
    padding = int(1) + seconds

    return f"{hours:02}:{minutes:02}:{padding:02}"


def upper_camel_case(input_str):  # format any input string into upperCamelCaseText
    # Split the string into words
    words = input_str.split()

    # Capitalize the first letter of each word and join them together
    upper_camel_case_str = ''.join([word.capitalize() for word in words])

    return upper_camel_case_str

def add_audio(videoclip,duration,prompt):

    # format audio duration to H:M:S
    audioLength = format_duration(duration)
    print("Adding audio to video...")

    musicDir = "audio/music/"  # Set the path for music
    audioDir = "audio/"
    # Get a list of all files in the directory
    musicFiles = os.listdir(musicDir)

    if musicFiles:  # If files exist
        random_file = random.choice(musicFiles)  # pick a random file in dir
        
        musicAudio = AudioSegment.from_file(musicDir + random_file, format="mp3")
        ttsAudio = AudioSegment.from_file("audio/ttsOut.wav", format="wav")

        musicAudio = musicAudio - 15.0 # decrease audio by 10 db
        ttsAudio = ttsAudio - 1.0 # decrease volume 5 db

        # Overlay sound2 over musicAudio at position 0  (use louder instead of musicAudio to use the louder version)
        overlay = musicAudio.overlay(ttsAudio, position=0)

        # simple export
        overlay.export("audio/finalAudio.mp3", format="mp3")
        combinedAudio= AudioFileClip("audio/finalAudio.mp3").set_duration(audioLength)
    else:
        print("Directory is empty")

    new_audioclip = CompositeAudioClip([combinedAudio])
    videoclip.audio = new_audioclip
    # Volume factor, 25 percent volume
    videoclip = videoclip.volumex(.75)
    videoclip.write_videofile(
        (upper_camel_case(prompt)+".mp4")) #TODO make output dir for final videos
    
    os.remove('ttsOut.wav') #deletes the used tts audio file after the audio has been added to video
    os.remove('finalAudio.mp3') #deletes the last video audio
    
    print("Audio is complete!")
    return





#overlay_audio()