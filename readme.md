# Web Scraper and ETL Project

This project implements a web scraper, ETL worker, and LLM (Large Language Model) worker for extracting insights from web pages and performing data processing tasks.

## Attention!

This project is very much WIP and most likely wont work!

## Project Structure

The project consists of the following components:

- **Scraper**: A web scraper service that fetches web pages and extracts content.
- **ETL Worker**: An ETL (Extract, Transform, Load) worker service that cleans and loads data into a PostgreSQL database.
- **LLM Worker**: A worker service that processes raw content using a Large Language Model and sends the transformed data to the ETL Worker.

## Setup and Installation

1. Clone the repository:

   ```bash
   git clone <repository_url>

2. Set up the environment:

    ```bash
    cd llm_scraper

3. Start the project using Docker Compose:

    ```bash
    docker-compose up -d

4. Access the REST endpoints of each service to interact with them.

## Usage

Once the project is running using Docker Compose, you can access the REST endpoints of each service. Here are the default URLs for accessing the services:

Scraper: http://localhost:20010
LLM Worker: http://localhost:20020
ETL Worker: http://localhost:20030

## TODO 

Implement the LLM Worker to process the raw content from the Scraper and send transformed data to the ETL Worker.