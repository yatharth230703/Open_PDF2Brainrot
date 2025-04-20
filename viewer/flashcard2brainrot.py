import os
import asyncio
import concurrent.futures
import random
import numpy as np
import tempfile
import json
import wave
import re


from kokoro import KPipeline
import soundfile as sf
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips,
    CompositeAudioClip, VideoClip
)
from moviepy.config import change_settings
from vosk import Model, KaldiRecognizer
from pathlib import Path
###adding directories
base_dir = Path(__file__).parent
#####################
def add_pause_between_sentences(text, pause_lines=2):
    """Inserts multiple newlines between sentences to simulate pauses."""
    pause = '\n' * pause_lines
    return re.sub(r'([.?!])\s+', r'\1' + pause, text)
change_settings({
    "IMAGEMAGICK_BINARY": base_dir / "models" / "magick.exe"
})

VOSK_MODEL_PATH =   str(base_dir / "models" / "vosk-model-en-us-0.22-lgraph")
def generate_kokoro_audio(text, voice='af_heart'):
    pipeline = KPipeline(lang_code='a')
    generator = pipeline(text, voice=voice, speed=0.9, split_pattern=r'\n+')

    audio_chunks = []
    chunks_info = []  
    current_time = 0.0
    for i, (gs, ps, audio) in enumerate(generator):
        print(f"[{i}] Text: {gs} | Phonemes: {ps}")
        chunk_audio = audio
        duration = len(chunk_audio) / 24000  
        audio_chunks.append(chunk_audio)
        chunks_info.append((gs, current_time, current_time + duration))
        current_time += duration

    full_audio = np.concatenate(audio_chunks)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
        sf.write(temp_audio.name, full_audio, 24000)
        return temp_audio.name, chunks_info

def get_word_timestamps(audio_path, model_path=VOSK_MODEL_PATH):
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model path '{model_path}' does not exist. "
                                "Please download a model from https://alphacephei.com/vosk/models and extract it.")
    wf = wave.open(audio_path, "rb")
    model = Model(model_path)
    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)

    words_timestamps = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            if "result" in result:
                words_timestamps.extend(result["result"])
    final_result = json.loads(rec.FinalResult())
    if "result" in final_result:
        words_timestamps.extend(final_result["result"])
    return words_timestamps
