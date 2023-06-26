from flask import Flask, jsonify, request
import threading
import time
from bs4 import BeautifulSoup, Comment

from kafka import KafkaProducer
import requests
import logging

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variables to track the scraping thread and its status
scraping_thread = None
scraping_in_progress = False

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = "broker:9092"
KAFKA_TOPIC = "llm_ingest"


# Function to scrape a web page
def scrape_page(web_page):
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
    soup = BeautifulSoup(content, "html.parser")

    # Remove <script> tags
    for script in soup("script"):
        script.extract()
        for header in soup.find_all("head"):
            header.decompose()

    # Remove script tags
    for script in soup.find_all("script"):
        script.decompose()

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


# Function to send the cleaned content to Kafka
def send_to_kafka(producer: KafkaProducer, content):
    # value=content.encode("utf-8")
    response = producer.send(KAFKA_TOPIC, value=content.encode("utf-8"))
    logger.info(f"Sent content to Kafka: {response}")


# Function to perform the web scraping
def perform_scraping(web_pages):
    global scraping_in_progress

    # Set the scraping in progress flag to True
    scraping_in_progress = True
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
        send_to_kafka(producer, cleaned_content)

        # Introduce a 5-second delay
        time.sleep(5)

    # Flush and close the Kafka producer
    producer.flush()
    producer.close()
    logger.info("Web scraping finished.")

    # Set the scraping in progress flag to False
    scraping_in_progress = False


# Endpoint to start the web scraping process
@app.route("/start", methods=["POST"])
def start_scraping():
    global scraping_thread

    # Check if the scraping is already in progress
    if scraping_in_progress:
        return jsonify({"message": "Web scraping is already in progress."}), 400

    # Get the list of web pages from the request body
    web_pages = request.json.get("web_pages", [])
    logger.info(f"Starting web scraping for web pages: {web_pages}")

    # Create a new thread for scraping
    scraping_thread = threading.Thread(target=perform_scraping, args=(web_pages,))
    scraping_thread.start()

    return jsonify({"message": "Web scraping started successfully."})


# Endpoint to stop the web scraping process
@app.route("/stop", methods=["POST"])
def stop_scraping():
    global scraping_thread, scraping_in_progress

    # Check if the scraping is in progress
    if scraping_in_progress:
        # Stop the scraping thread
        scraping_thread.join()
        scraping_thread = None
        scraping_in_progress = False

        logger.info("Web scraping stopped.")
        return jsonify({"message": "Web scraping stopped successfully."})
    else:
        logger.info("No web scraping in progress.")
        return jsonify({"message": "No web scraping in progress."}), 400


# Endpoint to check the status of the web scraping process
@app.route("/status", methods=["GET"])
def check_status():
    global scraping_in_progress

    if scraping_in_progress:
        logger.info("Web scraping is running.")
        return jsonify({"status": "running"})
    else:
        logger.info("Web scraping is stopped.")
        return jsonify({"status": "stopped"})


if __name__ == "__main__":
    app.run(host="localhost", port=20010, debug=False)
