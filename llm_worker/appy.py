from flask import Flask, jsonify, request
from kafka import KafkaConsumer, KafkaProducer
import threading
import json

from llm_worker.llm import generate_insights

app = Flask(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'kafka_bootstrap_servers'
KAFKA_INPUT_TOPIC = 'input_topic_from_scraper'
KAFKA_OUTPUT_TOPIC = 'output_topic_to_etl_worker'

# Initialize Kafka consumer and producer
consumer = KafkaConsumer(KAFKA_INPUT_TOPIC, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

# Variable to track the LLM Worker thread
llm_thread = None

def process_content():
    for message in consumer:
        content = message.value.decode('utf-8')

        # Process the content using the LLM
        processed_data = process_with_llm(content)

        # Send the processed data to ETL Worker via Kafka
        send_to_kafka(KAFKA_OUTPUT_TOPIC, processed_data)

def process_with_llm(content):
    #TODO implement LLM logic 
    tokens = generate_insights(content)
    processed_data = []
    for token in tokens:
        json_obj = {'token': token}
        processed_data.append(json_obj)

    return processed_data

def send_to_kafka(topic, data):
    # Send data to Kafka
    producer.send(topic, value=json.dumps(data).encode('utf-8'))
    producer.flush()

    
# Endpoint to start the LLM Worker service
@app.route('/start', methods=['POST'])
def start_llm():
    global llm_thread

    # Check if the LLM Worker service is already running
    if llm_thread and llm_thread.is_alive():
        return jsonify({'message': 'LLM Worker service is already running.'}), 400

    # Create a new thread for LLM Worker service
    llm_thread = threading.Thread(target=process_content)
    llm_thread.start()

    return jsonify({'message': 'LLM Worker service started successfully.'})

# Endpoint to check the status of the LLM Worker service
@app.route('/status', methods=['GET'])
def check_status():
    if llm_thread and llm_thread.is_alive():
        return jsonify({'status': 'running'})
    else:
        return jsonify({'status': 'stopped'})

# Endpoint to stop the LLM Worker service
@app.route('/stop', methods=['POST'])
def stop_llm():
    global llm_thread

    # Check if the LLM Worker service is running
    if llm_thread and llm_thread.is_alive():
        # Stop the LLM Worker thread
        llm_thread.join()
        llm_thread = None

        return jsonify({'message': 'LLM Worker service stopped successfully.'})
    else:
        return jsonify({'message': 'No LLM Worker service running.'}), 400


if __name__ == '__main__':
    app.run(debug=False)
