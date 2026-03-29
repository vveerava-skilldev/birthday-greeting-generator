import streamlit as st
from openai import OpenAI
YOUR_API_KEY="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"

client = OpenAI(api_key="YOUR_API_KEY")

st.title("🎂 Birthday Greeting Generator")

# Input fields
name = st.text_input("Enter Friend's Name")

style = st.selectbox(
    "Select Style",
    ["Fun", "Minimal", "Modern", "Friendship"]
)

# Generate button
if st.button("Generate Greetings"):

    if name:
        prompt = f"""
        Generate 3 simple birthday messages for {name}.
        Include a friendly tone, not too dramatic.
        Each message should be unique.
        Avoid repeating themes.
        Occasionally suggest an animated-style idea.
        Add signature: "Your lovingly - Thanu".
        Style: {style}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini", #gpt-5-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        output = response.choices[0].message.content

        st.subheader("🎉 Greeting Options")
        st.write(output)

    else:
        st.warning("Please enter a name")
