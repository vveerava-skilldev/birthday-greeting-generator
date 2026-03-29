import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
import random

st.set_page_config(page_title="Animated Birthday Cards", page_icon="🎂")

st.title("🎂 Animated Birthday Card Generator")

# -------------------------------
# Inputs
# -------------------------------
name = st.text_input("Enter Friend's Name")

style = st.selectbox(
    "Select Style",
    ["Fun", "Minimal", "Modern", "Friendship"]
)

# -------------------------------
# Animated GIF Backgrounds (FREE)
# -------------------------------
GIFS = {
    "Fun": [
        "https://media.giphy.com/media/3o6ZtpxSZbQRRnwCKQ/giphy.gif",
        "https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif"
    ],
    "Minimal": [
        "https://media.giphy.com/media/26ufdipQqU2lhNA4g/giphy.gif"
    ],
    "Modern": [
        "https://media.giphy.com/media/3o7TKtnuHOHHUjR38Y/giphy.gif"
    ],
    "Friendship": [
        "https://media.giphy.com/media/3o7btPCcdNniyf0ArS/giphy.gif"
    ]
}

def get_gif(style):
    return random.choice(GIFS.get(style, GIFS["Fun"]))

# -------------------------------
# Messages (Stylish + Clean)
# -------------------------------
def generate_messages(name):
    messages = [
        f"🎉 Happy Birthday {name}!\nWishing you endless smiles and happiness.\n\n💖 Your lovingly - Thanu",

        f"🎂 Dear {name},\nMay your day be calm, joyful and full of love.\n\n🌸 Your lovingly - Thanu",

        f"🎈 Hey {name}!\nCelebrate today, cherish always, smile forever.\n\n✨ Your lovingly - Thanu",

        f"🌟 Happy Birthday {name}!\nKeep shining and spreading positivity.\n\n💫 Your lovingly - Thanu"
    ]
    return random.sample(messages, 3)

# -------------------------------
# Create Card Image
# -------------------------------
def create_card(text):
    card = Image.new("RGB", (600, 400), "white")
    draw = ImageDraw.Draw(card)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()

    lines = text.split("\n")
    y = 80

    for line in lines:
        draw.text((40, y), line, fill="black", font=font)
        y += 40

    return card

# -------------------------------
# Generate Button
# -------------------------------
if st.button("✨ Generate Animated Cards"):

    if not name:
        st.warning("Please enter a name")
    else:
        messages = generate_messages(name)

        for i, msg in enumerate(messages):
            st.subheader(f"🎉 Option {i+1}")

            # Show animated GIF
            gif_url = get_gif(style)
            st.image(gif_url, caption="🎬 Animated Background")

            # Show styled message
            st.markdown(f"### 💌 Message\n{msg}")

            # Create downloadable card (static)
            card = create_card(msg)

            buf = BytesIO()
            card.save(buf, format="PNG")

            st.download_button(
                label="📥 Download Card",
                data=buf.getvalue(),
                file_name=f"{name}_card_{i+1}.png",
                mime="image/png"
            )
