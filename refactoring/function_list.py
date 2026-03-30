"""
mediafetch v1.0.5 - 25/03/26
By zonkedhobgoblin

A command-line Python utility to download YouTube videos and playlists 
as high-quality audio files using the yt_dlp library. Supports configurable 
codecs and bitrates.

This file is a collection of functions before refactoring.
"""
import subprocess
import platform
import json
import shutil
import sys
import urllib.request
import urllib.error
import gettext
import locale
from types import ModuleType # For module hints
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

# Global settings
#----------------------------------------------------
# Codec / Quality Settings
MEDIAFETCH_VER = "v1.0.5"
REPO_URL = "https://api.github.com/repos/ZonkedHobgoblin/mediafetch/releases/latest"
MMA_Q = ["128", "192", "256", "320"]
OPUS_Q = ["96", "128", "160"]
VORBIS_Q = ["128", "192"]
NA_Q = ["0"] # Used for lossless qualities so bitrate doesn't apply. (na = N/A)
CODEC_TYPES = {"mp3":MMA_Q, "m4a":MMA_Q, "aac":MMA_Q, "opus":OPUS_Q,
               "vorbis":VORBIS_Q, "flac":NA_Q, "alac":NA_Q, "wav":NA_Q}
#----------------------------------------------------
# Config Settings
valid_codecs = [*CODEC_TYPES]
valid_qualities = {item for sublist in CODEC_TYPES.values() for item in sublist}
script_path = Path(__file__).resolve()
default_settings = {"codec": "mp3", "quality": "320", "folder": "downloads", "update": True}
#----------------------------------------------------
# Other
os_name = platform.system()
#----------------------------------------------------

# gettext setup
# needs refactor and put into function
locales_dir = script_path.parent / "locales"
try:
    sys_lang, _ = locale.getlocale() 
    user_lang = sys_lang.split('_')[0] if sys_lang else 'en'
except Exception:
    user_lang = 'en'

try:
    lang = gettext.translation('mediafetch', localedir=locales_dir, languages=[user_lang, 'en'])
    lang.install()
    _ = lang.gettext
except FileNotFoundError:
    _ = gettext.gettext

# Functions (To be refactored and "dried")
#----------------------------------------------------
# CLI stuff
def clear() -> None:
    """Clears the terminal screen based on the operating system."""
    subprocess.run(('cls' if os_name == 'Windows' else 'clear'), shell=True)


def pause() -> None:
    """Pauses the script and waits for user input before continuing."""
    input(_("\nPress enter to continue..."))


def get_sanitized_num_input(prompt: str,
                            target_type: type,
                            min_value: int | float| None = None,
                            max_value: int | float | None = None) -> int | float:
    """
    Prompts the user for a numeric input and safely handles invalid data.

    Args:
        prompt (str): The text displayed to the user.
        target_type (type): The expected Python type (usually `int` or `float`).
        min_value (int/float, optional): The minimum allowed boundary.
        max_value (int/float, optional): The maximum allowed boundary.

    Returns:
        The cleaned numeric input matching the target_type.
    """
    while True:
        unclean_input = input(prompt)
        try:
            clean_input = target_type(unclean_input)
            if min_value is not None and clean_input < min_value:
                print(_("Error: Value cannot be below {min_value}.").format(min_value=min_value))
                continue
            if max_value is not None and clean_input > max_value:
                print(_("Error: Value cannot be above {max_value}.").format(max_value=max_value))
                continue
            return clean_input
        except ValueError:
            type_name = _("integer") if target_type is int else _("number")
            print(_("Error: Invalid input. Please enter a {type_name}.").format(type_name=type_name))


def get_sanitized_str_input(prompt: str,
                            string_list: list[str] | None = None,
                            allow_anycase: bool = False,
                            should_strip: bool = True) -> str:
    """
    Prompts the user for string input, sanitizes it, and restricts choices if needed.

    Args:
        prompt (str): The text displayed to the user.
        string_list (list, optional): A list of valid exact string matches allowed.
        allow_anycase (bool): If True, adherence to the list is not affected by caps.
        should_strip (bool): If True, removes leading/trailing whitespace.

    Returns:
        str: The sanitized string input.
    """
    if string_list is not None and allow_anycase:
        string_list = [item.lower() for item in string_list]
    while True:
        string_input = input(prompt)
        if should_strip:
            string_input = string_input.strip()
        if allow_anycase:
            string_input = string_input.lower()
        if string_list is not None and string_input not in string_list:
            print(_("Error: You must enter one of these options: "))
            print(*string_list, sep = ', ')
            continue
        return string_input


