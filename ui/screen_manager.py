class ScreenManager:
    """
    Stores and updates the active app screen.
    """

    def __init__(self, initial_screen: str = "menu"):
        self.current_screen = initial_screen

    def set_screen(self, screen_name: str):
        self.current_screen = screen_name

    def get_screen(self) -> str:
        return self.current_screen
