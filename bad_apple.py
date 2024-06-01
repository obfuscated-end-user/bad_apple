import ctypes
import pygame
import os
import shutil
import subprocess
import time
import yt_dlp
from PIL import Image

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
# ASCII_CHARS = [*" .:;+*?%S#@"]
ASCII_CHARS = [*" .:-=+*?#%@"]
SCALE_SIZE = 90
FPS = 15.5

def extract_frames_from_mp4(input_mp4):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_mp4,
        "cache/frames/frame%04d.png"
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print("Frame extraction successful!")
    except subprocess.CalledProcessError as e:
        print("Frame extraction failed!")
    os.system("cls" if os.name == "nt" else "clear")


def reduce_framerate_mp4(input_mp4, output_mp4):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_mp4,
        "-filter:v", "fps=15",
        output_mp4
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print("Framerate conversion successful!")
    except subprocess.CalledProcessError as e:
        print("Framerate conversion failed!")
    os.system("cls" if os.name == "nt" else "clear")


def extract_audio_from_mp4(input_mp4, output_mp3):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_mp4,
        output_mp3
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print("Audio extraction successful!")
    except subprocess.CalledProcessError as e:
        print("Audio extraction failed!")
    os.system("cls" if os.name == "nt" else "clear")


# https://youtu.be/v_raWlX7tZY
def resize_image(image, new_width=SCALE_SIZE):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return (resized_image)


def grayscale(image):
    return image.convert("L")


def pixels_to_ascii(image):
    pixels = image.getdata()
    # multiply each "pixel" by 2 to widen the image in the terminal
    return "".join([ASCII_CHARS[pixel // 25] * 2 for pixel in pixels])


def resize_images_in_frames():
    FRAMES_FOLDER = os.listdir(f"{THIS_FOLDER}/cache/frames")
    # print("")
    for item in FRAMES_FOLDER:
        if os.path.isfile(f"{THIS_FOLDER}/cache/frames/{item}"):
            im = Image.open(f"{THIS_FOLDER}/cache/frames/{item}")
            f, _ = os.path.splitext(f"{THIS_FOLDER}/cache/frames/{item}")
            im_resize = im.resize((300, 168))
            im_resize.save(f + "_resized.png", "PNG", quality=90)
            os.remove(f"{THIS_FOLDER}/cache/frames/{item}")
            print(f"\033[1A\033[KResizing images... ({FRAMES_FOLDER.index(item)}/{len(FRAMES_FOLDER)})")


def play_music_file(mp3_file):
    pygame.mixer.init()
    pygame.mixer.music.load(mp3_file)
    pygame.mixer.music.play()


def render_frames(new_width):
    FRAMES_FOLDER = os.listdir(f"{THIS_FOLDER}/cache/frames")

    # force maximize terminal window
    user32 = ctypes.WinDLL("user32")
    SW_MAXIMISE = 3
    hWnd = user32.GetForegroundWindow()
    user32.ShowWindow(hWnd, SW_MAXIMISE)

    play_music_file("cache/audio/track.mp3")

    for item in FRAMES_FOLDER:
        try:
            image = Image.open(f"cache/frames/{item}")
        except:
            print("not a valid image")
        
        new_image_data = pixels_to_ascii(grayscale(resize_image(image)))
        
        pixel_count = len(new_image_data)  
        ascii_image = "\n".join([new_image_data[index:(index + new_width)] for index in range(0, pixel_count, new_width)])

        print(chr(27) + "[2J")
        print(ascii_image)
        time.sleep(1 / FPS) # remove the delay for debugging
    os.system("cls" if os.name == "nt" else "clear")
    print("\n" * 50 + "終")


videos = "cache/videos"
if not os.path.exists(videos):
    os.makedirs(videos)

audio = "cache/audio"
if not os.path.exists(audio):
    os.makedirs(audio)

frames = "cache/frames"
if not os.path.exists(frames):
    os.makedirs(frames)

    # REMOVE DEBUG
    try:
        os.remove("cache/videos/bad_apple_temp.mp4")
    except:
        print("cache/videos/bad_apple_temp.mp4 doesnt exist")

    try:
        os.remove("cache/videos/bad_apple.mp4")
    except:
        print("cache/videos/bad_apple.mp4 doesnt exist")
    # UNTIL HERE

    ydl_opts = {
        "format": "worst",
        # "listformats": True,
        "ignoreerrors": True,
        "outtmpl": "cache/videos/bad_apple_temp.mp4"
    }

    ids = [
        "FtutLA63Cp8", # 【東方】Bad Apple!! ＰＶ【影絵】(not the official upload, but has more views than the official one)
        "i41KoE0iMYU", # [Alstroemeria Records]Bad Apple!! feat.nomico(Shadow Animation Version)[ACVS.008_Tr.00] (official upload)
        "9lNZ_Rnr7Jc", # Bad Apple!! - Full Version w/video [Lyrics in Romaji, Translation in English]
        "v-fc1zv31zE", # wtf?
        "Uds7g3M-4lQ", # BAND-MAID / Thrill (スリル) (Official Music Video) (AUDIO SYNC ISSUES)
        "WJq4jWSQNd8", # - Go ! Bwaaah ! (short video for debugging)
    ]

    with yt_dlp.YoutubeDL(ydl_opts) as y:
        y.download([f"https://youtu.be/watch?v={ids[0]}"])

    reduce_framerate_mp4("cache/videos/bad_apple_temp.mp4", "cache/videos/bad_apple.mp4")
    extract_audio_from_mp4("cache/videos/bad_apple_temp.mp4", "cache/audio/track.mp3")
    extract_frames_from_mp4("cache/videos/bad_apple.mp4")
    resize_images_in_frames()
    render_frames(SCALE_SIZE * 2)

    try:
        shutil.rmtree("cache/videos")
    except:
        print("cache/videos not deleted")

else:
    render_frames(SCALE_SIZE * 2)
