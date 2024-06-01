# write python code that plays bad apple video from youtube in the terminal using ascii characters
# write python code that plays bad apple video from youtube in the terminal using ascii characters, use yt_dlp and ffmpeg-python

# import ffmpeg
import os
import shutil
import subprocess
import sys
import yt_dlp

from PIL import Image
from time import sleep

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
ASCII_CHARS = [*"@#S%?*+;:,."]
ASCII_CHARS.reverse()
SCALE_SIZE = 70

def reduce_framerate_mp4(input, output):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input,
        "-filter:v", "fps=15",
        output
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print("Framerate conversion successful!")
    except subprocess.CalledProcessError as e:
        print("Framerate conversion failed!")

def extract_frames_from_mp4(input):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input,
        "frames/frame%05d.png"
    ]

    try:
        subprocess.run(ffmpeg_cmd, check=True)
        print("Frame extraction successful!")
    except subprocess.CalledProcessError as e:
        print("Frame extraction failed!")

# https://youtu.be/v_raWlX7tZY
def resize_image(image, new_width=SCALE_SIZE):
    width, height = image.size
    ratio = height/width
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return (resized_image)


def grayify(image):
    return image.convert("L")


def pixels_to_ascii(image):
    pixels = image.getdata()
    # multiply each "pixel" by 2 to widen the image in the terminal
    return "".join([ASCII_CHARS[pixel // 25] * 2 for pixel in pixels])


def resize_images_in_frames():
    FRAMES_FOLDER = os.listdir(f"{THIS_FOLDER}/frames")
    for item in FRAMES_FOLDER:
        if os.path.isfile(f"{THIS_FOLDER}/frames/{item}"):
            im = Image.open(f"{THIS_FOLDER}/frames/{item}")
            f, _ = os.path.splitext(f"{THIS_FOLDER}/frames/{item}")
            im_resize = im.resize((240, 180))
            im_resize.save(f + "_resized.png", "PNG", quality=90)
            os.remove(f"{THIS_FOLDER}/frames/{item}")
            print(f"({item}) image resize successful.")


def render_frames(new_width):
    FRAMES_FOLDER = os.listdir(f"{THIS_FOLDER}/frames")
    # print(FRAMES_FOLDER[1159])
    # print(f"{FRAMES_FOLDER}\n{os.path.exists(FRAMES_FOLDER)}")

    for item in FRAMES_FOLDER:
        try:
            image = Image.open(f"frames/{item}") # RANDOM FRAME
        except:
            print("not a valid image")
        
        new_image_data = pixels_to_ascii(grayify(resize_image(image)))
        
        pixel_count = len(new_image_data)  
        ascii_image = "\n".join([new_image_data[index:(index + new_width)] for index in range(0, pixel_count, new_width)])

        os.system("cls" if os.name == "nt" else "clear")
        print(ascii_image)
        sleep(0.025)

videos = "videos"
if not os.path.exists(videos):
    print("don't render in terminal yet")
    os.makedirs(videos)

frames = "frames"
if not os.path.exists(frames):
    os.makedirs(frames)
    try:
        os.remove("videos/bad_apple_temp.mp4")
    except:
        print("videos/bad_apple_temp.mp4 doesnt exist")

    try:
        os.remove("videos/bad_apple.mp4")
    except:
        print("videos/bad_apple.mp4 doesnt exist")
    # UNTIL HERE

    ydl_opts = {
        "format": "worst",
        # "listformats": True,
        "ignoreerrors": True,
        "outtmpl": "videos/bad_apple_temp.mp4"
    }

    # https://youtu.be/watch?v=WJq4jWSQNd8 - Go ! Bwaaah ! (short video for debugging)
    # https://youtu.be/watch?v=FtutLA63Cp8 - 【東方】Bad Apple!! ＰＶ【影絵】(not the official upload, but has more views than the official one)
    # https://youtu.be/watch?v=i41KoE0iMYU - [Alstroemeria Records]Bad Apple!! feat.nomico(Shadow Animation Version)[ACVS.008_Tr.00] (official upload)

    with yt_dlp.YoutubeDL(ydl_opts) as y:
        y.download(["https://youtu.be/watch?v=FtutLA63Cp8"])

    reduce_framerate_mp4("videos/bad_apple_temp.mp4", "videos/bad_apple.mp4")
    extract_frames_from_mp4("videos/bad_apple.mp4")
    resize_images_in_frames()
    print("then render it")
    render_frames(SCALE_SIZE*2)

    try:
        shutil.rmtree("videos")
    except:
        print("videos not deleted")

else:
    print("render in terminal")
    render_frames(SCALE_SIZE*2)

""" try:
    shutil.rmtree("frames")
except:
    print("frames not deleted") """
