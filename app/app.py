import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config( #ana sayfa bilgileri
    page_title="Telco Churn Analytics Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded"
)
#chartları burda importluyoruz, exceptionları henüz bazı chartlar oluşmamışken kullandık
try:
    from charts_mehmet import render_x_charts
except ImportError:
    render_x_charts = None

try:
    from charts_arsen import render_y_charts 
except ImportError:
    render_y_charts = None

try:
    from charts_isil import render_z_charts 
except ImportError:
    render_z_charts = None

def load_css(file_name="styles.css"): #css dosyasını yüklüyoruz
    css_path = Path(__file__).parent / file_name
    if css_path.exists():        
        with open(css_path, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

@st.cache_data
def load_data(): #3 çeşit data dosyamız var raw olanın yanında, proccessed ve probs. Genelde processedi kullanıcaz
    current_dir = Path(__file__).parent
    data_dir = current_dir.parent / "data" / "processed"
    
    clean_data_path = data_dir / "Telco_processed.csv"    
            
    probs_path = data_dir / "telco_churn_with_probs.csv"
    
    if clean_data_path:
        df_clean = pd.read_csv(clean_data_path)
        
        # --- MAPPING İŞLEMLERİ ---
        
        # 1. Binary (0/1 -> No/Yes)
        binary_cols = ["Partner", "Dependents", "PhoneService", "PaperlessBilling", "SeniorCitizen"]
        for col in binary_cols:
            if col in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[col]):
                df_clean[col] = df_clean[col].map({0: "No", 1: "Yes"}).fillna(df_clean[col])

        # 2. Cinsiyet
        if "gender" in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean["gender"]):
             df_clean["gender"] = df_clean["gender"].map({0: "Female", 1: "Male"}).fillna(df_clean["gender"])

        # 3. Çoklu Servisler
        multi_cols = [
            "OnlineSecurity", "DeviceProtection", "TechSupport", 
            "StreamingTV", "StreamingMovies", "OnlineBackup" 
        ]
        for col in multi_cols:
             if col in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[col]):
                mapping = {0: "No", 1: "No internet service", 2: "Yes"}
                df_clean[col] = df_clean[col].map(mapping).fillna(df_clean[col])

        if "MultipleLines" in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean["MultipleLines"]):
             df_clean["MultipleLines"] = df_clean["MultipleLines"].map({0: "No", 1: "No phone service", 2: "Yes"}).fillna(df_clean["MultipleLines"])

        # 4. PaymentMethod
        if "PaymentMethod" in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean["PaymentMethod"]):
            payment_map = {
                0: "Bank transfer (automatic)",
                1: "Credit card (automatic)",
                2: "Electronic check",
                3: "Mailed check"
            }
            df_clean["PaymentMethod"] = df_clean["PaymentMethod"].map(payment_map).fillna(df_clean["PaymentMethod"])

        # 5. Ana Değişkenler
        if "Contract" in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean['Contract']):
            contract_map = {0: "Month-to-month", 1: "One year", 2: "Two year"}
            df_clean['Contract'] = df_clean['Contract'].map(contract_map).fillna(df_clean['Contract'])

        if "InternetService" in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean['InternetService']):
            internet_map = {0: "DSL", 1: "Fiber optic", 2: "No Service"}
            df_clean['InternetService'] = df_clean['InternetService'].map(internet_map).fillna(df_clean['InternetService'])

        if "Churn" in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean['Churn']):
            churn_map = {0: "No", 1: "Yes"}
            df_clean['Churn'] = df_clean['Churn'].map(churn_map).fillna(df_clean['Churn'])
            
    else:
        st.error("Data not found.")
        st.stop()

    df_probs = None
    if probs_path.exists():
        df_probs = pd.read_csv(probs_path) #probs dosyasını da oku
    
    return df_clean, df_probs #ve okunanları döndür ve yükle(aşşağıda)

df, df_probs = load_data()


st.sidebar.header("Filter Panel")

# --- Ana Filtreler ---
st.sidebar.subheader("Basic Filters")

