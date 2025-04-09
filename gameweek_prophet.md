#   Gameweek Prophet Documentation

##   1. Introduction

###   1.1 Overview

Gameweek Prophet is a personal project to build an AI that predicts Fantasy Premier League (FPL) player points for each gameweek, evolving into a user-facing product.

###   1.2 Purpose & Goals

A side project to develop skills in data engineering (Spark), product design, and web development while providing a practical tool for FPL decisions. The goal is to assist casual FPL players in making better lineup decisions.

###   1.3 Target Audience

Casual FPL players using the app weekly to inform transfer decisions based on predicted player points.

##   2. Product Vision

* Phase 1: 
    * FPL player point predictions
    * Data exploration via a Looker dashboard (interactive filtering of players).
* Phase 2: 
    * User interaction with data via a web application
* Phase 3:
    * Interacting with AI agent on web application

##   3. Architecture and Design

###   3.1 System Architecture

#### 3.1.1 Data Sources
* FPL API
* Historical FPL Seasons

#### 3.1.1 Storage
    gs://your-bucket-name/
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

#### 3.1.1 Ingestion
| Function Name                     | Description                                  | Data Source        | Data Type          |
| :-------------------------------- | :------------------------------------------- | :----------------- | :----------------- |
| `ingest_fpl_api_bootstrap_static`   | Ingests data from FPL API bootstrap-static/  | FPL API            | Bootstrap Static   |
| `ingest_fpl_api_fixtures`           | Ingests data from FPL API fixtures/          | FPL API            | Fixtures           |
| `ingest_fpl_api_element_summary`    | Ingests data from FPL API element-summary/   | FPL API            | Element Summary    |
| `ingest_fpl_api_event_live`         | Ingests data from FPL API event/{}/live/     | FPL API            | Event Live         |
| `ingest_fpl_api_entry`              | Ingests data from FPL API entry/             | FPL API            | Entry              |
| `ingest_fpl_api_entry_history`      | Ingests data from FPL API entry/{}/history  | FPL API            | Entry History      |
| `ingest_historical_csv_player_data` | Ingests historical player data               | Historical CSVs    | Player Data        |

