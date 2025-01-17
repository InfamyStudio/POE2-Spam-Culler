import logging
import re
import time

class CoreSpamMonitor:
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
    def __init__(self, logger: logging.Logger, lists: tuple):
        self.logger = logger
        self.last_size = 0
        self.spam_hosts, self.spam_discord = lists
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
                                
                                spam_analysis = self.analyse_spam_content(message_content)
                                if spam_analysis['is_spam']:
                                    spam_report = {
                                        'timestamp': time.strftime('%d-%m-%Y %H:%M:%S'),
                                        'player': player_name,
                                        'message': message_content,
                                        'spam_details': spam_analysis
                                    }
                                    self.logger.info(f"Spam detected: {spam_report}")   
                                    return spam_report 
        except Exception as e:
            self.logger.error(f"Error checking for spam: {e}", exc_info=True)