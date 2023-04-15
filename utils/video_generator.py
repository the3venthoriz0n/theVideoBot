import os,re,shutil
from moviepy.editor import *
from moviepy.video.io.VideoFileClip import VideoFileClip
from utils.get_stock_video import *
from utils.script_generator import *
from utils.tts import *
from utils.overlay_audio import *


# Function to create a video based on a given prompt
def create_video(prompt):  #TODO get words per minute

    #toggle between script gen
    gptOutput = format_script(gen_script_gpt(prompt))  # returns a tuple
    # davinciOutput = format_script(gen_script_davinci(prompt))

    # Assign formatted script and keywords
    script = gptOutput[0]  # first index in tuple
    keywords = gptOutput[1]  # second index

    # Print the script and keywords
    print(f"\n---SCRIPT---\n\n{script}")
    print(f"\n---KEYWORDS---\n\n{', '.join(keywords)}")

    # Test Pexels search with the given keywords
    test_pexels_search(keywords)

    # Set up the video folder and remove any existing files
    video_folder = "generated_videos" #TODO make this a hidden folder
    if os.path.exists(video_folder):
        shutil.rmtree(video_folder)
    os.makedirs(video_folder)

    # Split the script into sentences
    sentences = re.split(r'(?<=\.)\s+', script)

    # Initialize variables for video clips and used video URLs
    video_clips = []
    used_video_urls = set()

    # Download and process video clips for each sentence in the script
    for idx, sentence in enumerate(sentences):  # TODO this does not rotate through keywords?
        # Try to find a stock video for each keyword
        video_url = None
        while video_url is None and keywords:
            keyword = keywords.pop(0)
            attempts = 0
            # Check for a valid video URL that hasn't been used
            while attempts < 10:
                candidate_video_url = get_stock_video(keyword)
                if candidate_video_url and candidate_video_url not in used_video_urls:
                    video_url = candidate_video_url
                    used_video_urls.add(video_url)
                    break
                attempts += 1
            # If a valid video URL is found, break the loop
            if video_url:
                break
        # Download and process the video clip if a URL is found
        if video_url:
            video_name = f"scene_{idx + 1}.mp4"
            save_path = os.path.join(video_folder, video_name)
            download_video_file(video_url, save_path)
            clip = VideoFileClip(save_path)
            video_clips.append(clip)
    # If video clips are found, create the final video
    if video_clips:
        # Function to split text into phrases with a maximum number of words
        def split_into_phrases(text, max_words):
            words = text.split()
            phrases = [' '.join(words[i:i + max_words])
                       for i in range(0, len(words), max_words)]
            return phrases
        # Prepare captions for the video
        max_words_per_caption = 4
        captions_text = split_into_phrases(script, max_words_per_caption)
        captions = []
        total_duration = 0
        video_width = 720
        # Adjust this value to set the maximum width for the captions
        caption_width = int(video_width * 0.9)

        for i, caption_text in enumerate(captions_text):
            # Increase caption_duration by 0.5 if there's a period in the caption
            extra_duration = 0.5 if '.' in caption_text else 0

            caption_duration = 0.1 * len(caption_text.split()) + 0.8 + extra_duration
            start_time = total_duration
            end_time = start_time + caption_duration

            #TODO add font folder
            caption = TextClip(caption_text, fontsize=68, color='rgb(255, 213, 0)', align='center', bg_color='rgba(0, 0, 0, 0.55)',
                               font="Nunito-ExtraBold.ttf", size=(caption_width, None), method="caption")  # please keep this note 237, 205, 0
            caption = caption.set_position(('center', 'center')).set_duration(
                caption_duration).set_start(start_time)

            captions.append(caption)
            total_duration += caption_duration
        clip_duration = total_duration / len(video_clips)  # set audio length to
       
        # Function to resize video clips to a target size
        def resize_clip(clip, size=(720, 1280)):  # this is a nested function
            aspect_ratio = clip.size[0] / clip.size[1]
            target_aspect_ratio = size[0] / size[1]

            if aspect_ratio > target_aspect_ratio:  # landscape aspect ratio
                new_width = int(clip.size[1] * target_aspect_ratio)
                new_height = clip.size[1]
            else:  # portrait aspect ratio
                new_width = clip.size[0]
                new_height = int(clip.size[0] / target_aspect_ratio)

            crop_x = (clip.size[0] - new_width) // 2
            crop_y = (clip.size[1] - new_height) // 2

            cropped_clip = clip.crop(
                x1=crop_x, y1=crop_y, x2=crop_x + new_width, y2=crop_y + new_height)
            return cropped_clip.fx(vfx.resize, width=size[0], height=size[1])
        
        # Resize and concatenate video clips
        resized_video_clips = [resize_clip(clip).subclip(0, clip_duration) for clip in video_clips]
        final_video = concatenate_videoclips(resized_video_clips, method="compose")
        
        # Combine video clips with captions
        final_video_with_captions = CompositeVideoClip(
            [final_video] + captions, size=(720, 1280)).set_duration(total_duration)
        
        #audio options change to true if you want audio, false if you dont
        vidAudio = True;
        if vidAudio:
            add_audio(final_video_with_captions,total_duration,prompt)  # combine audio and add video
        else:
            final_video_with_captions.write_videofile(f"{'-'.join(prompt.split())}.mp4", codec="libx264", audio_codec="aac", audio=False)
        
        print("Video creation complete!")
    else:
        print("No valid video URLs found for any of the script sentences.")
    return
