from bs4 import BeautifulSoup, Comment
from kafka import KafkaProducer
import requests
import logging
import json
import time
import random
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def scrape_page(web_page):
    """
    Scrape the web page content using the provided URL.

    Args:
        web_page (str): The URL of the web page to be scraped.

    Returns:
        str: The scraped content of the web page as a string.
    """
    logger.info(f"Scraping web page: {web_page}")
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
        "Accept-Language": "en-US, en;q=0.5",
    }

    # TODO implement timeout
    response = requests.get(web_page, headers=HEADERS)
    content = response.text

    return content


# Function to filter out tags from the scraped content
def filter_tags(content):
    """
    Filter out specific HTML tags and attributes from the scraped content.

    Args:
        content (str): The HTML content to be filtered.

    Returns:
        str: The cleaned HTML content with filtered tags and attributes.
    """
    soup = BeautifulSoup(content, "html.parser")

    # Remove <script> tags
    for script in soup("script"):
        script.extract()

    for header in soup.find_all("head"):
        header.decompose()

    # Remove style tags
    for style in soup.find_all("style"):
        style.decompose()

    # Remove footer tags
    for footer in soup.find_all("footer"):
        footer.decompose()

    # Remove navigation tags
    for nav in soup.find_all("nav"):
        nav.decompose()

    # Remove image tags
    for img in soup.find_all("img"):
        img.decompose()

    # Remove link tags
    for link in soup.find_all("link"):
        link.decompose()

    # Remove HTML comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        comment.extract()

    # Remove classes and attributes
    for tag in soup.find_all():
        tag.attrs = {}

    # Remove double quotes from tag content
    for tag in soup.find_all():
        if tag.string:
            tag.string = tag.string.replace('"', "")
    for tag in soup.find_all():
        if tag.string:
            tag.string = tag.string.replace("'", "`")

    cleaned_content = str(soup)

    return cleaned_content


# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = "broker:9092"
KAFKA_TOPIC = "llm_ingest"


# Function to send the cleaned content to Kafka
def send_to_kafka(
    producer: KafkaProducer, content, insights, data_dictionary, web_page
):
    """
    Send the cleaned content, insights, and data_dictionary to the Kafka topic 'llm_ingest'.

    Args:
        producer (KafkaProducer): The KafkaProducer instance to send messages.
        content (str): The cleaned HTML content to be sent to Kafka.
        insights (str): The specific insights extracted from the content.
        data_dictionary (dict): A dictionary representing the schema for the data in the content.
    """
    headers = [
        ("insights", insights.encode("utf-8")),
        ("data_dictionary", json.dumps(data_dictionary).encode("utf-8")),
        ("web_page", web_page.encode("utf-8")),
    ]

    response = producer.send(
        KAFKA_TOPIC, value=content.encode("utf-8"), headers=headers
    )
    logger.info(f"Sent content to Kafka: {response}")


# Function to perform the web scraping
def perform_scraping(web_pages, data_dictionary, insights):
    """
    Perform web scraping for a list of web pages and send the cleaned content
    to the Kafka topic 'llm_ingest'.

    Args:
        web_pages (list): List of web page URLs to be scraped.
        data_dictionary (dict): A dictionary representing the schema for the data in the content.
        insights (str): The specific insights to be extracted from the content.
    """
    logger.info("Web scraping started.")

    # Kafka producer initialization
    producer: KafkaProducer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    for web_page in web_pages:
        # Perform scraping for each web page
        scraped_content = scrape_page(web_page)
        logger.info(f"Scraped content from web page: {web_page}")

        # Filter out <script> and <head> tags
        cleaned_content = filter_tags(scraped_content)

        # Send the cleaned content through Kafka
        send_to_kafka(
            producer,
            cleaned_content,
            data_dictionary=data_dictionary,
            insights=insights,
            web_page=web_page,
        )

        # Generate a random delay between 10 and 15 seconds
        delay_seconds = random.randint(10, 15)

        # Introduce the random delay
        time.sleep(delay_seconds)

    # Flush and close the Kafka producer
    producer.flush()
    producer.close()
    logger.info("Web scraping finished.")