#----------------------------------------------------
# Dependency & Updating stuff
#---------------------------------------
# Parsing & Getting from Github
def parse(version_string: str) -> tuple[int, ...]:
    """Converts a version string (x.x.x) into compareble tutples"""
    clean_version = version_string.lstrip('vV')
    return tuple(map(int, clean_version.split('.')))


def request_github_ver(package: str, repo: str, cur_ver: str, silent: bool = True) -> list[bool | str]:
    """
    Ping Github api, check if newer release exists.
    Return gives:
    Bool - Needs update? True/False
    Latest version of package (parsed)
    Latest version of package (Un-Parsed)
    """
    req = urllib.request.Request(repo, headers={"User-Agent": "mediafetch"})

    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            data = json.loads(response.read().decode('utf-8'))
            latest_version_raw = data.get('tag_name')
            latest_version = parse(latest_version_raw)
            current_version = parse(cur_ver)

            if latest_version > current_version:
                if not silent:
                    clear()
                    print(_("Update Available:\nA newer version of {package} has been released!\n"
                            "Current Version: {cur_ver}\nLatest Version: {latest_version_raw}\n"
                            "It is recommended you install the latest version, for reasons such"
                            " as bug fixes.").format(package=package, cur_ver=cur_ver, latest_version_raw=latest_version_raw))
                    pause()
                return [True, latest_version, latest_version_raw]
            else:
                return [False, latest_version, latest_version_raw]
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError) as error:
        print(_("Failed to connect to GitHub to check for updates. Are you connected to the internet?\n"
                "Script will not retry updating {package} until next launch.\n"
                "Error: {error}\nTo stop this message, "
                "set 'Update Checking' to false in the config menu.").format(package=package, error=error))
        pause()

    except Exception as error:
        print(_("An unexpected error occured while trying to check for {package} updates!\n"
                "Error: {error}\nTo stop this message, set 'Update Checking' to false "
                "in the config menu.").format(package=package, error=error))
        pause()

#---------------------------------------
# yt_dlp Stuff
def get_ytdlp(update_arg: int) -> ModuleType:
    try:
        clear()
        if update_arg == 1:
            print(_("Attempting to update module yt_dlp..."))
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "yt_dlp"], check=True)
            print(_("\nSuccesfully updated yt_dlp!\n"))
        elif update_arg == 2:
            clear()
            print(_("Attempting to install module yt_dlp..."))
            # sys.executable ensures it uses the pip associated with the current Python env
            subprocess.run([sys.executable, "-m", "pip", "install", "yt_dlp"], check=True)
            print(_("\nSuccesfully installed yt_dlp!\n"))
        else:
            print(_("Something went wrong."))
            pause()
            sys.exit(1)
        pause()
        import yt_dlp
        return yt_dlp
    except Exception as error:
        py_cmd = 'py' if os_name == 'Windows' else 'python3'
        upgrade_flag = '--upgrade ' if update_arg == 1 else ''
        print(_("\nAuto-Install failed. Please open your terminal and run this command:\n"
                "{py_cmd} -m pip install {upgrade_flag}yt_dlp\n"
                "Error: {error}").format(py_cmd=py_cmd, upgrade_flag=upgrade_flag, error=error))
        pause()
        sys.exit(1)

def check_ytdlp(can_update: bool) -> int:
    """
    We check yt_dlp's current status and return it:
    0 = Up-To-Date, nothing should be done
    1 = Out-Of-Date, needs updating
    2 = Not-Installed, needs installing
    Pass this to main and use match case we decide what to do
    """
    clear()
    try:
        ytdlp_ver = version('yt_dlp')
        if can_update and (update_data := request_github_ver("yt_dlp", "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest",
                                              ytdlp_ver, True))[0]:
            latest_version = update_data[2]
            print(_("yt_dlp is outdated!\nCurrent: {ytdlp_ver}\n"
                    "Latest: {latest_version}\nWould you like this script to attempt "
                    "installation of the latest version via pip? (Y/N)").format(ytdlp_ver=ytdlp_ver, latest_version=latest_version))
            if get_sanitized_str_input("> ", ['y', 'n'], True, True) == 'y' :
                return 1
        return 0

    except PackageNotFoundError:
        print(_("Missing dependency! yt_dlp is not installed.\nWould you like "
                "this script to attempt installation via pip? (Y/N)\n"))
        if get_sanitized_str_input("> ", ['y', 'n'], True,
                                   True) == 'y' :
            return 2
        else:
            py_cmd = 'py' if os_name == 'Windows' else 'python3'
            print(_("\nyt_dlp is required to run MediaFetch!\n"
                    "Please open your terminal and run this command:\n"
                    "{py_cmd} -m pip install yt_dlp").format(py_cmd=py_cmd))
            pause()
            sys.exit(1)
    
    except Exception as error:
        print(_("An error occured when checking for yt_dlp's version!\n"
                "Error: {error}").format(error=error))
        pause()
        sys.exit(1)


