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

Art_Institute_of_Chicago_API_URL = "https://api.artic.edu/api/v1/artworks"

#---------------------------
# SESSION STATE (managing magic)
#---------------------------
session = requests.Session()

if "artwork" not in st.session_state:
    st.session_state.artwork = None

if "interpretation" not in st.session_state:
    st.session_state.interpretation = ""

if "user_input" not in st.session_state:
    st.session_state.user_input = ""
# ---------------------------
# ARTIC API
# ---------------------------
def get_random_painting():
    """
    Fetch a random painting from the Art Institute of Chicago.
    """

    random_page = random.randint(1, 500)

    try:
        response = session.get(
            f"{Art_Institute_of_Chicago_API_URL}/search",
            params={
                "page": random_page,
                "limit": 25,
                "q": "painting",
                "query[term][is_public_domain]": True,
                "query[exists][field]": "image_id",
                "fields": (
                    "id,title,image_id,artist_title,artist_display,"
                    "date_display,medium_display,dimensions,"
                    "description,classification_title,style_title,theme_titles"
                )
            },
            timeout=10
        )

        response.raise_for_status()

        data = response.json().get("data", [])

    except Exception as e:
        print(f"ARTIC API error: {e}")
        return None

    paintings = []

    for obj in data:

        image_id = obj.get("image_id")

        if not image_id:
            continue

        image_url = (
            f"https://www.artic.edu/iiif/2/"
            f"{image_id}/full/843,/0/default.jpg"
        )

        paintings.append({
            "id": obj.get("id"),
            "title": obj.get("title", "Untitled"),
            "artist": obj.get("artist_title", "Unknown Artist"),
            "artist_display": obj.get("artist_display", ""),
            "date": obj.get("date_display", "Unknown Date"),
            "medium": obj.get("medium_display", "Unknown Medium"),
            "dimensions": obj.get("dimensions", ""),
            "description": obj.get("description", ""),
            "style": obj.get("style_title", ""),
            "themes": obj.get("theme_titles", []),
            "image": image_url,
            "source": "Art Institute of Chicago"
        })

    if not paintings:
        return None

    return random.choice(paintings)
#----------------------------
# AI INTERPRETATION
#----------------------------
def generate_interpretation(user_input, artwork):
    """
    Generate an interpretive reflection connecting the user's input
    with the selected artwork's symbolism, medium, and context.
    """

    prompt = f"""
    You are an art oracle.

    A user has shared the following personal context:
    "{user_input}"

    They have been shown this artwork from the Art Institute of Chicago:

    Title: {artwork['title']}
    Artist: {artwork['artist']}
    Date: {artwork['date']}
    Medium: {artwork['medium']}
    Dimensions: {artwork['dimensions']}
    Style: {artwork['style']}
    Themes: {', '.join(artwork['themes']) if artwork['themes'] else 'None listed'}
    Description: {artwork['description']}

    Your task:
    Write a reflective interpretation (5–6 sentences) that connects:
    - the user's personal context
    - the artwork’s visual qualities, medium, and historical moment
    - the artist’s approach or sensibility (if relevant)

    Guidelines:
    - Do not be literal or obvious
    - Avoid generic art language
    - Treat the artwork as a living presence
    - Let meaning emerge rather than “explaining” it

    Output only the interpretation text.
    """

    try:
        response = model_interpret.generate_content(prompt)
        text = response.text.strip()
        return text if text else "The archive remains quiet."
    except Exception as e:
        print(f"Interpretation error: {e}")
        return "The archive remains quiet."
#---------------------------
# UI
# ---------------------------
st.title("Echo Archive")
st.write(
    "A quiet experiment in reflection. "
    "An artwork is drawn at random from the Art Institute of Chicago. "
    "Meaning emerges after."
)

# --- USER INPUT ---
with st.form("context_form"):
    user_input = st.text_input(
        "What’s on your mind right now?",
        placeholder="A thought, question, your recent search history"
    )
    submit = st.form_submit_button("Draw an artwork")

# --- HANDLE SUBMISSION ---
if submit:
    if not user_input.strip():
        st.warning("Please share a thought or fragment of context.")
        st.stop()

    st.session_state.user_input = user_input
    st.session_state.interpretation = ""

    with st.spinner("Searching the archive…"):
        artwork = None
    for _ in range(3):
        artwork = get_random_painting()
        if artwork:
            break
    if artwork is None:
        st.error("The archive returned nothing. Please try again.")
        st.stop()

    st.session_state.artwork = artwork


# --- DISPLAY ARTWORK ---
if st.session_state.artwork:
    art = st.session_state.artwork

    st.image(art["image"], use_container_width=True)
    st.markdown(f"**{art['title']}**")
    st.caption(f"{art['artist']}, {art['date']}")
    st.caption(f"Medium: {art['medium']}")

    if art["description"]:
        with st.expander("About this work"):
            st.write(art["description"])

    st.divider()

    # --- INTERPRETATION ---
    interpret = st.button("Reflect on this artwork")

    if interpret and not st.session_state.interpretation:
        with st.spinner("Interpreting…"):
            st.session_state.interpretation = generate_interpretation(
                st.session_state.user_input,
                art
            )

    if st.session_state.interpretation:
        st.markdown("### Reflection")
        st.write(st.session_state.interpretation)