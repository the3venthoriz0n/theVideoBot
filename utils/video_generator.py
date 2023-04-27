import os,re,shutil
from moviepy.editor import *
from moviepy.video.io.VideoFileClip import VideoFileClip
from utils.get_stock_video import *
from utils.script_generator import *
from utils.tts import *
from utils.overlay_audio import *
from utils.resize_and_crop_clip import *

# Function to create a video based on a given prompt
def create_video(prompt):
    gptOutput = format_script(gen_script_gpt(prompt))
    script = gptOutput[0]
    keywords = gptOutput[1]

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

    for idx, sentence in enumerate(sentences):
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

            # Add try-except block to handle invalid video files
            try:
                clip = VideoFileClip(save_path)
                resized_cropped_clip = resize_and_crop_clip(clip)
                video_clips.append(resized_cropped_clip)
            except Exception as e:
                print(f"Error while processing the video file {save_path}: {e}")
                continue

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
        caption_width = int(video_width * 0.9)

        for i, caption_text in enumerate(captions_text):
            caption_duration = 0.1 * len(caption_text.split()) + 0.8
            start_time = total_duration
            end_time = start_time + caption_duration

            caption = TextClip(caption_text, fontsize=68, color='rgb(255, 213, 0)', align='center', bg_color='rgba(0, 0, 0, 0.55)',
                               font="Nunito-ExtraBold.ttf", size=(caption_width, None), method="caption")
            caption = caption.set_position(('center', 'center')).set_duration(
                caption_duration).set_start(start_time)

            captions.append(caption)
            total_duration += caption_duration

        clip_duration = total_duration / len(video_clips)

        final_video = concatenate_videoclips(video_clips, method="compose")
        
        final_video_with_captions = CompositeVideoClip(
            [final_video] + captions, size=(720, 1280)).set_duration(total_duration)

        vidAudio = True
        if vidAudio:
            add_audio(final_video_with_captions, total_duration, prompt)
        else:
            final_video_with_captions.write_videofile(f"{'-'.join(prompt.replace(':', '_').split())}.mp4", codec="libx264", audio_codec="aac", audio=False)
        print("Video creation complete!")
    else:
        print("No valid video URLs found for any of the script sentences.")
    return
