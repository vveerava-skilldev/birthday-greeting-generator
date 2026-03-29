import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import requests
from io import BytesIO
import random
import imageio

st.set_page_config(page_title="🎂 Birthday Studio", page_icon="🎂")

st.title("🎂 Birthday Card + Music Generator")

# -------------------------------
# Inputs
# -------------------------------
name = st.text_input("Enter Friend's Name")

theme = st.selectbox(
    "Theme",
    ["Floral 🌸", "Party 🎈", "Elegant ✨", "Minimal 🎁"]
)

mode = st.radio(
    "Message Mode",
    ["🧠 Auto", "🎨 Custom"]
)

custom_msg = ""
if mode == "🎨 Custom":
    custom_msg = st.text_area("Enter message")

music_style = st.selectbox(
    "Music Style",
    ["Fun 🎉", "Emotional 💖", "Rap 🎤", "Classic 🎼"]
)

# -------------------------------
# GIF Backgrounds
# -------------------------------
GIFS = [
    "https://media.giphy.com/media/3o6ZtpxSZbQRRnwCKQ/giphy.gif",
    "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif",
    "https://media.giphy.com/media/3o7TKtnuHOHHUjR38Y/giphy.gif"
]

def get_gif():
    return random.choice(GIFS)

# -------------------------------
# Smart Messages
# -------------------------------
def smart_messages(name, theme):
    base = [
        f"Happy Birthday {name}!",
        f"Hey {name}!",
        f"Dear {name},"
    ]

    lines = [
        "Wishing you happiness and smiles",
        "Celebrate today and enjoy every moment",
        "Keep shining always"
    ]

    sign = "💖 Your lovingly - Thanu"

    return [f"{random.choice(base)}\n{random.choice(lines)}\n\n{sign}"]

# -------------------------------
# Lyrics Generator
# -------------------------------
def generate_lyrics(name, style):
    return f"""
🎶 Happy Birthday {name} 🎶

Today is your special day,
Smile bright in every way!
Dream big and shine so bright,
Celebrate with joy tonight!

💖 Your lovingly - Thanu
"""

# -------------------------------
# Music Links
# -------------------------------
MUSIC = {
    "Fun 🎉": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
    "Emotional 💖": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-2.mp3",
    "Rap 🎤": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-3.mp3",
    "Classic 🎼": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3"
}

# -------------------------------
# Decorations
# -------------------------------
def draw_decor(draw, w, h, theme):
    for _ in range(10):
        draw.text((random.randint(0,w), random.randint(0,h)), "✨")

# -------------------------------
# Create Animated GIF
# -------------------------------
def create_gif(gif_url, text, theme):
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
            [(20, frame.height-150), (frame.width-20, frame.height-20)],
            fill=(255,255,255,200)
        )

        lines = text.split("\n")
        y = frame.height - 140

        for line in lines:
            w = draw.textlength(line, font=font)
            x = (frame.width - w) // 2
            draw.text((x,y), line, fill="black", font=font)
            y += 30

        draw_decor(draw, frame.width, frame.height, theme)

        frames.append(frame.convert("P"))

    buf = BytesIO()
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=100,
        loop=0
    )
    buf.seek(0)
    return buf

# -------------------------------
# Convert GIF to Video
# -------------------------------
def gif_to_video(gif_bytes):
    gif = Image.open(gif_bytes)
    frames = []

    for frame in ImageSequence.Iterator(gif):
        frames.append(frame.convert("RGB"))

    video_path = "/mnt/data/output.mp4"

    imageio.mimsave(video_path, frames, fps=10)

    return video_path

# -------------------------------
# Generate
# -------------------------------
if st.button("🚀 Generate"):

    if not name:
        st.warning("Enter name")
    else:
        msg = custom_msg if (mode=="🎨 Custom" and custom_msg) else smart_messages(name, theme)[0]

        gif_url = get_gif()
        st.image(gif_url, caption="Preview")

        gif_card = create_gif(gif_url, msg, theme)

        st.image(gif_card, caption="🎨 Animated Card")

        st.download_button("📥 Download GIF", gif_card, file_name="card.gif")

        # Lyrics
        lyrics = generate_lyrics(name, music_style)
        st.text_area("🎶 Lyrics", lyrics, height=200)

        st.audio(MUSIC[music_style])

        # Video
        video_file = gif_to_video(gif_card)

        st.video(video_file)

        with open(video_file, "rb") as f:
            st.download_button("📥 Download Video", f, file_name="birthday.mp4")
