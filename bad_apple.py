import ctypes
import datetime
import os
import random
import shutil
import subprocess
import time
import yt_dlp

from PIL import Image
from pygame import mixer

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

# each charset should have 11 chars
ASCII_CHARSETS = [
    [*" .:;+*?%S#X"],
    [*"X#S%?+*;:. "], # reverse
    [*" .:-=+*?#%@"],
    [*" .:;+*?%S#@"],
    [*" .:;+*?%S# "], # outlines only
    [*"          @"],
    [*"         # "],
    [*"       %S# "],
]

CHARSET = ASCII_CHARSETS[0]

SCALE_SIZE = 82
# RATE_CONST = 42
RATE_CONST = 45.5 # adjust this if it syncs like ass
FPS = 1 / RATE_CONST
# FPS = float(input("enter fps: "))


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


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


def reduce_framerate_mp4(input_mp4, output_mp4):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_mp4,
        # "-filter:v", "fps=15",
        "-filter:v", "fps=24",
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
    return "".join([CHARSET[pixel // 25] * 2 for pixel in pixels])


def resize_frames():
    FRAMES_FOLDER = os.listdir(f"{THIS_FOLDER}/cache/frames")
    for item in FRAMES_FOLDER:
        if os.path.isfile(f"{THIS_FOLDER}/cache/frames/{item}"):
            im = Image.open(f"{THIS_FOLDER}/cache/frames/{item}")
            f, _ = os.path.splitext(f"{THIS_FOLDER}/cache/frames/{item}")
            im_resize = im.resize((300, 168))
            im_resize.save(f + "_resized.png", "PNG", quality=90)
            os.remove(f"{THIS_FOLDER}/cache/frames/{item}")
            print(f"\033[1A\033[KResizing images... ({FRAMES_FOLDER.index(item)}/{len(FRAMES_FOLDER)})")


def play_music_file(mp3_file):
    mixer.init()
    mixer.music.load(mp3_file)
    mixer.music.play()


# https://vocaloidlyrics.fandom.com/wiki/Bad_Apple!!
# yes, i'm aware that this is from another bad apple cover, just happened to also cover the shadow art version shit as well
bad_apple_lyrics = {
    ("00:01.00", "00:29.07"): " ",
    ("00:29.08", "00:32.55"): "流れてく　時の中ででも",
    ("00:32.56", "00:36.08"): "気だるさが　ほらグルグル廻って",
    ("00:36.09", "00:39.47"): "私から　離れる心も",
    ("00:39.48", "00:42.90"): "見えないわ　そう知らない？",
    ("00:42.91", "00:46.43"): "自分から　動くこともなく",
    ("00:46.44", "00:49.91"): "時の隙間に　流され続けて",
    ("00:49.92", "00:53.39"): "知らないわ　周りのことなど",
    ("00:53.40", "00:56.92"): "私は私　それだけ",
    ("00:56.93", "01:00.09"): "夢見てる？　なにも見てない？",
    ("01:00.08", "01:03.35"): "語るも無駄な　自分の言葉",
    ("01:03.36", "01:06.84"): "悲しむなんて　疲れるだけよ",
    ("01:06.85", "01:10.27"): "何も感じず　過ごせばいいの",
    ("01:10.28", "01:13.70"): "戸惑う言葉　与えられても",
    ("01:13.71", "01:17.38"): "自分の心　ただ上の空",
    ("01:17.39", "01:20.77"): "もし私から　動くのならば",
    ("01:20.78", "01:24.30"): "すべて変えるのなら　黒にする",
    ("01:24.31", "01:27.78"): "こんな自分に　未来はあるの？",
    ("01:27.79", "01:31.21"): "こんな世界に　私はいるの？",
    ("01:31.22", "01:34.64"): "今切ないの？　今悲しいの？",
    ("01:34.65", "01:38.21"): "自分の事も　わからないまま",
    ("01:38.22", "01:41.61"): "歩むことさえ　疲れるだけよ",
    ("01:41.62", "01:45.13"): "人のことなど　知りもしないわ",
    ("01:45.14", "01:48.65"): "こんな私も　変われるもなら",
    ("01:48.66", "01:52.56"): "もし変われるのなら　白になる",
    ("01:52.57", "02:06.44"): " ",
    ("02:06.45", "02:09.91"): "流れてく　時の中ででも",
    ("02:09.92", "02:13.45"): "気だるさが　ほらグルグル廻って",
    ("02:13.46", "02:16.97"): "私から　離れる心も",
    ("02:16.98", "02:20.34"): "見えないわ　そう知らない？",
    ("02:20.35", "02:23.92"): "自分から　動くこともなく",
    ("02:23.93", "02:27.35"): "時の隙間に　流され続けて",
    ("02:27.36", "02:30.83"): "知らないわ　周りのことなど",
    ("02:30.84", "02:34.27"): "私は私　それだけ",
    ("02:34.28", "02:37.28"): "夢見てる？　なにも見てない？",
    ("02:37.29", "02:40.80"): "語るも無駄な　自分の言葉",
    ("02:40.81", "02:44.20"): "悲しむなんて　疲れるだけよ",
    ("02:44.21", "02:47.72"): "何も感じず　過ごせばいいの",
    ("02:47.73", "02:51.29"): "戸惑う言葉　与えられても",
    ("02:51.30", "02:54.68"): "自分の心　ただ上の空",
    ("02:54.69", "02:58.16"): "もし私から　動くのならば",
    ("02:58.17", "03:01.68"): "すべて変えるのなら　黒にする",
    ("03:01.69", "03:05.12"): "動くのならば　動くのならば",
    ("03:05.13", "03:08.70"): "すべて壊すわ　すべて壊すわ",
    ("03:08.71", "03:12.28"): "悲しむならば　悲しむならば",
    ("03:12.29", "03:15.62"): "私の心　白く変われる？",
    ("03:15.63", "03:19.11"): "貴方の事も　私のことも",
    ("03:19.12", "03:22.54"): "全ての事も　まだ知らないの",
    ("03:22.55", "03:26.07"): "重い目蓋を　開けたのならば",
    ("03:26.08", "03:30.07"): "すべて壊すのなら　黒になれ",
    ("03:30.08", "03:31.08"): " ",
}

timestamp_list = []
for key in bad_apple_lyrics:
    timestamp_list.append(key)


# https://stackoverflow.com/questions/45265044/how-to-check-a-time-is-between-two-times-in-python
def is_between_time(time, time_range):
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= time <= time_range[1]


global counter_lyrics
counter_lyrics = 0


def swtich_lyrics(timestamp):
    global counter_lyrics
    if counter_lyrics == len(timestamp_list):
        counter_lyrics = len(timestamp_list) - 1

    if is_between_time(timestamp, timestamp_list[counter_lyrics]):
        print(f"\n{bcolors.FAIL}{bcolors.BOLD}{bad_apple_lyrics[timestamp_list[counter_lyrics - 1]]}{bcolors.ENDC}\n")
        counter_lyrics = counter_lyrics + 1
    else:
        print(f"\n{bcolors.BOLD}{bcolors.FAIL}{bad_apple_lyrics[timestamp_list[counter_lyrics - 1]]}{bcolors.ENDC}\n")


def render_frames(new_width):
    FRAMES_FOLDER = os.listdir(f"{THIS_FOLDER}/cache/frames")
    os.system("cls" if os.name == "nt" else "clear")
    
    # https://emojicombos.com/touhou-text-art
    cirno_doll = (
    "⠀⢀⣒⠒⠆⠤⣀⡀\n"
    "⢠⡛⠛⠻⣷⣶⣦⣬⣕⡒⠤⢀⣀\n"
    "⡿⢿⣿⣿⣿⣿⣿⡿⠿⠿⣿⣳⠖⢋⣩⣭⣿⣶⡤⠶⠶⢶⣒⣲⢶⣉⣐⣒⣒⣒⢤⡀\n"
    "⣿⠀⠉⣩⣭⣽⣶⣾⣿⢿⡏⢁⣴⠿⠛⠉⠁⠀⠀⠀⠀⠀⠀⠉⠙⠲⢭⣯⣟⡿⣷⣘⠢⡀\n"
    "⠹⣷⣿⣿⣿⣿⣿⢟⣵⠋⢠⡾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣿⣿⣾⣦⣾⣢ \n"
    "⠀⠹⣿⣿⣿⡿⣳⣿⠃⠀⣼⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢻⣿⣿⣿⠟ \n"
    "⠀⠀⠹⣿⣿⣵⣿⠃⠀⠀⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣷⡄\n"
    "⠀⠀⠀⠈⠛⣯⡇⠛⣽⣦⣿⠀⠀⠀⠀⢀⠔⠙⣄⠀⠀⠀⠀⠀⠀⣠⠳⡀⠀⠀⠀⠀⢿⡵⡀    ー   あたいったら最強ね！\n"
    "⠀⠀⠀⠀⣸⣿⣿⣿⠿⢿⠟⠀⠀⠀⢀⡏⠀⠀⠘⡄⠀⠀⠀⠀⢠⠃⠀⠹⡄⠀⠀⠀⠸⣿⣷⡀\n"
    "⠀⠀⠀⢰⣿⣿⣿⣿⡀⠀⠀⠀⠀⠀⢸⠒⠤⢤⣀⣘⣆⠀⠀⠀⡏⢀⣀⡠⢷⠀⠀⠀⠀⣿⡿⠃\n"
    "⠀⠀⠀⠸⣿⣿⠟⢹⣥⠀⠀⠀⠀⠀⣸⣀⣀⣤⣀⣀⠈⠳⢤⡀⡇⣀⣠⣄⣸⡆⠀⠀⠀⡏\n"
    "⠀⠀⠀⠀⠁⠁⠀⢸⢟⡄⠀⠀⠀⠀⣿⣾⣿⣿⣿⣿⠁⠀⠈⠙⠙⣯⣿⣿⣿⡇⠀⠀⢠⠃\n"
    "⠀⠀⠀⠀⠀⠀⠀⠇⢨⢞⢆⠀⠀⠀⡿⣿⣿⣿⣿⡏⠀⠀⠀⠀⠀⣿⣿⣿⡿⡇⠀⣠⢟⡄\n"
    "⠀⠀⠀⠀⠀⠀⡼⠀⢈⡏⢎⠳⣄⠀⡇⠙⠛⠟⠛⠀⠀⠀⠀⠀⠀⠘⠻⠛⢱⢃⡜⡝⠈⠚⡄\n"
    "⠀⠀⠀⠀⠀⠘⣅⠁⢸⣋⠈⢣⡈⢷⠇⠀⠀⠀⠀⠀⣄⠀⠀⢀⡄⠀⠀⣠⣼⢯⣴⠇⣀⡀⢸\n"
    "⠀⠀⠀⠀⠀⠀⠈⠳⡌⠛⣶⣆⣷⣿⣦⣄⣀⠀⠀⠀⠈⠉⠉⢉⣀⣤⡞⢛⣄⡀⢀⡨⢗⡦⠎\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠈⠑⠪⣿⠁⠀⠐⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⠉⠁⢸⠀⠀⠀⠄⠙⡆\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⣀⠤⠚⡉⢳⡄⠡⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣏⠁⣠⣧⣤⣄⣀⡀⡰⠁\n"
    "⠀⠀⠀⠀⠀⢀⠔⠉⠀⠀⠀⠀⢀⣧⣠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣅⡀\n"
    "⠀⠀⠀⠀⠀⢸⠆⠀⠀⠀⣀⣼⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠟⠋⠁⣠⠖⠒⠒⠛⢿⣆\n"
    "⠀⠀⠀⠀⠀⠀⠑⠤⠴⠞⢋⣵⣿⢿⣿⣿⣿⣿⣿⣿⠗⣀⠀⠀⠀⠀⠀⢰⠇⠀⠀⠀⠀⢀⡼⣶⣤\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⡠⠟⢛⣿⠀⠙⠲⠽⠛⠛⠵⠞⠉⠙⠳⢦⣀⣀⡞⠀⠀⠀⠀⡠⠋⠐⠣⠮⡁\n"
    "⠀⠀⠀⠀⠀⠀⠀⢠⣎⡀⢀⣾⠇⢀⣠⡶⢶⠞⠋⠉⠉⠒⢄⡀⠉⠈⠉⠀⠀⠀⣠⣾⠀⠀⠀⠀⠀⢸⡀\n"
    "⠀⠀⠀⠀⠀⠀⠀⠘⣦⡀⠘⢁⡴⢟⣯⣞⢉⠀⠀⠀⠀⠀⠀⢹⠶⠤⠤⡤⢖⣿⡋⢇⠀⠀⠀⠀⠀⢸\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠵⠗⠺⠟⠖⢈⡣⡄⠀⠀⠀⠀⢀⣼⡤⣬⣽⠾⠋⠉⠑⠺⠧⣀⣤⣤⡠⠟⠃\n"
    "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠷⠶⠦⠶⠞⠉"
    )

    # force maximize terminal window
    # https://stackoverflow.com/questions/2790825/how-can-i-maximize-a-specific-window-with-python
    user32 = ctypes.WinDLL("user32")
    SW_MAXIMISE = 3
    hwnd = user32.GetForegroundWindow()
    user32.ShowWindow(hwnd, SW_MAXIMISE)

    print(f"\n\n\n\n\n{bcolors.FAIL}Bad Apple!!{bcolors.ENDC}\nOrignally composed by ZUN\nCover by Alstroemeria Records feat. nomico\n")
    time.sleep(2)
    print(f"Programmed by {bcolors.WARNING}横浜{bcolors.ENDC}\n")
    time.sleep(2)
    print(f"{bcolors.WARNING}Seizure warning: flashing lights!{bcolors.ENDC}\nYou may want to close other programs to reduce lag.\n\n")
    time.sleep(2)
    print(f"{bcolors.OKCYAN}{cirno_doll}{bcolors.ENDC}")
    time.sleep(3)

    # play_music_file("cache/audio/track.mp3")

    start = datetime.datetime.now()
    for frame in FRAMES_FOLDER:
        try:
            image = Image.open(f"cache/frames/{frame}")
        except:
            print("not a valid image")
        
        new_image_data = pixels_to_ascii(grayscale(resize_image(image)))
        
        pixel_count = len(new_image_data)  
        ascii_image = "\n".join([new_image_data[index:(index + new_width)] for index in range(0, pixel_count, new_width)])

        # print(chr(27) + "[2J")
        colors = [
            bcolors.HEADER,
            bcolors.OKBLUE,
            bcolors.OKCYAN,
            bcolors.OKGREEN,
            bcolors.WARNING,
            bcolors.FAIL
        ]
        
        os.system("cls" if os.name == "nt" else "clear") # removes jittering up and down
        print(ascii_image)
        # print(f"{random.choice(colors)}{ascii_image}{bcolors.ENDC}") # random flashing colors

        lyrics_time = datetime.datetime.now()
        lyrics_time_str = str(lyrics_time - start)[2:10]
        swtich_lyrics(lyrics_time_str)
        print(lyrics_time_str)

        time.sleep(FPS) # comment out this line for debugging

    end = datetime.datetime.now()
    duration = str(end - start)[2:10]
    
    os.system("cls" if os.name == "nt" else "clear")
    print("\n" * 50 + "終")
    print(f"time taken to render frames: {duration}") # should be close to 3:44


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
        "WJq4jWSQNd8", # Go ! Bwaaah ! (short video for debugging)
        "dQw4w9WgXcQ", # ギターと孤独と蒼い惑星
    ]

    with yt_dlp.YoutubeDL(ydl_opts) as y:
        y.download([f"https://youtu.be/watch?v={ids[0]}"])

    reduce_framerate_mp4("cache/videos/bad_apple_temp.mp4", "cache/videos/bad_apple.mp4")
    extract_audio_from_mp4("cache/videos/bad_apple_temp.mp4", "cache/audio/track.mp3")
    extract_frames_from_mp4("cache/videos/bad_apple.mp4")
    resize_frames()
    render_frames(SCALE_SIZE * 2)

    try:
        shutil.rmtree("cache/videos")
    except:
        print("cache/videos not deleted")

else:
    render_frames(SCALE_SIZE * 2)