def generate_brainrot_video(video_path, original_text, voice='af_jessica', output_path="output.mp4", model_path=VOSK_MODEL_PATH, bgm_path=None):
    try:
        print(f"[+] Generating audio for: {output_path}")
        audio_path, _ = generate_kokoro_audio(original_text, voice)

        video = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration

        if video.duration >= audio_duration:
            video = video.subclip(0, audio_duration)
        else:
            loop_count = int(audio_duration // video.duration)
            remainder = audio_duration - (video.duration * loop_count)
            clips = [video] * loop_count
            if remainder > 0:
                clips.append(video.subclip(0, remainder))
            video = concatenate_videoclips(clips)

        if bgm_path is not None:
            bgm_clip = AudioFileClip(bgm_path).set_duration(audio_duration)
            bgm_clip = bgm_clip.volumex(0.3)
            combined_audio = CompositeAudioClip([audio_clip, bgm_clip])
            final_video = video.set_audio(combined_audio)
        else:
            final_video = video.set_audio(audio_clip)

        word_timestamps = get_word_timestamps(audio_path, model_path)

        text_clips = []
        for word_info in word_timestamps:
            word = word_info.get("word", "").strip()
            if not word:
                continue
            start_time = word_info.get("start", 0)
            end_time = word_info.get("end", start_time + 0.3)
            duration = end_time - start_time

            txt_clip = TextClip(
                word,
                fontsize=60,
                color='yellow',
                font='Comic-Sans-MS',
                stroke_color='black',
                stroke_width=2,
                method='caption'
            )
            txt_clip = txt_clip.set_pos('center').set_duration(duration).set_start(start_time)
            text_clips.append(txt_clip)

        final = CompositeVideoClip([final_video, *text_clips])
        final.write_videofile(output_path, codec="libx264", audio_codec="aac", fps=24)

        if os.path.exists(audio_path):
            os.remove(audio_path)
        print(f"[✓] Saved: {output_path}")
    except Exception as e:
        print(f"[!] Error while processing {output_path}: {e}")
async def generate_videos_async(video_dir, bgm_dir, text_list, voice='af_jessica', model_path=VOSK_MODEL_PATH, output_dir=None):
    loop = asyncio.get_event_loop()
    max_workers = 3

    video_files = [os.path.join(video_dir, f) for f in os.listdir(video_dir)
                   if f.lower().endswith(('.mp4', '.mov', '.avi', '.mkv'))]
    if not video_files:
        raise Exception("No video files found in the specified video directory.")

    bgm_files = [os.path.join(bgm_dir, f) for f in os.listdir(bgm_dir)
                 if f.lower().endswith(('.mp3', '.wav', '.aac', '.m4a'))]
    if not bgm_files:
        raise Exception("No background music files found in the specified music directory.")

    if output_dir is None:
        output_dir = os.getcwd()
    os.makedirs(output_dir, exist_ok=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        tasks = []
        for i, text in enumerate(text_list, start=1):
            selected_video = random.choice(video_files)
            selected_bgm = random.choice(bgm_files)
            output_filename = os.path.join(output_dir, f"{i}.mp4")
            task = loop.run_in_executor(
                executor,
                generate_brainrot_video,
                selected_video, text, voice, output_filename, model_path, selected_bgm
            )
            tasks.append(task)
        await asyncio.gather(*tasks)

VIDEO_DIR = base_dir / "background_video"
BGM_DIR =  base_dir / "background_audio" 
OUTPUT_DIR = base_dir / "brainrot_output"

# text_entries = [
#     add_pause_between_sentences("Multiprogramming systems manage multiple processes concurrently, rapidly switching the CPU between them to give the illusion of parallelism."),
#     add_pause_between_sentences("Concurrency control is crucial in systems with multiple disks to prevent newer requests from monopolizing resources while older requests remain unfulfilled."),
#     add_pause_between_sentences("Processes, especially threads, play a vital role in modeling and controlling concurrency, ensuring efficient resource utilization across multiple tasks."),
#     add_pause_between_sentences("User PCs utilize multiple background processes for tasks like email monitoring and antivirus updates, alongside explicit user applications such as printing and web browsing."),
#     add_pause_between_sentences("Imagine you're juggling many balls. That's like a computer doing many things at once! Multiprogramming is like quickly throwing each ball up and down, one after the other, so it looks like they're all in the air at the same time. Some programs need to wait for their turn, and we need to make sure one doesn't hog all the time, like a greedy kid who won't share their toys.\n\n Think of different people doing different jobs in a house - one is cooking, one is cleaning, one is watching TV. To manage this, the operating system switches between them quickly, giving the illusion that all these tasks are happening simultaneously. This approach simplifies managing parallel activities by utilizing a model of sequential processes."),
# ]

def brainrot_wrapper(
    video_dir,                
    bgm_dir,                  
    text_entries,
    voice="af_jessica",
    model_path=VOSK_MODEL_PATH,
    output_dir=None,          
):
    if isinstance(video_dir, Path):
        video_dir = str(video_dir)
    if isinstance(bgm_dir, Path):
        bgm_dir = str(bgm_dir)
    if isinstance(output_dir, Path) or output_dir is None:
        output_dir = str(output_dir) if output_dir else None

    asyncio.run(
        generate_videos_async(
            video_dir=video_dir,
            bgm_dir=bgm_dir,
            text_list=text_entries,
            voice=voice,
            model_path=model_path,
            output_dir=output_dir,
        )
    )



