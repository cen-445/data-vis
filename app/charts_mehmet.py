import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

def map_categorical_values(df):
    """Converts data to readable labels."""
    df_mapped = df.copy()
    
    mappings = {
        'Contract': {0: 'Month-to-month', 1: 'One year', 2: 'Two year'},
        'InternetService': {0: 'DSL', 1: 'Fiber optic', 2: 'No'},
        'Churn': {0: 'No', 1: 'Yes'},
        'SeniorCitizen': {0: 'Non-Senior', 1: 'Senior'}
    }
    
    for col, mapping in mappings.items():
        if col in df_mapped.columns and pd.api.types.is_numeric_dtype(df_mapped[col]):
            df_mapped[col] = df_mapped[col].map(mapping).fillna(df_mapped[col])
        elif col in df_mapped.columns:
            df_mapped[col] = df_mapped[col].astype(str)

    cols_to_str = ['PaymentMethod', 'TechSupport', 'OnlineSecurity', 'StreamingTV', 'DeviceProtection', 'PaperlessBilling', 'Partner']
    for col in cols_to_str:
        if col in df_mapped.columns:
            df_mapped[col] = df_mapped[col].astype(str)

    return df_mapped

def calculate_retention(df, group_col, metric_type='retention'):
    """Calculates Survival or Hazard Rate."""
    if df.empty: return [], []

    max_tenure = int(df['tenure'].max()) if 'tenure' in df.columns else 72
    x_axis = np.arange(1, max_tenure + 1)
    traces = []
    colors = ['#00F2EA', '#FF0055', '#FFD700', '#333333'] 
    
    if group_col in df.columns:
        groups = df[group_col].unique()
        for idx, group in enumerate(groups):
            sub_df = df[df[group_col] == group]
            total_users = len(sub_df)
            if total_users == 0: continue
            
            y_data = []
            if metric_type == 'retention':
                for t in x_axis:
                    remaining = len(sub_df[sub_df['tenure'] > t])
                    y_data.append((remaining / total_users) * 100)
                fill_opt = 'tozeroy'
            else:
                for t in x_axis:
                    at_risk = len(sub_df[sub_df['tenure'] >= t])
                    churned_at_t = len(sub_df[(sub_df['tenure'] == t) & (sub_df['Churn'].isin(['Yes', '1']))])
                    
                    if at_risk > 0:
                        rate = (churned_at_t / at_risk) * 100
                    else:
                        rate = 0
                    y_data.append(rate)
                fill_opt = 'none'
            
            traces.append(go.Scatter(
                x=x_axis, y=y_data, 
                mode='lines+markers', 
                name=str(group),
                line=dict(width=3, color=colors[idx % len(colors)], shape='spline'),
                marker=dict(size=4, line=dict(width=1, color='white')),
                fill=fill_opt, 
                fillcolor=f"rgba({int(colors[idx%len(colors)][1:3],16)}, {int(colors[idx%len(colors)][3:5],16)}, {int(colors[idx%len(colors)][5:7],16)}, 0.1)" if fill_opt != 'none' else None,
                hovertemplate=f"<b>{group}</b><br>Month: %{{x}}<br>{'Retention' if metric_type=='retention' else 'Risk'}: %%{{y:.1f}}<extra></extra>"
            ))
    return traces, x_axis

