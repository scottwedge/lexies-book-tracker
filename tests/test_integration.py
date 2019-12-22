# -*- encoding: utf-8
"""
I don't want to do browser testing quite yet, but this exists as a useful
proof-of-concept if/when I want to try it.
"""

from faker import Faker
from flask_testing import LiveServerTestCase
import pytest
from selenium import webdriver

from src import app


@pytest.mark.skip()
class TestIntegration(LiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser = webdriver.Firefox()
        cls.browser.implicitly_wait(1)
        cls.fake = Faker()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()

    def create_app(self):
        app.config["TESTING"] = True
        app.config["LIVESERVER_PORT"] = 0
        return app

    def test_can_register_user(self):
        self.browser.get(self.get_server_url())

        messages = self.browser.find_elements_by_id("messages")
        assert len(messages) == 1
        messages_li = [
            li_tag.text for li_tag in messages[0].find_elements_by_tag_name("li")
        ]

        assert messages_li == ["Please log in to access this page."]
