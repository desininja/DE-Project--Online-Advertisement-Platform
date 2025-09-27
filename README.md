-----

# 🚀 DE Project: Real-Time Online Advertising Platform

## The Challenge: End-to-End Real-Time Advertising

**"The rapid, dynamic nature of digital advertising demands a robust platform capable of real-time campaign management, instantaneous ad auctions, and reliable financial reconciliation."**

Existing or simple advertising solutions often struggle to simultaneously manage **campaign lifecycle control**, execute **real-time bidding (RTB) auctions** under a specific model (e.g., second-price), and maintain **accurate, low-latency financial ledgers** for campaign budgets. This project was built to solve this by creating a **scalable, event-driven system**—complete with separate interfaces for campaign managers and clients—to ensure campaigns are run, ads are served, and billing/budget updates occur with minimal delay and maximum accuracy.

-----

## 💡 Project Overview

This project outlines the architecture and implementation of a data-intensive online advertising platform. It simulates the entire lifecycle of an ad campaign, from **creation and management** to **serving ads** (via auction), **tracking user feedback**, and **generating reports**. The system uses a microservices-oriented architecture with modern data engineering tools to create a robust and scalable pipeline.

-----

## 🛠️ Technology Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend/API** | **Python**, **FastAPI**| Core application logic and Ad Server/Feedback API. |
| **Messaging** | **Apache Kafka** | Event-driven pipeline for campaign instructions and user feedback. |
| **State Store** | **PostgreSQL**, MySQL | Low-latency storage for active Ad Campaigns and User Profiles. |
| **Data Processing** | **Apache Spark (PySpark)** | Stream processing of user feedback for archival and reporting. |
| **Data Warehouse** | **PostgreSQL** | Storage layer for batch analytics and report generation (Future work). |
| **Deployment** | **Docker**, Docker Compose, Crontab | Containerization and scheduling of services. |
| **Libraries** | `confluent-kafka`, `asyncpg`, `pydantic` | Core integration libraries. |

-----

## ⚙️ Architecture & Data Flow

The platform follows a distributed, **event-driven architecture** that mimics a real-world ad exchange.

The diagram below illustrates the data flow and ETL (Extract, Transform, Load) pipeline:
![ETL Architecture Diagram](Ads_Campaign_ETL_Architecture.jpg)

### Key Components

  * **Ad Data Producer (`kafka_ads_data_producer.py`)**: A simulation script that reads campaign data from a CSV and publishes campaign instructions to the **Ad Campaign Kafka Queue**.
  * **Ad Manager (`AdManager.py`)**: A consumer service that processes campaign instructions, enriches the data (e.g., calculates CPM), and persists the campaign details in the **PostgreSQL/MySQL database**.
  * **Ad Server (`AdServer.py`)**: A **FastAPI** application responsible for real-time ad delivery. It queries the database for eligible ads, conducts a **second-price auction** for the winning ad, and logs the served ad event.
  * **Feedback Handler (API)**: An endpoint within the `AdServer` that receives user interactions (views, clicks, acquisitions). It calculates and **updates the campaign budget** in the database *immediately* and publishes an enriched feedback event to the **User Feedback Kafka Queue**.
  * **User Feedback Writer (`feedbackWriter.py`)**: A **PySpark streaming job** that reliably consumes enriched user feedback from Kafka and writes it to a file system for downstream batch analysis and archiving.
  * **Slot Budget Manager (Cron)**: A scheduled Python script that manages **budget distribution** by uniformly dividing the leftover campaign budget across remaining time slots.
  * **User Simulator (`user_simulator.py`)**: A script that mimics user interactions by making requests to the Ad Server and sending back feedback.

-----

## 📊 Data Schemas

### Kafka Queues

| Queue | Topic | Purpose |
| :--- | :--- | :--- |
| **Ad Campaign** | `de-project-ads-topic` | Campaign creation, update, and stop instructions. |
| **User Feedback** | `feedback-handler-queue` | Enriched user interaction data for archiving and billing. |

| Ad Campaign Queue Schema |

| Column | Description |
| :--- | :--- |
| `Text` | Text in the advertisement |
| `Category` | Category of the product |
| `Keywords` | Textual keywords |
| `Campaign ID` | Unique identifier for the campaign |
| `Action` | Type of campaign instruction (`New Campaign`, `Update Campaign`, `Stop Campaign`) |
| `Target Gender` | `M`, `F`, or `All` |
| `Target Age Range` | Age range, `0-0` for all ages |
| `Target City` | City, `All` for no specific city |
| `Target State` | State, `All` for no specific state |
| `Target Country` | Country, `All` for no specific country |
| `Target Income Bucket` | `H`, `M`, `L`, or `All` |
| `Target Device` | Device type |
| `CPC` | Cost Per Click |
| `CPA` | Cost Per Action |
| `Budget` | Total campaign budget |
| `Date Range` | Date range for the campaign |
| `Time Range` | Time range for the campaign |


