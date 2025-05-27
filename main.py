from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
import os
import argparse # Import argparse

def combine_video_with_audio_control(
    video_path,
    background_audio_path,
    output_path,
    original_video_audio_volume=1.0,
    background_music_volume=0.5
):
    """
    Combines a video with background audio, allowing volume adjustment for both.
    (Function content remains the same as before)
    """
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at '{video_path}'")
        return False
    if not os.path.exists(background_audio_path):
        print(f"Error: Background audio file not found at '{background_audio_path}'")
        return False

    video_clip = None
    bg_music_clip = None
    bg_music_final = None
    original_audio = None
    final_audio = None
    video_with_new_audio = None

    try:
        print(f"Loading video: {video_path}")
        video_clip = VideoFileClip(video_path)
        video_duration = video_clip.duration

        print(f"Loading background audio: {background_audio_path}")
        bg_music_clip = AudioFileClip(background_audio_path)

        # --- Adjust background music ---
        if bg_music_clip.duration < video_duration:
            print("Background music is shorter than video. Looping music...")
            num_loops = int(video_duration / bg_music_clip.duration) + 1
            looped_clips = [bg_music_clip] * num_loops
            bg_music_clip_looped = CompositeAudioClip(looped_clips)
            bg_music_final = bg_music_clip_looped.subclipped(0, video_duration)
            if bg_music_clip_looped != bg_music_final: bg_music_clip_looped.close()
        elif bg_music_clip.duration > video_duration:
            print("Background music is longer than video. Trimming music...")
            bg_music_final = bg_music_clip.subclipped(0, video_duration)
        else:
            bg_music_final = bg_music_clip # Durations match

        print(f"Adjusting background music volume to {background_music_volume*100}%")
        # Use with_volume_scaled() instead of volumex()
        if bg_music_final is bg_music_clip:
            bg_music_final = bg_music_clip.copy().with_volume_scaled(background_music_volume)
        else:
            bg_music_final = bg_music_final.with_volume_scaled(background_music_volume)


        # --- Prepare final audio track ---
        audio_tracks_to_combine = []

        if video_clip.audio:
            print(f"Original video has audio. Adjusting its volume to {original_video_audio_volume*100}%")
            # Use with_volume_scaled() instead of volumex()
            original_audio = video_clip.audio.with_volume_scaled(original_video_audio_volume)
            audio_tracks_to_combine.append(original_audio)
        else:
            print("Original video has no audio track.")

        audio_tracks_to_combine.append(bg_music_final)

        if audio_tracks_to_combine:
            print("Combining audio tracks...")
            final_audio = CompositeAudioClip(audio_tracks_to_combine)
        else:
            print("Warning: No audio tracks to combine. Video will be silent.")
            final_audio = None # Should not happen if bg_music is always added

        print("Setting final audio to video clip...")
        video_with_new_audio = video_clip.with_audio(final_audio)

        print(f"Writing output video to: {output_path}")
        video_with_new_audio.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            threads=os.cpu_count() or 1,
            logger='bar'
        )
        print("Video processing complete!")
        return True

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        print("Cleaning up resources...")
        if video_clip: video_clip.close()
        # Only close bg_music_clip if it wasn't directly assigned to bg_music_final and then modified
        # The .copy() above for bg_music_final helps ensure original bg_music_clip is safe to close
        if bg_music_clip and (bg_music_final is None or bg_music_final != bg_music_clip):
             bg_music_clip.close()
        if original_audio: original_audio.close()
        if bg_music_final: bg_music_final.close()
        if final_audio: final_audio.close()
        # video_with_new_audio is based on video_clip, its resources are tied.


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Combine a video with background audio and adjust volumes.")
    parser.add_argument("video_path", help="Path to the input video file.")
    parser.add_argument("background_audio_path", help="Path to the background audio file.")
    parser.add_argument(
        "--output_path", 
        help="Path to save the combined output video. If not provided, will auto-generate as 'generated_{input_video_name}.{ext}'"
    )
    parser.add_argument(
        "--original_volume",
        type=float,
        default=1.0,
        help="Volume multiplier for the video's original audio (e.g., 0.5 for 50%%, 1.0 for 100%%, 0.0 to mute). Default: 1.0"
    )
    parser.add_argument(
        "--bg_volume",
        type=float,
        default=0.5,
        help="Volume multiplier for the background music (e.g., 0.5 for 50%%, 1.0 for 100%%). Default: 0.5"
    )
    parser.add_argument(
        "--create_dummy_files",
        action='store_true', # This makes it a flag, no value needed after it
        help="If set, creates dummy video and audio files for testing if they don't exist. Ignores other path arguments if used for dummy creation."
    )


    args = parser.parse_args()

    if args.create_dummy_files:
        dummy_video_file = "my_test_video.mp4"
        dummy_audio_file = "my_background_music.mp3"
        print("--- Creating dummy files for testing ---")
        if not os.path.exists(dummy_video_file):
            from moviepy import ColorClip, AudioArrayClip
            import numpy as np
            print(f"Creating dummy video: {dummy_video_file}")
            clip = ColorClip(size=(640, 480), color=(255, 0, 0), duration=5)
            duration = 5; fps = 44100; t = np.linspace(0, duration, int(fps * duration), endpoint=False)
            original_sound_array = 0.3 * np.sin(2 * np.pi * 110 * t)
            original_sound_array_stereo = np.array([original_sound_array, original_sound_array]).T
            original_audio_clip_dummy = AudioArrayClip(original_sound_array_stereo, fps=fps)
            clip = clip.set_audio(original_audio_clip_dummy)
            clip.write_videofile(dummy_video_file, fps=24, codec="libx264", audio_codec="aac")
            clip.close()
            original_audio_clip_dummy.close()
        else:
            print(f"Dummy video '{dummy_video_file}' already exists.")

        if not os.path.exists(dummy_audio_file):
            from moviepy import AudioArrayClip
            import numpy as np
            print(f"Creating dummy audio: {dummy_audio_file}")
            duration = 3; fps = 44100; t = np.linspace(0, duration, int(fps * duration), endpoint=False)
            audio_data = 0.5 * np.sin(2 * np.pi * 440 * t)
            audio_data_stereo = np.array([audio_data, audio_data]).T
            audio_clip_dummy = AudioArrayClip(audio_data_stereo, fps=fps)
            audio_clip_dummy.write_audiofile(dummy_audio_file, codec='mp3')
            audio_clip_dummy.close()
        else:
            print(f"Dummy audio '{dummy_audio_file}' already exists.")
        print("Dummy files created/checked. To run the main script, provide paths without --create_dummy_files.")

    else:
        # Auto-generate output path if not provided
        if not args.output_path:
            video_dir = os.path.dirname(args.video_path)
            video_name = os.path.basename(args.video_path)
            name_without_ext, ext = os.path.splitext(video_name)
            generated_name = f"generated_{name_without_ext}{ext}"
            args.output_path = os.path.join(video_dir, generated_name)
            print(f"Output path not specified. Auto-generating: {args.output_path}")
        
        print("\n--- Starting video combination process ---")
        success = combine_video_with_audio_control(
            video_path=args.video_path,
            background_audio_path=args.background_audio_path,
            output_path=args.output_path,
            original_video_audio_volume=args.original_volume,
            background_music_volume=args.bg_volume
        )
        if success:
            print(f"Successfully created: {args.output_path}")
        else:
            print(f"Failed to create: {args.output_path}")