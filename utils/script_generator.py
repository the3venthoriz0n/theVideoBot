import openai
from utils.tts import *

# ---SCRIPT Creation Via OpenAI

# Cache for video scripts
video_script_cache = {}

def gen_script_gpt(prompt): # TODO write another gpt role to generate keywords

    if prompt in video_script_cache:
        return video_script_cache[prompt]

    # Read the template from the file
    with open("behavior.txt", "r") as file:
        behavior = file.read()

    # Replace the placeholder with the user-defined prompt
    modified_prompt = behavior.format(prompt=prompt)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": behavior}, # This is how the bot behaves
            {"role": "user", "content": modified_prompt},
        ]
    )
    result = ''
    for choice in response.choices:
        result += choice.message.content
    return result,prompt

def gen_script_davinci(prompt): # This is the old method of generating video scripts
    if prompt in video_script_cache:
        return video_script_cache[prompt]

    # Read the template from the file
    with open("behavior.txt", "r") as file:
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

def format_script(scriptWPrompt): # TODO re-write this function, it's a little whack

    response_text = scriptWPrompt[0] # input is a tuple, this is first item of list. ("this is", "a", "tuple")
    prompt = scriptWPrompt[1]

    # Find the index of the "Keywords:" heading
    keywords_index = response_text.find("Keywords:") # this returns an index

    if keywords_index != -1: # if the index is non negative
        # Extract the script and keywords after the "Keywords:" heading
        video_script = response_text[:keywords_index].strip()
        keywords = response_text[keywords_index + len("Keywords:"):].strip().split(", ")
    else: #otherwise there are no keywords
        video_script = response_text
        keywords = []

    video_script_cache[prompt] = (video_script, keywords)
    text_to_speech(video_script) # Generate text to speech
    return video_script,keywords # return tuple

