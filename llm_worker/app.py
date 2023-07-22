from flask import Flask, jsonify
import threading
import logging
from llm_scripts import process_content

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Variable to track the LLM Worker thread
llm_thread = None


@app.route("/start", methods=["POST"])
def start_llm():
    """
    Endpoint to start the LLM Worker service.

    Returns:
        jsonify: JSON response indicating the status of the operation.
    """
    global llm_thread

    # Check if the LLM Worker service is already running
    if llm_thread and llm_thread.is_alive():
        return jsonify({"message": "LLM Worker service is already running."}), 400

    # Create a new thread for LLM Worker service
    llm_thread = threading.Thread(target=process_content)
    llm_thread.start()

    logger.info("LLM Worker service started.")
    return jsonify({"message": "LLM Worker service started successfully."})


@app.route("/status", methods=["GET"])
def check_status():
    """
    Endpoint to check the status of the LLM Worker service.

    Returns:
        jsonify: JSON response indicating the status of the LLM Worker service.
    """
    if llm_thread and llm_thread.is_alive():
        logger.info("LLM Worker service is running.")
        return jsonify({"status": "running"})
    else:
        logger.info("LLM Worker service is stopped.")
        return jsonify({"status": "stopped"})


@app.route("/stop", methods=["POST"])
def stop_llm():
    """
    Endpoint to stop the LLM Worker service.

    Returns:
        jsonfy: JSON response indicating the status of the operation.
    """
    global llm_thread

    # Check if the LLM Worker service is running
    if llm_thread and llm_thread.is_alive():
        # Stop the LLM Worker thread
        llm_thread.join()
        llm_thread = None

        logger.info("LLM Worker service stopped.")
        return jsonify({"message": "LLM Worker service stopped successfully."})
    else:
        logger.info("No LLM Worker service running.")
        return jsonify({"message": "No LLM Worker service running."}), 400




if __name__ == "__main__":
    app.run(host="localhost", port=20020, debug=False)
