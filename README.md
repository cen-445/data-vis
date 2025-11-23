# Telco Customer Churn Analytics Dashboard

An interactive Streamlit dashboard application developed for telecommunications customer churn analysis. This project visualizes customer data, predicts churn risk, and performs customer segmentation.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Dataset](#dataset)
- [Installation](#installation)
- [Usage](#usage)
- [Requirements](#requirements)
- [Project Members](#project-members)
- [Report](#report)

## ✨ Features

- **Interactive Dashboard**: Modern and user-friendly Streamlit-based interface
- **Advanced Filtering**: Data analysis with multiple filtering options
- **Visualizations**: 
  - Retention and Hazard curves
  - Risk heatmaps
  - Sankey diagrams
  - Treemap visualizations
  - Faceted histograms
  - Strip plots
  - Customer segmentation charts
- **Churn Prediction**: Machine learning-based churn risk scoring
- **Customer Segmentation**: Customer groups using K-Means clustering

## 📁 Project Structure

```
data-vis/
├── app/
│   ├── app.py              # Main Streamlit application (Arsen)
│   ├── charts_isil.py      # Işıl's visualization module (Risk Model)
│   ├── charts_mehmet.py     # Mehmet's visualization module (Lookup Data)
│   ├── charts_arsen.py      # Arsen's visualization module (Segmentation)
│   └── styles.css          # CSS styles (Arsen)
├── data/
│   ├── raw/                # Raw dataset
│   │   └── Telco-Customer-Churn.csv
│   └── processed/          # Processed datasets
│       ├── Telco_processed.csv #(Mehmet)
│       └── telco_churn_with_probs.csv #(Işıl)
├── notebooks/              # Jupyter notebooks
│   ├── preprocess (1).ipynb #(Mehmet)
│   └── train.ipynb #(Işıl)
├── dvc.yaml                # DVC pipeline configuration #(Işıl)
├── requirements.txt        # Python dependencies
├── DATASET.md             # Dataset documentation #(Mehmet)
└── README.md              # This file
```

## 📊 Dataset

This project uses the **Telco Customer Churn** dataset. For detailed information about the dataset, please refer to the [DATASET.md](DATASET.md) file.

**Dataset Characteristics:**
- **Source**: [Kaggle - Telco Customer Churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn/data)
- **Number of Rows**: 7,043 customers
- **Number of Columns**: 21 features
- **Target Variable**: Churn (Customer churn)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd data-vis
```

### 2. Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 💻 Usage

### Running the Application

To run the main application, use the following command:

```bash
streamlit run app/app.py
```

The application will automatically open in your default browser (usually at `http://localhost:8501`).

### Dashboard Features

1. **Filter Panel**: You can apply various filters from the sidebar on the left:
   - Contract type
   - Internet service
   - Tenure (subscription duration)
   - All other features

2. **Key Metrics**: Important metrics are displayed at the top of the dashboard:
   - Total number of customers
   - Churn count
   - Churn rate
   - Average monthly charges

3. **Tabs**:
   - **X: Lookup Data** (Mehmet): Retention curves, violin plots, and Sankey diagrams
   - **Y: Segmentation** (Arsen): Churn distribution treemap, customer distribution histograms, and spending distribution strip plots
   - **Z: Risk Model** (İşil): AI-based risk analysis, risk heatmaps, and K-Means customer segmentation

### Data Processing

You can use Jupyter notebooks to process raw data:

```bash
jupyter notebook notebooks/preprocess\ \(1\).ipynb
```

For model training:

```bash
jupyter notebook notebooks/train.ipynb
```

## 📦 Requirements

Main dependencies:

- **Streamlit** (1.37.0): Web application framework
- **Pandas** (2.2.2): Data processing
- **NumPy** (1.26.4): Numerical computations
- **Plotly** (5.23.0): Interactive visualizations
- **Scikit-learn** (1.5.0): Machine learning
- **DVC** (3.50.2): Data versioning

For the complete list of dependencies, please refer to the `requirements.txt` file.

## 👥 Project Members

### Mehmet Çağlar - Lookup Data Module

**Main Goal**: Data preprocessing and customer lifecycle analysis through retention and flow visualizations.

**Visualization Techniques**:
- **Retention Alpha Curve**: Tracks customer longevity to identify "danger months" where steep drops reveal early dissatisfaction among specific groups (e.g., Fiber Optic users)
- **Payment Density & Contract Analysis (Split Violin Plot)**: Visualizes price sensitivity by comparing retained vs. churned customers, confirming if high prices are the main driver forcing specific contract holders to leave
- **Customer Lifecycle Flow (Sankey Diagram)**: Maps the full customer journey to distinguish between losing people versus losing money, revealing whether the business is facing high-volume churn or the financial bleeding of high-value customers

**Technical Implementation**:
- Data preprocessing in `preprocess.ipynb` using Pandas and Scikit-learn to clean data, fill missing values, and transform categorical variables for machine learning
- Interactive "Alpha Terminal" dashboard in `charts_mehmet.py` featuring three core analytical tools
- Project documentation: Created `README.md` and `DATASET.md` files

### Arsen Denisenko - Segmentation Module

**Main Goal**: Customer segmentation and churn behavior exploration through interactive visualizations.

**Visualization Techniques**:
- **Churn Treemap**: Hierarchical visualization of churn distribution across customer segments
- **Faceted Tenure Histogram**: Customer distribution analysis faceted by Internet Service Type and Churn status
- **Spending Strip Plot**: Distribution of charges (monthly and total) grouped by contract type and churn status

**Key Insights & Findings**:
- Clear identification of high-risk, high-value customer groups, particularly short-tenure, high-charge customers on month-to-month contracts
- Visual insights support targeted retention strategies, emphasizing early intervention and prioritized support for segments with both high churn likelihood and strong lifetime value potential

**Technical Implementation**:
- Interactive Streamlit dashboard with Plotly-based visualizations
- Basic css implementation, dynamic hover details, and user-friendly layout in `charts_arsen.py`

### Işıl Çağlar - Risk Model Module

**Main Goal**: Detect root causes of churn, identify high-risk profiles, and optimize retention budgets using AI-driven segmentation.

**Visualization Techniques**:
- **Risk Heatmap**: Reveals churn risk patterns across tenure and monthly charges dimensions
- **High Risk Radar**: Interactive scatter plot for identifying customers requiring immediate intervention
- **AI-Driven Customer Segments**: K-Means clustering with dual-view analysis (Radar and Bar charts)

**Key Insights & Findings**:
- **Loyalty Buffer Effect**: While high monthly charges create a 76% churn risk for new customers, this drops to 22% for loyal ones
- **Churn Triage Strategy**: Retention resources should be prioritized on the "Orange Zone" (70-90% risk) rather than the "Red Zone" (>90% risk) to maximize ROI (Return on Investment)
- **Tech Support Investment**: Providing Tech Support to high-risk segments (specifically Cluster 3) serves as a critical investment rather than a cost, increasing Customer Lifetime Value by 5-6 times and significantly reducing churn

**Technical Implementation**:
- CatBoost classifier selected for superior performance to calculate individual churn probabilities using `predict_proba`
- Generated `telco_churn_with_probs.csv` dataset that powers the interactive dashboard
- Python libraries: Pandas, Plotly, Scikit-learn, and CatBoost
- Implementation in `charts_isil.py`
- Data versioning: Configured and implemented DVC (Data Version Control) pipeline for data versioning and reproducibility (`dvc.yaml`)

## 📄 Report

The project report was written by **Işıl Çağlar**. The report documents the project methodology, analysis results, and findings from the Telco Customer Churn analysis.

## 📝 Notes

- The application uses processed datasets from the `data/processed/` folder
- The `telco_churn_with_probs.csv` file is required for churn predictions
- Data versioning is performed using DVC

## 🔧 Troubleshooting

**If you encounter a "Data not found" error:**
- Make sure the required CSV files are in the `data/processed/` folder
- Run the data processing notebook to generate processed data

**If you encounter an import error:**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Check that the virtual environment is activated

## 📄 License

This project is developed for educational purposes.