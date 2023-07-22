## LLM Scraper Project

The LLM Scraper project implements a web scraper, ETL worker, and LLM (Large Language Model) worker
for extracting insights from web pages and performing data processing tasks. The project aims to
provide a scalable and efficient solution for web data extraction and analysis.

### Project Components

The project consists of the following components:

1. **Scraper**: A web scraper service that fetches web pages and extracts content.

2. **LLM Worker**: A worker service that processes raw content using a Large Language Model and
   sends the transformed data to the ETL Worker.

3. **ETL Worker**: An ETL (Extract, Transform, Load) worker service that cleans and loads data into
   a PostgreSQL database.

### Attention!

This project is a Work in Progress (WIP) and may not be fully functional or suitable for production
use. The implementation is ongoing, and certain features might not work as expected.

### Setup and Installation

To run the LLM Scraper project, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/muffinhydra/llm_scraper.git
    cd llm_scraper
    ```

2. Set up the environment:

    The project uses Docker Compose to manage the services. Ensure you have Docker and Docker
    Compose installed on your system.

3. Start the project using Docker Compose:

    ```bash
    docker-compose up -d
    ```

4. Access the REST endpoints of each service to interact with them.

### Usage

Once the project is running using Docker Compose, you can access the REST endpoints of each service.
Here are the default URLs for accessing the services:

-   Scraper: [http://localhost:20010](http://localhost:20010)
-   LLM Worker: [http://localhost:20020](http://localhost:20020)
-   ETL Worker: [http://localhost:20030](http://localhost:20030)

### Disclaimer

This project is provided as-is, and there is no guarantee of its functionality or suitability for
any specific purpose. Users are advised to review and test the code thoroughly before using it in
production environments.