#---------------------------------------
# FFmpeg stuff
def checknget_ffmpeg() -> bool:
    """
    Checks system path for FFmpeg dependency. 
    If missing, prompts the user with OS-specific automated installation options.
    """
    if shutil.which('ffmpeg') is not None:
        return True
    
    clear()
    print(_("Missing dependency! FFmpeg is missing\nyt_dlp requires FFmpeg to "
            "extract and convert audio files."))
    auto_install = get_sanitized_str_input(_("Would you like this script to "
                                             "attempt installation, or view "
                                             "installation instructions "
                                             "yourself? (Y/N)\n> ")
                                           , ["y", "n"], True, True)
    clear()
    match os_name:
        case "Windows":
            if auto_install == "y":
                try:
                    print(_("Attempting auto install via winget..."))
                    subprocess.run(['winget', 'install', 'ffmpeg',
                                    '--accept-package-agreements',
                                    '--accept-source-agreements'],
                                   check=True)
                    print(_("\nFFmpeg succesfully installed! Script will "
                            "restart..."))
                    pause()
                    subprocess.Popen(['start', 'cmd', '/K', sys.executable,
                                      script_path])
                    sys.exit(0)
                except Exception as error:
                    print(_("\nAuto-Install error, please review manual "
                            "instructions! (Is winget missing?)\nError: {error}").format(error=error))
                    pause()
            clear()
            print(_("Manual FFmpeg installation:\nOption 1: Open CMD and "
                    "run: winget install ffmpeg\nOption 2: Download from: "
                    "https://github.com/BtbN/FFmpeg-Builds/releases"))
            pause()
            sys.exit(1)
            
        case "Darwin":
            has_brew = shutil.which("brew") is not None
            if auto_install == "y":
                if has_brew:
                    try:
                        print(_("Attempting auto install via Homebrew..."))
                        subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
                        print(_("\nFFmpeg succesfully installed! Script will "
                                "restart..."))
                        pause()
                        applescript = ('tell application "Terminal" to do script '
                        f'"{sys.executable} {script_path}"')
                        subprocess.Popen(['osascript', '-e', applescript])
                        sys.exit(0)
                    except Exception as error:
                        print(_("\nAuto-Install error, please review manual "
                                "instructions!\nError:{error}").format(error=error))
                        pause()
                else:
                    print(_("Homebrew was not found, Please review manual "
                            "instructions!"))
                    pause()
                
            clear()
            print(_("Manual FFmpeg installation:\nStep 1. Install Homebrew if "
                    "missing: https://brew.sh/\nStep 2. Open Terminal and run: "
                    "brew install ffmpeg"))
            pause()
            sys.exit(1)

        case "Linux":
            if auto_install == "y":
                print(_("Attempting auto install via sudo apt...\n"
                        "NOTE: You may be prompted to enter your sudo password "
                        "below."))
                try:
                    subprocess.run(['sudo', 'apt', 'install', '-y', 'ffmpeg'],
                                   check=True)
                    if shutil.which("gnome-shell") is not None:
                        print(_("\nFFmpeg succesfully installed! Script will "
                                "restart..."))
                        pause()
                        subprocess.Popen(['gnome-terminal', '--',
                                          sys.executable, script_path])
                        sys.exit(1)
                    else:
                        print(_("\nFFmpeg succesfully installed! Please open the"
                                " script again..."))
                        pause()
                        sys.exit(1)
                except Exception as error:
                    print(_("\nAuto-Install error, please review manual "
                            "instructions!\nError: {error}").format(error=error))
                    pause()
            clear()
            print(_("Manual FFmpeg installation:\nDebian/Ubuntu: sudo apt install"
                    " ffmpeg\nArch Linux:  sudo pacman -S ffmpeg\nFedora:      "
                    "sudo dnf install ffmpeg"))
            pause()
            sys.exit(1)
        case _:
            clear()
            print(_("\nPossibly unsupported operating system!\nPlease search "
                    "online for: 'How to install FFmpeg on (Your OS)'"))
            pause()
            sys.exit(1)


#---------------------------------------
# Python Version Checking
def check_py() -> None:
    """Ensures the script is running on a compatible version of Python."""
    if sys.version_info < (3, 10):
        print(_("This script requires Python 3.10 or higher!"))
        pause()
        sys.exit(0)


