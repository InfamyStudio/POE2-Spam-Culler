import asyncio
from pathlib import Path
import json
from core_plugins.core_logging import CoreLogging
from core_plugins.core_poe_window_detection import CorePOEWindow
from core_plugins.core_spam_monitor import CoreSpamMonitor
from core_plugins.core_plugin_loader import PluginLoader

class Main:
    def __init__(self):
        self.logger = CoreLogging().logger
        self.init_config()
        self.init_plugin_config()
        self.plugin_loader = PluginLoader(self.logger)
        self.plugin_loader.load_enabled_plugins(self.plugins_enabled)
        self.spam_hosts, self.spam_discord = self.init_lists()
        self.spam_monitor = CoreSpamMonitor(self.logger, (self.spam_hosts, self.spam_discord))
        self.poe_window = CorePOEWindow(self.logger)

    def init_config(self):
        """
        Initialises the configuration for the client by loading settings from a JSON file.

        Raises:
            Exception: If there is an error loading the configuration file.
        """
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
            self.log_path = Path(self.config['log_path'])
            if not self.log_path.exists():
                self.logger.error(f"Log file not found at {self.log_path}")
                return
            self.logger.info(f"Monitoring log file: {self.log_path}")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            raise

    def init_lists(self):
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
        
        for file_path, target_set in [('spam_hosts.txt', spam_hosts), ('spam_discord.txt', spam_discord)]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    target_set.update(line.strip().lower() for line in f if line.strip())
                self.logger.info(f"Loaded {len(target_set)} entries from {file_path}")
            except FileNotFoundError:
                self.logger.error(f"Required file {file_path} not found")
                raise
            except Exception as e:
                self.logger.error(f"Error loading {file_path}: {e}")
                raise
        return spam_hosts, spam_discord
    
    def init_plugin_config(self):
        """
        Initialises the configuration for the client by loading settings from a JSON file.
        Raises:
            Exception: If there is an error loading the configuration file.
        """
        try:
            with open('config.json', 'r') as f:
                self.config = json.load(f)
            self.plugins_enabled = self.config['plugins_enabled']
            self.logger.info(f"Monitoring log file: {self.log_path}")
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            raise

    async def main(self):
        try:
            self.spam_monitor.last_size = self.log_path.stat().st_size
            while True:
                try:
                    spam_results = await self.spam_monitor.check_for_spam(self.log_path)
                    if spam_results:
                        self.plugin_loader.call_plugin_method('process_spam', spam_results)
                    await asyncio.sleep(0.1)
                except Exception as e:
                    self.logger.error(f"Error in main loop: {e}")
                    await asyncio.sleep(5)
        except Exception as e:
            self.logger.error(f"Fatal error: {e}")
            raise

if __name__ == "__main__":
    try:
        main = Main()
        asyncio.run(main.main())
    except KeyboardInterrupt:
        main.logger.info("Shutting down spam monitor")
    except Exception as e:
        main.logger.error(f"Fatal error: {e}")
        raise