from pytubefix import YouTube
from pytubefix.exceptions import RegexMatchError, VideoUnavailable
import ffmpeg
import os
import sys


def main():
    video_url = input("Enter the YouTube video URL: ")

    if input("Automatically download highest quality version? y/n: ") == 'y':
        download_video(video_url, True)
    else:
        print_info(video_url)
        download_video(video_url, False)


def download_video(url, highest_quality: bool):
    try:
        yt = YouTube(url)

        # Get video
        if highest_quality == True:
            video_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc().first()
        else:
            video_stream = get_stream_by_tag(yt, audio=False)

        print("Video size:", video_stream.filesize_mb, "MB")

        # Get audio
        if highest_quality == True:
            audio_stream = yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc().first()
        else:
            audio_stream = get_stream_by_tag(yt, audio=True)

        print("Audio size:", audio_stream.filesize_mb, "MB")

        # Download files
        print("Downloading video, please wait...")
        video_path = video_stream.download(output_path='E:/Downloads', filename='video.mp4')
        print("Video download complete.\n")

        print("Downloading audio, please wait...")
        audio_path = audio_stream.download(output_path='E:/Downloads', filename='audio.mp4')
        print("Audio download complete.\n")

        #Combine video and audio streams using ffmpeg
        print("Combining streams to video file...")
        combine_video_audio(video_path, audio_path, video_stream.bitrate, audio_stream.bitrate, yt.title)
        print(f"Download and merge completed: {yt.title}")

    except RegexMatchError:
        print("Invalid URL format.")
    except VideoUnavailable:
        print("The video is unavailable.")
    except Exception as e:
        print(f"An error occurred: {e}")


def print_info(url):
    
    yt = YouTube(url)
    print("Title:", yt.title)
    print()
    print("Printing video information...")
    print()

    #Print info of all available streams (how this info is displayed could definitely be improved...)
    print("Video Streams:")
    for stream in yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc():
        print(stream, "Size:", stream.filesize_mb, "MB")

    print()

    print("Audio Streams:")
    for stream in yt.streams.filter(adaptive=True, file_extension='mp4', only_audio=True).order_by('abr').desc():
        print(stream, "Size:", stream.filesize_mb, "MB")

    print()

def get_stream_by_tag(yt, audio: bool):
    str = "Enter itag for video stream: "
    if audio:
        str = "Enter itag for audio stream: "

    # Loop to handle user input (can be improved in the future by checking if itag entered is currently in list of streams)
    while True:
        try:
            cmd = input(str).strip()
            #cmd = cmd.replace('"','') # handle quotes in case user types them in with the number

            if cmd in ['q', 'quit', 'exit', 'cancel']:
                sys.exit()
            
            tag = int(cmd)
            return yt.streams.get_by_itag(tag)
        
        except ValueError:
            print("Error: Must enter a number for the itag (Type 'q' to cancel)")
        
        except (KeyboardInterrupt, SystemExit):
            print("Forced exit")
            sys.exit()

        except:
            print("Error reading user input (Type 'q' to cancel)")
            pass


def combine_video_audio(video_path, audio_path, v_bitrate, a_bitrate, title):
        output_path = f'E:/Downloads/{title}.mp4'

        # Combine video and audio using ffmpeg
        input_video = ffmpeg.input(video_path)
        input_audio = ffmpeg.input(audio_path)
        ffmpeg_output = ffmpeg.output(input_video, input_audio, output_path, vcodec='copy', acodec='aac', video_bitrate = v_bitrate, audio_bitrate = a_bitrate)
        ffmpeg_output.run()

        # Clean up the separate files
        os.remove(video_path)
        os.remove(audio_path)


if __name__ == "__main__":
    main()