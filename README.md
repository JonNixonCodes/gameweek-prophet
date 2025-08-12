# Gameweek Prophet 🔮⚽📊  
**Gameweek Prophet** is a machine learning project that predicts FPL player points for each gameweek. Built using **Spark** for ETL, **AutoML** for model training, and deployed on **Vertex AI**, this project aims to bring data-driven insights to Fantasy Premier League.  

## 🚀 Features  
- **Data Ingestion**: Collects data from the FPL API and historical CSVs.  
- **ETL Pipeline**: Uses **PySpark** on Vertex AI Workbench to clean and transform data.  
- **ML Model**: Trains an AutoML model to predict weekly FPL points.  
- **Deployment**: Deploys the trained model for real-time inference.  

## 📂 Project Structure  

    gameweek-prophet/
    ├── .venv/                           # Python virtual environment
    ├── data/                            # Local datasets
    │   ├── model/                       # Trained models
    │   ├── processed/                   # Processed data
    │   └── raw/                         # Raw ingested data
    ├── docs/                            # Project documentation and iterations
    ├── notebooks/                       # Jupyter notebooks for exploration and development
    ├── scripts/                         # Utility and deployment scripts
    ├── src/                             # Source code
    │   ├── bigquery/                    # BigQuery SQL definitions
    │   └── cloud_functions/             # Google Cloud Functions
    │       ├── ingest_fpl_api/          # FPL API ingestion function
    │       └── ingest_fpl_historical/   # FPL historical data ingestion function
    ├── tests/                           # Unit and integration tests
    ├── LICENSE                          # Project license
    ├── README.md                        # Project documentation
    └── requirements.txt                 # Python dependencies

## 🚀 How to Use

### Executing Scripts

The `scripts/` directory contains various utility and deployment scripts. To execute a script, navigate to the `scripts/` directory and run it using `bash` or `sh`:

```bash
cd scripts/
bash your_script_name.sh
```

Remember to make the script executable if necessary: `chmod +x your_script_name.sh`.

### Opening Notebooks

The `notebooks/` directory contains Jupyter notebooks for data exploration, analysis, and model development. To open and run these notebooks:

1.  **Ensure Jupyter is Installed:** If you don't have Jupyter installed, you can install it via pip:
    ```bash
pip install jupyter
    ```
    It's recommended to do this within your project's virtual environment.

2.  **Start Jupyter Lab/Notebook:** Navigate to the project's root directory and start Jupyter Lab or Jupyter Notebook:
    ```bash
jupyter lab
    # or
jupyter notebook
    ```
    This will open a new tab in your web browser, displaying the Jupyter interface. You can then navigate to the `notebooks/` directory and open any `.ipynb` file.

## 🛠️ Setup  
### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/yourusername/gameweek-prophet.git
cd gameweek-prophet
```

### 2️⃣ Install Dependencies
pip install -r requirements.txt

##   Acknowledgments

###  Data Sources

* **FPL API:** The Fantasy Premier League API (https://fantasy.premierleague.com/api/) provides the real-time and historical FPL data necessary for this project.
* **Historical CSVs:** The historical CSV datasets were sourced from the vaastav/Fantasy-Premier-League GitHub repository, which has been crucial for model training.

###  Libraries and Tools

* **PySpark:** Apache PySpark was used for efficient data processing and ETL.
* **AutoML:** Google Cloud AutoML provided the tools for automated machine learning model training.
* **Vertex AI:** Google Cloud Vertex AI was used for model training and deployment.
* **Looker:** Looker was used for data visualization in Phase 1.
* **Next.js:** Next.js is being used for web application development in Phase 2.
* **Vercel:** Vercel will be used for web application deployment in Phase 2.
* **Git:** Git is used for version control.

###  Documentation

* **FPL API Documentation:** The Fantasy Premier League API documentation on Medium (https://medium.com/@frenzelts/fantasy-premier-league-api-endpoints-a-detailed-guide-acbd5598eb19) was an essential resource for understanding the API structure and endpoints.

## 📜 License
This project is licensed under the MIT License.