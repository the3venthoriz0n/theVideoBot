import os
import openai
import requests
import re
import shutil
import textwrap
import random
from moviepy.editor import *

# Set your API keys, make a file called api_key.txt and paste api keys
with open('api_key.txt', 'r') as f:
    OPENAI_API_KEY = f.readline().strip()
    PEXELS_API_KEY = f.readline().strip()
    PIXABAY_API_KEY = f.readline().strip()

# Configure the OpenAI API client
openai.api_key = OPENAI_API_KEY

# Cache for video scripts
video_script_cache = {}

def get_stock_video(keyword):
    video_url = get_stock_video_pexels(keyword)
    if video_url is None:
        video_url = get_stock_video_pixabay(keyword)
    return video_url

def get_stock_video_pexels(keyword):
    pexels_url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": keyword, "per_page": 5}

    response = requests.get(pexels_url, headers=headers, params=params)
    data = response.json()

    if data and "videos" in data and data["videos"]:
        video = random.choice(data["videos"])
        video_url = video["video_files"][0]["link"]
        return video_url

    return None

def get_stock_video_pixabay(keyword):
    pixabay_url = "https://pixabay.com/api/videos/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": keyword,
        "per_page": 5,
    }

    response = requests.get(pixabay_url, params=params)
    data = response.json()

    if data and "hits" in data and data["hits"]:
        video = random.choice(data["hits"])
        video_url = video["videos"]["medium"]["url"]
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
        f"Craft a captivating, informative, and emotional video script using this:'{prompt}' as a base. Have an expressive, positive tone. End with a call to subscribe for more content"
        f"Then, Please provide a list of 5 versatile and captivating nouns that can be used to search for engaging stock videos across various topics. These nouns should be general enough to yield interesting results when used in a stock video API search, while still being visually appealing and relevant to a diverse range of subjects. Make sure to separate the nouns with spaces so that multiple nouns are not percieved as one."
        f"Separate the script and the keywords with a line break, do not add subscribe to the list of keywords.\n\n"
        f"Script:\n"
    )
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=modified_prompt,
        max_tokens=800,
        n=1,
        stop=None,
        temperature=0.9,
    )

    response_text = response.choices[0].text.strip()

    # Find the index of the last line break
    last_line_break_index = response_text.rfind('\n')

    if last_line_break_index != -1:
        # Extract the script and keywords after the last line break
        video_script = response_text[:last_line_break_index].strip()
        keywords = response_text[last_line_break_index:].strip().split(', ')
    else:
        video_script = response_text
        keywords = []


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
            phrases = [' '.join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
            return phrases

        max_words_per_caption = 3
        captions_text = split_into_phrases(script, max_words_per_caption)

        captions = []
        total_duration = 0
        for i, caption_text in enumerate(captions_text):
            caption_duration = 0.1 * len(caption_text.split()) + .5
            start_time = total_duration
            end_time = start_time + caption_duration
            caption = TextClip(caption_text, fontsize=50, color='white', align='center', bg_color="black", font="Nunito-ExtraBold.ttf")
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
        final_video_with_captions.write_videofile(f"{'-'.join(prompt.split())}.mp4", codec="libx264", audio_codec="aac", audio=False)

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