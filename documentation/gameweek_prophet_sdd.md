#   Gameweek Prophet - Software Design Document

##   1. Introduction

###   1.1 Purpose

This document outlines the software design for the Minimum Viable Product (MVP) of Gameweek Prophet, a web-based application designed to provide Fantasy Premier League (FPL) players with data-driven insights and player recommendations to aid in team selection and management. The MVP focuses on delivering core features to enable users to make informed decisions quickly and efficiently.

###   1.2 Scope

The initial release will be a web-based application. Key features will include an interactive dashboard, player recommendations, and important player updates.

###   1.3 Goals and Objectives

* Empower casual FPL players to make informed team management decisions quickly and efficiently.
* Provide actionable insights and recommendations without requiring extensive FPL knowledge or time commitment.
* Offer a user-friendly experience via web application.

##    2. Functional Requirements

###   2.1 Interactive Dashboard

* The dashboard will present key player information and recommendations in a clear and concise format.
* A scoring system will allow users to quickly compare player potential. The scoring system will be based on:
* Past performance (e.g., points, goals, assists)
* Predicted future performance (expected points, derived from the ML model)
* Availability (injury status, likelihood of starting, and average minutes played)
* The dashboard will be developed using Looker.

###   2.2 Player Recommendations

* The application will provide weekly player recommendations for transfers and captaincy.
* Recommendations will be based on data from the FPL API, including past performance, upcoming fixtures, player price and value, expected points, and injury news.

###   2.3 Important Player Updates

* The application will highlight crucial player information that could impact team selection, such as potential price drops, injury status updates, announcements of double gameweeks, and suspensions.

##   3. Technical Design

###   3.1 System Architecture

#### 3.1.1 Data Sources

* FPL API:
    * Source: https://fantasy.premierleague.com/api/
    * Documentation: https://medium.com/@frenzelts/fantasy-premier-league-api-endpoints-a-detailed-guide-acbd5598eb19
    * Endpoints:
        * bootstrap-static/
        * fixtures/
        * element-summary/{element_id}/
        * event/{gameweek-id}/live/
        * entry/{manager_id}/
        * entry/{manager_id}/history
* Historical FPL Seasons:
    * Source: vaastav/Fantasy-Premier-League GitHub repository.
    * Description: CSV files of all players in the English Premier League with their respective team and total fantasy points.

#### 3.1.2 Data Ingestion

Cloud Run Functions will be used to ingest data from the FPL API and other sources.

| Function Name                  | Description                                 | Data Source        |
| :----------------------------- | :------------------------------------------ | :----------------- |
| `ingest_fpl_api`               | Ingests data from FPL API endpoints         | FPL API            |
| `ingest_fpl_historical`        | Ingests data from historical FPL seasons    | Historical CSVs    |

#### 3.1.3 Storage

* Raw and processed data will be stored in Google Cloud Storage.
* Data will be stored in its native format initially, with processed data stored in Parquet format.

        gs://gameweek-prophet-dev/
        ├── models/
        │   └── fpl_prediction_model/
        │       ├── version=1/
        │       │   ├── model.joblib
        │       │   ├── metadata.json  # (e.g., training date, parameters)
        │       └── version=2/
        │           ├── model.joblib
        │           ├── metadata.json
        │       └── ...
        ├── raw/
        │   └── fpl_api/
        │       ├── bootstrap_static/
        │       │   └── source_date=YYYY-MM-DD/
        │       │       └── data.json
        │       └── fixtures/
        │       │   └── source_date=YYYY-MM-DD/
        │       │       └── data.json
        │       └── ...
        │   └── historical_csvs/
        │       ├── fixtures/
        │       │   └── source_date=YYYY-MM-DD/
        │       │       └── data.csv
        │       └── merged_gw/
        │       │   └── source_date=YYYY-MM-DD/
        │       │       └── data.csv
        │       └── ...
        └── processed/
            └── fpl_data/
                ├── source_date=YYYY-MM-DD/
                │   └── data.parquet
                ├── source_date=YYYY-MM-DD/
                │   └── data.parquet
                └── ...

**metadata.json**
```json
{
    "training_date": "2024-07-10 10:00:00",
    "dataset_version": "v2.0",
    "model_parameters": {
        "n_estimators": 100,
        "learning_rate": 0.01
    },
    "evaluation_metrics": {
        "rmse": 1.25,
        "r2_score": 0.85
    }
}
```

