import logging
import time
from pynput.keyboard import Key, Controller

keyboard = Controller()

def press_enter():
    keyboard.press(Key.enter)
    keyboard.release(Key.enter)

class Plugin:
    def __init__(self, logger: logging.Logger):
        self.name = "Auto Ignore"
        self.version = "0.1.0"
        self.logger = logger

    def process_spam(self, spam_results: dict) -> bool:
        """
        Simply simulates the user opening the chat window with Enter, typing "/ignore <player>" command, then pressing Enter again to submit.

        TODO: If PoE 2 window is not focused, it should either ignore "process_spam" call or it should focus the window first before running keyboard simulation

        Args:
            spam_results: Results from spam detection {"timestamp": ?, "player": ?, "message": ?, "spam_details": ?}
        """
        if spam_results["spam_details"]["is_spam"] == False:
            return True

        # Open chat window
        press_enter()
        time.sleep(0.1)

        ignore_command = f"/ignore {spam_results["player"]}"

        # Type "/ignore <player>"
        for char in ignore_command:
            keyboard.press(char)
            keyboard.release(char)

        # Send command
        time.sleep(0.1)
        press_enter()

        self.logger.info(f"Ignore request sent for user: {key}")
        return True # Return True to indicate that the plugin processed the spam results

if __name__ == "__main__":
    # Example usage
    logger = logging.getLogger(__name__)
    plugin = Plugin(logger)
    spam_results = {"timestamp": "0000", "player": "AnnoyingSpammer", "message": "Use this coupon code to get %1 off on Divine Orbs", "spam_details": {"is_spam": True}}
    plugin.process_spam(spam_results)
