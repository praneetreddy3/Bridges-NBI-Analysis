# Bridges-NBI-Analysis

**Predictive Modeling of U.S. Bridge Posting Status Using National Bridge Inventory Data with Apache Spark**

## Overview

This project analyzes and predicts bridge posting status (truck load restrictions) across the United States using 950,000+ records from the National Bridge Inventory (2024-2025). The analysis employs Apache Spark for distributed machine learning, MongoDB for NoSQL data querying, and comprehensive feature engineering to achieve predictive accuracy with ROC-AUC > 0.90.

**Key Technologies:** Apache Spark, Python, Machine Learning (Logistic Regression, Decision Trees, XGBoost), MongoDB, Databricks, Feature Engineering

## Results Summary

- **Best Model:** XGBoost with hyperparameter tuning
- **ROC-AUC Score:** 0.93
- **Accuracy:** 0.83
- **F1-Score:** 0.87
- **Dataset:** 950,000+ bridge records from FHWA National Bridge Inventory
- **Features Engineered:** 26 features including interaction terms and nonlinear transformations

## Project Objectives

This research addresses two key research questions:

- **RQ1 (Inferential Analysis):** Using baseline features (bridge age, span length, truck traffic, movability, materials) with statistical hypothesis testing
- **RQ2 (Predictive Modeling):** Advanced feature engineering including interaction terms (age×truck, span×truck, age×span), polynomial transformations (age², log(span), truck²), and categorical binning

## Dataset

