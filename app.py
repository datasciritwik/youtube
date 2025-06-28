import streamlit as st
import os
import subprocess
import tempfile
import urllib.parse
from main import combine_video_with_audio_control

st.set_page_config(page_title="Video + Audio Combiner", layout="centered")
st.title("Batch Video + Background Audio Combiner")

# Initialize session state for processed videos
if 'processed_videos' not in st.session_state:
    st.session_state.processed_videos = {}

if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

def download_file_with_wget(url, output_path=None):
    """
    Download a file using wget via subprocess
    
    Args:
        url (str): URL of the file to download
        output_path (str, optional): Path where to save the file
    
    Returns:
        tuple: (success: bool, file_path: str, error_message: str)
    """
    try:
        # Create temp directory if no output path specified
        if output_path is None:
            # Extract filename from URL
            parsed_url = urllib.parse.urlparse(url)
            filename = os.path.basename(parsed_url.path)
            if not filename or '.' not in filename:
                filename = "downloaded_file"
            
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f"_{filename}")
            output_path = temp_file.name
            temp_file.close()
        
        # Build wget command
        wget_cmd = [
            'wget',
            '--no-check-certificate',  # Skip SSL certificate verification if needed
            '--timeout=30',             # Set timeout
            '--tries=3',                # Number of retries
            '-O', output_path,          # Output file
            url
        ]
        
        # Execute wget command
        result = subprocess.run(
            wget_cmd,
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        
        if result.returncode == 0:
            return True, output_path, ""
        else:
            return False, None, result.stderr
            
    except subprocess.TimeoutExpired:
        return False, None, "Download timeout - file may be too large or connection too slow"
    except FileNotFoundError:
        return False, None, "wget command not found. Please install wget on your system."
    except Exception as e:
        return False, None, f"Download error: {str(e)}"

# Add URL input section
st.header("Download Files from URLs")
with st.expander("Download videos/audio from URLs using wget"):
    url_input = st.text_area(
        "Enter URLs (one per line)",
        placeholder="https://example.com/video.mp4\nhttps://example.com/audio.mp3",
        help="Enter one URL per line. Supports any file type that wget can download."
    )
    
    download_button = st.button("Download Files", type="secondary")
    
    if download_button and url_input.strip():
        urls = [url.strip() for url in url_input.strip().split('\n') if url.strip()]
        
        if urls:
            st.write(f"Downloading {len(urls)} file(s)...")
            download_progress = st.progress(0)
            
            downloaded_files = []
            
            for idx, url in enumerate(urls):
                with st.spinner(f"Downloading from {url}..."):
                    success, file_path, error = download_file_with_wget(url)
                    
                    if success:
                        st.success(f"✅ Downloaded: {os.path.basename(file_path)}")
                        downloaded_files.append(file_path)
                    else:
                        st.error(f"❌ Failed to download {url}: {error}")
                
                download_progress.progress((idx + 1) / len(urls))
            
            if downloaded_files:
                st.info(f"Successfully downloaded {len(downloaded_files)} file(s). You can now use them in the processing below.")

st.divider()

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

# Reset processed videos when new files are uploaded
if uploaded_videos:
    current_video_names = [video.name for video in uploaded_videos]
    if 'last_uploaded_videos' not in st.session_state or st.session_state.last_uploaded_videos != current_video_names:
        st.session_state.processed_videos = {}
        st.session_state.processing_complete = False
        st.session_state.last_uploaded_videos = current_video_names

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

    # Processing button
    submit = st.button("Start Processing", type="primary", disabled=st.session_state.processing_complete)
    
    if submit and not st.session_state.processing_complete:
        st.session_state.processed_videos = {}
        progress_bar = st.progress(0)
        
        for idx, video_file in enumerate(uploaded_videos):
            with st.spinner(f"Processing {video_file.name}... ({idx + 1}/{len(uploaded_videos)})"):
                # Save video to temp file
                temp_video = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.name)[1])
                temp_video.write(video_file.read())
                temp_video.flush()
                
                output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video_file.name)[1])
                output_path = output_temp.name
                temp_video.close()
                output_temp.close()

                # Call combine function
                success = combine_video_with_audio_control(
                    video_path=temp_video.name,
                    background_audio_path=audio_path,
                    output_path=output_path,
                    original_video_audio_volume=original_volume,
                    background_music_volume=bg_volume
                )

                if success:
                    # Read the processed video data and store in session state
                    with open(output_path, "rb") as f:
                        video_data = f.read()
                    
                    st.session_state.processed_videos[video_file.name] = {
                        'data': video_data,
                        'output_path': output_path,
                        'success': True
                    }
                else:
                    st.session_state.processed_videos[video_file.name] = {
                        'data': None,
                        'output_path': None,
                        'success': False
                    }
                
                # Clean up temp video file
                try:
                    os.unlink(temp_video.name)
                except:
                    pass
                
                # Update progress
                progress_bar.progress((idx + 1) / len(uploaded_videos))
        
        st.session_state.processing_complete = True
        st.success("All videos processed!")

    # Display results if processing is complete
    if st.session_state.processing_complete and st.session_state.processed_videos:
        st.header("Processed Videos")
        
        # Add a reset button
        if st.button("Process New Videos", type="secondary"):
            st.session_state.processed_videos = {}
            st.session_state.processing_complete = False
            st.rerun()
        
        for video_name, result in st.session_state.processed_videos.items():
            if result['success']:
                st.success(f"✅ Processed: {video_name}")
                
                # Video preview
                if result['output_path'] and os.path.exists(result['output_path']):
                    st.video(result['output_path'])
                
                # Download button with data from session state
                st.download_button(
                    label=f"📥 Download {video_name}",
                    data=result['data'],
                    file_name=f"combined_{video_name}",
                    mime="video/mp4",
                    key=f"download_{video_name}"
                )
            else:
                st.error(f"❌ Failed to process: {video_name}")
            
            st.divider()

else:
    st.info("Please upload at least one video file to begin.")
    # Clear session state when no videos are uploaded
    if 'processed_videos' in st.session_state:
        st.session_state.processed_videos = {}
        st.session_state.processing_complete = False