contract_options = sorted(df["Contract"].unique().astype(str))
selected_contract = st.sidebar.multiselect("Contract Type", options=contract_options, default=contract_options)

internet_options = sorted(df["InternetService"].unique().astype(str))
selected_internet = st.sidebar.multiselect("Internet Service Type", options=internet_options, default=internet_options)

min_tenure = int(df["tenure"].min())
max_tenure = int(df["tenure"].max())
selected_tenure_range = st.sidebar.slider("Tenure", min_tenure, max_tenure, (min_tenure, max_tenure))

# --- Diğer Filtreler ---
st.sidebar.markdown("---")
with st.sidebar.expander("Advanced Filters"):
    
    dynamic_filters = {}
    exclude_columns = ['customerID', 'Contract', 'InternetService', 'tenure', 'Churn']
    
    for col in df.columns:
        if col not in exclude_columns:
            unique_val_count = df[col].nunique()
            is_numeric = pd.api.types.is_numeric_dtype(df[col])
            
            # Sadece 15'ten fazla değeri olan GERÇEK sayısal sütunlar için Slider
            if is_numeric and unique_val_count > 15:
                min_val = float(df[col].min())
                max_val = float(df[col].max())
                if min_val < max_val:
                    dynamic_filters[col] = st.slider(f"{col}", min_val, max_val, (min_val, max_val))
            else:
                # Geri kalan her şey Multiselect olsun
                if unique_val_count < 50: 
                    options = sorted(df[col].unique().astype(str))
                    dynamic_filters[col] = st.multiselect(f"{col}", options=options, default=options)

st.sidebar.caption("Project Members: Işıl Çağlar, Mehmet Çağlar, Arsen Denisenko")

def filter_dataframe(data): #dataframe filtreleme fonksiyonu
    if data is None: return None
    
    mask = (
        (data["Contract"].astype(str).isin(selected_contract)) &
        (data["InternetService"].astype(str).isin(selected_internet)) &
        (data["tenure"] >= selected_tenure_range[0]) &
        (data["tenure"] <= selected_tenure_range[1])
    )
    df_temp = data[mask]
    
    for col, value in dynamic_filters.items():
        if isinstance(value, tuple): 
            df_temp = df_temp[(df_temp[col] >= value[0]) & (df_temp[col] <= value[1])]
        elif isinstance(value, list):
            if not value: return df_temp[0:0]
            df_temp = df_temp[df_temp[col].astype(str).isin(value)]
            
    return df_temp

df_filtered = filter_dataframe(df) #filtreyi uygula

df_probs_filtered = None
if df_probs is not None and df_filtered is not None:
    common_indices = df_filtered.index.intersection(df_probs.index)
    df_probs_filtered = df_probs.loc[common_indices]


st.title("Telco Customer Churn Analysis") #site bilgileri ve dizaynı

col1, col2, col3, col4 = st.columns(4)

if df_filtered is not None:
    total_customers = len(df_filtered)
    churn_count = df_filtered[df_filtered["Churn"].astype(str).isin(["Yes", "1"])].shape[0]
    churn_rate = (churn_count / total_customers * 100) if total_customers > 0 else 0
    avg_charge = df_filtered["MonthlyCharges"].mean() if not df_filtered.empty else 0

    col1.metric("Total Customers", f"{total_customers:,}")
    col2.metric("Total Churn", f"{churn_count:,}")
    col3.metric("Percantage Churn", f"%{churn_rate:.1f}", delta_color="inverse")
    col4.metric("Avrg. Monthly Charges", f"${avg_charge:.2f}")

st.markdown("---")

tab_x, tab_y, tab_z = st.tabs(["📈 X: Lookup Data", "🔄 Y: Segmentation", "🤖 Z: Risk Model"])

with tab_x:
    if render_x_charts: render_x_charts(df_filtered)
    else: st.info("Missing Module")

with tab_y:
    if df_filtered is not None and render_y_charts: render_y_charts(df_filtered)
    else: st.warning("Missing Module")

with tab_z:
    if df_probs_filtered is not None and render_z_charts: render_z_charts(df_probs_filtered)
    else: st.info("Missing Module")