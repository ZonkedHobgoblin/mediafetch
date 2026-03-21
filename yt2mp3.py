"""
yt2mp3 v1.0.3 - 21/03/26
By zonkedhobgoblin

A command-line Python utility to download YouTube videos and playlists 
as high-quality audio files using the yt_dlp library. Supports configurable 
codecs and bitrates.
"""
import subprocess
import platform
import json
import shutil
import sys
from pathlib import Path

# Global settings for codec mapping
MMA_Q = ["128", "192", "256", "320"]
OPUS_Q = ["96", "128", "160"]
VORBIS_Q = ["128", "192"]
NA_Q = ["0"] # Used for lossless qualities so bitrate doesn't apply. (na = N/A)
CODEC_TYPES = {"mp3":MMA_Q, "m4a":MMA_Q, "aac":MMA_Q, "opus":OPUS_Q,
                   "vorbis":VORBIS_Q, "flac":NA_Q, "alac":NA_Q, "wav":NA_Q}
valid_codecs = [*CODEC_TYPES]
valid_qualities = {item for sublist in CODEC_TYPES.values() for item in sublist}
script_path = Path(__file__).resolve()
os_name = platform.system()


def clear() -> None:
    """Clears the terminal screen based on the operating system."""
    subprocess.run(('cls' if os_name == 'Windows' else 'clear'), shell=True)


def pause() -> None:
    """Pauses the script and waits for user input before continuing."""
    input("\nPress enter to continue . . . ")


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
                print(f"Error: Value cannot be below {min_value}.")
                continue
            if max_value is not None and clean_input > max_value:
                print(f"Error: Value cannot be above {max_value}.")
                continue
            return clean_input
        except ValueError:
            type_name = "integer" if target_type == int else "number"
            print(f"Error: Invalid input. Please enter a {type_name}.")


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
            print(f"Error: You must enter one of these options: ")
            print(*string_list, sep = ', ')
            continue
        return string_input


def import_ytdlp() -> module:
    # yt_dlp checking and setup
    try:
        import yt_dlp
        return yt_dlp
    except ImportError:
        print("Missing dependency! yt_dlp is not installed.")
        auto_install = get_sanitized_str_input("Would you like this script to "
                                               "attempt installation via pip? "
                                               "(Y/N)\n> ", ['y', 'n'], True,
                                               True)
    
        if auto_install == 'y':
            try:
                print("Attempting to install yt_dlp...")
                # sys.executable ensures it uses the pip associated with the current Python environment
                subprocess.run([sys.executable, "-m", "pip", "install", "yt_dlp"], check=True)
                print("Successfully installed yt_dlp!\n")
                pause()
                import yt_dlp  # Import it now that it's installed
                return yt_dlp
            except Exception as error:
                print(f"\nAuto-Install failed. Please open your terminal and run 'pip install yt_dlp'.\nError: {error}")
                pause()
                sys.exit(1)
        else:
            print("Please install yt_dlp manually to use this script. Open your terminal and run 'pip install yt_dlp'.")
            pause()
            sys.exit(1)

            
def download_video(yt_dlp: module, url: str, codec: str, quality: str, folder: str) -> None:
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

        print(f"Downloading: {url}")
        
        # Pass the ydl_opts dict to the downloader
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            
        print("Downloading finished! \n")
        
    except yt_dlp.utils.DownloadError as error:
        print(f"yt_dlp encountered a download error! Error: {error}\n")
        
    except Exception as error:
        print(f"Failed to download. Error: {error}\n")


def menu() -> int:
    """Displays the main menu and captures the user's choice."""
    clear()
    print("yt2mp3 - Download Youtube videos as audio files\n"
          "\n1 - Download\n2 - Config\n3 - About\n4 - Quit\n")
    return(get_sanitized_num_input("> ", int, 1, 4))


def downloader(yt_dlp: module, config_settings: dict[str, str]) -> None:
    """Handles the download flow from the main menu."""
    clear()
    link = input("Enter YouTube URL (Video or Playlist): ")
    download_video(yt_dlp, link, config_settings["codec"], config_settings["quality"],
                   config_settings["folder"])
    pause()
    

