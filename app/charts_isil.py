import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

def render_z_charts(df: pd.DataFrame):
    # 1. css
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;500;700&display=swap');
    div[data-testid="stMetric"] {
        background-color: #161B22;
        border-left: 4px solid #FF0055;
        color: #E0E0E0;
    }
    h3, h4 { color: #FF0055 !important; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)
    if df.empty:
        st.warning("nothing to show, please enable some filters.")
        return
    

    st.markdown("### 🤖 Z: AI Risk & Pattern Analysis")
    
    if df is None or df.empty:
        st.warning("Insufficient data for analysis.")
        return

    # Numeric conversions
    cols_to_numeric = ['TotalCharges', 'MonthlyCharges', 'tenure', 'churn_probability']
    for col in cols_to_numeric:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=cols_to_numeric)

    # ---------------------------------------------------------
    # 1. HEATMAP (Interactive Binning)
    # ---------------------------------------------------------
    st.markdown("#### 1. Risk Heatmap: Tenure vs. MonthlyCharges")
    st.caption("Dark red areas indicate the highest churn risk. Analyze the density of segments.")

    # Interactive: Bin Size
    col_opt1, col_opt2 = st.columns([1, 3])
    with col_opt1:
        bin_size = st.select_slider("Bin Size (MonthlyCharges)", options=[5, 10, 20, 25], value=10)
    
    df_heat = df.copy()
    
    # Binning Process
    df_heat["Monthly_Bin"] = pd.cut(df_heat["MonthlyCharges"], bins=range(0, 150, bin_size), right=False)
    df_heat["tenure_bucket"] = pd.cut(df_heat["tenure"], bins=[0, 12, 24, 48, 1000], labels=["0-12 Mo", "12-24 Mo", "24-48 Mo", "48+ Mo"])

    heatmap_data = df_heat.groupby(["Monthly_Bin", "tenure_bucket"])["churn_probability"].mean().reset_index()
    
    # Pivot and Sort
    heatmap_matrix = heatmap_data.pivot(index="Monthly_Bin", columns="tenure_bucket", values="churn_probability")
    heatmap_matrix = heatmap_matrix.sort_index(ascending=False) # High charges on top
    
    # Convert Index to string for visualization
    heatmap_matrix.index = heatmap_matrix.index.astype(str)

    fig1 = px.imshow(
        heatmap_matrix,
        labels=dict(x="tenure_bucket", y="Monthly_Bin", color="churn_probability"),
        x=heatmap_matrix.columns,
        y=heatmap_matrix.index,
        
        color_continuous_scale="RdYlGn_r", 
        
        text_auto=".0%", 
        aspect="auto"
    )
    fig1.update_layout(
        title_text="",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        height=400
    )
    st.plotly_chart(fig1, use_container_width=True)
    # ---------------------------------------------------------
    # 2. SCATTER PLOT (Filter: Risk Threshold)
    # ---------------------------------------------------------
    st.markdown("#### 2. High Risk Radar (Alarm Level)")
    st.caption("Identify customers requiring immediate intervention based on predicted risk.")

    # Slider: Risk Threshold
    risk_threshold = st.slider(
        "🚨 Alarm Level (Risk Ratio %)", 
        min_value=0, max_value=90, value=0, step=5, # Varsayılanı 0 yaptık ki ilk açılışta hepsi görünsün
        help="Example: If you select 80, only customers with >= 80% churn risk will be displayed."
    )
    
    # Filtering
    risk_mask = (df["churn_probability"] * 100) >= risk_threshold
    filtered_df = df[risk_mask]

    if not filtered_df.empty:
        fig2 = px.scatter(
            filtered_df,
            x="MonthlyCharges",
            y="TotalCharges",
            color="churn_probability",
            
            color_continuous_scale="Portland", 
            range_color=[0, 1], # 0mavi, 1 kırmızı            
            size="churn_probability", 
            size_max=12,
            hover_data=["tenure", "Contract", "InternetService"],
            opacity=0.8,
            labels={"churn_probability": "Risk Score"})
        
        fig2.update_layout(
            title=f"{len(filtered_df)} Customers Found with Risk >= {risk_threshold}%",
            plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color="white"),
            xaxis=dict(showgrid=True, gridcolor='#333', title="MonthlyCharges"),
            yaxis=dict(showgrid=True, gridcolor='#333', title="TotalCharges"),
            height=450 )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning(f"No customers found above {risk_threshold}% risk level (Good news!).")

    # 3. AI SEGMENTS (Dual View: Radar & Bar)
    st.markdown("#### 3. AI-Driven Customer Segments (Dual Analysis)")
    st.caption("Compare behavioral DNA using Radar (Shape) and Bar (Magnitude) charts side-by-side.")

    # K-Means 
    cluster_cols = ["tenure", "MonthlyCharges", "TotalCharges", "churn_probability"]
    df_cluster = df[cluster_cols].dropna()

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df_cluster["Cluster"] = kmeans.fit_predict(df_cluster)
    
    cluster_means = df_cluster.groupby("Cluster").mean().reset_index()

    scaler = MinMaxScaler()
    cluster_means_scaled = cluster_means.copy()
    cluster_means_scaled[cluster_cols] = scaler.fit_transform(cluster_means[cluster_cols])

    df_melted = cluster_means_scaled.melt(id_vars="Cluster", var_name="Feature", value_name="Normalized_Value")
    df_melted["Cluster"] = df_melted["Cluster"].apply(lambda x: f"Cluster {x}")

    # ınteractive Selection
    all_clusters = sorted(df_melted["Cluster"].unique())
    selected_clusters = st.multiselect(
        "Select Segments to Compare", 
        all_clusters, 
        default=all_clusters[:2] )

    if selected_clusters:
        df_filtered = df_melted[df_melted["Cluster"].isin(selected_clusters)]
        
        common_color_sequence = px.colors.qualitative.Bold

        # EKRANI İKİYE BÖLME
        col_radar, col_bar = st.columns(2)

        # SOL: RADAR CHART 
        with col_radar:
            st.markdown("**Shape Analysis (Radar)**")
            fig_radar = px.line_polar(
                df_filtered, 
                r="Normalized_Value", 
                theta="Feature", 
                color="Cluster", 
                line_close=True,
                markers=True,
                color_discrete_sequence=common_color_sequence, # Aynı renk paleti
                range_r=[0, 1] # Sabit ölçek
            )
            fig_radar.update_traces(fill='toself', opacity=0.3)
            fig_radar.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True, showticklabels=False, gridcolor="#444"),
                    angularaxis=dict(gridcolor="#444", tickfont=dict(color="white"))
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="white"),
                legend=dict(orientation="h", y=-0.2), # Legend altta
                height=400,
                margin=dict(l=40, r=40, t=20, b=20)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        # SAĞ: BAR CHART 
        with col_bar:
            st.markdown("**Magnitude Analysis (Bar)**")
            fig_bar = px.bar(
                df_filtered, 
                x="Feature", 
                y="Normalized_Value", 
                color="Cluster", 
                barmode="group",
                text_auto=".2f",
                color_discrete_sequence=common_color_sequence # Aynı renk paleti
            )
            
            fig_bar.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color="white"),
                xaxis=dict(showgrid=False, title=""),
                yaxis=dict(showgrid=True, gridcolor='#333', title="Scale (0-1)", range=[0, 1]),
                legend=dict(orientation="h", y=-0.2), # Legend altta
                height=400,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    else:
        st.info("Please select at least one segment to view the chart.")

    # data Table
    with st.expander("View Actual Cluster Means (Real Values)"):
        st.dataframe(cluster_means.style.format("{:.2f}").background_gradient(cmap="Reds"))