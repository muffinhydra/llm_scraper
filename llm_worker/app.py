from flask import Flask, jsonify, request
from kafka import KafkaConsumer, KafkaProducer
import threading
import json
import logging

from llm_external import get_insights_from_llm

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = "broker:9092"
KAFKA_INPUT_TOPIC = "llm_ingest"
KAFKA_OUTPUT_TOPIC = "etl_ingest"


# Variable to track the LLM Worker thread
llm_thread = None


data_dictionary = {
    "name": "string; name of product",
    "price": "float; price of product",
    "rating": "float; amount of stars",
    "reviews": "integer; amount of reviews",
    "rank": "integer; rank of product",
}
insights = "products"


def process_content():
    # Initialize Kafka consumer and producer
    consumer = KafkaConsumer(
        KAFKA_INPUT_TOPIC, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS
    )
    for message in consumer:
        content = message.value.decode("utf-8")

        # Process the content using the LLM
        processed_data = process_with_llm(content)

        # Send the processed data to ETL Worker via Kafka
        send_to_kafka(KAFKA_OUTPUT_TOPIC, processed_data)


def process_with_llm(content):
    logger.info("Processing content with LLM.")
    # TODO implement LLM logic
    tokens = get_insights_from_llm(content, data_dictionary, insights)
    data = json.loads(tokens.replace("\\n", "").replace('\\\\"', '"'))
    logger.info(f"Generated artifacts: {data}")
    return data


def send_to_kafka(topic, data):
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    # Send data to Kafka
    response = producer.send(topic, value=json.dumps(data).encode("utf-8"))
    producer.flush()
    logger.info(f"Sent data to Kafka topic '{topic}': {data}, response: {response}")


# Endpoint to start the LLM Worker service
@app.route("/start", methods=["POST"])
def start_llm():
    global llm_thread

    # Check if the LLM Worker service is already running
    if llm_thread and llm_thread.is_alive():
        return jsonify({"message": "LLM Worker service is already running."}), 400

    # Create a new thread for LLM Worker service
    llm_thread = threading.Thread(target=process_content)
    llm_thread.start()

    logger.info("LLM Worker service started.")
    return jsonify({"message": "LLM Worker service started successfully."})


# Endpoint to check the status of the LLM Worker service
@app.route("/status", methods=["GET"])
def check_status():
    if llm_thread and llm_thread.is_alive():
        logger.info("LLM Worker service is running.")
        return jsonify({"status": "running"})
    else:
        logger.info("LLM Worker service is stopped.")
        return jsonify({"status": "stopped"})


# Endpoint to stop the LLM Worker service
@app.route("/stop", methods=["POST"])
def stop_llm():
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
