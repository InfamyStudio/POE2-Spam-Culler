import re
import asyncio
from pathlib import Path
import win32gui
import json
import time
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Sets up logging for the POE2 Spam Culler application.
    This function configures a logger named 'poe2_spam_culler' with the INFO logging level.
    It sets up two handlers:
    - A RotatingFileHandler that writes log messages to 'spam_monitor.log', with a maximum file size of 5 MB and up to 5 backup files.
    - A StreamHandler that outputs log messages to the console.
    Both handlers use a formatter that includes the timestamp, log level, and message in the log output.
    Returns:
        logger: Configured logger instance.
    """
    logger = logging.getLogger('poe2_spam_culler')
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    file_handler = RotatingFileHandler('spam_monitor.log', maxBytes=5*1024*1024, backupCount=5)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def load_spam_lists():
    """
    Loads spam host and spam Discord lists from text files.
    This function reads two files, 'spam_hosts.txt' and 'spam_discord.txt', and loads their contents into sets.
    Each line in the files is stripped of leading/trailing whitespace, converted to lowercase, and added to the respective set.
    If a file is not found, a FileNotFoundError is logged and raised.
    Any other exceptions encountered during file reading are also logged and raised.
    Returns:
        tuple: A tuple containing two sets:
            - spam_hosts (set): A set of spam host entries.
            - spam_discord (set): A set of spam Discord entries.
    Raises:
        FileNotFoundError: If either 'spam_hosts.txt' or 'spam_discord.txt' is not found.
        Exception: If any other error occurs during file reading.
    """
    spam_hosts = set()
    spam_discord = set()
    logger = logging.getLogger('poe2_spam_culler')
    
    for file_path, target_set in [('spam_hosts.txt', spam_hosts), ('spam_discord.txt', spam_discord)]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                target_set.update(line.strip().lower() for line in f if line.strip())
            logger.info(f"Loaded {len(target_set)} entries from {file_path}")
        except FileNotFoundError:
            logger.error(f"Required file {file_path} not found")
            raise
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            raise
    
    return spam_hosts, spam_discord

class POEWindow:
    """
    A class to represent and interact with the Path of Exile 2 game window.
    Attributes:
    -----------
    hwnd : int or None
        Handle to the Path of Exile 2 window.
    last_find_attempt : int
        Timestamp of the last attempt to find the window.
    logger : logging.Logger
        Logger instance for logging messages.
    Methods:
    --------
    find_poe_window():
        Attempts to find the Path of Exile 2 window and sets the hwnd attribute if found.

    To note this class is a helper function to locate the POE2 window and allows for expansion such as:
    - Bringing POE2 to foreground
    - Sending key inputs to an in focus POE2 window
    This is merely a helper class to allow for building upon actual interactions with the POE2 window.
    """
    def __init__(self, logger: logging.Logger):
        self.hwnd = None
        self.last_find_attempt = 0
        self.logger = logger
        self.find_poe_window()

    def find_poe_window(self):
        """
        Finds the Path of Exile 2 window by enumerating through all visible windows.
        This method uses the win32gui library to enumerate through all visible windows
        and checks if the window title contains "Path of Exile 2". If such a window is found,
        it sets the hwnd attribute to the handle of the first matching window and logs the window title.
        Returns:
            bool: True if the Path of Exile 2 window is found, False otherwise.
        Logs:
            - Info: If the Path of Exile 2 window is found, logs the window title.
            - Warning: If the Path of Exile 2 window is not found.
            - Error: If an exception occurs during the search process, logs the error message.
        """
        try:
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if "Path of Exile 2" in title:
                        windows.append(hwnd)
                return True

            windows = []
            win32gui.EnumWindows(callback, windows)

            if windows:
                self.hwnd = windows[0]
                self.logger.info(f"POE window found: {win32gui.GetWindowText(self.hwnd)}")
                return True
            
            self.logger.warning("POE window not found")
            return False
            
        except Exception as e:
            self.logger.error(f"Error finding POE window: {e}")
            return False

class SpamMonitor:
    """
    A class to monitor and analyze spam content in log files.
    Attributes:
        logger (Logger): Logger instance for logging messages.
        last_size (int): The size of the log file during the last check.
        spam_hosts (list): List of spam hostnames.
        spam_discord (list): List of spam discord patterns.
        url_patterns (list): Compiled regex patterns for detecting URLs.
        from_pattern (Pattern): Compiled regex pattern for extracting player messages.
        discord_patterns (list): Compiled regex patterns for detecting Discord invites.
        currency_patterns (list): Compiled regex patterns for detecting currency offers.
        coupon_patterns (list): Compiled regex patterns for detecting coupon codes.
    Methods:
        compile_patterns():
            Compiles regex patterns for detecting spam content.
        analyse_spam_content(message):
            Analyses a given message for spam content.
        async check_for_spam(log_file):
            Checks the log file for spam content and logs detected spam.
    """
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.last_size = 0
        self.spam_hosts, self.spam_discord = load_spam_lists()
        self.compile_patterns()
        
    def compile_patterns(self):
        """
        Compiles various regular expression patterns used for detecting spam.
        This method compiles the following patterns:
        - `url_patterns`: Matches URLs from a predefined list of spam hosts.
        - `from_pattern`: Matches log entries indicating the source of a message.
        - `discord_patterns`: Matches potential Discord usernames or invites.
        - `currency_patterns`: Matches currency exchange rates in the format "ex/div".
        - `coupon_patterns`: Matches coupon codes and their discount percentages.
        If an error occurs during the compilation of any pattern, it logs the error and raises an exception.
        """
        try:
            host_pattern = '|'.join(map(re.escape, self.spam_hosts))
            self.url_patterns = [
                re.compile(rf'(?i)(?:www[,.])?(?:{host_pattern})[,.](?:com|net|org)')
            ]

            self.from_pattern = re.compile(r'\[INFO Client \d+\] ([^:]+): (.+)')

            self.discord_patterns = [
                re.compile(rf'(?i)(?:add\s+)?discord[:.\s]*([a-zA-Z0-9]+)')
            ]
            self.currency_patterns = [
                re.compile(r'(?i)((?:ex|div)/\s*\d+(?:\.\d+)?)\s*\$')
            ]
        
            self.coupon_patterns = [
                re.compile(r'(?i)(?:coupon|code)[\s:]*([a-z0-9]+)(?:[^\d]+(\d+)%\s*off)')
            ]
                
        except Exception as e:
            self.logger.error(f"Error compiling patterns: {e}")
            raise

    def analyse_spam_content(self, message: str):
        """
        Analyses the given message for spam content based on predefined patterns.
        Args:
            message (str): The message to be analysed.
        Returns:
            dict: A dictionary containing the following keys:
            - 'is_spam' (bool): Indicates if the message is considered spam.
            - 'detected_urls' (list): List of URLs detected in the message.
            - 'detected_discord' (list): List of Discord invites detected in the message.
            - 'currency_offers' (list): List of currency offers detected in the message.
            - 'coupon_codes' (list): List of coupon codes detected in the message.
        Raises:
            Exception: If an error occurs during the analysis, logs the error and returns a dictionary with 'is_spam' set to False.
        """
        try:
            spam_indicators = {
                'is_spam': False,
                'detected_urls': [],
                'detected_discord': [],
                'currency_offers': [],
                'coupon_codes': []
            }
            
            message_lower = message.lower()
            
            for pattern in self.url_patterns:
                matches = pattern.findall(message_lower)
                if matches:
                    spam_indicators['is_spam'] = True
                    spam_indicators['detected_urls'].extend(matches)
            
            for pattern in self.discord_patterns:
                matches = pattern.findall(message_lower)
                if matches:
                    spam_indicators['is_spam'] = True
                    spam_indicators['detected_discord'].extend(matches)
            
            for pattern in self.currency_patterns:
                matches = pattern.findall(message_lower)
                if matches:
                    spam_indicators['is_spam'] = True
                    spam_indicators['currency_offers'].extend(matches)
            
            for pattern in self.coupon_patterns:
                matches = pattern.findall(message_lower)
                if matches:
                    spam_indicators['is_spam'] = True
                    spam_indicators['coupon_codes'].extend(matches)

            return spam_indicators
        except Exception as e:
            self.logger.error(f"Error analysing content: {e}")
            return {'is_spam': False}

    async def check_for_spam(self, log_file):
        """
        Asynchronously checks the POE2 log file for spam messages.
        This method reads new content from the specified log file since the last check,
        analyses it for spam, and logs any detected spam messages.
        Args:
            log_file (Path): The path to the POE2 log file.
        Raises:
            Exception: If an error occurs while checking for spam, it is logged with traceback information.
        Logs:
            - Error if the log file does not exist.
            - Warning if the log file was truncated.
            - Debug information for each message found in the log file.
            - Info for each detected spam message with details.
        """
        try:
            if not log_file.exists():
                self.logger.error(f"Log file not found: {log_file}")
                return

            current_size = log_file.stat().st_size
            if current_size < self.last_size:
                self.logger.warning("Log file was truncated, resetting position")
                self.last_size = 0
                
            if current_size > self.last_size:
                with open(log_file, 'r', encoding='utf-8') as file:
                    file.seek(self.last_size)
                    new_content = file.read()
                    self.last_size = current_size

                    for line in new_content.splitlines():
                        if '[INFO Client' in line:
                            from_match = self.from_pattern.search(line)
                            if from_match:
                                player_name = from_match.group(1)
                                player_name = re.sub(r'^[^a-zA-Z0-9]+', '', player_name)
                                message_content = from_match.group(2)
                                self.logger.debug(f"Found message - Player: {player_name}, Content: {message_content}")
                                
                                spam_analysis = self.analyze_spam_content(message_content)
                                if spam_analysis['is_spam']:
                                    spam_report = {
                                        'timestamp': time.strftime('%d-%m-%Y %H:%M:%S'),
                                        'player': player_name,
                                        'message': message_content,
                                        'spam_details': spam_analysis
                                    }
                                    self.logger.info(f"Spam detected: {spam_report}")    
        except Exception as e:
            self.logger.error(f"Error checking for spam: {e}", exc_info=True)

async def main():
    logger = setup_logging()
    logger.info("Starting POE2 Spam Culler - v1.0")
    
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        log_path = Path(config['log_path'])
        monitor = SpamMonitor(logger)
        window = POEWindow(logger)
        
        if not log_path.exists():
            logger.error(f"Log file not found at {log_path}")
            return
            
        monitor.last_size = log_path.stat().st_size
        logger.info(f"Monitoring log file: {log_path}")

        while True:
            try:
                await monitor.check_for_spam(log_path)
                await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.getLogger('poe2_spam_culler').info("Shutting down spam monitor")
    except Exception as e:
        logging.getLogger('poe2_spam_culler').error(f"Fatal error: {e}")
        raise