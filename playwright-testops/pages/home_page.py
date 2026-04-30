from core.base_page import BasePage


class HomePage(BasePage):

    # URL = "http://localhost:3000"
    PATH = ""  # 首页路径
    LOGO = "text=TestOps"

    def __init__(self, page):
        super().__init__(page)

    def is_logo_visible(self):
        return self.is_visible(self.LOGO)