def config(config_settings: dict[str, str], config_path: Path) -> None:
    """Handles the configuration sub-menu, allowing the user to mutate settings."""
    clear()
    print("yt2mp3 config\n1 - Audio File Type\n2 - Audio Quality\n3 - "
          "Download Folder")
    match get_sanitized_num_input("> ", int, 1, 3):
        case 1:
            clear()
            print("1 - Audio File Type\nCurrent type selected:"
                  f" {config_settings.get('codec')}\n"
                  "Please select one of the following "
                  "audio file types:")
            print(*valid_codecs, sep=', ')
            config_settings.update({"codec":
                                    get_sanitized_str_input("> ", valid_codecs,
                                                            True, True)})
            # Automatically assign the highest available bitrate for the new codec
            config_settings.update({"quality":
                                    ((CODEC_TYPES.get(
                                        config_settings.get("codec")))[-1])})
            save_config(config_settings, config_path)
            print("Codec type set!")
            pause()
        case 2:
            clear()
            # If the codec is lossless (e.g. "0"), skip quality selection
            if not CODEC_TYPES.get(config_settings.get('codec'))[0] == "0" :
                print("2 - Audio Quality\nCurrent Audio type & quality:\n"
                      f"Type: {config_settings.get('codec')}\n"
                      f"Quality: {config_settings.get('quality')}\n"
                      "Please select one of the following preferred "
                      "qualities available for your chosen audio type:")
                print(*(CODEC_TYPES.get(config_settings.get('codec'))))
                config_settings.update({"quality":
                                        get_sanitized_str_input("> ",
                                                                CODEC_TYPES.get(
                                                                    config_settings.get('codec')),
                                                                True, True)})
                save_config(config_settings, config_path)
                print("Audio quality set!")
                pause()
            else:
                print("2 - Audio Quality\nCurrent Audio type & quality:\n"
                      f"Type: {config_settings.get('codec')} (Lossless)\n"
                      "Quality: N/A\nYou have selected a lossless audio "
                      "quality type. You cannot select a quality for this audio"
                      " type!")
                pause()
        case 3:
            clear()
            print("3 - Audio file download folder\nThe current folder where "
                  "audio files will download.\nIf no path is given before folder"
                  " name (So putting 'downloads' rather than 'C:/Downloads')"
                  ", it will create and download the audio in the same folder "
                  "as the python script.\nCurrent Folder: "
                  f"{config_settings.get('folder')}\nPlease enter the name or path"
                  " to a folder, or press enter to cancel.")
            new_path = get_sanitized_str_input("> ", None, None, True)
            # User hit enter without typing anything
            if not new_path:
                print("Audio file download folder unchanged!")
                pause()
                return
            if Path(new_path).is_absolute():
                config_settings.update({"folder":new_path})
                save_config(config_settings, config_path)
                print("Audio file download folder set!")
                pause()
            elif Path(script_path.parent / new_path).is_absolute():
                config_settings.update({"folder":new_path})
                save_config(config_settings, config_path)
                print("Audio file download folder set!")
                pause()
                
            else:
                print("Path formatted incorrectly!")
                pause()


def about() -> None:
    """Displays information about the script."""
    clear()
    print("About:\n\nyt2mp3 v1.0.0 by zonkedhobgoblin\n"
          "https://github.com/ZonkedHobgoblin/yt2mp3\n\n"
          "Using yt_dlp, convert videos or playlists into audio"
          " files.\nCan be configured to change the output type.\n"
          "Chosen codecs and qualities are preferred, not guaranteed"
          " to be downloaded as.\nUsually, this only applies to qualities.\n"
          "Ensure FFmpeg is set up before using.\n\n")
    pause()


def save_config(config_settings: dict[str, str], config_path: Path) -> None:
    """Saves the current configuration dictionary to a local JSON file."""
    try:
        with open(config_path, 'w') as config_file:
                json.dump(config_settings, config_file, indent=4)
    except Exception as error:
        print("An error occured while trying to save config settings!"
              f"Error: {error}")
        pause()

    
def load_config(config_path: Path) -> dict[str, str]:
    """
    Loads configuration from a JSON file. 
    If the file is missing or corrupted, writes and returns default settings.
    
    Returns:
        dict: The loaded or default configuration settings.
    """
    default_settings = {"codec": "mp3", "quality": "320", "folder": "downloads"}
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
        print("Config file is possibly corrupted! Using default settings and "
              "resetting file. This can be due to invalid values or invalid "
              f"formatting of .json file.\nError: {error}")
        pause()
        with open(config_path, 'w') as config_file:
                json.dump(default_settings, config_file, indent=4)
        return default_settings


