from flask import Flask, jsonify, request
import threading
import time
from bs4 import BeautifulSoup
from kafka import KafkaProducer
import requests


app = Flask(__name__)

# Variables to track the scraping thread and its status
scraping_thread = None
scraping_in_progress = False

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'kafka_bootstrap_servers'
KAFKA_TOPIC = 'kafka_topic'

# Function to perform the web scraping
def perform_scraping(web_pages):
    global scraping_in_progress

    # Set the scraping in progress flag to True
    scraping_in_progress = True

    # Kafka producer initialization
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    for web_page in web_pages:
        # Perform scraping for each web page
        scraped_content = scrape_page(web_page)

        # Filter out <script> and <head> tags
        cleaned_content = filter_tags(scraped_content)

        # Send the cleaned content through Kafka
        send_to_kafka(producer, cleaned_content)

    # Set the scraping in progress flag to False
    scraping_in_progress = False

# Function to scrape a web page
def scrape_page(web_page):
    #TODO implement timeout
    response = requests.get(web_page)
    content = response.text

    return content

# Function to filter out tags from the scraped content
def filter_tags(content):
    soup = BeautifulSoup(content, 'html.parser')

    # Remove <script> tags
    for script in soup('script'):
        script.extract()

    # Remove <head> tag
    head = soup.head
    if head:
        head.extract()

    cleaned_content = str(soup)

    return cleaned_content

# Function to send the cleaned content to Kafka
def send_to_kafka(producer, content):
    producer.send(KAFKA_TOPIC, value=content.encode('utf-8'))

# Function to perform the web scraping
def perform_scraping(web_pages):
    global scraping_in_progress

    # Set the scraping in progress flag to True
    scraping_in_progress = True

    # Kafka producer initialization
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

    for web_page in web_pages:
        # Perform scraping for each web page
        scraped_content = scrape_page(web_page)

        # Filter out <script> and <head> tags
        cleaned_content = filter_tags(scraped_content)

        # Send the cleaned content through Kafka
        send_to_kafka(producer, cleaned_content)

        # Introduce a 5-second delay
        time.sleep(5)

    # Flush and close the Kafka producer
    producer.flush()
    producer.close()

    # Set the scraping in progress flag to False
    scraping_in_progress = False



# Endpoint to start the web scraping process
@app.route('/start', methods=['POST'])
def start_scraping():
    global scraping_thread

    # Check if the scraping is already in progress
    if scraping_in_progress:
        return jsonify({'message': 'Web scraping is already in progress.'}), 400

    # Get the list of web pages from the request body
    web_pages = request.json.get('web_pages', [])

    # Create a new thread for scraping
    scraping_thread = threading.Thread(target=perform_scraping, args=(web_pages,))
    scraping_thread.start()

    return jsonify({'message': 'Web scraping started successfully.'})

# Endpoint to stop the web scraping process
@app.route('/stop', methods=['POST'])
def stop_scraping():
    global scraping_thread, scraping_in_progress

    # Check if the scraping is in progress
    if scraping_in_progress:
        # Stop the scraping thread
        scraping_thread.join()
        scraping_thread = None
        scraping_in_progress = False

        return jsonify({'message': 'Web scraping stopped successfully.'})
    else:
        return jsonify({'message': 'No web scraping in progress.'}), 400

# Endpoint to check the status of the web scraping process
@app.route('/status', methods=['GET'])
def check_status():
    global scraping_in_progress

    if scraping_in_progress:
        return jsonify({'status': 'running'})
    else:
        return jsonify({'status': 'stopped'})

if __name__ == '__main__':
    app.run(debug=False)
