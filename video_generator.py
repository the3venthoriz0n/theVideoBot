
import random
import os, openai, requests, re, shutil, textwrap, subprocess
#import pyttsx3
import random, os, openai, requests, re, shutil, textwrap, subprocess
from moviepy.editor import * # import everything from moviepy
from moviepy.video.io.VideoFileClip import VideoFileClip
#from pydub import AudioSegment

'''
Welcome to our shitty project and always remember you can put a nice dress on an ugly gal!

'''

project_prompt = input("Enter your video prompt: ") #prompt users for input

#--API Init---
with open('api_key.txt', 'r') as f: # Set your API keys, make a file called api_key.txt and paste api keys
    OPENAI_API_KEY = f.readline().strip()
    PEXELS_API_KEY = f.readline().strip()
    PIXABAY_API_KEY = f.readline().strip()

# Configure the OpenAI API client
openai.api_key = OPENAI_API_KEY


#---Stock Video---

def get_stock_video_pexels(keyword):
    pexels_url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": keyword, "per_page": 5}

    response = requests.get(pexels_url, headers=headers, params=params)
    data = response.json()

    if data and "videos" in data and data["videos"]:
        video = random.choice(data["videos"])
        video_url = video["video_files"][0]["link"]
        print(f"Pexels: Found video for keyword '{keyword}'")
        return video_url

    print(f"Pexels: No video found for keyword '{keyword}'")
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
        print(f"Pixabay: Found video for keyword '{keyword}'")
        return video_url

    print(f"Pixabay: No video found for keyword '{keyword}'")
    return None

def get_stock_video(keyword):
    video_url = get_stock_video_pexels(keyword)
    if video_url is None:
        print(f"Switching to Pixabay for keyword '{keyword}'")
        video_url = get_stock_video_pixabay(keyword)
    return video_url

def test_pexels_search(keywords):
    for keyword in keywords:
        video_url = get_stock_video(keyword)
        if video_url:
            print(f"Keyword '{keyword}' found video: {video_url}")
        else:
            print(f"Keyword '{keyword}' did not find any video.")


# ---SCRIPT Creation Via OpenAI

# Cache for video scripts
video_script_cache = {}

def gen_script_gpt(prompt): # This function generates scripts with gpt
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You Generate Video Scripts for Youtube"}, # This is how the bot behaves
            {"role": "user", "content": prompt},
        ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content

    print(result)
    return result,prompt

def gen_script_davinci(prompt): # This is the old method of generating video scripts
    if prompt in video_script_cache:
        return video_script_cache[prompt]

    # Read the template from the file
    with open("template.txt", "r") as file:
        template = file.read()

    # Replace the placeholder with the user-defined prompt
    modified_prompt = template.format(prompt=prompt)

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=modified_prompt,
        max_tokens=800,
        n=1,
        stop=None,
        temperature=0.5,
    )

    response_text = response.choices[0].text.strip()
    return response_text,prompt

def format_script(scriptWPrompt): # This formats the script and generates keywords

    response_text = scriptWPrompt[0] # input is a tuple, this is first item of list. ("this is", "a", "tuple")
    prompt = scriptWPrompt[1]

    # Find the index of the last line break
    last_line_break_index = response_text.rfind('\n')

    if last_line_break_index != -1:
        # Extract the script and keywords after the last line break
        video_script = response_text[:last_line_break_index].strip()
        # TODO fix the keyword generation, stack etc.
        keywords = response_text[last_line_break_index:].strip().split(', ')
    else:
        video_script = response_text
        keywords = []

    # Find the index of the "Keywords:" heading
    keywords_index = response_text.find("Keywords:")

    if keywords_index != -1:
        # Extract the script and keywords after the "Keywords:" heading
        video_script = response_text[:keywords_index].strip()
        keywords = response_text[keywords_index +
                                 len("Keywords:"):].strip().split(", ")
    else:
        video_script = response_text
        keywords = []

    video_script_cache[prompt] = (video_script, keywords)
    return video_script, keywords


def generate_video_script_full(prompt): # this function determines what generates the script
    
    #return format_script(gen_script_davinci(prompt)) # Use old prompt generator
    return format_script(gen_script_gpt(prompt)) # Use GPT as prompt generator


def upper_camel_case(input_str): # format any input string into upperCamelCaseText
    # Split the string into words
    words = input_str.split()

    # Capitalize the first letter of each word and join them together
    upper_camel_case_str = ''.join([word.capitalize() for word in words])

    return upper_camel_case_str


def download_video_file(url, save_path): # this code is not called and does not run
    response = requests.get(url, stream=True)

    with open(save_path, "wb") as f:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, f)


# ---Video Creation

def create_video(prompt):
    #script, keywords = generate_video_script(prompt)
    script, keywords = generate_video_script_full(prompt)
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

    for idx, sentence in enumerate(sentences):#hello
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

        if video_url: #this code does not run?
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

        max_words_per_caption = 4
        captions_text = split_into_phrases(script, max_words_per_caption)
        captions = []
        total_duration = 0
        video_width = 720
        caption_width = int(video_width * 0.9)  # Adjust this value to set the maximum width for the captions

        for i, caption_text in enumerate(captions_text):
            caption_duration = 0.1 * len(caption_text.split()) + .8
            start_time = total_duration
            end_time = start_time + caption_duration

            caption = TextClip(caption_text, fontsize=68, color='rgb(255, 213, 0)', align='center', bg_color='rgba(0, 0, 0, 0.55)', font="Nunito-ExtraBold.ttf", size=(caption_width, None), method="caption") #please keep this note 237, 205, 0
            caption = caption.set_position(('center', 'center')).set_duration(caption_duration).set_start(start_time)

            captions.append(caption)
            total_duration += caption_duration
        clip_duration = total_duration / len(video_clips) # set audio length to
        
        def resize_clip(clip, size=(720, 1280)): #this is a nested function
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
        
        def format_duration(duration):
            hours = int(duration / 3600)
            minutes = int((duration % 3600) / 60)
            seconds = int(duration % 60)
            padding = int(1) + seconds

            return f"{hours:02}:{minutes:02}:{padding:02}"


        def add_audio(videoclip):

            audioLength = format_duration(total_duration) #format audio duration to H:M:S
            print("Adding audio to video...")
        
            dir_path = "The music/" # Set the path for music
            files = os.listdir(dir_path) # Get a list of all files in the directory

            if files: # If files exist
                random_file = random.choice(files) # pick a random file in dir
                audioclip = AudioFileClip(dir_path + random_file).set_duration(audioLength) # choose that file, set to length of video
            else:
                print("Directory is empty")

            new_audioclip = CompositeAudioClip([audioclip])
            videoclip.audio = new_audioclip
            videoclip = videoclip.volumex(.25)  # Volume factor, 25 percent volume
            videoclip.write_videofile((upper_camel_case(project_prompt)+".mp4"))

            print("Audio is complete!")
            return

        resized_video_clips = [resize_clip(clip).subclip(0, clip_duration) for clip in video_clips]
        final_video = concatenate_videoclips(resized_video_clips, method="compose")
        final_video_with_captions = CompositeVideoClip([final_video] + captions, size=(720, 1280)).set_duration(total_duration)
        add_audio(final_video_with_captions) #add audio to video

        print("Video creation complete!")
    else:
        print("No valid video URLs found for any of the script sentences.")


create_video(project_prompt)