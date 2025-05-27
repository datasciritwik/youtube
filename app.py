import streamlit as st
import os
from main import combine_video_with_audio_control
import tempfile

st.set_page_config(page_title="Video + Audio Combiner", layout="centered")
st.title("Batch Video + Background Audio Combiner")

# Allow user to upload up to 10 video files
uploaded_videos = st.file_uploader(
    "Upload up to 10 video files (mp4, mov, etc.)",
    type=["mp4", "mov", "avi", "mkv"],
    accept_multiple_files=True,
    key="video_uploader",
    help="You can upload up to 10 video files at once."
)

# Optional audio upload
uploaded_audio = st.file_uploader(
    "Upload background audio (optional, mp3, wav, etc.)",
    type=["mp3", "wav", "aac", "ogg"],
    accept_multiple_files=False,
    key="audio_uploader",
    help="If not provided, will use 'background.mp3' in the current folder."
)

def get_default_audio_path():
    default_audio = "background.mp3"
    if os.path.exists(default_audio):
        return default_audio
    return None

if uploaded_videos:
    st.write(f"{len(uploaded_videos)} video(s) uploaded.")
    # Audio selection
    if uploaded_audio:
        # Save uploaded audio to a temp file
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_audio.name)[1])
        temp_audio.write(uploaded_audio.read())
        temp_audio.flush()
        audio_path = temp_audio.name
    else:
        audio_path = get_default_audio_path()
        if not audio_path:
            st.warning("No background audio uploaded and no 'background.mp3' found. Please upload an audio file.")
            st.stop()

    # Volume controls
    st.sidebar.header("Audio Volume Settings")
    original_volume = st.sidebar.slider("Original Video Audio Volume", 0.0, 1.0, 1.0, 0.05)
    bg_volume = st.sidebar.slider("Background Music Volume", 0.0, 1.0, 0.5, 0.05)

    submit = st.button("Start Processing", type="primary")

    if submit:
        results = []
        for idx, video_file in enumerate(uploaded_videos):
            with st.spinner(f"Processing {video_file.name}..."):
                # Save video to temp file
                temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.name)[1])
                temp_video.write(video_file.read())
                temp_video.flush()
                output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.name)[1])
                output_path = output_temp.name
                temp_video.close()
                # Call combine function
                success = combine_video_with_audio_control(
                    video_path=temp_video.name,
                    background_audio_path=audio_path,
                    output_path=output_path,
                    original_video_audio_volume=original_volume,
                    background_music_volume=bg_volume
                )
                if success:
                    with open(output_path, "rb") as f:
                        st.success(f"Processed: {video_file.name}")
                        # Video preview
                        st.video(output_path)
                        st.download_button(
                            label=f"Download {video_file.name}",
                            data=f.read(),
                            file_name=f"combined_{video_file.name}",
                            mime="video/mp4"
                        )
                else:
                    st.error(f"Failed to process: {video_file.name}")
else:
    st.info("Please upload at least one video file to begin.")
