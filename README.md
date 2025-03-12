# Gameweek Prophet 🔮⚽📊  
**Gameweek Prophet** is a machine learning project that predicts FPL player points for each gameweek. Built using **Spark** for ETL, **AutoML** for model training, and deployed on **Vertex AI**, this project aims to bring data-driven insights to Fantasy Premier League.  

## 🚀 Features  
- **Data Ingestion**: Collects data from the FPL API and historical CSVs.  
- **ETL Pipeline**: Uses **PySpark** on Vertex AI Workbench to clean and transform data.  
- **ML Model**: Trains an AutoML model to predict weekly FPL points.  
- **Deployment**: Deploys the trained model for real-time inference.  

## 📂 Project Structure  
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

## 📜 License
This project is licensed under the MIT License.
