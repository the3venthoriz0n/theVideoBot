import random,os,re,shutil
from moviepy.editor import *  # import everything from moviepy
from moviepy.video.io.VideoFileClip import VideoFileClip
from utils.get_stock_video import *
from utils.script_generator import *


def upper_camel_case(input_str):  # format any input string into upperCamelCaseText
    # Split the string into words
    words = input_str.split()

    # Capitalize the first letter of each word and join them together
    upper_camel_case_str = ''.join([word.capitalize() for word in words])

    return upper_camel_case_str


# ---Video Creation

def create_video(prompt):  # TODO Clean up, maybe break into separate parts?
    gptOutput = format_script(gen_script_gpt(prompt))  # returns a tuple
    # davinciOutput = format_script(gen_script_davinci(prompt))

    script = gptOutput[0]  # first index in tuple
    keywords = gptOutput[1]  # second index

    print(f"\n---SCRIPT---\n\n{script}")
    print(f"\n---KEYWORDS---\n\n{', '.join(keywords)}")

    test_pexels_search(keywords)
    video_folder = "generated_videos"
    if os.path.exists(video_folder):
        shutil.rmtree(video_folder)
    os.makedirs(video_folder)

    sentences = re.split(r'(?<=\.)\s+', script)
    video_clips = []
    used_video_urls = set()

    for idx, sentence in enumerate(sentences):  # TODO clean this messy code up
        video_url = None
        while video_url is None and keywords:
            keyword = keywords.pop(0)
            attempts = 0
            while attempts < 10:
                candidate_video_url = get_stock_video(keyword)
                if candidate_video_url and candidate_video_url not in used_video_urls:
                    video_url = candidate_video_url
                    used_video_urls.add(video_url)
                    break
                attempts += 1

            if video_url:
                break

        if video_url:
            video_name = f"scene_{idx + 1}.mp4"
            save_path = os.path.join(video_folder, video_name)
            download_video_file(video_url, save_path)
            clip = VideoFileClip(save_path)
            video_clips.append(clip)

    if video_clips:
        def split_into_phrases(text, max_words):
            words = text.split()
            phrases = [' '.join(words[i:i + max_words])
                       for i in range(0, len(words), max_words)]
            return phrases

        max_words_per_caption = 4
        captions_text = split_into_phrases(script, max_words_per_caption)
        captions = []
        total_duration = 0
        video_width = 720
        # Adjust this value to set the maximum width for the captions
        caption_width = int(video_width * 0.9)

        for i, caption_text in enumerate(captions_text):
            # What does this mean? 8 words per minute?
            caption_duration = 0.1 * len(caption_text.split()) + .8
            start_time = total_duration
            end_time = start_time + caption_duration

            caption = TextClip(caption_text, fontsize=68, color='rgb(255, 213, 0)', align='center', bg_color='rgba(0, 0, 0, 0.55)',
                               font="Nunito-ExtraBold.ttf", size=(caption_width, None), method="caption")  # please keep this note 237, 205, 0
            caption = caption.set_position(('center', 'center')).set_duration(
                caption_duration).set_start(start_time)

            captions.append(caption)
            total_duration += caption_duration
        clip_duration = total_duration / \
            len(video_clips)  # set audio length to

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

        def format_duration(duration):  # Format a messy duration into H:M:S
            hours = int(duration / 3600)
            minutes = int((duration % 3600) / 60)
            seconds = int(duration % 60)
            padding = int(1) + seconds

            return f"{hours:02}:{minutes:02}:{padding:02}"

        def add_audio(videoclip):

            # format audio duration to H:M:S
            audioLength = format_duration(total_duration)
            print("Adding audio to video...")

            dir_path = "audio/"  # Set the path for music
            # Get a list of all files in the directory
            files = os.listdir(dir_path)

            if files:  # If files exist
                random_file = random.choice(files)  # pick a random file in dir
                # choose that file, set to length of video
                audioclip = AudioFileClip(
                    dir_path + random_file).set_duration(audioLength)
            else:
                print("Directory is empty")

            new_audioclip = CompositeAudioClip([audioclip])
            videoclip.audio = new_audioclip
            # Volume factor, 25 percent volume
            videoclip = videoclip.volumex(.25)
            videoclip.write_videofile(
                (upper_camel_case(prompt)+".mp4"))

            print("Audio is complete!")
            return

        resized_video_clips = [resize_clip(clip).subclip(
            0, clip_duration) for clip in video_clips]
        final_video = concatenate_videoclips(
            resized_video_clips, method="compose")
        final_video_with_captions = CompositeVideoClip(
            [final_video] + captions, size=(720, 1280)).set_duration(total_duration)
        add_audio(final_video_with_captions)  # add audio to video

        print("Video creation complete!")
    else:
        print("No valid video URLs found for any of the script sentences.")
    return
