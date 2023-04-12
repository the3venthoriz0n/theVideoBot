import os
import openai
import requests
import re
import shutil
from moviepy.editor import *

# Set your API keys, make a file called api_key.txt and paste api keys
with open('api_key.txt', 'r') as f:
    OPENAI_API_KEY = f.readline().strip()
    PEXELS_API_KEY = f.readline().strip()

# Configure the OpenAI API client
openai.api_key = OPENAI_API_KEY

# Cache for video scripts
video_script_cache = {}

def get_stock_video(keyword):
    pexels_url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": keyword, "per_page": 5}

    response = requests.get(pexels_url, headers=headers, params=params)
    data = response.json()

    if data and "videos" in data and data["videos"]:
        video_url = data["videos"][0]["video_files"][0]["link"]
        return video_url

    return None

def test_pexels_search(keywords):
    for keyword in keywords:
        video_url = get_stock_video(keyword)
        if video_url:
            print(f"Keyword '{keyword}' found video: {video_url}")
        else:
            print(f"Keyword '{keyword}' did not find any video.")

def generate_video_script(prompt):
    if prompt in video_script_cache:
        return video_script_cache[prompt]

    modified_prompt = (
        f"Please generate a concise video script (60 seconds or less) about '{prompt}'. "
        f"Then, provide a list of 5 relevant nouns that will be easily searchable in a stock video API search. "
        f"Separate the script and the keywords with a line break.\n\n"
        f"Script:\n"
    )
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=modified_prompt,
        max_tokens=800,
        n=1,
        stop=None,
        temperature=0.6,
    )

    response_text = response.choices[0].text.strip()

    # Find the index of the "Keywords:" heading
    keywords_index = response_text.find("Keywords:")

    if keywords_index != -1:
        # Extract the script and keywords after the "Keywords:" heading
        video_script = response_text[:keywords_index].strip()
        keywords = response_text[keywords_index + len("Keywords:"):].strip().split(", ")
    else:
        video_script = response_text
        keywords = []

    video_script_cache[prompt] = (video_script, keywords)
    return video_script, keywords

def create_video(prompt):
    script, keywords = generate_video_script(prompt)
    print(f"Generated script:\n{script}")
    print(f"Generated keywords:\n{', '.join(keywords)}")

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
        while keywords:
            keyword = keywords.pop(0)
            attempts = 0
            while attempts < 5:
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
        # Split the script into phrases, not words
        phrases = re.split(r'(?<=\.)\s+|, |; |: |\? |\! |\(|\)', script)
        short_phrases = [phrase.strip() for phrase in phrases if phrase.strip()]

        captions = []
        total_duration = 0
        for i, phrase in enumerate(short_phrases):
            # Adjust caption_duration based on the length of the phrase
            caption_duration = 0.1 * len(phrase.split()) + 1
            start_time = total_duration
            end_time = start_time + caption_duration
            caption = TextClip(phrase, fontsize=60, color='white', align='center', bg_color="black", font="Nunito-ExtraBold.ttf")
            caption = caption.set_position(('center', 'center')).set_duration(caption_duration).set_start(start_time)
            captions.append(caption)
            total_duration += caption_duration

        clip_duration = total_duration / len(video_clips)
        
        def resize_clip(clip, size=(720, 1280)):
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

            cropped_clip = clip.crop(x1=crop_x, y1=crop_y, x2=crop_x + new_width, y2=crop_y + new_height)
            return cropped_clip.fx(vfx.resize, width=size[0], height=size[1])

        resized_video_clips = [resize_clip(clip).subclip(0, clip_duration) for clip in video_clips]
        final_video = concatenate_videoclips(resized_video_clips, method="compose")

        final_video_with_captions = CompositeVideoClip([final_video] + captions, size=(720, 1280)).set_duration(total_duration)
        final_video_with_captions.write_videofile("final_video.mp4", codec="libx264", audio_codec="aac")

        print("Video creation complete! Check the final_video.mp4 file.")
    else:
        print("No valid video URLs found for any of the script sentences.")

def download_video_file(url, save_path):
    response = requests.get(url, stream=True)

    with open(save_path, "wb") as f:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, f)

project_prompt = input("Enter your video prompt: ")
create_video(project_prompt)