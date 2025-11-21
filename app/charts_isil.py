import streamlit as st
import plotly.express as px
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler

def render_z_charts(df: pd.DataFrame):
    st.markdown("### Risk and Patterns")

    st.markdown("#### 1. Risk Heatmap: Tenure vs. Monthly Charges")
    st.caption("This heatmap shows which customer profiles (based on Tenure and Charges) have the highest risk of churning.")

    df_heat = df.copy()
    
    df_heat["Monthly_Bin"] = pd.cut(df_heat["MonthlyCharges"], bins=range(0, 140, 10), right=False).astype(str)
    df_heat["tenure_bucket"] = pd.cut(df_heat["tenure"], bins=[0, 12, 24, 48, 1000], labels=["0-12 Months", "12-24 Months", "24-48 Months", "48+ Months"])

    heatmap_data = df_heat.groupby(["Monthly_Bin", "tenure_bucket"])["churn_probability"].mean().reset_index()
    heatmap_matrix = heatmap_data.pivot(index="Monthly_Bin", columns="tenure_bucket", values="churn_probability")
    
    fig1 = px.imshow(
        heatmap_matrix,
        labels=dict(x="Tenure", y="Monthly Charges ($)", color="Risk Probability"),
        x=heatmap_matrix.columns,
        y=heatmap_matrix.index,
        color_continuous_scale="RdYlGn_r",
        text_auto=".2f",
        aspect="auto"
    )
    fig1.update_layout(title_text="Mean Churn Risk Heatmap")
    st.plotly_chart(fig1, use_container_width=True)

    st.markdown("---")

    st.markdown("#### 2. Churn Probability Landscape")
    st.caption("Distribution based on customer payment habits. The color of the dots indicates the risk predicted by AI.")

    fig2 = px.scatter(
        df,
        x="MonthlyCharges",
        y="TotalCharges",
        color="churn_probability",
        color_continuous_scale="Jet",
        hover_data=["tenure", "Contract"],
        opacity=0.6,
        title="Monthly vs Total Charges (Color: Churn Probability)"
    )
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("---")

    st.markdown("#### 3. AI-Driven Customer Segments (K-Means)")
    st.caption("AI (K-Means) grouped customers into 4 main segments based on similar behaviors. The Radar Chart below shows the characteristics of these groups.")

    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    
    cluster_cols = ["tenure", "MonthlyCharges", "TotalCharges", "churn_probability"]
    df_cluster = df[cluster_cols].dropna()

    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    df_cluster["Cluster"] = kmeans.fit_predict(df_cluster)
    
    cluster_means = df_cluster.groupby("Cluster").mean().reset_index()

    scaler = MinMaxScaler()
    cluster_means_scaled = cluster_means.copy()
    cluster_means_scaled[cluster_cols] = scaler.fit_transform(cluster_means[cluster_cols])

    df_melted = cluster_means_scaled.melt(id_vars="Cluster", var_name="Feature", value_name="Value")
    df_melted["Cluster"] = df_melted["Cluster"].astype(str)

    fig3 = px.line_polar(
        df_melted, 
        r="Value", 
        theta="Feature", 
        color="Cluster", 
        line_close=True,
        markers=True,
        title="Customer Segment Profiles (Normalized Values)"
    )
    fig3.update_traces(fill='toself')
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("**Actual Cluster Means:**")
    st.dataframe(cluster_means.style.format("{:.2f}"))