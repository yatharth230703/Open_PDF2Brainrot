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
- **pip** (or `pipenv` / `poetry`)  
- Optional but recommended: a virtual environment

---

## 🔧 Installation & Setup

1. **Clone this repo**  
   ```bash
   git clone https://github.com/yatharth230703/Open_PDF2Brainrot.git
  
   cd Open_PDF2Brainrot
