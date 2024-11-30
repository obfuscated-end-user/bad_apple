import ctypes
import gc
import os
# import sys

from datetime import datetime
from PIL.Image import open
from pygame import mixer
from random import choice
from subprocess import run, CalledProcessError
from shutil import rmtree
from time import sleep
from yt_dlp import YoutubeDL

gc.collect()

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

# each charset should have 11 chars
# anything fullwidth (CJK characters, hiragana, katakana, etc) will render like ass
# i know that not all of these are ASCII characters
ASCII_CHARSETS = [
    [*" .:;+*?%S#X"],
    # [*"X#S%?+*;:. "], # reverse
    [*" .:-=+*?#%@"],
    [*" .:;+*?%S#@"],
    [*" .:;+*?%S# "], # outlines only
    [*"          @"],
    [*"         # "],
    [*"       %S# "],
    [*"          ｱ"],
    [*" ﾉﾆﾐﾁﾂｦﾛﾀﾈﾎ"],
    [*" 0123456789"],
    # [*"dQw4w9WgXcQ"],
    [*" ▁▂▃▄▅▆▚▙▇█"],
    [*" ░░░▒▒▒▓▓▓█"],
    [*" ⠠⡐⠥⡕⡞⡟⡷⡾⡿⣿"],
]

columns, _ = os.get_terminal_size()

SCALE_SIZE = 80
# 38.4 original
RATE_CONST = 36.7000001 # adjust this if it syncs like ass, 38.50000001
FPS = 1 / RATE_CONST

# EXPERIMENTAL
FLASH_COLORS = False
RANDOM_CHARSET = False
RANDOM_CHARSET_PER_FRAME = False

if RANDOM_CHARSET:
    CHARSET = choice(ASCII_CHARSETS)
else:
    CHARSET = ASCII_CHARSETS[2]


# https://stackoverflow.com/questions/287871/how-do-i-print-colored-text-to-the-terminal
class bcolors:
    HEADER      = "\033[95m"
    OKBLUE      = "\033[94m"
    OKCYAN      = "\033[96m"
    OKGREEN     = "\033[92m"
    WARNING     = "\033[93m"
    FAIL        = "\033[91m"
    ENDC        = "\033[0m"
    BOLD        = "\033[1m"
    UNDERLINE   = "\033[4m"


def reduce_framerate_mp4(input_mp4, output_mp4):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_mp4,
        # "-filter:v", "fps=15",
        "-filter:v", "fps=24",
        output_mp4
    ]

    try:
        run(ffmpeg_cmd, check=True)
        print("Framerate conversion successful!")
    except CalledProcessError:
        print("Framerate conversion failed!")
    os.system("cls" if os.name == "nt" else "clear")


def extract_audio_from_mp4(input_mp4, output_mp3):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_mp4,
        output_mp3
    ]

    try:
        run(ffmpeg_cmd, check=True)
        print("Audio extraction successful!")
    except CalledProcessError:
        print("Audio extraction failed!")
    os.system("cls" if os.name == "nt" else "clear")


def extract_frames_from_mp4(input_mp4):
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", input_mp4,
        "cache/frames/frame%04d.png" # frame_0001.png, frame_0002.png, ...
    ]

    try:
        run(ffmpeg_cmd, check=True)
        print("Frame extraction successful!")
    except CalledProcessError:
        print("Frame extraction failed!")


# https://stackoverflow.com/questions/21517879/python-pil-resize-all-images-in-a-folder
def resize_frames():
    FRAMES_FOLDER = os.listdir(f"{THIS_FOLDER}/cache/frames")
    for item in FRAMES_FOLDER:
        if os.path.isfile(f"{THIS_FOLDER}/cache/frames/{item}"):
            im = open(f"{THIS_FOLDER}/cache/frames/{item}")
            f, _ = os.path.splitext(f"{THIS_FOLDER}/cache/frames/{item}")
            im_resize = im.resize((300, 168))
            im_resize.save(f + "_resized.png", "PNG", quality=90)
            os.remove(f"{THIS_FOLDER}/cache/frames/{item}")
            print(f"\033[1A\033[KResizing images... ({FRAMES_FOLDER.index(item)}/{len(FRAMES_FOLDER)})")


# https://youtu.be/v_raWlX7tZY
def resize_image(image, new_width=SCALE_SIZE):
    width, height = image.size
    ratio = height / width
    new_height = int(new_width * ratio)
    resized_image = image.resize((new_width, new_height))
    return resized_image


def grayscale(image):
    return image.convert("L")


