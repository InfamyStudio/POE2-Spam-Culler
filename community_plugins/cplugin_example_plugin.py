import logging

class Plugin:
    def __init__(self, logger: logging.Logger):
        self.name = "Example Plugin"
        self.version = "1.0.0"
        self.logger = logger
        
    def process_spam(self, spam_results: dict) -> bool:
        """
        Example plugin showing you how you can create your own plugin to process spam results.
        
        Args:
            spam_results: Results from spam detection
        """
        for key, value in spam_results.items():
            self.logger.info(f"Key: {key}, Value: {value}")
        return True # Return True to indicate that the plugin processed the spam results