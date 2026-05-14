---
title: Echo Archive
emoji: 🎨
colorFrom: blue
colorTo: indigo
sdk: streamlit
python_version: "3.11"
app_file: app.py
pinned: false
---

# Echo Archive

Echo Archive is an AI-assisted interpretive art experience built with Streamlit, Gemini 2.5 Flash, and the Art Institute of Chicago API.

The application retrieves a random artwork from the Art Institute of Chicago collection and connects it to concepts, thoughts, or tensions provided by the user. Rather than positioning AI as a therapeutic or emotionally prescriptive voice, the system focuses on grounded visual analysis and conceptual association.

Echo Archive explores how generative systems can mediate encounters between users and archival material while preserving ambiguity, interpretation, and personal authorship.

---

# System Architecture

```text
User Concepts / Reflection Input
        ↓
[Art Institute of Chicago API]
        ↓
Artwork Retrieval + Metadata Filtering
        ↓
Streamlit Artwork Display
        ↓
[Gemini 2.5 Flash]
Concise Visual Description
        ↓
[Gemini 2.5 Flash]
Concept Connection Layer
        ↓
Optional User Reflection
        ↓
Email Archival System
```

---

# Core Interaction Model

The system separates interpretation into distinct stages:

### 1. Artwork Retrieval
A random artwork is selected from the Art Institute of Chicago API and filtered for richer contextual metadata.

### 2. Visual Description
Gemini generates a concise museum-style description focused on visible composition, material, subject matter, and form.

### 3. Concept Connections
The model connects the user's concepts or thoughts to visual and thematic elements within the artwork using a restrained curatorial tone.

### 4. User Reflection
Users can optionally write and archive their own reflections inspired by the encounter.

---

# Key Design Decisions

## Retrieval Before Generation

The experience is grounded in real museum records rather than AI-generated imagery or fictional archives.

## Interpretation Without Persona Simulation

The application intentionally avoids:
- therapist-style AI behavior
- emotional roleplay
- mystical narration
- companion-style interaction

Instead, Gemini functions as an interpretive layer that connects user concepts to the artwork in an analytical and observational manner.

## Separation of Description and Interpretation

Visual description and conceptual interpretation are handled independently to avoid redundancy and maintain clarity.

## Human-Centered Reflection

The final reflective layer belongs to the user rather than the model. The system supports interpretation without attempting to emotionally speak for the participant.

---

# Tech Stack

- Streamlit
- Python
- Google Gemini 2.5 Flash
- Art Institute of Chicago API
- Resend Email API
- python-dotenv

---

# Core Features

- Randomized artwork retrieval
- Metadata-aware artwork filtering
- AI-generated visual descriptions
- Concept-to-artwork interpretation pipeline
- User-authored reflections
- Email archiving system
- Session state persistence in Streamlit

---

# Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Create a `.env` file with:

```env
GEMINI_API_KEY=your_key_here
RESEND_API_KEY=your_key_here
```