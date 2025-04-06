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

#### 3.1.1 Ingestion
* Cloud Functions

#### 3.1.1 ETL
* [Dataproc Serverless for Spark Batch](https://cloud.google.com/dataproc-serverless/docs/overview#spark-batch)

#### 3.1.1 ML
* Train model locally using scikit-learn and exported to [Vertex AI Workbench](https://cloud.google.com/vertex-ai/docs/training/exporting-model-artifacts#scikit-learn).
* Deployed using Vertex AI Workbench [batch predictions](https://cloud.google.com/vertex-ai/docs/predictions/get-batch-predictions).
    
        We tried using AutoML for training however the costs were high for training a basic linear regression model.

#### 3.1.1 Back-end
* BigQuery as data connection for Looker Studio.

#### 3.1.1 Front-end
* Phase 1: Looker Studio dashboard.
* Phase 2: Next.js web application.

#### 3.1.1 Orchestration
* Cloud Workflows

#### 3.1.1 Deployment
* Phase 1: Vertex AI, Looker Studio.
* Phase 2: Vertex AI, Vercel (for Next.js).

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