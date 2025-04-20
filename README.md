# Open PDF2Brainrot: Open source ,free solution for converting your notes into brainrot content .

A Django‑powered web app that lets you upload a PDF, automatically turns each page into a “flashcard” (JSON) plus short “Brainrot” videos, and then provides a slick UI to browse your flashcards side‑by‑side with their videos.

---

## 🚀 Features

- **Upload a PDF** (up to 25 pages) via a simple web form  
- **Automatic conversion** of each page into:
  - A JSON flashcard (`flashcards/flashcard_N.json`)  
  - A folder of short `.mp4` videos (`videos/flashcard_N/*.mp4`)  
- **Interactive viewer**:
  - Left panel: nicely formatted JSON flashcards  
  - Right panel: upright video player with slide‑up/down navigation  
  - Sidebar: numbered buttons to switch between flashcards  

---

## 📋 Prerequisites

- **Python 3.8+**  
- **pip**  
- **FFmpeg** (required by MoviePy – install via `brew install ffmpeg`, `sudo apt install ffmpeg`, or download from https://ffmpeg.org)  

---

## 🔧 Installation & Setup

1. **Download the ML & audio models**  
   Grab the zipped models from:  
   https://drive.google.com/file/d/1RBSbAR_t0IW8y9GdcHLcs4tl_A6BUrfY/view?usp=sharing  

2. **Replace the `viewer/` assets**  
   - Unzip and place the downloaded **models** folder into `viewer/`  
   - Copy your **background videos** folder into `viewer/` as well  

3. **Populate environment variables**  
   Create a file named `.env` at the project root and add your Gemini API key:  
   ```ini
   GEMINI_API_KEY=your_actual_key_here

4. **Install Python dependencies**  
   Install all modules from requirements.txt  
   ```bash
   pip install -r requirements.txt

5. **Run the development server**
   Run the project
   ```bash
   cd Open_PDF2Brainrot
   python manage.py runserver
6. **Open Browser**
   Visit http://127.0.0.1:8000/
   
8. **Upload a PDF & wait**
   The “Processing…” overlay will appear, then redirect you to the flashcard+video viewer.