def pixels_to_ascii(image):
    pixels = image.getdata()
    # multiply each "pixel" by 2 to widen the image in the terminal
    if RANDOM_CHARSET_PER_FRAME:
        return "".join([choice(ASCII_CHARSETS)[pixel // 25] * 2 for pixel in pixels])
    else:
        return "".join([CHARSET[pixel // 25] * 2 for pixel in pixels])


def play_music_file(mp3_file):
    mixer.init()
    mixer.music.load(mp3_file)
    mixer.music.play()


# https://vocaloidlyrics.fandom.com/wiki/Bad_Apple!!
# synced ONLY for this video: https://youtu.be/watch?v=FtutLA63Cp8
# used this for syncing: https://lrcgenerator.com
# yes, i'm aware that this is from another bad apple cover, just happened to also cover the shadow art version shit as well
bad_apple_lyrics = {
    ("00:01.00", "00:29.07"): "",
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
    ("01:52.57", "02:06.44"): "",
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
    ("03:30.08", "03:31.08"): "",
    ("03:32.08", "03:33.08"): "",
}

timestamp_list = [key for key in bad_apple_lyrics]


# https://stackoverflow.com/questions/45265044/how-to-check-a-time-is-between-two-times-in-python
def is_between_time(time, time_range: tuple):
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= time <= time_range[1]


global lrc_count
lrc_count = 0


def render_lyrics(timestamp):
    global lrc_count
    if lrc_count == len(timestamp_list):
        lrc_count = len(timestamp_list) - 1

    if is_between_time(timestamp, timestamp_list[lrc_count]):
        print(f"\n{bcolors.FAIL}{bcolors.BOLD}{bad_apple_lyrics[timestamp_list[lrc_count - 1]].center(columns - 7)}{bcolors.ENDC}")
        lrc_count = lrc_count + 1
    else:
        print(f"\n{bcolors.BOLD}{bcolors.FAIL}{bad_apple_lyrics[timestamp_list[lrc_count - 1]].center(columns - 7)}{bcolors.ENDC}")


colors = [
    bcolors.HEADER,
    bcolors.OKBLUE,
    bcolors.OKCYAN,
    bcolors.OKGREEN,
    bcolors.WARNING,
    bcolors.FAIL,
    bcolors.BOLD,
    bcolors.ENDC
]


def render_frames(new_width):
    FRAMES_FOLDER = os.listdir(f"{THIS_FOLDER}/cache/frames")
    os.system("cls" if os.name == "nt" else "clear")
    
    # https://emojicombos.com/touhou-text-art
    cirno_fumo = (
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

    print(f"\n\n\n\n\n{bcolors.FAIL}Bad Apple!!{bcolors.ENDC}\nComposed by ZUN\nCover by Alstroemeria Records feat. nomico\n")
    sleep(2)
    print(f"Programmed by {bcolors.WARNING}横浜{bcolors.ENDC}\n")
    sleep(2)
    print(f"{bcolors.WARNING}Seizure warning: flashing lights!{bcolors.ENDC}\nMay not work properly if you have other terminal windows open.\nYou may want to close other programs to reduce lag.\n\n")
    sleep(2)
    print(f"{bcolors.OKCYAN}{cirno_fumo}{bcolors.ENDC}\n\n")
    sleep(3)
    print(f"{bcolors.FAIL}少女祈祷中{bcolors.ENDC}\n")

    FRAMES_FOLDER_LENGTH = len(os.listdir(f"{THIS_FOLDER}/cache/frames"))
    
    frames_list = [None] * FRAMES_FOLDER_LENGTH
    frames_list = []

    for frame_image in FRAMES_FOLDER:
        try:
            image = open(f"cache/frames/{frame_image}")
        except:
            print("invalid file")
        
        new_image_data = pixels_to_ascii(grayscale(resize_image(image)))
        pixel_count = len(new_image_data)
        ascii_image = " \n".join([f"| {new_image_data[index:(index + new_width)]} |".center(columns - 1) for index in range(0, pixel_count, new_width)])

        if FLASH_COLORS:
            frames_list.append(f"{choice(colors)}{ascii_image}{bcolors.ENDC}") # random flashing colors
        else:
            frames_list.append(ascii_image)
        print(f"\033[1A\033[KConverting images into text... ({FRAMES_FOLDER.index(frame_image)}/{len(FRAMES_FOLDER)})")

    play_music_file("cache/audio/track.mp3")

    start = datetime.now()

    for frame in frames_list:
        os.system("cls" if os.name == "nt" else "clear") # removes jittering up and down
        print(f"X-{'-' * SCALE_SIZE * 2}-X".center(columns - 1))
        # print(sys.getsizeof(frame), FRAMES_FOLDER_LENGTH) # 9287 5258
        print(frame)
        print(f"X-{'-' * SCALE_SIZE * 2}-X".center(columns - 1))
        lyrics_time_str = str(datetime.now() - start)[2:10]
        render_lyrics(lyrics_time_str)
        print(lyrics_time_str.center(columns - 1))
        sleep(FPS) # comment out this line for debugging

    end = datetime.now()
    duration = str(end - start)[2:10]
    
    os.system("cls" if os.name == "nt" else "clear")
    sleep(3)
    print("\n" * 25 + f"{bcolors.OKCYAN}{cirno_fumo}{bcolors.ENDC}" + "\n" * 10 + "終")
    print(f"Time taken to render frames: {duration}") # should be close to 3:44


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

    with YoutubeDL(ydl_opts) as y:
        y.download([f"https://youtu.be/watch?v={ids[0]}"])

    reduce_framerate_mp4("cache/videos/bad_apple_temp.mp4", "cache/videos/bad_apple.mp4")
    extract_audio_from_mp4("cache/videos/bad_apple_temp.mp4", "cache/audio/track.mp3")
    extract_frames_from_mp4("cache/videos/bad_apple.mp4")
    resize_frames()
    render_frames(SCALE_SIZE * 2)

    try:
        rmtree("cache/videos")
    except:
        print("cache/videos not deleted")

else:
    render_frames(SCALE_SIZE * 2)