Ad Campaign Queue Schema Example
```JSON
{"text": "Transmission Oil Cooler Assembly for 2014-2017 Toyota Highlander LE, LE Plus, Limited, XLE | V6 3.5L | 32910-48190", "category": "Tools & Hardware", "keywords": "automotive,oils,fluids", "campaign_id": "8cf1b846-8f97-11f0-b7f6-0e087721c0e9", "action": "New Campaign", "target_gender": "F", "target_age_range": "{'start': '20', 'end': '45'}", "target_city": "All", "target_state": "All", "target_country": "India", "target_income_bucket": "M", "target_device": "All", "cpc": "0.00066", "cpa": "0.0529", "budget": "500", "date_range": "{'start': '2025-09-12', 'end': '2025-09-13'}", "time_range": "{'start': '5:00:00', 'end': '18:00:00'}"}
```

### Database Tables (PostgreSQL or MySQL)

#### `ads` (Campaign Configuration)

Stores campaign data and derived attributes, including the live **`budget`** and **`current_slot_budget`** for real-time auction eligibility checks.

| Column | Datatype | Description |
| :--- | :--- | :--- |
| `text` | `NVARCHAR` | Text of the advertisement |
| `category` | `NVARCHAR` | Category of the product |
| `keywords` | `NVARCHAR` | Textual keywords |
| `campaign_id` | `NVARCHAR` | Unique identifier for the campaign |
| `status` (Derived) | `NVARCHAR` | `ACTIVE` or `INACTIVE` |
| `target_gender` | `NVARCHAR` | `M`, `F`, or `All` |
| `target_age_start` | `INT` | Target age lower limit |
| `target_age_end` | `INT` | Target age upper limit |
| `target_city` | `NVARCHAR` | Target city, `All` for no specific city |
| `target_state` | `NVARCHAR` | Target state, `All` for no specific state |
| `target_country` | `NVARCHAR` | Target country, `All` for no specific country |
| `target_income_bucket` | `NVARCHAR` | `H`, `M`, `L`, or `All` |
| `target_device` | `NVARCHAR` | Target device type |
| `cpc` | `DOUBLE` | Cost Per Click |
| `cpa` | `DOUBLE` | Cost Per Action |
| `cpm` (Derived) | `DOUBLE` | Cost Per Mille (calculated from CPC and CPA) |
| `budget` | `DOUBLE` | Total campaign budget |
| `current_slot_budget` (Derived) | `DOUBLE` | Budget for the current 10-minute slot |
| `date_range_start` | `NVARCHAR` | Campaign start date |
| `date_range_end` | `NVARCHAR` | Campaign end date |
| `time_range_start` | `NVARCHAR` | Campaign start time |
| `time_range_end` | `NVARCHAR` | Campaign end time |

#### `users` (User Profiles)

| Column | Datatype | Description |
| :--- | :--- | :--- |
| `id` | `NVARCHAR` | User Identifier |
| `age` | `INT` | Age of the user |
| `gender` | `NVARCHAR` | Gender of the user |
| `internet_usage` | `NVARCHAR` | Daily average internet usage |
| `income_bucket` | `NVARCHAR` | Estimated income bucket (`H`, `M`, `L`) |
| `user_agent_string` | `NVARCHAR` | User-agent string |
| `device_type` | `NVARCHAR` | Type of device used |
| `websites` | `NVARCHAR` | Websites liked by the user |
| `movies` | `NVARCHAR` | Movies liked by the user |
| `music` | `NVARCHAR` | Music liked by the user |
| `program` | `NVARCHAR` | Programs liked by the user |
| `books` | `NVARCHAR` | Books liked by the user |
| `negatives` | `NVARCHAR` | Keywords representing dislikes |
| `positives` | `NVARCHAR` | Keywords representing likes |

#### `served_ads` (Served Event Log)

A record of every ad that won the auction and was displayed to a user.

| Column | Datatype | Description |
| :--- | :--- | :--- |
| `request_id` | `NVARCHAR` | Identifier for the ad serve request |
| `campaign_id` | `NVARCHAR` | Identifier for the campaign |
| `user_id` | `NVARCHAR` | Identifier for the user |
| `auction_cpm` | `DOUBLE` | CPM decided during the auction |
| `auction_cpc` | `DOUBLE` | CPC decided during the auction |
| `auction_cpa` | `DOUBLE` | CPA decided during the auction |
| `target_age_range` | `NVARCHAR` | Combined age range |
| `target_location` | `NVARCHAR` | Combined city, state, and country |
| `target_gender` | `NVARCHAR` | Target gender |
| `target_income_bucket` | `NVARCHAR` | Target income bucket |
| `target_device_type` | `NVARCHAR` | Target device type |
| `campaign_start_time` | `NVARCHAR` | Combined campaign start date and time |
| `campaign_end_time` | `NVARCHAR` | Combined campaign end date and time |
| `timestamp` | `TIMESTAMP` | Timestamp of the event |

-----

## 🔗 API Endpoints

### 1\. Ad Server (Real-Time Auction)

