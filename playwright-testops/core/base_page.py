from core.config import get_base_url

class BasePage:

    def __init__(self, page):
        self.page = page
        self.base_url = get_base_url()

    def open(self, path=""):
        self.page.goto(self.base_url + path)

    def click(self, locator: str):
        self.page.locator(locator).click()

    def input(self, locator: str, text: str):
        self.page.locator(locator).fill(text)

    def get_text(self, locator: str) -> str:
        return self.page.locator(locator).inner_text()

    def is_visible(self, locator: str) -> bool:
        return self.page.locator(locator).is_visible()

    def wait_for(self, locator: str):
        self.page.locator(locator).wait_for()