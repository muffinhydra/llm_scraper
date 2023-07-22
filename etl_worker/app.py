import threading
import logging
from flask import Flask, jsonify
from etl_scripts import perform_etl


app = Flask(__name__)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

etl_thread = None


@app.route("/start", methods=["POST"])
def start_etl():
    """
    Endpoint to start the ETL process.

    This endpoint creates a new thread for the ETL process if it's not already running.

    :return: JSON response with the status of the ETL process.
    """
    global etl_thread

    # Check if the ETL is already in progress
    if etl_thread and etl_thread.is_alive():
        return jsonify({"message": "ETL is already in progress."}), 400

    # Create a new thread for ETL
    etl_thread = threading.Thread(target=perform_etl)
    etl_thread.start()

    logging.info("ETL started successfully.")
    return jsonify({"message": "ETL started successfully."})


@app.route("/status", methods=["GET"])
def check_status():
    """
    Endpoint to check the status of the ETL process.

    :return: JSON response with the status of the ETL process (running or stopped).
    """
    global etl_thread

    # Check if the ETL is in progress
    if etl_thread and etl_thread.is_alive():
        return jsonify({"status": "running"})
    else:
        return jsonify({"status": "stopped"})


@app.route("/stop", methods=["POST"])
def stop_etl():
    """
    Endpoint to stop the ETL process.

    This endpoint stops the ETL process by joining the ETL thread.

    :return: JSON response with the status of the ETL process.
    """
    global etl_thread

    # Check if the ETL is in progress
    if etl_thread and etl_thread.is_alive():
        # Stop the ETL thread
        etl_thread.join()
        etl_thread = None

        logging.info("ETL stopped successfully.")
        return jsonify({"message": "ETL stopped successfully."})
    else:
        return jsonify({"message": "No ETL in progress."}), 400


if __name__ == "__main__":
    app.run(host="localhost", port=20030, debug=False)
