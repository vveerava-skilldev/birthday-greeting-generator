import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import random
import time

st.set_page_config(page_title="Birthday Card Generator", page_icon="🎂")

st.title("🎂 Birthday Card Generator")

# -------------------------------
# Inputs
# -------------------------------
name = st.text_input("Enter Friend's Name")

style = st.selectbox(
    "Select Style",
    ["Fun", "Minimal", "Modern", "Friendship"]
)

# -------------------------------
# Text Generator
# -------------------------------
def generate_messages(name):
    templates = [
        f"Happy Birthday {name}! Wishing you lots of happiness and smiles. 🎉\nYour lovingly - Thanu",
        f"Hey {name}, hope your day is filled with joy and laughter! 🎂\nYour lovingly - Thanu",
        f"{name}, another year, more memories! Have a wonderful birthday! 🎈\nYour lovingly - Thanu",
        f"Happy Birthday {name}! Keep shining and smiling always 😊\nYour lovingly - Thanu",
        f"Dear {name}, wishing you a calm and beautiful year ahead 🌸\nYour lovingly - Thanu"
    ]
    return random.sample(templates, 3)

# -------------------------------
# Pollinations Image (Primary)
# -------------------------------
def generate_image(prompt):
    try:
        url = f"https://image.pollinations.ai/prompt/{prompt}"
        response = requests.get(url, timeout=8)

        if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
            return Image.open(BytesIO(response.content))
    except:
        pass

    return None

# -------------------------------
# Backup Image (Always works)
# -------------------------------
def fallback_image():
    try:
        url = "https://picsum.photos/512"
        response = requests.get(url)
        return Image.open(BytesIO(response.content))
    except:
        return Image.new("RGB", (512, 512), "lightblue")

# -------------------------------
# Final Image Fetcher
# -------------------------------
def get_image(prompt):
    img = generate_image(prompt)

    if img:
        return img

    st.warning("⚠️ AI image unavailable, using backup image")
    return fallback_image()

# -------------------------------
# Card Creator (Improved Layout)
# -------------------------------
def create_card(image, text):
    image = image.resize((512, 512))

    card = Image.new("RGB", (512, 720), "white")
    card.paste(image, (0, 0))

    draw = ImageDraw.Draw(card)

    try:
        font = ImageFont.truetype("arial.ttf", 22)
    except:
        font = ImageFont.load_default()

    # Wrap text
    words = text.split()
    lines = []
    line = ""

    for word in words:
        if len(line + word) < 38:
            line += word + " "
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    y_text = 530
    for line in lines:
        draw.text((20, y_text), line, fill="black", font=font)
        y_text += 28

    return card

# -------------------------------
# Generate Button
# -------------------------------
if st.button("Generate Cards"):

    if not name:
        st.warning("Please enter a name")
    else:
        messages = generate_messages(name)

        for i, msg in enumerate(messages):
            st.subheader(f"🎉 Option {i+1}")

            prompt = f"{style} birthday card for {name}, soft colors, aesthetic, clean design"

            img = get_image(prompt)

            st.image(img, caption="Generated Image")

            st.write(msg)

            # Create final card
            card = create_card(img, msg)

            buf = BytesIO()
            card.save(buf, format="PNG")

            st.download_button(
                label="📥 Download Card",
                data=buf.getvalue(),
                file_name=f"{name}_birthday_card_{i+1}.png",
                mime="image/png"
            )
