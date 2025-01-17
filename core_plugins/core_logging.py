import logging
from logging.handlers import RotatingFileHandler

class CoreLogging:
    def __init__(self):
        self.logger = self.setup_logging()

    def setup_logging(self):
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