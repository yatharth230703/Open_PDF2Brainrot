from __future__ import annotations
import logging
import re
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Tuple
import json
import PyPDF2

from .flashcards_trail1 import pdf_to_text_array, flashcard
from .flashcard2brainrot import brainrot_wrapper, add_pause_between_sentences

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
LG = logging.getLogger(__name__)


def count_pdf_pages(pdf_path: Path) -> int:
    with pdf_path.open("rb") as fh:
        reader = PyPDF2.PdfReader(fh)
        return len(reader.pages)


def sanitize_filename(name: str, default: str = "file") -> str:
    nfkd = unicodedata.normalize("NFKD", name)
    ascii_only = nfkd.encode("ascii", "ignore").decode()
    cleaned = re.sub(r"[^\w\s-]", "", ascii_only).strip().lower()
    cleaned = re.sub(r"[-\s]+", "_", cleaned)
    return cleaned or default


def process_flashcards_for_videos(
    all_flashcards: List[dict], chunk_size: int = 5
) -> List[Tuple[str, str]]:
    subheading_points: List[Tuple[str, str]] = []
    for flash in all_flashcards:
        for heading_name, heading_content in flash.items():
            if isinstance(heading_content, dict):
                for sub, pts in heading_content.items():
                    for pt in pts:
                        subheading_points.append((sub, pt))
            elif isinstance(heading_content, list):
                for pt in heading_content:
                    subheading_points.append((heading_name, pt))
            else:
                LG.warning("Unexpected type %s – skipped", type(heading_content))

    video_entries: List[Tuple[str, str]] = []
    current_chunk, current_subs, sequence = [], set(), []

    for sub, point in subheading_points:
        current_chunk.append(point)
        if sub not in current_subs:
            sequence.append(sub)
            current_subs.add(sub)

        if len(current_chunk) >= chunk_size:
            name = "__".join(sequence) or f"chunk_{len(video_entries)+1}"
            text = add_pause_between_sentences(" ".join(current_chunk))
            video_entries.append((sanitize_filename(name), text))
            current_chunk, current_subs, sequence = [], set(), []
    if current_chunk:
        name = "__".join(sequence) or f"chunk_{len(video_entries)+1}"
        text = add_pause_between_sentences(" ".join(current_chunk))
        video_entries.append((sanitize_filename(name), text))

    return video_entries


def convert_pdf(pdf_path: Path, output_root: Path, chunk_size: int = 5) -> None:
    LG.info("Converting %s → %s", pdf_path, output_root)
    pages = count_pdf_pages(pdf_path)
    if pages > 25:
        raise ValueError(f"PDF too large ({pages} pages; max 25)")

    flashcard_json_dir = output_root / "flashcards"
    flashcard_json_dir.mkdir(parents=True, exist_ok=True)
    video_output_dir = output_root / "videos"
    video_output_dir.mkdir(parents=True, exist_ok=True)

    LG.info("Extracting text …")
    pages_text = pdf_to_text_array(str(pdf_path))

    LG.info("Generating flashcards …")
    flashcards: List[dict] = [None] * len(pages_text) 
    with ThreadPoolExecutor(max_workers=5) as pool:
        future_map = {
            pool.submit(flashcard, text, "General Topic", []): idx
            for idx, text in enumerate(pages_text)
        }
        for fut in as_completed(future_map):
            idx = future_map[fut]
            try:
                flashcards[idx] = fut.result()
            except Exception as exc:
                LG.warning("Flashcard %d failed: %s", idx + 1, exc)
                flashcards[idx] = {}

    flashcards = [f or {} for f in flashcards]
    for idx, data in enumerate(flashcards, start=1):
        dest = flashcard_json_dir / f"flashcard_{idx}.json"
        with dest.open("w") as fh:
            json.dump(data, fh, indent=4)
        LG.info("Wrote %s", dest)

    for idx, data in enumerate(flashcards, start=1):
        entries = process_flashcards_for_videos([data], chunk_size)
        if not entries:
            LG.warning("No points in flashcard %d; skipping", idx)
            continue

        names, texts = zip(*entries)
        fc_vid_dir = video_output_dir / f"flashcard_{idx}"
        fc_vid_dir.mkdir(exist_ok=True)

        LG.info("Rendering %d videos for flashcard %d …", len(names), idx)
        brainrot_wrapper(
            video_dir=Path(__file__).parent / "background_video",
            bgm_dir=Path(__file__).parent / "background_audio",
            text_entries=list(texts),
            output_dir=fc_vid_dir
        )

        generated = sorted(fc_vid_dir.glob("*.mp4"), key=lambda p: int(p.stem))
        for src, nice in zip(generated, names):
            dst = src.with_name(f"{nice}.mp4")
            try:
                src.rename(dst)
            except FileExistsError:
                LG.error("Cannot rename %s → %s (exists)", src.name, dst.name)

    LG.info("Conversion complete; videos in %s", video_output_dir.resolve())


def main() -> None:
    while True:
        inp = input("Path to PDF file: ").strip()
        pdf_path = Path(inp).expanduser()
        if not pdf_path.exists():
            LG.error("File not found.")
            continue
        break

    root = Path.cwd() / sanitize_filename(pdf_path.stem)
    convert_pdf(pdf_path, root)
    LG.info("All done!")


if __name__ == "__main__":
    main()
