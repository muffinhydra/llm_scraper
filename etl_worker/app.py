import threading
import logging
from flask import Flask, jsonify, request
from kafka import KafkaConsumer
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = "broker:9092"
KAFKA_TOPIC = "etl_ingest"

# PostgreSQL configuration
POSTGRES_HOST = "llm_scraper-postgres-1"
POSTGRES_PORT = "5432"
POSTGRES_DB = "scraper_db"
POSTGRES_USER = "scraper_etl"
POSTGRES_PASSWORD = "waldfee"

# Initialize PostgreSQL connection
engine = create_engine(
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

etl_thread = None


def perform_etl():
    global etl_thread

    # Initialize Kafka consumer
    consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    for message in consumer:
        packet = message.value.decode("utf-8")

        # Process and clean the packet
        cleaned_data = process_packet(packet)

        # Load the cleaned data into the PostgreSQL database
        load_data(cleaned_data)

    etl_thread = None


def process_packet(packet):
    logging.info("Processing packet: %s", packet)

    # Process and clean the packet using Pandas
    data = pd.read_json(packet)
    cleaned_data = clean_data(data)

    logging.info("Packet processed successfully.")
    return cleaned_data


def clean_data(df: pd.DataFrame):
    logging.info("Cleaning data...")

    # Drop duplicate rows
    df = df.drop_duplicates()

    # Drop missing values
    df = df.dropna()

    # Remove leading/trailing whitespaces from column names
    df.columns = df.columns.str.strip()

    logging.info("Data cleaning completed.")
    return df


def load_data(cleaned_data):
    # Load the cleaned data into the PostgreSQL database using SQLAlchemy
    try:
        cleaned_data.to_sql("table_name", engine, if_exists="append", index=False)
        logging.info("Data loaded into PostgreSQL.")
    except Exception as e:
        logging.error("Error loading data into PostgreSQL: %s", str(e))


@app.route("/start", methods=["POST"])
def start_etl():
    global etl_thread

    # Check if the ETL is already in progress
    if etl_thread and etl_thread.is_alive():
        return jsonify({"message": "ETL is already in progress."}), 400

    # Create a new thread for ETL
    etl_thread = threading.Thread(target=perform_etl)
    etl_thread.start()

    logging.info("ETL started successfully.")
    return jsonify({"message": "ETL started successfully."})


# Endpoint to check the status of the ETL process
@app.route("/status", methods=["GET"])
def check_status():
    global etl_thread

    # Check if the ETL is in progress
    if etl_thread and etl_thread.is_alive():
        return jsonify({"status": "running"})
    else:
        return jsonify({"status": "stopped"})


# Endpoint to stop the ETL process
@app.route("/stop", methods=["POST"])
def stop_etl():
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
