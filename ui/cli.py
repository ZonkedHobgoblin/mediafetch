import subprocess
import sys
from utils.core_utils import _
from core.constants import OS_NAME, MEDIAFETCH_VER


class CLIInterface:
    
    
    def __init__(self, config_ref, dependency_ref, downloader_ref, updater_ref):
        self.config = config_ref
        self.dependency = dependency_ref
        self.downloader = downloader_ref
        self.updater = updater_ref
        
        
    def run(self):
        self.config.load()
        self.current_config = self.config.settings
        while True:
            CLIUtils.clear()
            self.menu()
            match CLIUtils.get_sanitized_num_input("> ", int, 1, 4):
                case 1:
                    CLIUtils.clear()
                    self.handle_downloader()
                case 2:
                    CLIUtils.clear()
                    pass#self.config()
                case 3:
                    CLIUtils.clear()
                    self.show_about()
                case 4:
                    break
    
    
    def menu(self) -> None:
        """Displays the main menu and captures the user's choice."""
        print(_("MediaFetch - Download Youtube videos as audio files\n"
                "\n1 - Download\n2 - Config\n3 - About\n4 - Quit\n"))
        
        
    def show_about(self) -> None:
        """Displays information about the script."""
        print(_("About:\n\nMediaFetch {mediafetch_ver} by zonkedhobgoblin\n"
        "https://github.com/ZonkedHobgoblin/mediafetch\n\n"
        "Using yt_dlp, convert videos or playlists into audio"
        " files.\nCan be configured to change the output type.\n"
        "Chosen codecs and qualities are preferred, not guaranteed"
        " to be downloaded as.\nUsually, this only applies to qualities.\n"
        "Ensure FFmpeg is set up before using.\n\n").format(mediafetch_ver=MEDIAFETCH_VER))
        CLIUtils.pause()
        
    def handle_downloader(self) -> None:
        """Handles the download flow from the main menu."""
        CLIUtils.clear()
        link = input(_("Enter YouTube URL (Video or Playlist): "))
        print(_("Downloading: {url}").format(url=link))
        status = self.downloader.download_audio(link, self.current_config["codec"], 
                                                self.current_config["quality"], 
                                                self.current_config["folder"])                      
        match status:
            case "SUCCESS":
                pass
            
            case "ERR_DOWNLOAD":
                print("Error downloading video!")
            
            case "ERR_UNKOWN" | _:
                print("Something went wrong!")
        CLIUtils.pause()
            
        print(_("Downloading finished! \n"))
        CLIUtils.pause()
        
    def handle_config_io(self) -> None:
        """Handles the loading and saving of the config manager."""
        status = self.config.load()
        match status:
            case "SUCCESS":
                pass
                
            case "ERR_CORRUPT":
                print(_("Config file is possibly corrupted! Using default settings."))
                pass
                
            case "ERR_NOTFOUND":
                print(_("Config file not found! Using default settings."))
                pass
            
            case "ERR_PARSE":
                print(_("Config file contains incorrect values! Using default settings."))
                pass
                
            case "ERR_UNKOWN":
                print(_("An unknown error occured! Using default settings."))
                pass
            
            case _:
                print(_("Something went wrong when attempting to load config file. Exiting."))
                sys.exit(1)
                
        status = self.config.save()
        match status:
            case "SUCCESS":
                pass
            case "ERR_SAVE":
                print(_("Something went wrong when attempting to save config file. Exiting."))
                sys.exit(1)
                


class CLIUtils:
    
    
    @staticmethod
    def clear() -> None:
        """Clears the terminal screen based on the operating system."""
        subprocess.run(('cls' if OS_NAME == 'Windows' else 'clear'), shell=True)


    @staticmethod
    def pause() -> None:
        """Pauses the script and waits for user input before continuing."""
        input(_("\nPress enter to continue..."))


    @staticmethod
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
                if target_type is int:
                    print(_("Error: Invalid input. Please enter an integer."))
                else:
                    print(_("Error: Invalid input. Please enter a number."))


    @staticmethod
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