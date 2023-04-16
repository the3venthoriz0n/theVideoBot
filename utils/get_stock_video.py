import openai,requests,shutil,random

# --API Init---
# Set your API keys, make a file called api_key.txt and paste api keys
with open('api_key.txt', 'r') as f:
    OPENAI_API_KEY = f.readline().strip()
    PEXELS_API_KEY = f.readline().strip()
    PIXABAY_API_KEY = f.readline().strip()

# Configure the OpenAI API client
openai.api_key = OPENAI_API_KEY


# this code is not called and does not run
def download_video_file(url, save_path):
    response = requests.get(url, stream=True)

    with open(save_path, "wb") as f:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, f)



# ---Stock Video---

def get_stock_video_pexels(keyword):
    pexels_url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": keyword, "per_page": 5, "min_width": 1920, "min_height": 1080}

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
        "min_width": 1920,
        "min_height": 1080,
    }

    response = requests.get(pixabay_url, params=params)
    data = response.json()

    if data and "hits" in data and data["hits"]:
        video = random.choice(data["hits"])
        video_url = video["videos"]["large"]["url"]
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