**Source:** [Federal Highway Administration (FHWA) National Bridge Inventory](https://www.fhwa.dot.gov/bridge/nbi.cfm)

**Size:** 950,000+ bridge records across all U.S. states

**Features Used (15 NBI Items):**
- Bridge age, span length, average daily traffic, truck traffic percentage
- Main span material and design type
- Owner agency and state information
- Bridge posting code (target variable)

**Download Instructions:**
1. Visit FHWA NBI website
2. Download Excel files for 2024-2025
3. Select the 15 required NBI items (see documentation)
4. Save as `Finalinfobridgedataset_2024and2025.xlsx`

## Architecture

```
Data Pipeline:
Excel Dataset → Data Cleaning → Feature Engineering → Distributed ML (Spark) → Model Evaluation
                                     ↓
                           MongoDB NoSQL Storage
                                     ↓
                         Databricks SQL Visualization
```

### Feature Engineering (RQ2)

**Engineered Features (26 total):**
- Base features: 7 original features
- Interaction terms: age×truck, span×truck, age×span (3 features)
- Polynomial transforms: age², log(span), truck² (3 features)
- Categorical bins: Material, design, agency encodings (13 features)

**Class Imbalance Handling:** Inverse frequency weighting (imbalance ratio: 0.093)

## Technical Stack

| Component | Technology |
|-----------|-----------|
| Big Data Processing | Apache Spark 3.5.1 |
| Machine Learning | PySpark MLlib, XGBoost |
| Data Processing | Pandas, NumPy |
| Database | MongoDB, Databricks SQL |
| Visualization | Matplotlib, Seaborn, Databricks |
| Compute Environment | Google Colab / Local machine |

## Repository Structure

```
Bridges-NBI-Analysis/
├── README.md                           # This file
├── .gitignore                          # Git ignore rules
├── src/
│   ├── data_cleaning.py               # Data preprocessing script
│   └── requirements.txt                # Python dependencies
├── notebooks/
│   └── analysis.ipynb                 # Main ML analysis (Jupyter)
├── data/
│   ├── README.md                      # Data documentation
│   └── [CSV/Excel files excluded]     # Download from FHWA
├── results/
│   └── visualizations/                # Generated Databricks charts
│       ├── topstateswithhighestbridgecount.png
│       ├── Distributionofbridgesbyyearbuilt.png
│       ├── top10stateswithhighestdailytraffic.png
│       ├── MostcommonMainSpanMaterial.png
│       ├── top10statesbytrucktraffic.png
│       └── Distributionofbridgesbytop10owneragencies.png
├── docs/
│   ├── AIT614_Final_Paper.pdf         # Detailed research paper
│   └── MongoDB_Integration.md         # NoSQL setup guide
└── sql/
    └── databricks_queries.sql         # Visualization SQL queries
```

## Getting Started

### Prerequisites

- **Python:** 3.7+
- **Java:** JDK 17+ (required for PySpark)
- **RAM:** 8GB minimum (16GB recommended)
- **Storage:** 2GB free space
- **Optional:** Databricks account (free tier), MongoDB (local or Atlas)

### Installation

#### 1. Install Java JDK 17
```bash
# macOS
brew install openjdk@17

# Windows
# Download from https://adoptium.net/ and set JAVA_HOME

# Linux
sudo apt install openjdk-17-jdk-headless
```

#### 2. Set Up Python Environment
```bash
# Clone or download this repository
git clone https://github.com/praneetreddy3/Bridges-NBI-Analysis.git
cd Bridges-NBI-Analysis

# Install dependencies
pip install -r src/requirements.txt
```

#### 3. Prepare Data
```bash
# Download dataset from FHWA (see Dataset section above)
# Place Excel file in data/ folder as: Finalinfobridgedataset_2024and2025.xlsx

# Run data cleaning script
python src/data_cleaning.py
# Output: data/CleanedBridgeDataset_2024and2025.csv (950K+ rows)
```

## Usage

### Option A: Local Execution (Recommended for Development)

```bash
# 1. Open Jupyter Notebook
jupyter notebook

# 2. Navigate to: notebooks/analysis.ipynb
# 3. Update DATA_PATH in Cell 2 to point to your cleaned CSV
# 4. Run all cells (Cell → Run All)
# Expected runtime: 15-45 minutes depending on system
```

### Option B: Google Colab (Cloud Execution)

```
1. Go to https://colab.research.google.com
2. Upload: notebooks/analysis.ipynb
3. Upload: data/CleanedBridgeDataset_2024and2025.csv
4. Update DATA_PATH in Cell 2
5. Runtime → Run All
```

### Step 3: Databricks Visualizations (Optional)

```
1. Sign up at https://databricks.com (free tier)
2. Create workspace and upload CSV data
3. Create table: cleaned_bridge_dataset_2024_and_2025
4. Run queries from: sql/databricks_queries.sql
5. Generate and export PNG visualizations
6. Save to: results/visualizations/
```

### Step 4: MongoDB Integration (Optional)

#### Local MongoDB
```bash
# Start MongoDB service
mongod

# Import data using Python
python -c "from src.mongo_import import import_data; import_data('data/CleanedBridgeDataset_2024and2025.csv')"
```

#### MongoDB Atlas (Cloud)
```
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create M0 free cluster
3. Get connection string
4. Update connection credentials in Python script
5. Run import script
```

## Expected Output

### Machine Learning Metrics
```
XGBoost Results:
- ROC-AUC:        0.93
- Accuracy:       0.83
- F1-Score:       0.87
- Precision:      0.33
- Recall:         0.89
```

### Databricks Visualizations (6 Charts)
- Top states by bridge count
- Bridge age distribution (1900+)
- States by average daily traffic
- Main span material distribution
- Truck traffic by state (pie chart)
- Top owner agencies (pie chart)

### Database
- Database: `bridge_db`
- Collection: `bridges`
- Documents: ~950,000 records
- Ready for NoSQL queries and aggregations

## Key Findings

1. **Truck traffic** is the strongest predictor of bridge posting status
2. **Bridge age** combined with traffic creates significant interaction effects
3. **Material and design type** impact load restrictions significantly
4. **Regional patterns** show variation in posting policies across states
5. **Feature engineering** improves model ROC-AUC from 0.75 (RQ1) to 0.93 (RQ2)

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Java not found | Install JDK 17 and set `JAVA_HOME` environment variable |
| Memory errors | Reduce Spark driver memory in notebook Cell 1, or use Google Colab |
| File not found | Verify paths in `data_cleaning.py` and notebook Cell 2 |
| Column mismatch | Ensure Excel has all 15 required NBI items |
| MongoDB connection failed | Verify MongoDB is running; check connection string for Atlas |

## Research Paper

For detailed methodology, statistical analysis, and comprehensive results, see:
📄 **[AIT614_Final_Paper.pdf](docs/AIT614_Final_Paper.pdf)**

## Author

**Praneet Chinthala**
- M.S. Data Analytics Engineering, George Mason University
- Email: praneetreddy66@gmail.com
- GitHub: [@praneetreddy3](https://github.com/praneetreddy3)

## License

This project is for educational purposes. Data sourced from FHWA is public domain.

## Acknowledgments

- Federal Highway Administration (FHWA) for National Bridge Inventory data
- George Mason University (AIT 614 Course)
- Databricks and MongoDB for platform access
- Apache Spark and open-source ML communities

---

**Last Updated:** April 2026
