# write python code that plays bad apple video from youtube in the terminal using ascii characters
# write python code that plays bad apple video from youtube in the terminal using ascii characters, use yt_dlp and ffmpeg-python

"""
FFMPEG
https://youtu.be/ucXTQ0V8qMA
"""
""" 
import os
import time
# import youtube_dl
import yt_dlp as youtube_dl
import ffmpeg
from PIL import Image

# Download the video from YouTube
ydl_opts = {
    'outtmpl': 'bad_apple.mp4',  # Save the video as bad_apple.mp4
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com/watch?v=FtutLA63Cp8'])  # Download the video

# Convert the video to a series of images
(
    ffmpeg
    .input('bad_apple.mp4')
    .filter('fps', fps=24)
    .output('pipe:', format='image2', vframes=1)
    .run()
    # .run(capture_stdout=True)
    # .run(pipe_stdout=True)
)

# Define a function to convert an image to ASCII characters
def pixels_to_ascii(image):
    ascii_chars = "@%#*+=-:. "
    ascii_img = ""
    for i in range(0, image.width, 2):
        for j in range(image.height):
            r, g, b = image.getpixel((i, j))
            grayscale = int(0.299 * r + 0.587 * g + 0.114 * b)
            ascii_img += ascii_chars[grayscale // 32]
        ascii_img += "\n"
    return ascii_img

# Define a function to display the ASCII characters in the terminal
def play_video(ascii_frames):
    for ascii_frame in ascii_frames:
        print(ascii_frame)
        time.sleep(0.04)  # Sleep for 1/24th of a second (4 frames per second)

# Convert the video to ASCII frames
images = (
    ffmpeg
    .input('bad_apple.mp4')
    .filter('fps', fps=24)
    .output('%04d.jpg', start_number=0, vframes=1)
    .run()
)
ascii_frames = [pixels_to_ascii(Image.open(f'{i}.jpg')) for i in range(1, 1751)]  # There are 1750 frames in the video

# Display the ASCII frames in the terminal
play_video(ascii_frames)

# Clean up
os.remove('bad_apple.mp4')
for i in range(1, 1751):
    os.remove(f'{i}.jpg') """

import os
# import youtube_dl
import yt_dlp as youtube_dl
from ffmpeg import FFmpeg

# Download video using yt_dlp
ydl_opts = {
    'outtmpl': 'video.mp4',  # Save video as video.mp4
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download(['https://www.youtube.com/watch?v=yzC6N3PaoWo'])  # Bad Apple video

# Convert video to audio using ffmpeg-python
ffmpeg = FFmpeg(executable='ffmpeg')  # Ensure ffmpeg is installed and accessible in the system PATH
stream = ffmpeg.input('video.mp4')
stream = ffmpeg.output(stream, 'output.mp3')
ffmpeg.run()

# Play audio in the terminal
os.system('mpg123 output.mp3')  # Ensure mpg123 is installed and accessible in the system PATH