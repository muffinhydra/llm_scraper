import logging

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from kafka import KafkaConsumer
from urllib.parse import urlparse

load_dotenv(dotenv_path="../.env")

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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def process_packet(packet):
    """
    Process a packet received from Kafka.

    Args:
        packet (str): JSON-formatted data packet received from Kafka.

    Returns:
        pd.DataFrame: Processed and cleaned data as a pandas DataFrame.
    """
    logging.info("Processing packet: %s", packet)

    # Process and clean the packet using Pandas
    data = pd.read_json(packet)
    cleaned_data = clean_data(data)

    logging.info("Packet processed successfully.")
    return cleaned_data


def extract_base_url_and_path(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    path = parsed_url.path
    return base_url, path


def clean_data(df: pd.DataFrame):
    """
    Clean the data by performing the following operations:
    - Drop duplicate rows
    - Drop missing values
    - Remove leading/trailing whitespaces from column names

    Args:
        df (pd.DataFrame): Input DataFrame to be cleaned.

    Returns:
        pd.DataFrame: Cleaned DataFrame.
    """
    logging.info("Cleaning data...")

    # Drop duplicate rows
    df = df.drop_duplicates()

    # Drop missing values
    df = df.dropna()

    # Remove leading/trailing whitespaces from column names
    df.columns = df.columns.str.strip()

    logging.info("Data cleaning completed.")
    return df


def load_data(cleaned_data, url):
    """
    Load the cleaned data into the PostgreSQL database using SQLAlchemy.

    Args:
        cleaned_data (pd.DataFrame): Cleaned DataFrame to be loaded into the database.
    """

    table_name, path = extract_base_url_and_path(url)
    cleaned_data["path"] = path
    try:
        cleaned_data.to_sql(table_name, engine, if_exists="append", index=False)
        logging.info("Data loaded into PostgreSQL.")
    except Exception as e:
        logging.error("Error loading data into PostgreSQL: %s", str(e))


# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = "broker:9092"
KAFKA_TOPIC = "etl_ingest"


def perform_etl():
    """
    Perform ETL (Extract, Transform, Load) process by consuming messages from Kafka,
    processing and cleaning the packets, and loading them into the PostgreSQL database.
    """
    global etl_thread

    # Initialize Kafka consumer
    consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    for message in consumer:
        packet = message.value.decode("utf-8")

        headers = message.headers
        web_page = None
        # Process headers and extract insights and data_dictionary values
        for header_key, header_value in headers:
            if header_key == "web_page":
                web_page = header_value.decode("utf-8")

        # Process and clean the packet
        cleaned_data = process_packet(packet)

        # Load the cleaned data into the PostgreSQL database
        load_data(cleaned_data, web_page)

    etl_thread = None
