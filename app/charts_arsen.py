import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def render_y_charts(df: pd.DataFrame): #Benim (arsen) plotlarımın olduğu fonksiyon
    
    if df.empty: #tüm filtrelerin kapalı olduğu durum için
        st.warning("Nothing to show, please enable some filters.")
        return

    st.markdown("### 🔄 Y - Segmentation")
    st.markdown("This part inspects the hierarchical distribution of customer groups, based on Churn, Customer type, and Spending,\
                 to reveal which segments contribute most to revenue and which are at higher risk of cancellation.")
    st.markdown("---")

    
    st.subheader("1. Churn Distribution ")
    st.caption("This treemap shows the categorization of customer churn amounts and percentages by some categories , Customers are first grouped by their \
               Internet Service Type, then they are further divided by their respective payment method and finally grouped by whether they churn or not.")
    
    #treemap grafiği

    df_treemap = df.copy()
    df_treemap['World'] = 'All Customers' #tüm verileri çekip world olarak kaydediyoruz
    
    service_colors = { #renk bilgileri
        'All Customers': 'rgba(0,0,0,0)', 
        'Fiber optic': '#3B82F6',          
        'DSL': '#F97316',                  
        'No Service': '#10B981',
        '(?)': '#6B7280'
    }
    
    fig_treemap = px.treemap( #treemap objesini bu parametrelerle oluşturuyoruz
        df_treemap, 
        path=['World', 'InternetService', 'PaymentMethod', 'Churn'],
        color='InternetService', 
        color_discrete_map=service_colors,
    )

    fig_treemap.update_layout(  #graphın sayfadaki yerine, özelliklerine ait parametreler
        height=750,
        margin=dict(t=65, l=10, r=10, b=10),
        title=dict(
            text="Churn Distribution w.r.t. Internet Service Type and Payment Method",
            y=0.98, x=0, xanchor='left', yanchor='top',
            font=dict(size=24), pad=dict(b=20) 
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", size=15, color="white"),
        hoverlabel=dict(bgcolor="white", font_size=14, font_family="Inter, sans-serif", font=dict(color="black"))
    )
    
    fig_treemap.update_traces( #trace bilgileri
        textinfo="label+value+percent parent", 
        root_color="rgba(0,0,0,0)",
        pathbar=dict(visible=True, textfont=dict(family="Inter, sans-serif", size=15, color="white")),
        marker=dict(line=dict(width=2, color='black')),
        hovertemplate='<b>%{label}</b><br>Customer Count: %{value}<br>Group Percantage: %{percentParent:.1%}<extra></extra>'
    )
    
    st.plotly_chart(fig_treemap, use_container_width=True) #display the chart
    
    st.markdown("---")

    #faceted histogram

    st.subheader("2. Customer Distribution")
    st.caption("This faceted histogram shows the distribution of customers with respect to the tenure parameter. The data is faceted by Iternet Service\
               Type and Churn, meaning we can further inspect the customer distributon w.r.t. these two parameters simultaniously.")

    fig_hist = px.histogram( #initialization parametreleri
        df, 
        x="tenure", 
        color="Churn", 
        facet_row="Churn",
        facet_col="InternetService", 
        nbins=50, 
        
        facet_row_spacing=0.12, 
        facet_col_spacing=0.05, 
        
        color_discrete_map={'Yes': '#EF553B', 'No': '#00CC96'},
        title="Customer Distribution w.r.t Tenure faceted by Internet Service Type and Churn.",
        category_orders={
            "InternetService": ["DSL", "Fiber optic", "No Service"],
            "Churn": ["Yes", "No"]
        }
    )
    
    fig_hist.update_layout( #sayfa konumu ayarlanması
        height=750, 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white"),
        
        # Ortak Eksen Başlıkları (Korundu)
        xaxis_title="tenure", 
        yaxis_title="count",
        
        bargap=0.15, 
        margin=dict(t=80, b=100, l=80, r=60),
        
        showlegend=False # legendi kapıyoruz çünkü zaten churn durumunu eksende belirttik
    )
    
    # y eksenleri: bağımsız
    fig_hist.update_yaxes(matches=None, showticklabels=True)
    
    # x eksenleri: ortak
    fig_hist.update_xaxes(matches='x')
    
    # facet başlıklarını temizliyoruz ki yandaki şekilde çıkmasın ("InternetService=DSL" -> "DSL")
    fig_hist.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    
    st.plotly_chart(fig_hist, use_container_width=True) #plotu gösteriyoruz

    st.markdown("---")

    #strip plot

    st.subheader("3. Spending Distribution")
    st.caption("This strip plot shows the distribution of charges, both monthly and total. Customers are grouped into six types based on whether or not they churn and their contract type\
               . Then based on their charges they are placed into the plot.")
    
    #total chargeları Na değerleri 0 yaparak ayıklıyoruz, hala kaldıysa tabi çünkü processed datayı kullanıyoruz

    df_strip = df.copy()
    df_strip['TotalCharges'] = pd.to_numeric(df_strip['TotalCharges'], errors='coerce').fillna(0)
    
    #striplerin indelenmesi
    contract_base = {'Month-to-month': 0, 'One year': 3, 'Two year': 6}
    churn_offset = {'Yes': 0, 'No': 1} 
    
    df_strip['x_pos'] = df_strip.apply(lambda row: contract_base[row['Contract']] + churn_offset[row['Churn']], axis=1)

    #jitter için random bir seed seçiyoruz
    np.random.seed(42)
    df_strip['x_jittered'] = df_strip['x_pos'] + np.random.uniform(-0.25, 0.25, size=len(df_strip))

    #churn yes veya churn noya göre filtreleme

    df_yes = df_strip[df_strip['Churn'] == 'Yes']
    df_no = df_strip[df_strip['Churn'] == 'No']

    #figürü yaratıp trace ve layoutlarını yukarda yaptığımız gibi ayarlıyoruz

    fig_combined = go.Figure()

    fig_combined.add_trace(go.Scatter(
        x=df_yes['x_jittered'],
        y=df_yes['MonthlyCharges'],
        mode='markers',
        name='Churn',
        marker=dict(
            size=6,
            color=df_yes['TotalCharges'], 
            colorscale=[[0, "#ffa1a0"], [1, "#CE0000"]],            
            opacity=0.8,
            showscale=True,
            colorbar=dict(title="Total Charges (Churn)", x=1.05, len=0.5, y=0.8) 
        ),
        customdata=np.stack((df_yes['Contract'], df_yes['tenure']), axis=-1),
        hovertemplate='<b>%{customdata[0]} (Churn)</b><br>Monthly: $%{y}<br>Tenure: %{customdata[1]} Month<extra></extra>'
    ))

    fig_combined.add_trace(go.Scatter(
        x=df_no['x_jittered'],
        y=df_no['MonthlyCharges'],
        mode='markers',
        name='No Churn',
        marker=dict(
            size=6,
            color=df_no['TotalCharges'],  
            colorscale=[[0, "#bef0be"], [1, "#009500"]],            
            opacity=0.7,                  
            showscale=True,
            colorbar=dict(title="Total Charges (No Churn)", x=1.05, len=0.5, y=0.2) 
        ),
        customdata=np.stack((df_no['Contract'], df_no['tenure']), axis=-1),
        hovertemplate='<b>%{customdata[0]} (No Churn)</b><br>Monthly: $%{y}<br>Tenure: %{customdata[1]} Month<extra></extra>'
    ))

    fig_combined.update_layout(
        height=700, 
        title="Spending Distribution w.r.t Contract Type and Churn",
        margin=dict(t=80, l=50, r=50, b=80),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color="white", size=14),
        yaxis_title="Monthly Charges (Dollars)",
        xaxis_title="Contract Type and Churn Status",
        showlegend=False, 
        
        xaxis=dict(
            tickmode='array',
            tickvals=[0, 1, 3, 4, 6, 7],
            ticktext=[
                "Monthly<br>(Churn)", "Monthly<br>(No Churn)", 
                "One Year<br>(Churn)", "One Year<br>(No Churn)", 
                "Two Year<br>(Churn)", "Two Year<br>(No Churn)"
            ],
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False
        ),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
    )

    st.plotly_chart(fig_combined, use_container_width=True) #ve plotu gösteriyoruz