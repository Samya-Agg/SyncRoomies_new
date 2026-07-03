from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from home.models import Student_choices, profile
import time


class RecommendationSeleniumTest(StaticLiveServerTestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username="samya", password="pass123", first_name="Samya", last_name="A"
        )
        self.user2 = User.objects.create_user(
            username="udita", password="pass123", first_name="Udita", last_name="S"
        )

        profile.objects.create(
            user=self.user1, contact="9999999999", email="samya@test.com", year="1", gender="F"
        )
        profile.objects.create(
            user=self.user2, contact="8888888888", email="udita@test.com", year="1", gender="F"
        )

        Student_choices.objects.create(
            student_id=self.user1, name="Samya Aggarwal", gender="F",
            Q1=4, Q2=3, Q3=5, Q4=2, Q5=4, Q6=2, Q7=5, Q8=2, Q9=4, Q10=3
        )
        Student_choices.objects.create(
            student_id=self.user2, name="Udita Sharma", gender="F",
            Q1=5, Q2=4, Q3=3, Q4=2, Q5=5, Q6=1, Q7=4, Q8=3, Q9=3, Q10=4
        )

        chrome_path = r"C:\Users\Dell\OneDrive\Desktop\chromedriver-win64\chromedriver.exe"  

        chrome_options = Options()
        chrome_options.add_argument("--headless=new")   
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        service = Service(chrome_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def tearDown(self):
        self.driver.quit()

    def test_recommendation_page_loads_matches(self):
        self.driver.get(f"{self.live_server_url}/login/")

        self.driver.find_element(By.NAME, "username").send_keys("samya")
        self.driver.find_element(By.NAME, "password").send_keys("pass123")

        login_btn = self.driver.find_element(By.TAG_NAME, "button")
        login_btn.click()

        time.sleep(2)

        self.driver.get(f"{self.live_server_url}/results/")

        time.sleep(2)

        page_source = self.driver.page_source

        self.assertIn("Udita Sharma", page_source)
