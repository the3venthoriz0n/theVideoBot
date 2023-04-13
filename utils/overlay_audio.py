from pydub import AudioSegment
# AudioSegment.ffmpeg = "C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
# AudioSegment.converter = "C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"

def overlay_audio():

    sound1 = AudioSegment.from_mp3("audio/coniferous-forest-142569.mp3")
    sound2 = AudioSegment.from_mp3("audio/ttsOut.mp3")

    # sound1 6 dB louder
    #louder = sound1 + 6

    # Overlay sound2 over sound1 at position 0  (use louder instead of sound1 to use the louder version)
    overlay = sound1.overlay(sound2, position=0)


    # simple export
    overlayedAudio = overlay.export("audio/finalAudio.mp3", format="mp3")
    print("exported audio")

    return overlayedAudio



overlay_audio()