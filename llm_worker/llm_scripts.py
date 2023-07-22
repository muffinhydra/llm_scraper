from kafka import KafkaConsumer, KafkaProducer
import json
import logging

from llm_external import get_insights_from_llm


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = "broker:9092"
KAFKA_INPUT_TOPIC = "llm_ingest"
KAFKA_OUTPUT_TOPIC = "etl_ingest"


def process_content():
    """
    Process content received from the Kafka topic 'llm_ingest' using LLM and send the processed data
    to the Kafka topic 'etl_ingest' via Kafka producer.
    """
    # Initialize Kafka consumer and producer
    consumer = KafkaConsumer(
        KAFKA_INPUT_TOPIC, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS
    )

    for message in consumer:
        logger.info("message")
        logger.info(message)

        content = message.value.decode("utf-8")

        # Extract headers from the Kafka message
        headers = message.headers
        data_dictionary = None
        insights = None
        web_page = None
        # Process headers and extract insights and data_dictionary values
        for header_key, header_value in headers:
            if header_key == "insights":
                insights = header_value.decode("utf-8")
            elif header_key == "data_dictionary":
                data_dictionary = json.loads(header_value.decode("utf-8"))
            elif header_key == "web_page":
                web_page = header_value.decode("utf-8")

        # Process the content using the LLM with insights and data_dictionary
        processed_data = process_with_llm(content, data_dictionary, insights)

        # Send the processed data to ETL Worker via Kafka with headers
        send_to_kafka(processed_data, web_page)


def process_with_llm(content, data_dictionary, insights):
    """
    Process the content using the Language Model (LLM) to extract insights based on the given
    data_dictionary and insights.

    Args:
        content (str): The content to be processed using LLM.
        data_dictionary (dict): A dictionary that serves as a schema for the data in the content.
        insights (str): The specific insights to be extracted from the content.

    Returns:
        dict: The processed data containing extracted insights as a dictionary.
    """
    logger.info("Processing content with LLM.")
    # TODO implement LLM logic
    tokens = get_insights_from_llm(content, data_dictionary, insights)
    data = json.loads(tokens.replace("\\n", "").replace('\\\\"', '"'))
    logger.info(f"Generated artifacts: {data}")
    return data


def send_to_kafka(data, web_page):
    """
    Send the data to the specified Kafka topic using Kafka producer.

    Args:
        topic (str): The Kafka topic to which the data will be sent.
        data (dict): The data to be sent to the Kafka topic.
    """
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    # Send data to Kafka
    response = producer.send(
        KAFKA_OUTPUT_TOPIC,
        value=json.dumps(data).encode("utf-8"),
        headers=[("web_page", web_page.encode("utf-8"))],
    )
    producer.flush()
    logger.info(
        f"Sent data to Kafka topic '{KAFKA_OUTPUT_TOPIC}': {data}, response: {response}"
    )
