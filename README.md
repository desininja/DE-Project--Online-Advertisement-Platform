# Online Advertising Platform

This project implements a scalable, real-time online advertising platform. It simulates the entire lifecycle of an ad campaign, from creation and management to serving ads, running auctions, handling user feedback, and processing data for analytics. The system is built using a microservices-oriented architecture with modern data engineering tools.

## Architecture

The platform follows a distributed, event-driven architecture.

*   **Campaign Ingestion**: Ad campaign instructions (New, Update, Stop) are published to a Kafka topic.
*   **Ad Management**: An `Ad Manager` service consumes these instructions, enriches the data (e.g., calculates CPM), and stores the ad campaign details in a PostgreSQL database.
*   **Ad Serving**: A FastAPI-based `Ad Server` receives requests from user devices. It queries the database for eligible ads based on user targeting information (location, device type).
*   **Auction**: The `Ad Server` conducts a second-price auction among eligible ads to determine the winner. The winning ad is served to the user, and the serving event is logged.
*   **Feedback Loop**: A `User Simulator` mimics user interactions (views, clicks, acquisitions) and sends this feedback to a `Feedback Handler` endpoint on the `Ad Server`.
*   **Feedback Processing**: The `Feedback Handler` calculates the campaign expenditure based on the user's action, updates the campaign budget in the database, and publishes an enriched feedback message to a separate Kafka topic.
*   **Data Warehousing**: A PySpark streaming application consumes the enriched feedback messages and writes them to a file system in a structured format (JSON), ready for batch analysis, reporting, and archiving.

Architecture Diagram:


## Key Components & Scripts

*   `Main Scripts/AdManager.py`: Consumes ad campaign data from Kafka, processes it, and loads it into the PostgreSQL `ads` table.
*   `Main Scripts/AdServer.py`: A FastAPI application that serves ads via a `GET` endpoint and handles user feedback via a `POST` endpoint. It manages the auction logic and budget updates.
*   `kafka_ads_data_producer.py`: A simple producer to read ad campaign data from a CSV and publish it to Kafka, simulating the campaign management interface.
*   `user_simulator.py`: Simulates user traffic by making requests to the `Ad Server` and sending back feedback.
*   `Main Scripts/feedbackWriter.py`: A PySpark streaming job to consume processed feedback from Kafka and write it to the file system for archival and analysis.
*   `Main Scripts/club_files.py`: A utility script to consolidate the distributed output files from the Spark job into a single file.

## Technology Stack

*   **Backend**: Python, FastAPI
*   **Database**: PostgreSQL
*   **Messaging Queue**: Apache Kafka
*   **Data Processing**: Apache Spark (PySpark)
*   **Libraries**: `confluent-kafka`, `pykafka`, `asyncpg`, `psycopg2`, `pydantic`, `dotenv`

## Database Schema

The system uses a PostgreSQL database with the following key tables:

*   `online_ads.ads`: Stores details of all ad campaigns, including targeting criteria, budget, status, and performance metrics (CPC, CPA, CPM).
*   `online_ads.served_ads`: Logs every ad that is served, including auction details and the user it was served to.
*   `online_ads.user`: Contains user data for simulation purposes.

## Setup & Installation

1.  **Prerequisites**:
    *   Python 3.13.5
    *   Docker and Docker Compose
    *   An Apache Spark installation (for `feedbackWriter.py`)

2.  **Clone the Repository**:
    ```bash
    git clone https://github.com/your-username/DE-Project--Online-Advertisement-Platform.git
    cd DE-Project--Online-Advertisement-Platform
    ```

3.  **Environment Variables**:
    Create a `.env` file in the root directory by copying an example file .
    ```bash
    cp .env.example .env
    ```
    Fill in the `.env` file with your database credentials, Kafka broker addresses, and other configuration details.

4.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

5.  **Start Infrastructure**:
    It is recommended to run Kafka using Docker Compose. A `docker-compose.yml` file should be created for this.
    ```bash
    docker-compose up -d
    ```

## How to Run the Simulation

Execute the scripts in separate terminal windows in the following order:

1.  **Start the kafka_ads_data_producer.py**: This script will take data from `kafka_ads_output.csv` and publish it to Kafka.
    ```bash
    python kafka_ads_data_producer.py
    ```

2.  **Start the Ad Manager**: This service will wait for new campaign messages.
    ```bash
    python "Main Scripts/AdManager.py"
    ```

3.  **Start the Feedback Writer**: This Spark job will listen for user feedback events.
    ```bash
    # Example submission command, adjust for your Spark setup
    spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1 "Main Scripts/feedbackWriter.py"
    ```

4.  **Start the Ad Server**: This will expose the API endpoints for serving ads and receiving feedback.
    ```bash
    uvicorn "Main Scripts.AdServer:app" --host 0.0.0.0 --port 8000
    ```

5.  **Publish Ad Campaigns**: Run the producer to load campaign data into Kafka.
    ```bash
    python kafka_ads_data_producer.py
    ```

6.  **Start the User Simulator**: This will begin generating requests to the Ad Server.
    ```bash
    python user_simulator.py <db_host> <db_user> <db_pass> <db_name> http <ad_server_host> <ad_server_port> <feedback_handler_host> <feedback_handler_port>
    
    # Example:
    python user_simulator.py localhost postgres mypassword postgres http localhost 8000 localhost 8000
    ```

## Project Scope & Future Work

This project covers the core functionality of an ad platform. The original project scope also includes several other components that could be implemented as future work:

*   **Slot Budget Manager**: A cron job to periodically redistribute leftover campaign budgets across future time slots to ensure uniform spending.
*   **Data Archiver**: Use a tool like Sqoop to export aggregated data from PostgreSQL to a data warehouse like Apache Hive for long-term storage.
*   **Reporting Dashboard**: Build analytics reports and visualizations on top of the archived data in Hive using a tool like Apache Hue or Superset to derive business insights (e.g., top-spending campaigns, user CTR by demographic).
*   **Containerize All Services**: Create Dockerfiles for each Python application to make the entire stack fully containerized and easier to deploy.

