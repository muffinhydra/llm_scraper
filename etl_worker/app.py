import threading
from flask import Flask, jsonify, request
from kafka import KafkaConsumer
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'kafka_bootstrap_servers'
KAFKA_TOPIC = 'kafka_topic'

# PostgreSQL configuration
POSTGRES_HOST = 'postgres_host'
POSTGRES_PORT = 'postgres_port'
POSTGRES_DB = 'postgres_db'
POSTGRES_USER = 'postgres_user'
POSTGRES_PASSWORD = 'postgres_password'

# Initialize Kafka consumer
consumer = KafkaConsumer(KAFKA_TOPIC, bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)

# Initialize PostgreSQL connection
engine = create_engine(
    f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
)

def perform_etl():
    for message in consumer:
        packet = message.value.decode('utf-8')

        # Process and clean the packet
        cleaned_data = process_packet(packet)

        # Load the cleaned data into the PostgreSQL database
        load_data(cleaned_data)

def process_packet(packet):

    # Process and clean the packet using Pandas
    data = pd.read_json(packet)

 

    cleaned_data = data

    return cleaned_data

def load_data(cleaned_data):
    # Load the cleaned data into the PostgreSQL database using SQLAlchemy
    cleaned_data.to_sql('table_name', engine, if_exists='append', index=False)


@app.route('/start', methods=['POST'])
def start_etl():
    global etl_thread

    # Check if the ETL is already in progress
    if etl_thread and etl_thread.is_alive():
        return jsonify({'message': 'ETL is already in progress.'}), 400

    # Create a new thread for ETL
    etl_thread = threading.Thread(target=perform_etl)
    etl_thread.start()

    return jsonify({'message': 'ETL started successfully.'})

# Endpoint to check the status of the ETL process
@app.route('/status', methods=['GET'])
def check_status():
    if threading.active_count() > 1:
        return jsonify({'status': 'running'})
    else:
        return jsonify({'status': 'stopped'})

# Endpoint to stop the ETL process
@app.route('/stop', methods=['POST'])
def stop_etl():
    global etl_thread

    # Check if the ETL is in progress
    if etl_thread and etl_thread.is_alive():
        # Stop the ETL thread
        etl_thread.join()
        etl_thread = None

        return jsonify({'message': 'ETL stopped successfully.'})
    else:
        return jsonify({'message': 'No ETL in progress.'}), 400

if __name__ == '__main__':
    app.run(debug=False)
