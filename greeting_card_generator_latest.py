import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import requests
from io import BytesIO
import random
import tempfile
import os

from moviepy.editor import ImageSequenceClip, AudioFileClip

st.set_page_config(page_title="🎂 Birthday Studio Pro", page_icon="🎂")

st.title("🎂 Birthday Card + Music + Video Generator")

# -------------------------------
# Inputs
# -------------------------------
name = st.text_input("Enter Name")

mode = st.radio("Message Mode", ["🧠 Auto", "🎨 Custom"])

custom_msg = ""
if mode == "🎨 Custom":
    custom_msg = st.text_area("Enter your message")

music_style = st.selectbox(
    "Music Style",
    ["Fun 🎉", "Emotional 💖", "Classic 🎼"]
)

# -------------------------------
# GIFs
# -------------------------------
GIFS = [
    "https://media.giphy.com/media/3o6ZtpxSZbQRRnwCKQ/giphy.gif",
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"
]

def get_gif():
    return random.choice(GIFS)

# -------------------------------
# Messages
# -------------------------------
def smart_msg(name):
    return f"""🎉 Happy Birthday {name}!
Wishing you joy, smiles and success!

💖 Your lovingly - Thanu"""

# -------------------------------
# Music URLs (FREE)
# -------------------------------
MUSIC = {
    "Fun 🎉": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "Emotional 💖": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "Classic 🎼": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
}

# -------------------------------
# Create GIF Card
# -------------------------------
def create_gif(gif_url, text):
    response = requests.get(gif_url)
    gif = Image.open(BytesIO(response.content))

    frames = []

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
    except:
        font = ImageFont.load_default()

    for frame in ImageSequence.Iterator(gif):
        frame = frame.convert("RGBA")
        draw = ImageDraw.Draw(frame)

        draw.rectangle(
            [(20, frame.height-160), (frame.width-20, frame.height-20)],
            fill=(255,255,255,200)
        )

        y = frame.height - 150
        for line in text.split("\n"):
            w = draw.textlength(line, font=font)
            x = (frame.width - w) // 2
            draw.text((x, y), line, fill="black", font=font)
            y += 35

        frames.append(frame)

    return frames

# -------------------------------
# Create Video with Audio 🎬🎶
# -------------------------------
def create_video(frames, audio_url):
    # Save audio temp
    audio_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    audio_path = audio_temp.name

    audio_data = requests.get(audio_url).content
    with open(audio_path, "wb") as f:
        f.write(audio_data)

    # Convert PIL frames → list of arrays
    frame_list = [frame.convert("RGB") for frame in frames]

    # Save video temp
    video_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video_path = video_temp.name

    # Create video
    clip = ImageSequenceClip([f for f in frame_list], fps=10)

    audio = AudioFileClip(audio_path).subclip(0, clip.duration)
    clip = clip.set_audio(audio)

    clip.write_videofile(video_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)

    return video_path, audio_path

# -------------------------------
# Generate
# -------------------------------
if st.button("🚀 Generate"):

    if not name:
        st.warning("Enter name")
    else:
        msg = custom_msg if (mode=="🎨 Custom" and custom_msg) else smart_msg(name)

        gif_url = get_gif()

        st.image(gif_url, caption="Preview")

        frames = create_gif(gif_url, msg)

        # Show first frame preview
        st.image(frames[0], caption="🎨 Card Preview")

        # Create video
        video_file, audio_file = create_video(frames, MUSIC[music_style])

        # Show video
        st.video(video_file)

        # Download
        with open(video_file, "rb") as f:
            st.download_button("📥 Download Video", f, file_name="birthday.mp4")

        # Cleanup
        try:
            os.remove(video_file)
            os.remove(audio_file)
        except:
            pass