def render_x_charts(df_input: pd.DataFrame):
    
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Exo+2:wght@300;500;700&display=swap');
    html, body, [class*="css"] { font-family: 'Exo 2', sans-serif; }
    
    div[data-testid="stMetric"] {
        background-color: #f0f2f6; 
        padding: 15px; border-radius: 8px;
        border-left: 4px solid #00F2EA; 
        color: black;
    }
    label[data-testid="stMetricLabel"] {color: #555;}
    div[data-testid="stMetricValue"] {color: #000;}

    h1, h2, h3 { color: #00F2EA !important; font-weight: 700; }
    </style>
    """, unsafe_allow_html=True)

    if df_input is None or df_input.empty:
        st.warning("No data to display.")
        return

    df = map_categorical_values(df_input)
    cols_numeric = ['TotalCharges', 'MonthlyCharges', 'tenure']
    for col in cols_numeric:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce')

    st.markdown("## 📈 TELCO /// ALPHA TERMINAL")
    st.caption("Advanced Intelligence Module")
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Total Customers", f"{len(df):,}")
    with c2: st.metric("Avg Charge", f"${df['MonthlyCharges'].mean():.1f}" if 'MonthlyCharges' in df.columns else "$0")
    with c3: 
        churn_rate = (df[df['Churn'].isin(['Yes', 1])].shape[0] / len(df) * 100)
        st.metric("Churn Rate", f"%{churn_rate:.1f}")
    st.markdown("---")

    st.subheader("1. Retention Alpha Curve (Yearly Intervals)")
    
    valid_group_cols = [c for c in ['Contract', 'PaymentMethod', 'InternetService', 'TechSupport', 'OnlineSecurity', 'DeviceProtection'] if c in df.columns]
    
    c_ctrl1, c_ctrl2 = st.columns([1.5, 2.5])
    with c_ctrl1:
        group_col = st.selectbox("1. Segmentation Criteria:", valid_group_cols, index=valid_group_cols.index('InternetService') if 'InternetService' in valid_group_cols else 0)
    with c_ctrl2:
        view_mode = st.radio("2. View Mode:", 
                             ["Retention Curve (Cumulative Retention %)", "Churn Hazard Risk (Periodic Churn Risk %)"],
                             horizontal=True)
        
    metric_type = 'retention' if "Retention" in view_mode else 'hazard'
    traces, x_axis = calculate_retention(df, group_col, metric_type)
    
    if traces:
        fig1 = go.Figure(data=traces)
        
        max_val = int(df['tenure'].max()) if 'tenure' in df.columns else 72
        tick_vals = []
        tick_text = []
        
        for i in range(0, max_val, 12):
            start = i
            end = i + 12
            mid_point = start + 6 
            if mid_point > max_val: break
            
            tick_vals.append(mid_point)
            tick_text.append(f"{start}-{end} Months")

        fig1.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)", 
            height=400,
            xaxis=dict(
                title="Tenure Intervals", 
                tickmode='array',
                tickvals=tick_vals,
                ticktext=tick_text,
                showgrid=False,
                zeroline=False
            ),
            yaxis=dict(
                title="Retention Rate %", 
                showgrid=False,
                zeroline=False
            ),
            legend=dict(orientation="h", y=1.1)
        )
        st.plotly_chart(fig1, use_container_width=True)

    st.subheader("2. Payment Density & Contract Analysis (Interactive)")
    
    if all(c in df.columns for c in ["Contract", "MonthlyCharges", "Churn"]):
        
        fig2 = go.Figure()

        common_props = dict(
            meanline_visible=True,
            box_visible=True,
            width=1.2,
            points=False,
            opacity=0.8
        )

        fig2.add_trace(go.Violin(
            x=df['Contract'][df['Churn'] == 'No'],
            y=df['MonthlyCharges'][df['Churn'] == 'No'],
            legendgroup='No', scalegroup='No', name='No (Retained)',
            side='negative',
            line_color='#00F2EA', 
            fillcolor='rgba(0, 242, 234, 0.5)',
            **common_props
        ))
        
        fig2.add_trace(go.Violin(
            x=df['Contract'][df['Churn'] == 'Yes'],
            y=df['MonthlyCharges'][df['Churn'] == 'Yes'],
            legendgroup='Yes', scalegroup='Yes', name='Yes (Churn)',
            side='positive',
            line_color='#FF0055',
            fillcolor='rgba(255, 0, 85, 0.5)',
            **common_props
        ))

        fig2.update_layout(
            violingap=0, violinmode='overlay',
            template="plotly_white",
            paper_bgcolor="rgba(0,0,0,0)", 
            plot_bgcolor="rgba(0,0,0,0)",
            height=500,
            xaxis=dict(
                title="<b>Contract Type</b>",
                title_font=dict(size=14),
                showgrid=True, 
                gridcolor='rgba(0,0,0,0.05)'
            ),
            yaxis=dict(
                title="<b>Monthly Charges ($)</b>",
                title_font=dict(size=14),
                showgrid=True, 
                gridcolor='rgba(0,0,0,0.05)',
                zeroline=False
            ),
            legend=dict(
                orientation="h", 
                y=1.05, x=0.5, xanchor='center',
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='rgba(0,0,0,0.1)', borderwidth=1
            )
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Missing columns for Chart 2.")

    st.subheader("3. Customer Lifecycle Flow (Sankey)")
    
    col_sankey1, col_sankey2 = st.columns([1, 2])
    with col_sankey1:
        dimension = st.selectbox("Starting Criteria (Left Column):", 
                                ['Contract', 'InternetService', 'PaymentMethod', 'TechSupport'], 
                                index=0, key='sankey_dim')
    with col_sankey2:
        measure = st.radio("Measurement Metric (Flow Thickness):", 
                           ["Customer Count (Volume)", "Monthly Revenue ($ Revenue)"], 
                           horizontal=True, key='sankey_meas')

    required_cols_sankey = [dimension, 'tenure', 'Churn', 'MonthlyCharges']
    if all(c in df.columns for c in required_cols_sankey):
        try:
            bins = [0, 12, 24, 48, 72, 100]
            labels = ['0-1 Year', '1-2 Years', '2-4 Years', '4-6 Years', '6+ Years']
            df['TenureGroup'] = pd.cut(df['tenure'], bins=bins, labels=labels, right=False)
            
            sankey_df = df.dropna(subset=[dimension, 'TenureGroup', 'Churn']).copy()
            
            sankey_df['Source_lbl'] = sankey_df[dimension]
            sankey_df['Tenure_lbl'] = sankey_df['TenureGroup'].astype(str)
            sankey_df['Churn_lbl'] = sankey_df['Churn'].apply(lambda x: f"Churn: {x}")

            all_nodes = list(sankey_df['Source_lbl'].unique()) + \
                        list(sankey_df['Tenure_lbl'].unique()) + \
                        list(sankey_df['Churn_lbl'].unique())
            
            node_map = {v: i for i, v in enumerate(all_nodes)}

            links = {'source': [], 'target': [], 'value': [], 'customdata': []}

            def get_metric(sub_d):
                if "Revenue" in measure:
                    return sub_d['MonthlyCharges'].sum()
                return len(sub_d)

            g1 = sankey_df.groupby(['Source_lbl', 'Tenure_lbl'])
            for (src, target), sub_df in g1:
                val = get_metric(sub_df)
                if val > 0:
                    links['source'].append(node_map[src])
                    links['target'].append(node_map[target])
                    links['value'].append(val)
                    links['customdata'].append(f"{len(sub_df)} Customers<br>${sub_df['MonthlyCharges'].sum():,.0f}")

            g2 = sankey_df.groupby(['Tenure_lbl', 'Churn_lbl'])
            for (src, target), sub_df in g2:
                val = get_metric(sub_df)
                if val > 0:
                    links['source'].append(node_map[src])
                    links['target'].append(node_map[target])
                    links['value'].append(val)
                    links['customdata'].append(f"{len(sub_df)} Customers<br>${sub_df['MonthlyCharges'].sum():,.0f}")

            node_colors = []
            node_map_colors = {} 

            palette = {
                'Yes': "#FF0055", 'No': "#00F2EA", 
                'Month-to-month': "#FFD700", 'One year': "#00A8E8", 'Two year': "#44FF00",
                'DSL': "#FF9F1C", 'Fiber optic': "#D90429", 'No': "#888888",
                'Electronic check': "#B5179E", 'Mailed check': "#4CC9F0", 
                'Bank transfer (automatic)': "#4361EE", 'Credit card (automatic)': "#3A0CA3",
                '0-1 Year': "#9966FF", '1-2 Years': "#3366FF", '2-4 Years': "#00CC99", 
                '4-6 Years': "#FF9933", '6+ Years': "#FF3399"
            }

            for idx, node in enumerate(all_nodes):
                color = "#AAAAAA"
                for key, val in palette.items():
                    if key == node or (key in node and len(key) > 3):
                        color = val
                        break
                node_colors.append(color)
                node_map_colors[idx] = color

            link_colors = []
            for src_i in links['source']:
                c_hex = node_map_colors.get(src_i, "#888888")
                c_hex = c_hex.lstrip('#')
                rgb = tuple(int(c_hex[i:i+2], 16) for i in (0, 2, 4))
                link_colors.append(f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.4)")

            hovertemplate = "%{source.label} → %{target.label}<br>" + \
                            "<b>%{value:,.0f} " + ("$" if "Revenue" in measure else "Customers") + "</b><br>" + \
                            "Detail: %{customdata}<extra></extra>"

            fig3 = go.Figure(data=[go.Sankey(
                valueformat = ",.0f",
                valuesuffix = " $" if "Revenue" in measure else " Customers",
                node=dict(
                    pad=25, thickness=15,
                    line=dict(color="white", width=0.5),
                    label=all_nodes,
                    color=node_colors,
                    hovertemplate='%{label}<br>Total: %{value:,.0f}<extra></extra>'
                ),
                link=dict(
                    source=links['source'],
                    target=links['target'],
                    value=links['value'],
                    color=link_colors,
                    customdata=links['customdata'],
                    hovertemplate=hovertemplate
                )
            )])
            
            fig3.update_layout(
                title_text="", 
                font_size=13, 
                height=600,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig3, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating Sankey: {e}")
    else:
        st.info("Missing columns for Sankey chart.")
