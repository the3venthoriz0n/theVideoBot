# theVideoBot

Welcome! Here are basic steps to get up an running


# Retrieve API Keys

OpenAI
Pexels
Pixabay

Create a file called "api_key.txt" and paste the api keys respectively on lines 1,2,3 etc.

## Install Python

https://www.python.org/downloads/

### Add Python to PATH

setx PATH "%PATH%;C:\Python34\Scripts" or setx PATH "%PATH%;C:\Users\[yourUser]\AppData\Local\Programs\Python\Python311\Scripts"

## Install Virtual Environment

`pip install virtualenv`
`python -m venv [yourVirtualEnvNameHere]`

## Activate the Virtual Environment

`.\venv\Scripts\Activate.ps1` (Windows Powershell)
`.\venv\Scripts\Activate.bat` (Windows CMD)

# Install Requirements

`pip install -r requirements.txt`

install imagemagick making sure to check "Install legacy utilities (e.g. convert)

https://imagemagick.org/script/download.php#windows

Version	                                    Description
ImageMagick-7.1.1-6-Q16-HDRI-x64-dll.exe	Win64 dynamic at 16 bits-per-pixel component with High-dynamic-range imaging enabled


## View API usage for OpenAI

https://platform.openai.com/account/usage


## Troubleshooting

### Git

`git merge --abort`