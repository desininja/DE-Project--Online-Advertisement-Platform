# DE Project: Online Advertisement Platform

This project outlines the architecture and implementation of a data-intensive online advertising platform. The system is designed to handle advertising campaigns, serve ads to users, track user feedback, and generate reports. It uses a variety of data engineering tools to create a robust and scalable pipeline.

-----

### Project Architecture

The platform is comprised of several interconnected components, mirroring a real-world advertising system.

  - **Campaign Manager Interface**: An interface for campaign managers to create, update, and stop ad campaigns.
  - **Ad Manager**: Reads campaign instructions from a Kafka queue, processes them, and updates the MySQL database.
  - **Ad Server**: Serves ads to users by holding a second-price auction among eligible ads. It uses user data to determine which ads to serve.
  - **Feedback Handler**: Receives user interaction data (views, clicks, acquisitions) via an API, enriches the data, and publishes it to a Kafka queue.
  - **Slot Budget Manager**: A cron job that runs every 10 minutes to uniformly distribute the leftover ad campaign budget across the remaining time slots.
  - **User Feedback Writer**: A PySpark consumer job that reads enriched user feedback from Kafka and writes it to HDFS for archiving and billing.
  - **Data Archiver**: A Sqoop job that exports ad data from MySQL to Hive for long-term storage and analysis.
  - **Report Generator**: An Apache Hue component that runs queries on the archived data in Hive to generate various business reports and metrics.

-----

### Datasets

This project utilizes three public datasets for simulation and analysis:

  - **Amazon Advertisements**: Data related to Amazon's advertisements from 2019.
  - **ADS 16 dataset**: Used to determine user preferences for advertisements.
  - **Advertising dataset**: Contains user demographics and internet usage patterns.

Additionally, a pre-provided user dataset is used:

  - **User Dataset**: `https://de-capstone-project1.s3.amazonaws.com/users_500k.csv`

-----

### Data Schemas

#### Kafka Queues

  - **Ad Campaign Kafka Queue**: This queue is used for campaign instructions.
      - **Topic**: `de-capstone1`
      - **Kafka Broker**: `18.211.252.152:9092`

| Column             | Description                                                                 |
| ------------------ | --------------------------------------------------------------------------- |
| `Text`             | Text in the advertisement                                                   |
| `Category`         | Category of the product                                                     |
| `Keywords`         | Textual keywords                                                            |
| `Campaign ID`      | Unique identifier for the campaign                                          |
| `Action`           | Type of campaign instruction (`New Campaign`, `Update Campaign`, `Stop Campaign`) |
| `Target Gender`    | `M`, `F`, or `All`                                                            |
| `Target Age Range` | Age range, `0-0` for all ages                                               |
| `Target City`      | City, `All` for no specific city                                            |
| `Target State`     | State, `All` for no specific state                                          |
| `Target Country`   | Country, `All` for no specific country                                      |
| `Target Income Bucket` | `H`, `M`, `L`, or `All`                                                     |
| `Target Device`    | Device type                                                                 |
| `CPC`              | Cost Per Click                                                              |
| `CPA`              | Cost Per Action                                                             |
| `Budget`           | Total campaign budget                                                       |
| `Date Range`       | Date range for the campaign                                                 |
| `Time Range`       | Time range for the campaign                                                 |

  - **User Feedback Kafka Queue**
      - **Topic**: `user-feedback`

This queue stores enriched user feedback data for archiving and billing. The data includes campaign details, user information, and interaction metrics.

#### MySQL Tables

  - **`users`**

| Column            | Datatype | Description                                      |
| ----------------- | -------- | ------------------------------------------------ |
| `id`              | `NVARCHAR` | User Identifier                                  |
| `age`             | `INT`      | Age of the user                                  |
| `gender`          | `NVARCHAR` | Gender of the user                               |
| `internet_usage`  | `NVARCHAR` | Daily average internet usage                     |
| `income_bucket`   | `NVARCHAR` | Estimated income bucket (`H`, `M`, `L`)          |
| `user_agent_string` | `NVARCHAR` | User-agent string                                |
| `device_type`     | `NVARCHAR` | Type of device used                              |
| `websites`        | `NVARCHAR` | Websites liked by the user                       |
| `movies`          | `NVARCHAR` | Movies liked by the user                         |
| `music`           | `NVARCHAR` | Music liked by the user                          |
| `program`         | `NVARCHAR` | Programs liked by the user                       |
| `books`           | `NVARCHAR` | Books liked by the user                          |
| `negatives`       | `NVARCHAR` | Keywords representing dislikes                   |
| `positives`       | `NVARCHAR` | Keywords representing likes                      |

  - **`ads`**

This table stores ad campaign data from the Kafka queue with additional derived attributes.