#----------------------------------------------------
# Downloading
def download_video(yt_dlp: ModuleType, url: str, codec: str, quality: str, folder: str) -> None:
    """
    Downloads audio from a YouTube URL using yt_dlp.

    Args:
        url (str): The YouTube video or playlist link.
        codec (str): The target audio format (e.g., 'mp3', 'flac').
        quality (str): The target bitrate (e.g., '256', '320').
        folder (str): The relative or absolute path to save the file.
    """
    ydl_opts = {
        # Audio Settings
        'format': 'bestaudio/best',
        'outtmpl': f'{folder}/%(title)s.%(ext)s', # Save in a downloads folder
        'postprocessors': [{
            'key': "FFmpegExtractAudio",
            'preferredcodec': codec,
            'preferredquality': quality,
        }],
        
        # Pretending to be the Android App (Instead of a web browser) stops
        # "Signature solving" and "n challenges" issues when downloading
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'ios'],
            }
        },

        'quiet': False,
        'no_warnings': True,
    }

    try:
        # Create the downloads folder if it doesn't exist in the current dir
        Path(folder).mkdir(parents=True, exist_ok=True)

        print(_("Downloading: {url}").format(url=url))
        
        # Pass the ydl_opts dict to the downloader
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            
        print(_("Downloading finished! \n"))
        
    except yt_dlp.utils.DownloadError as error:
        print(_("yt_dlp encountered a download error! Error: {error}\n").format(error=error))
        
    except Exception as error:
        print(_("Failed to download. Error: {error}\n").format(error=error))


#----------------------------------------------------
# Menu Stuff
def about() -> None:
    """Displays information about the script."""
    clear()
    print(_("About:\n\nMediaFetch {mediafetch_ver} by zonkedhobgoblin\n"
            "https://github.com/ZonkedHobgoblin/mediafetch\n\n"
            "Using yt_dlp, convert videos or playlists into audio"
            " files.\nCan be configured to change the output type.\n"
            "Chosen codecs and qualities are preferred, not guaranteed"
            " to be downloaded as.\nUsually, this only applies to qualities.\n"
            "Ensure FFmpeg is set up before using.\n\n").format(mediafetch_ver=MEDIAFETCH_VER))
    pause()

def downloader(yt_dlp: ModuleType, config_settings: dict[str, str | bool]) -> None:
    """Handles the download flow from the main menu."""
    clear()
    link = input(_("Enter YouTube URL (Video or Playlist): "))
    download_video(yt_dlp, link, config_settings["codec"], config_settings["quality"],
                   config_settings["folder"])
    pause()

def menu() -> int:
    """Displays the main menu and captures the user's choice."""
    clear()
    print(_("MediaFetch - Download Youtube videos as audio files\n"
            "\n1 - Download\n2 - Config\n3 - About\n4 - Quit\n"))
    return(get_sanitized_num_input("> ", int, 1, 4))