#### 3.1.1 ETL
For the ETL I wanted to learn Spark and for that reason I am thinking to use [Dataproc Serverless for Spark Batch](https://cloud.google.com/dataproc-serverless/docs/overview#spark-batch).

#### 3.1.1 MLOps
My main requirements for training and operationalising the Machine Learning part of this project my requirements are to keep costs low, and to be able to monitor and re-train my model. My current approach is to:
* Train model locally using scikit-learn and exported to [Vertex AI Workbench](https://cloud.google.com/vertex-ai/docs/training/exporting-model-artifacts#scikit-learn).

        We tried using AutoML for training however the costs were high for training a basic linear regression model.

* Deployed using Vertex AI Workbench [batch predictions](https://cloud.google.com/vertex-ai/docs/predictions/get-batch-predictions).
* Monitor model performance using [Vertex AI Model Monitoring](https://cloud.google.com/vertex-ai/docs/model-monitoring/overview).
    

#### 3.1.1 Back-end
For the backend, the current plan is to read the data using external tables in BigQuery, and run a simple pipeline to load data into a BigQuery table so that the data can be accessed from Looker Studio (front-end).

#### 3.1.1 Front-end
Currently the front-end is a Looker Studio dashboard. Future iteration of the Looker Studio dashboard will be mobile friendly and built with responsive design. In the future we will develop a React, Next.js web application.

#### 3.1.1 Orchestration
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

#### 3.1.1 Deployment
Current deployment will be done using the GCP services relevant for each section (Storage, ETL, MLOps, Back-end, Front-end, Orchestration).

Future iterations will use Vercel for deploying the front-end web application, back-end deployment TBD.

###   3.2 Data Flow
    Source
    --> Ingestion
    --> ETL
    |--> Prediction
    |   `--> Back-end
    |       `--> Front-end
    |--> Model Training

###   3.3 Future Considerations

* Scalability: Designing for increasing data volume and user traffic.
* Maintainability: Code structure, testing, and documentation for long-term development.
* API Development: Potential for exposing prediction data via an API.

##   4. Data Management

* FPL API:
    * URL: https://fantasy.premierleague.com/api/
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

###   4.2 Data Storage

* Raw and processed data stored in Google Cloud Storage.
* Raw data stored in native format.
* Processed data and predicted player points stored in Parquet format.

###   4.3 Data Transformation

* Ad-hoc batch processing of raw data using PySpark.
* Feature engineering (e.g., calculating xG, goals scored in the previous 4/16 game weeks).

##   5. Model Development

* Locally developed model hosted on Vertex AI Workbench.

##   6. Implementation Details

###   6.1 Technologies Used

* Phase 1:
    * PySpark
    * Jupyter Notebooks - for local development
    * Vertex AI - for deploying the model
    * Google Cloud Storage - for storing the data
    * BigQuery - for analysis and data visualisation
    * Looker - for front-end visualisation
* Phase 2:
    * Python
    * PySpark
    * AutoML
    * Vertex AI
    * Git
    * Next.js
    * Vercel
    * Cloud Functions
    * Dataproc
    * React

###   6.2 Project Structure

    fpl-points-prediction/
    │── data/                            # Local datasets (avoid committing large files)
    │── notebooks/                       # Jupyter notebooks for exploration 
    │── src/                             # Source code 
    │ ├── ingestion/                     # Data fetching scripts 
    │ ├── processing/                    # PySpark ETL scripts 
    │ ├── training/                      # AutoML training scripts 
    │ ├── deployment/                    # Model deployment scripts 
    │ ├── inference/                     # Prediction scripts 
    │── config/                          # Configuration files 
    │── tests/                           # Unit and integration tests 
    │── cloud/                           # Terraform/GCP deployment scripts (if applicable) 
    │── scripts/                         # Utility scripts 
    │── requirements.txt                 # Python dependencies 
    │── Dockerfile                       # Docker setup (if needed) 
    │── README.md                        # Project documentation

###   6.3 Code Repositories

* https://github.com/JonNixonCodes/gameweek-prophet
* Branches: main, dev

##   7. Deployment

###   7.1 Deployment Environment

* Phase 1:
    * Vertex AI: Used for training and deploying the ML model as an API.
    * Looker: Used for visualizing the data that is stored in GCS.
* Phase 2:
    * Vertex AI: Used for deploying the model.
    * Vercel: Used for deploying the Next.js web application.

###   7.2 Deployment Process

* Phase 1:
    * Deployment process will be manual.
    * Procedure, steps, and scripts to be documented at a later date.
* Phase 2:
    * Deployment will be through a CI/CD framework using Cloud Build.

##   8. Testing

###   8.1 Testing Strategy

TBC

###   8.2 Testing Frameworks/Tools

TBC

###   8.3 Test Coverage

TBC

##   9. Future Enhancements

###   9.1 Phase 2 Enhancements

* User Interface:
    * Next.js implementation.
    * User interface design: simple, user-friendly interface with "Gameweek Prophet" character.
* Performance Optimization: TBC

###   9.2 Phase 3 Enhancements

* User Interface:
    * AI agent interaction as the primary user interface for the web app.
    * Users can use natural language to ask the AI agent how best to optimize their team.
* Scalability and Monetization
    * Scalability Planning: TBC
    * Monetization Strategy (if applicable): TBC

##   10. Acknowledgments

###   10.1 Data Sources

* **FPL API:** The Fantasy Premier League API (https://fantasy.premierleague.com/api/) provides the real-time and historical FPL data necessary for this project.
* **Historical CSVs:** The historical CSV datasets were sourced from the vaastav/Fantasy-Premier-League GitHub repository, which has been crucial for model training.

###   10.2 Libraries and Tools

* **PySpark:** Apache PySpark was used for efficient data processing and ETL.
* **AutoML:** Google Cloud AutoML provided the tools for automated machine learning model training.
* **Vertex AI:** Google Cloud Vertex AI was used for model training and deployment.
* **Looker:** Looker was used for data visualization in Phase 1.
* **Next.js:** Next.js is being used for web application development in Phase 2.
* **Vercel:** Vercel will be used for web application deployment in Phase 2.
* **Git:** Git is used for version control.

###   10.3 Documentation

* **FPL API Documentation:** The Fantasy Premier League API documentation on Medium (https://medium.com/@frenzelts/fantasy-premier-league-api-endpoints-a-detailed-guide-acbd5598eb19) was an essential resource for understanding the API structure and endpoints.