def checknget_ffmpeg() -> bool:
    """
    Checks system path for FFmpeg dependency. 
    If missing, prompts the user with OS-specific automated installation options.
    """
    if shutil.which('ffmpeg') is not None:
        return True
    
    clear()
    print("Missing dependency! FFmpeg is missing\nyt_dlp requires FFmpeg to "
          "extract and convert audio files.")
    auto_install = get_sanitized_str_input("Would you like this script to "
                                           "attempt installation, or view "
                                           "installation instructions "
                                           "yourself? (Y/N)\n> "
                                           , ["y", "n"], True, True)
    clear()
    match os_name:
        case "Windows":
            if auto_install == "y":
                try:
                    print("Attempting auto install via winget...")
                    subprocess.run(['winget', 'install', 'ffmpeg',
                                    '--accept-package-agreements',
                                    '--accept-source-agreements'],
                                   check=True)
                    print("\nFFmpeg succesfully installed! Script will "
                          "restart...")
                    pause()
                    subprocess.Popen(['start', 'cmd', '/K', sys.executable,
                                      script_path])
                    sys.exit(0)
                except Exception as error:
                    print("\nAuto-Install error, please review manual "
                          f"instructions! (Is winget missing?)\nError: {error}")
                    pause()
            clear()
            print("Manual FFmpeg installation:\nOption 1: Open CMD and "
                  "run: winget install ffmpeg\nOption 2: Download from: "
                  "https://github.com/BtbN/FFmpeg-Builds/releases")
            pause()
            sys.exit(1)
            
        case "Darwin":
            has_brew = shutil.which("brew") is not None
            if auto_install == "y":
                if has_brew:
                    try:
                        print("Attempting auto install via Homebrew...")
                        subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
                        print("\nFFmpeg succesfully installed! Script will "
                              "restart...")
                        pause()
                        applescript = ('tell application "Terminal" to do script '
                        f'"{sys.executable} {script_path}"')
                        subprocess.Popen(['osascript', '-e', applescript])
                        sys.exit(0)
                    except Exception as error:
                        print("\nAuto-Install error, please review manual "
                              f"instructions!\nError:{error}")
                        pause()
                else:
                    print("Homebrew was not found, Please review manual "
                          "instructions!")
                    pause()
                
            clear()
            print("Manual FFmpeg installation:\nStep 1. Install Homebrew if "
                  "missing: https://brew.sh/\nStep 2. Open Terminal and run: "
                  "brew install ffmpeg")
            pause()
            sys.exit(1)

        case "Linux":
            if auto_install == "y":
                print("Attempting auto install via sudo apt...\n"
                      "NOTE: You may be prompted to enter your sudo password "
                      "below.")
                try:
                    subprocess.run(['sudo', 'apt', 'install', '-y', 'ffmpeg'],
                                   check=True)
                    if shutil.which("gnome-shell") is not None:
                        print("\nFFmpeg succesfully installed! Script will "
                              "restart...")
                        pause()
                        subprocess.Popen(['gnome-terminal', '--',
                                          sys.executable, script_path])
                        sys.exit(1)
                    else:
                        print("\nFFmpeg succesfully installed! Please open the"
                              " script again...")
                        pause()
                        sys.exit(1)
                except Exception as error:
                    print("\nAuto-Install error, please review manual "
                          f"instructions!\nError: {error}")
                    pause()
            clear()
            print("Manual FFmpeg installation:\nDebian/Ubuntu: sudo apt install"
                  " ffmpeg\nArch Linux:  sudo pacman -S ffmpeg\nFedora:      "
                  "sudo dnf install ffmpeg")
            pause()
            sys.exit(1)
        case _:
            clear()
            print("\nPossibly unsupported operating system!\nPlease search "
                  "online for: 'How to install FFmpeg on (Your OS)'")
            pause()
            sys.exit(1)


def check_py() -> None:
    """Ensures the script is running on a compatible version of Python."""
    if sys.version_info < (3, 10):
        print("This script requires Python 3.10 or higher!")
        pause()
        sys.exit(0)

        
if __name__ == "__main__":
    check_py()
    yt_dlp = import_ytdlp()
    checknget_ffmpeg()
    config_path = script_path.parent / "config.json"
    config_settings = load_config(config_path)
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
                print("Something went wrong. Please try again.\n")
                pause()