| Endpoint | Method | Functionality |
| :--- | :--- | :--- |
| **`/ad/user/<user_id>/serve`** | `GET` | Initiates the ad auction process and returns the winning ad. |
| **Example** | | `http://127.0.0.1:8000/ad/user/123/serve?device_type=All&city=Mumbai&state=Maharashtra` |

### 2\. Feedback Handler (Billing & Event Publishing)

| Endpoint | Method | Functionality |
| :--- | :--- | :--- |
| **`/ad/<ad_request_id>/feedback`** | `POST` | Receives user interaction (view, click, acquisition), deducts budget, and publishes the event. |
| **Example** | | `http://localhost:8080/ad/17001d26-0f72-11eb-8a4e-acde48001122/feedback` |

-----

## 📚 Datasets

The project uses four public datasets to simulate diverse user profiles and a rich set of ad campaigns:

1. **Amazon Advertisements**: Data related to Amazon's advertisements from 2019. https://www.kaggle.com/sachsene/amazons-advertisements 
2. **ADS 16 dataset**: Used to determine user preferences for advertisements. https://www.kaggle.com/groffo/ads16-dataset 
3. **Advertising dataset**: Contains user demographics and internet usage patterns. https://www.kaggle.com/tbyrnes/advertising
4. **Users dataset**: Contains users data, that is needed to store in Database[Postgres]. https://www.kaggle.com/datasets/junglisher/ad-users-dataset

-----

## 💻 Setup & Installation

### Prerequisites

  * **Python 3.12+**
  * **Docker** and **Docker Compose**
  * **Apache Spark** installation (for `feedbackWriter.py`)
  * **PostgreSQL** or MySQL

### 1\. Clone & Dependencies

```bash
git clone https://github.com/your-username/DE-Project--Online-Advertisement-Platform.git
cd DE-Project--Online-Advertisement-Platform

# Install dependencies
python3 -m venv myenv && source myenv/bin/activate
pip install -r requirements.txt
```

### 2\. Infrastructure (Kafka/DB)

  * **Database Setup**: Start your PostgreSQL/MySQL service and use `pgadmin4` (or similar) to create the `online_ads` schema and the **`users`**, **`ads`**, and **`served_ads`** tables (Schema details are above). *(See `Sequel_Queries.sql` for query examples.)*
  * **Kafka Setup**:
    ```bash
    # Assuming a docker-compose.yml file is present for Kafka
    docker-compose up -d

    # Manually create the two required topics
    docker exec broker kafka-topics.sh --create --topic de-project-ads-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    docker exec broker kafka-topics.sh --create --topic feedback-handler-queue --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
    ```

### 3\. Configuration

  * Create a `.env` file from the example: `cp .env.example .env`
  * Fill in all database credentials, Kafka broker addresses, and service ports.

-----

## ▶️ Running the Simulation

Execute the following steps in separate terminal windows to run the end-to-end simulation. It is recommended to let the system run for at least **one hour** to generate a substantial dataset.

1.  **Start the Ad Server (API)**

    ```bash
    uvicorn "Main Scripts.AdServer:app" --host 0.0.0.0 --port 8000
    ```

2.  **Start the Consumers**

    ```bash
    # Terminal 2: Ad Manager (DB writer)
    python "Main Scripts/AdManager.py"

    # Terminal 3: User Feedback Writer (Spark Streaming)
    # Adjust the Spark submit command for your environment
    spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1 "Main Scripts/feedbackWriter.py"
    ```

3.  **Start the Producers/Simulators**

    ```bash
    # Terminal 4: Publish Ad Campaigns
    python kafka_ads_data_producer.py

    # Terminal 5: User Simulator (Starts generating traffic)
    # The script takes configuration parameters; ensure they match your setup.
    python user_simulator.py <db_host> <db_user> <db_pass> <db_name> <protocol> <ad_server_host> <ad_server_port> <feedback_handler_host> <feedback_handler_port>
    # Example:
    # python user_simulator.py localhost postgres mypassword postgres http localhost 8000 localhost 8000
    ```

-----

## 📈 Data Analytics & Reporting

After the simulation is complete, the data in your database (`ads`, `served_ads`) and the archived files (from Spark) can be queried for business insights.

### Key Analytical Questions

  * Top 10 under-utilised Ad Campaigns
  * Top 10 spending Ad Campaigns
  * Total expenditure and Click-Through Rate (**CTR**) of all campaigns
  * Top 5 campaigns based on Interactivity (highest CTR)
  * Top 10 spending Ad Categories
  * Analysis of Auction price differences (e.g., winner's bid vs. second-highest bid)

-----

## 🔭 Project Scope & Future Work

While the core functional requirements have been met, the following components are natural extensions for further development:

  * **Reporting Dashboard**: Build analytics reports and visualizations on top of the archived data (e.g., in a Hive layer) using a BI tool like Apache Hue or Superset to derive business insights.
  * **Full Containerization**: Create Dockerfiles for *every* application service (Ad Manager, Ad Server, Producers) to make the entire stack fully portable and easier to deploy in cloud environments.
  * **Advanced Bidding Model**: Implement more sophisticated bidding strategies or an explicit **bid floor** logic in the Ad Server.
