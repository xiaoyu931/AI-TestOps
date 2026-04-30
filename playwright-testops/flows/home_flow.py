from pages.home_page import HomePage
from core.flow_result import FlowResult
import allure

class HomeFlow:

    def __init__(self, page):
        self.page = page
        self.home_page = HomePage(page)

    @allure.step("Open the homepage")
    def open_home_page(self):
        self.home_page.open(self.home_page.PATH)

    @allure.step("Check homepage loading")
    def check_home_loaded(self):
        visible = self.home_page.is_logo_visible()

        if visible:
            return FlowResult(True, "Homepage loaded successfully")
        else:
            return FlowResult(False, "Homepage failed to load: Logo not displayed")