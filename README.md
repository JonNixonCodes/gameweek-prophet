# Gameweek Prophet 🔮⚽📊  
**Gameweek Prophet** is a machine learning project that predicts FPL player points for each gameweek. Built using **Spark** for ETL, **AutoML** for model training, and deployed on **Vertex AI**, this project aims to bring data-driven insights to Fantasy Premier League.  

## 🚀 Features  
- **Data Ingestion**: Collects data from the FPL API and historical CSVs.  
- **ETL Pipeline**: Uses **PySpark** on Vertex AI Workbench to clean and transform data.  
- **ML Model**: Trains an AutoML model to predict weekly FPL points.  
- **Deployment**: Deploys the trained model for real-time inference.  

## 📂 Project Structure  

    gameweek-prophet/
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

## 🛠️ Setup  
### 1️⃣ Clone the Repository  
```bash
git clone https://github.com/yourusername/gameweek-prophet.git
cd gameweek-prophet
```

### 2️⃣ Install Dependencies
pip install -r requirements.txt

### 3️⃣ Run Jupyter Notebooks (Optional)
jupyter notebook

### 4️⃣ Run the ETL Pipeline
python src/processing/run_etl.py

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
