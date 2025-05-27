# Batch Video + Background Audio Combiner

This project provides a Streamlit web application and a Python script to batch combine video files with background audio, with adjustable volume controls for both the original video audio and the background music.

## Features
- Upload up to 10 video files at once.
- Optionally upload a background audio file (or use the default `background.mp3`).
- Adjust the volume of the original video audio and background music.
- Download each processed video after combining.
- Preview processed videos directly in the browser.

## Requirements
- Python 3.8+
- [MoviePy](https://zulko.github.io/moviepy/)
- [Streamlit](https://streamlit.io/)

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Streamlit Web App
Run the app:
```bash
streamlit run app.py
```

- Upload your video files (up to 10).
- Optionally upload a background audio file (mp3, wav, etc.).
- Adjust audio volumes in the sidebar.
- Click **Start Processing** to process all videos.
- Preview and download each processed video.

If no audio is uploaded, the app will use `background.mp3` from the current directory.

### 2. Command Line Script
You can also use the script directly:
```bash
python main.py <video_path> <background_audio_path> [--output_path OUTPUT] [--original_volume VOL] [--bg_volume VOL]
```

#### Example:
```bash
python main.py myvideo.mp4 background.mp3 --output_path result.mp4 --original_volume 0.8 --bg_volume 0.3
```

#### Create Dummy Files for Testing
```bash
python main.py --create_dummy_files
```

## Output
- Processed videos are saved with the prefix `combined_` (web app) or as specified (CLI).

## Notes
- Temporary files and outputs are ignored by `.gitignore`.
- For best results, use videos and audio with similar durations or let the app handle looping/trimming.

## License
MIT
