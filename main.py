import time
import telebot
import random
import pyshorteners
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv('TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
bot = telebot.TeleBot(TOKEN)


def shorten_url(long_url: str) -> str:
    try:
        type_tiny = pyshorteners.Shortener()
        short_url = type_tiny.tinyurl.short(long_url)
        return short_url
    except Exception as e:
        return long_url

def scrape_linkedin_jobs(job_title: str, location: str, pages: int = 1) -> list:
    pages = pages or 1

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920x1080")

    driver = webdriver.Chrome(options=options)
    driver.get(f"https://www.linkedin.com/jobs/search/?keywords={job_title}&location={location}&f_TPR=&f_WT=3%2C2")

    for i in range(pages):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        try:
            element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(text(), 'Show more jobs')]")
                )
            )
            element.click()
        except Exception:
            break
        time.sleep(random.uniform(3, 7))

    jobs = []
    soup = BeautifulSoup(driver.page_source, "html.parser")
    job_listings = soup.find_all(
        "div",
        class_="base-card relative w-full hover:no-underline focus:no-underline base-card--link base-search-card base-search-card--link job-search-card",
    )

    try:
        for job in job_listings[:10]:
            job_title = job.find("h3", class_="base-search-card__title").text.strip()
            job_title = (job_title[:50] + '...') if len(job_title) > 50 else job_title
            job_company = job.find("h4", class_="base-search-card__subtitle").text.strip()
            job_location = job.find("span", class_="job-search-card__location").text.strip()
            apply_link = job.find("a", class_="base-card__full-link")["href"]

            jobs.append(
                {
                    "title": job_title,
                    "company": job_company,
                    "location": job_location,
                    "link": shorten_url(apply_link),
                }
            )
    except Exception as e:

        return jobs

    driver.quit()
    send_jobs_to_telegram(jobs)

def send_jobs_to_telegram(jobs: list) -> None:
    message = "Vagas de estágios da semana:\n\n"
    for job in jobs:
        message += (
            f"Title: {job['title']}\n"
            f"Location: {job['location']}\n"
            f"Link da vaga: {job['link']}\n\n"
        )

    max_message_length = 4096
    if len(message) > max_message_length:
        messages = [message[i:i + max_message_length] for i in range(0, len(message), max_message_length)]
    else:
        messages = [message]

    for msg in messages:
        bot.send_message(CHAT_ID, msg, parse_mode='Markdown')
        time.sleep(1)

# Define command handler for /test
@bot.message_handler(commands=['test'])
def send_test_message(message):
    bot.send_message(CHAT_ID, "Test bem sucedido")

# Define command handler for /start to trigger the scraping manually
@bot.message_handler(commands=['start'])
def start_scraping(message):
    bot.send_message(CHAT_ID, "Iniciando scraping de vagas...")
    scrape_linkedin_jobs("estagio", "Brazil")

# Start the bot
bot.polling()
