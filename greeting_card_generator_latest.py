import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import requests
from io import BytesIO
import random
import tempfile
import os

from gtts import gTTS

from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

st.set_page_config(page_title="🎂 Birthday Studio", page_icon="🎂")

st.markdown("## 🎁 Personalized Birthday Song + Video Generator")
st.markdown("Enter a name → Get a custom song + video 🎶🎬")

# -------------------------------
# Input
# -------------------------------
name = st.text_input("Enter Name")

music_style = st.selectbox(
    "Music Style",
    ["Fun 🎉", "Emotional 💖", "Classic 🎼"]
)

# -------------------------------
# Music URLs
# -------------------------------
MUSIC = {
    "Fun 🎉": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "Emotional 💖": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "Classic 🎼": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3"
}

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
# Lyrics
# -------------------------------
def generate_lyrics(name):
    return f"""
🎶 Happy Birthday {name}! 🎶

Hey {name}, it's your special day,
Let's celebrate in a joyful way!
Clap your hands and sing out loud,
You're the brightest in the crowd!

Happy birthday to you,
All your dreams come true!
Keep shining every day,
In your own amazing way!

💖 From Thanu
"""

# -------------------------------
# Voice
# -------------------------------
def generate_voice(lyrics):
    tts = gTTS(text=lyrics, lang='en')

    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)

    return temp_audio.name

# -------------------------------
# Create frames
# -------------------------------
def create_frames(gif_url, text):
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
# Create video
# -------------------------------
def create_video(frames, voice_path, music_url):

    # download music
    music_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    music_data = requests.get(music_url).content
    with open(music_file.name, "wb") as f:
        f.write(music_data)

    video_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    video_path = video_temp.name

    frame_list = [f.convert("RGB") for f in frames]

    clip = ImageSequenceClip(frame_list, fps=10)

    voice = AudioFileClip(voice_path)
    music = AudioFileClip(music_file.name).volumex(0.2)

    final_audio = voice.set_audio(music)

    clip = clip.set_audio(final_audio)

    clip.write_videofile(
        video_path,
        codec="libx264",
        audio_codec="aac",
        verbose=False,
        logger=None
    )

    return video_path

# -------------------------------
# MAIN
# -------------------------------
if st.button("🎉 Generate Personalized Song + Video"):

    if not name:
        st.warning("Please enter a name")
    else:
        with st.spinner("✨ Creating your birthday magic..."):

            # lyrics
            lyrics = generate_lyrics(name)
            st.text_area("🎶 Your Song", lyrics, height=200)

            # voice
            voice_file = generate_voice(lyrics)

            # frames
            gif_url = get_gif()
            frames = create_frames(gif_url, lyrics)

            st.image(frames[0], caption="🎨 Preview")

            # video
            video_file = create_video(frames, voice_file, MUSIC[music_style])

            st.video(video_file)

            # download
            with open(video_file, "rb") as f:
                st.download_button(
                    "📥 Download Video",
                    f,
                    file_name=f"{name}_birthday.mp4"
                )

            # cleanup
            try:
                os.remove(video_file)
                os.remove(voice_file)
            except:
                pass

            st.success("🎉 Your video is ready!")
