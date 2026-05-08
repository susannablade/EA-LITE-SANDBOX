import os
import random
import streamlit as st
import requests
from dotenv import load_dotenv
import google.generativeai as genai

# ---------------------------
# CONFIG
# ---------------------------
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model_interpret = genai.GenerativeModel("gemini-2.5-flash")

ARTIC_API_URL = "https://api.artic.edu/api/v1/artworks"

session = requests.Session()

# ---------------------------
# SESSION STATE
# ---------------------------
DEFAULT_STATE = {
    "artwork": None,
    "interpretation": "",
    "user_input": ""
}

for key, value in DEFAULT_STATE.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------
# ARTIC API
# ---------------------------
def build_image_url(image_id):
    return (
        f"https://www.artic.edu/iiif/2/"
        f"{image_id}/full/843,/0/default.jpg"
    )


def get_random_artwork(retries=3):
    """
    Fetch a random artwork from the Art Institute of Chicago
    that contains an image.
    """

    for _ in range(retries):

        random_page = random.randint(1, 500)

        try:
            response = session.get(
                ARTIC_API_URL,
                params={
                    "page": random_page,
                    "limit": 25,
                    "fields": (
                        "id,title,image_id,artist_title,"
                        "artist_display,date_display,"
                        "medium_display,dimensions,"
                        "description,classification_title,"
                        "style_title,theme_titles"
                    )
                },
                timeout=10
            )

            response.raise_for_status()

            data = response.json().get("data", [])

        except Exception as e:
            print(f"ARTIC API error: {e}")
            continue

        artworks = []

        for obj in data:

            image_id = obj.get("image_id")

            if not image_id:
                continue

            artworks.append({
                "id": obj.get("id"),
                "title": obj.get("title") or "Untitled",
                "artist": obj.get("artist_title") or "Unknown Artist",
                "artist_display": obj.get("artist_display") or "",
                "date": obj.get("date_display") or "Unknown Date",
                "medium": obj.get("medium_display") or "Unknown Medium",
                "dimensions": obj.get("dimensions") or "",
                "description": obj.get("description") or "",
                "classification": obj.get("classification_title") or "",
                "style": obj.get("style_title") or "",
                "themes": obj.get("theme_titles") or [],
                "image": build_image_url(image_id),
                "source": "Art Institute of Chicago"
            })

        if artworks:
            return random.choice(artworks)

    return None


# ---------------------------
# AI INTERPRETATION
# ---------------------------
def generate_interpretation(user_input, artwork):

    prompt = f"""
    You are an art oracle.

    A user shared this personal context:

    "{user_input}"

    They were shown this artwork:

    Title: {artwork['title']}
    Artist: {artwork['artist']}
    Date: {artwork['date']}
    Medium: {artwork['medium']}
    Classification: {artwork['classification']}
    Style: {artwork['style']}
    Themes: {', '.join(artwork['themes']) if artwork['themes'] else 'None listed'}
    Description: {artwork['description']}

    Write a reflective interpretation in 5–6 sentences.

    Guidelines:
    - Avoid generic spiritual language
    - Do not summarize the artwork literally
    - Treat the artwork as emotionally alive
    - Connect visual atmosphere, history, material, and mood
    - Let meaning emerge indirectly
    - Be lyrical but restrained

    Output only the interpretation.
    """

    try:
        response = model_interpret.generate_content(prompt)

        if response and response.text:
            return response.text.strip()

        return "The archive remains quiet."

    except Exception as e:
        print(f"Interpretation error: {e}")
        return "The archive remains quiet."


# ---------------------------
# UI
# ---------------------------
st.title("Echo Archive")

st.write(
    "A quiet experiment in reflection. "
    "An artwork is drawn from the archive. "
    "Meaning arrives afterward."
)

# ---------------------------
# INPUT FORM
# ---------------------------
with st.form("archive_form"):

    user_input = st.text_input(
        "What is circling your mind right now?",
        placeholder="A thought, fragment, memory, or recent search"
    )

    submitted = st.form_submit_button("Draw from the archive")

# ---------------------------
# HANDLE SUBMISSION
# ---------------------------
if submitted:

    if not user_input.strip():
        st.warning("Please enter a thought or fragment first.")
        st.stop()

    st.session_state.user_input = user_input
    st.session_state.interpretation = ""

    with st.spinner("Searching the archive..."):

        artwork = get_random_artwork()

    if artwork is None:
        st.error("The archive returned nothing. Please try again.")
        st.stop()

    st.session_state.artwork = artwork

# ---------------------------
# DISPLAY ARTWORK
# ---------------------------
if st.session_state.artwork:

    art = st.session_state.artwork

    st.image(
        art["image"],
        use_container_width=True
    )

    st.markdown(f"### {art['title']}")

    st.caption(
        f"{art['artist']} · {art['date']}"
    )

    st.caption(
        f"{art['medium']}"
    )

    if art["classification"]:
        st.caption(
            f"Classification: {art['classification']}"
        )

    if art["description"]:

        with st.expander("About this work"):

            st.write(art["description"])

    st.divider()

    # ---------------------------
    # INTERPRET BUTTON
    # ---------------------------
    interpret = st.button(
        "Reflect on this artwork"
    )

    if interpret and not st.session_state.interpretation:

        with st.spinner("Listening closely..."):

            st.session_state.interpretation = (
                generate_interpretation(
                    st.session_state.user_input,
                    art
                )
            )

    # ---------------------------
    # DISPLAY INTERPRETATION
    # ---------------------------
    if st.session_state.interpretation:

        st.markdown("### Reflection")

        st.write(
            st.session_state.interpretation
        )