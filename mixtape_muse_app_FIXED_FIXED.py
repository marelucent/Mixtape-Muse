
import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import openai
import os
from dotenv import load_dotenv
import speech_recognition as sr
import webbrowser

# Load environment variables
load_dotenv()

# Spotify authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
))

# OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Interpret prompt with GPT
def interpret_with_gpt(prompt):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a poetic translator. When given a symbolic or emotional prompt, respond with a single Spotify-friendly search phrase that will return playlists. Use real musical genres, moods, or short descriptive tags like 'dream pop', 'ambient folk', 'cinematic chill', 'sunset indie', or 'emotional lofi'. Do not use full sentences or quotes. Just return the search phrase."},
            {"role": "user", "content": f"My mood is: {prompt}"}
        ]
    )
    return response.choices[0].message.content.strip()

# Voice capture and transcription
def capture_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Speak now...")
        audio = recognizer.listen(source, phrase_time_limit=5)
    try:
        st.success("📝 Transcribing...")
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        st.error("❌ Sorry, I couldn't understand that.")
        return ""
    except sr.RequestError:
        st.error("⚠️ Couldn't reach the speech service.")
        return ""

# Search Spotify playlists
def search_spotify(query):
    results = sp.search(q=query, type="playlist", limit=5)
    playlists = results.get("playlists", {}).get("items", [])
    return playlists

# App UI
st.title("🎶 Mixtape Muse")
st.markdown("Whisper your mood, image, or desire — and the Muse shall find your soundtrack.")

auto_open = st.checkbox("🌐 Auto-open first playlist", value=True)

# Text input block
user_prompt = st.text_input("🎧 What mood, image, or magic shall I find?")

if user_prompt:
    mood = interpret_with_gpt(user_prompt)
    st.success(f"🎶 Interpreted mood: *{mood}*")
    playlists = search_spotify(mood)
    if playlists:
        st.markdown("### ✨ The Muse offers you these Spotify playlists:")
        valid_playlists = [
            item for item in playlists
            if item and isinstance(item, dict)
            and item.get("name")
            and item.get("external_urls", {}).get("spotify")
]

        for idx, item in enumerate(valid_playlists, start=1):
            name = item["name"]
            url = item["external_urls"]["spotify"]
            st.markdown(f"{idx}. [{name}]({url})")

    if auto_open and playlists:
        first = playlists[0]
        if first and isinstance(first, dict):
            url = first.get("external_urls", {}).get("spotify")
            if url:
                        webbrowser.open(url)
    else:
        st.warning("🔇 The Muse found no playlists matching that phrase. Try something simpler or more common — like 'twilight vibes' or 'sunset roadtrip'")

# Voice input block
if st.button("🎤 Speak to the Muse"):
    spoken_text = capture_voice()
    if spoken_text:
        st.write(f"🗣️ You said: *{spoken_text}*")
        user_prompt = spoken_text
        mood = interpret_with_gpt(user_prompt)
        st.success(f"✨ Interpreted mood: *{mood}*")
        playlists = search_spotify(mood)
        if playlists:
            st.markdown("### 🎵 Playlists for you:")
            valid_playlists = [
                item for item in playlists
                if item and isinstance(item, dict)
                and item.get("name")
                and item.get("external_urls", {}).get("spotify")
]

            for idx, item in enumerate(valid_playlists, start=1):
                name = item["name"]
                url = item["external_urls"]["spotify"]
                st.markdown(f"{idx}. [{name}]({url})")

            if auto_open and playlists:
                url = playlists[0]["external_urls"]["spotify"]
                webbrowser.open(url)
        else:
            st.warning("🔇 No playlists found for that mood. Try something simpler.")
