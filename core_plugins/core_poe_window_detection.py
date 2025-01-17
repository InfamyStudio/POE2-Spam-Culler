import win32gui
import logging

class CorePOEWindow:
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