| Column                | Datatype  | Description                                                         |
| --------------------- | --------- | ------------------------------------------------------------------- |
| `text`                | `NVARCHAR`  | Text of the advertisement                                           |
| `category`            | `NVARCHAR`  | Category of the product                                             |
| `keywords`            | `NVARCHAR`  | Textual keywords                                                    |
| `campaign_id`         | `NVARCHAR`  | Unique identifier for the campaign                                  |
| `status` (Derived)    | `NVARCHAR`  | `ACTIVE` or `INACTIVE`                                                |
| `target_gender`       | `NVARCHAR`  | `M`, `F`, or `All`                                                    |
| `target_age_start`    | `INT`       | Target age lower limit                                              |
| `target_age_end`      | `INT`       | Target age upper limit                                              |
| `target_city`         | `NVARCHAR`  | Target city, `All` for no specific city                             |
| `target_state`        | `NVARCHAR`  | Target state, `All` for no specific state                           |
| `target_country`      | `NVARCHAR`  | Target country, `All` for no specific country                       |
| `target_income_bucket` | `NVARCHAR`  | `H`, `M`, `L`, or `All`                                             |
| `target_device`       | `NVARCHAR`  | Target device type                                                  |
| `cpc`                 | `DOUBLE`    | Cost Per Click                                                      |
| `cpa`                 | `DOUBLE`    | Cost Per Action                                                     |
| `cpm` (Derived)       | `DOUBLE`    | Cost Per Mille (calculated from CPC and CPA)                        |
| `budget`              | `DOUBLE`    | Total campaign budget                                               |
| `current_slot_budget` (Derived) | `DOUBLE` | Budget for the current 10-minute slot                            |
| `date_range_start`    | `NVARCHAR`  | Campaign start date                                                 |
| `date_range_end`      | `NVARCHAR`  | Campaign end date                                                   |
| `time_range_start`    | `NVARCHAR`  | Campaign start time                                                 |
| `time_range_end`      | `NVARCHAR`  | Campaign end time                                                   |

  - **`served_ads`**

This table stores a record of every ad served to a user.

| Column                | Datatype  | Description                                          |
| --------------------- | --------- | ---------------------------------------------------- |
| `request_id`          | `NVARCHAR`  | Identifier for the ad serve request                  |
| `campaign_id`         | `NVARCHAR`  | Identifier for the campaign                          |
| `user_id`             | `NVARCHAR`  | Identifier for the user                              |
| `auction_cpm`         | `DOUBLE`    | CPM decided during the auction                       |
| `auction_cpc`         | `DOUBLE`    | CPC decided during the auction                       |
| `auction_cpa`         | `DOUBLE`    | CPA decided during the auction                       |
| `target_age_range`    | `NVARCHAR`  | Combined age range                                   |
| `target_location`     | `NVARCHAR`  | Combined city, state, and country                    |
| `target_gender`       | `NVARCHAR`  | Target gender                                        |
| `target_income_bucket` | `NVARCHAR`  | Target income bucket                                 |
| `target_device_type`  | `NVARCHAR`  | Target device type                                   |
| `campaign_start_time` | `NVARCHAR`  | Combined campaign start date and time                |
| `campaign_end_time`   | `NVARCHAR`  | Combined campaign end date and time                  |
| `timestamp`           | `TIMESTAMP` | Timestamp of the event                               |

-----

### API Endpoints

#### Ad Server

  - **URL**: `<host>/ad/user/<user_id>/serve?device_type=<device_type>&city=<city>&state=<state>`
  - **HTTP Method**: `GET`
  - **Functionality**: Serves an ad to a user based on their details.

#### Feedback Handler

  - **URL**: `<host>/ad/<ad_request_id>/feedback`
  - **HTTP Method**: `POST`
  - **Functionality**: Receives user feedback (view, click, acquisition) for a specific ad request.

-----

### Project Tasks

1.  **MySQL Environment Setup**: Create the `users`, `ads`, and `served_ads` tables in MySQL with the provided schemas.
2.  **Ad Manager**: Develop a PyKafka consumer to read campaign instructions from Kafka, derive attributes like **CPM** and **status**, and perform `INSERT`/`UPDATE` operations on the `ads` table in MySQL.
      - **CPM Calculation**: `(Weight_CPC * Amount_CPC) + (Weight_CPA * Amount_CPA)` where `Weight_CPC = 0.0075` and `Weight_CPA = 0.0005`.
3.  **Ad Slot Budget Manager**: Create a Python script and a cron job that runs every 10 minutes to update the `current_slot_budget` in the `ads` table.
4.  **Ad Server**: Implement a Flask application to create the Ad Server API. The server must query the `ads` and `users` tables, perform a **second-price auction** on eligible ads, and store the served ad information in the `served_ads` table.
5.  **Feedback Handler**: Build a Flask API that receives user feedback, retrieves auction details from `served_ads`, calculates `expenditure` and `user_action`, updates the budget in the `ads` table, and publishes the enriched data to the user feedback Kafka queue.
6.  **User Feedback Writer**: Write a PySpark consumer job to read from the user feedback Kafka queue and write the data to HDFS.
7.  **Data Archiver**: Use a Sqoop command to export ad campaign data from MySQL to Hive.
8.  **Report Generator**: Use Apache Hue to run Hive queries and generate business intelligence reports, including:
      - Top 10 under-utilized and spending ad campaigns.
      - Total expenditure and CTR (Click-Through Rate) of campaigns.
      - Top interactive age groups, locations, genders, income buckets, and device types.
      - Top 10 spending ad categories.
      - Highest price differences in auction CPMs.

-----

### Project Setup and Execution

1.  Set up an EMR cluster with Hadoop, Sqoop, Hive, and Spark installed.
2.  Ensure the EBS Root Volume size is at least 20 GB.
3.  Execute **Task 1** to set up the MySQL tables.
4.  Execute **Task 2** for the Ad Manager and **Task 3** for the Slot Budget Manager.
5.  Run the **Ad Server** and **Feedback Handler** APIs (**Tasks 4 and 5**).
6.  Utilize the provided `user_simulator.py` script to simulate user behavior.
7.  Run the **User Feedback Writer** and **Data Archiver** jobs (**Tasks 6 and 7**).
8.  Use Apache Hue to perform the reporting tasks (**Task 8**).