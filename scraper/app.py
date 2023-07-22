import threading
import logging
from flask import Flask, jsonify, request
from scraping_scripts import perform_scraping

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variable to track the scraping thread
scraping_thread = None


@app.route("/start", methods=["POST"])
def start_scraping():
    """
    Endpoint to start the web scraping process.

    Request JSON Body:
    {
        "web_pages": ["url1", "url2", ...],  # List of web page URLs to scrape
        "data_dictionary": {...},           # Dictionary containing data schema for the scraped content
        "insights": "links"                 # Specific insights to extract from the scraped content
    }

    Returns:
        jsonify: JSON response indicating the status of the operation.
    """
    global scraping_thread

    # Check if the scraping is already in progress
    if scraping_thread and scraping_thread.is_alive():
        return jsonify({"message": "Web scraping is already in progress."}), 400

    # Get the list of web pages, data_dictionary, and insights from the request body
    data = request.json
    web_pages = data.get("web_pages", [])
    data_dictionary = data.get("data_dictionary", {})
    insights = data.get("insights", "")

    logger.info(f"Starting web scraping for web pages: {web_pages}")
    logger.info(f"Data dictionary: {data_dictionary}")
    logger.info(f"Insights: {insights}")

    # Create a new thread for scraping
    scraping_thread = threading.Thread(
        target=perform_scraping,
        args=(
            web_pages,
            data_dictionary,
            insights,
        ),
    )
    scraping_thread.start()

    return jsonify({"message": "Web scraping started successfully."})


@app.route("/stop", methods=["POST"])
def stop_scraping():
    """
    Endpoint to stop the web scraping process.

    Returns:
        jsonify: JSON response indicating the status of the operation.
    """
    global scraping_thread

    # Check if the scraping is in progress
    if scraping_thread and scraping_thread.is_alive():
        # Stop the scraping thread
        scraping_thread.join()
        scraping_thread = None

        logger.info("Web scraping stopped.")
        return jsonify({"message": "Web scraping stopped successfully."})
    else:
        logger.info("No web scraping in progress.")
        return jsonify({"message": "No web scraping in progress."}), 400


@app.route("/status", methods=["GET"])
def check_status():
    """
    Endpoint to check the status of the web scraping process.

    Returns:
        jsonify: JSON response indicating the status of the web scraping process.
    """
    global scraping_thread

    if scraping_thread and scraping_thread.is_alive():
        logger.info("Web scraping is running.")
        return jsonify({"status": "running"})
    else:
        logger.info("Web scraping is stopped.")
        return jsonify({"status": "stopped"})


if __name__ == "__main__":
    app.run(host="localhost", port=20010, debug=False)