#### 3.1.4 ETL

For the ETL I wanted to learn Spark and for that reason I am planning to use [Dataproc Serverless for Spark Batch](https://cloud.google.com/dataproc-serverless/docs/overview#spark-batch).

#### 3.1.5 MLOps

My main requirements for training and operationalising the Machine Learning part of this project my requirements are to keep costs low, and to be able to monitor and re-train my model. My current approach is to:
* Train model locally using scikit-learn and exported to [Vertex AI Workbench](https://cloud.google.com/vertex-ai/docs/training/exporting-model-artifacts#scikit-learn).

        We tried using AutoML for training however the costs were high for training a basic linear regression model.

* Deployed using Vertex AI Workbench [batch predictions](https://cloud.google.com/vertex-ai/docs/predictions/get-batch-predictions).
* Monitor model performance using [Vertex AI Model Monitoring](https://cloud.google.com/vertex-ai/docs/model-monitoring/overview).
    

#### 3.1.6 Back-end

Processed data from the ETL stage will be stored in Cloud Storage as parquet formatted and hive partitioned files. These will be read using BigQuery external tables, and an SQL data pipeline will load the data into a BigQuery table so that the data can be accessed from Looker Studio (front-end).

#### 3.1.7 Front-end

For the MVP the front-end is a Looker Studio dashboard. The Looker Studio dashboard will be mobile friendly and built with responsive design. Future iterations will be a cross-platform application designed using React Native and Expo.

#### 3.1.8 Orchestration

Our main requirement is to keep the costs low. For that reason I prefer to opt for a serverless solution. Below are some of the options that I am considering.
* **Option A**: Using Cloud Workflows for building an end-to-end pipeline from ingestion to updating the back-end. Scheduling will be done through a daily CRON job using Cloud Scheduler.

    **Pros**:
    * Pay per use model
    * Easy to integrate with other GCP services
    * Monitor workflows through UI
    * Execution control using conditions, iteration, parallel steps
    * Multiple options to trigger workflow: Manual, API, Scheduled
    * Handle error scenarios using retry logic

    **Cons**:
    * Less flexibility with scheduling, if event-driven or dynamic scheduling is required.
    * Less community support compared with the more popular Composer option.
    * Not as easy to manage multiple workflows and dependencies between workflows compared with Composer.

* **Option B**: Build each module separately, and use a combination of Cloud Scheduler for CRON jobs and Pub/Sub and Cloud Functions for event-driven triggers to orchestrate tasks.

    **Pros**:
    * Keep costs low, only paying for what I need.
    * Most flexibile option, since each task is modularised and I can completely control the flow.

    **Cons**:
    * Most complex as it requires developing multipe event-triggered Cloud Functions and pub/sub topics.

* **Option C**: Using Cloud Composer to build a DAG using Airflow.

    **Pros**:
    * More powerful and flexible compared with using Cloud Workflows.
    * Monitoring and UI is superior to Cloud Workflows.
    * Rich ecosystem: Airflow has a large developer community and also a plethora of Airflow connectors.

    **Cons**:
    * Most expensive. Significant costs to keep Composer running.

Based on the above considerations we have decided to use **Option A** to use Cloud Workflows for orchestration as it is a low cost option which also has all the feature that we require currently and to meet our future needs. I don't forsee the need to go for the more complex (and expensive) solution using Cloud Composer at any point in the future.

###   3.2 Deployment

* The MVP will be deployed using the relevant Google Cloud Platform (GCP) services for each component (e.g., Cloud Run Functions, Cloud Storage, Vertex AI, Looker).
* The deployment process for the MVP will be manual.

###   3.3 Technologies Used

* BigQuery
* Cloud Run Functions
* Cloud Storage
* Cloud Workflows
* Dataproc Serverless
* Looker
* Vertex AI

##   4. User Interface (UI) Design

* The UI will be an interactive dashboard built with Looker.
* The design will prioritize simplicity and ease of use, ensuring that casual users can easily navigate and understand the information.
* Key recommendations and updates will be prominently displayed for at-a-glance viewing.

##   9. Future Enhancements

* Future development phases will include:
    * A fully developed web application using React or Next.js.
    * Mobile applications for iOS and Android.
    * Enhanced features such as personalized recommendations and integration with user FPL accounts.
    * Users can use natural language to ask an AI chat agent how best to optimize their team.