def config(config_settings: dict[str, str | bool], config_path: Path) -> None:
    """Handles the configuration sub-menu, allowing the user to mutate settings."""
    clear()
    print(_("MediaFetch config\n1 - Audio File Type\n2 - Audio Quality\n3 - "
            "Download Folder\n4 - Update Checking"))
    match get_sanitized_num_input("> ", int, 1, 4):
        case 1:
            clear()
            print(_("1 - Audio File Type\nCurrent type selected:"
                    " {codec}\n"
                    "Please select one of the following "
                    "audio file types:").format(codec=config_settings.get('codec')))
            print(*valid_codecs, sep=', ')
            config_settings.update({"codec":
                                    get_sanitized_str_input("> ", valid_codecs,
                                                            True, True)})
            # Automatically assign the highest available bitrate for the new codec
            config_settings.update({"quality":
                                    ((CODEC_TYPES.get(
                                        config_settings.get("codec")))[-1])})
            save_config(config_settings, config_path)
            print(_("Codec type set!"))
            pause()
        case 2:
            clear()
            # If the codec is lossless (e.g. "0"), skip quality selection
            if not CODEC_TYPES.get(config_settings.get('codec'))[0] == "0" :
                print(_("2 - Audio Quality\nCurrent Audio type & quality:\n"
                        "Type: {codec}\n"
                        "Quality: {quality}\n"
                        "Please select one of the following preferred "
                        "qualities available for your chosen audio type:").format(
                            codec=config_settings.get('codec'), quality=config_settings.get('quality')))
                print(*(CODEC_TYPES.get(config_settings.get('codec'))))
                config_settings.update({"quality":
                                        get_sanitized_str_input("> ",
                                                                CODEC_TYPES.get(
                                                                    config_settings.get('codec')),
                                                                True, True)})
                save_config(config_settings, config_path)
                print(_("Audio quality set!"))
                pause()
            else:
                print(_("2 - Audio Quality\nCurrent Audio type & quality:\n"
                        "Type: {codec} (Lossless)\n"
                        "Quality: N/A\nYou have selected a lossless audio "
                        "quality type. You cannot select a quality for this audio"
                        " type!").format(codec=config_settings.get('codec')))
                pause()
        case 3:
            clear()
            print(_("3 - Audio file download folder\nThe current folder where "
                    "audio files will download.\nIf no path is given before folder"
                    " name (So putting 'downloads' rather than 'C:/Downloads')"
                    ", it will create and download the audio in the same folder "
                    "as the python script.\nCurrent Folder: "
                    "{folder}\nPlease enter the name or path"
                    " to a folder, or press enter to cancel.").format(folder=config_settings.get('folder')))
            new_path = get_sanitized_str_input("> ", None, None, True)
            # User hit enter without typing anything
            if not new_path:
                print(_("Audio file download folder unchanged!"))
                pause()
                return
            if Path(new_path).is_absolute():
                config_settings.update({"folder":new_path})
                save_config(config_settings, config_path)
                print(_("Audio file download folder set!"))
                pause()
            elif Path(script_path.parent / new_path).is_absolute():
                config_settings.update({"folder":new_path})
                save_config(config_settings, config_path)
                print(_("Audio file download folder set!"))
                pause()
                
            else:
                print(_("Path formatted incorrectly!"))
                pause()
        case 4:
            clear()
            print(_("4 - Update Checking\nEnable/Disable the script checking for updates on startup."
                    "\nCurrent status: {update}\nEnter a new status: (Y/N)").format(update=config_settings.get('update')))
            opt = get_sanitized_str_input("> ", ["y", "n"], True, True)
            config_settings.update({"update": opt == 'y'})
            save_config(config_settings, config_path)
            print(_("Update status changed! Now set to: {update}").format(update=config_settings.get('update')))
            pause()


#----------------------------------------------------
# Config save / loading
def save_config(config_settings: dict[str, str | bool], config_path: Path) -> None:
    """Saves the current configuration dictionary to a local JSON file."""
    try:
        with open(config_path, 'w') as config_file:
                json.dump(config_settings, config_file, indent=4)
    except Exception as error:
        print(_("An error occured while trying to save config settings!"
                "Error: {error}").format(error=error))
        pause()

    
def load_config(config_path: Path) -> dict[str, str | bool]:
    """
    Loads configuration from a JSON file. 
    If the file is missing or corrupted, writes and returns default settings.
    
    Returns:
        dict: The loaded or default configuration settings.
    """
    default_settings = {"codec": "mp3", "quality": "320", "folder": "downloads", "update": True}
    try:
        # Make a new config file and dump the default settings in
        if not config_path.exists():
            with open(config_path, 'w') as config_file:
                json.dump(default_settings, config_file, indent=4)
            return default_settings
        else:
            # Get our existing config file, and if its correct we return it
            with open(config_path, 'r') as config_file:
                loaded_config = json.load(config_file)
            codec = loaded_config.get('codec')
            quality = loaded_config.get('quality')
            # Validate our loaded config against our allowed variables
            if codec not in valid_codecs or quality not in valid_qualities:
                raise ValueError("Invalid or missing values in config.")
            return loaded_config
    except Exception as error:
        print(_("Config file is possibly corrupted! Using default settings and "
                "resetting file. This can be due to invalid values or invalid "
                "formatting of .json file.\nError: {error}").format(error=error))
        pause()
        with open(config_path, 'w') as config_file:
                json.dump(default_settings, config_file, indent=4)
        return default_settings


#----------------------------------------------------
# Main code loop
if  __name__ == "__main__":
    check_py()
    config_path = script_path.parent / "config.json"
    config_settings = load_config(config_path)
    if config_settings["update"]:
        request_github_ver("MediaFetch", "https://api.github.com/repos/ZonkedHobgoblin/mediafetch/releases/latest",
                           MEDIAFETCH_VER, False)
    match check_ytdlp(config_settings["update"]):
        case 1 | 2 as status:
            yt_dlp = get_ytdlp(status)
        case 0:
            import yt_dlp
            pass
    checknget_ffmpeg()
    while True:
        match menu():
            case 1:
                downloader(yt_dlp, config_settings)
            case 2:
                config(config_settings, config_path)
            case 3:
                about()
            case 4:
                break
            case _:
                print(_("Something went wrong. Please try again.\n"))
                pause()