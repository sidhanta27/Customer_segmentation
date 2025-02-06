import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

# Load dataset
@st.cache_data
def load_data():
    path = "C:/Users/sidha/OneDrive/Desktop/project_X/Online Retail.xlsx"
    df = pd.read_excel(path)
    df = df.dropna(subset=['CustomerID'])
    df = df.drop_duplicates()
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format="%d-%m-%Y %H:%M")
    df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
    df = df[df['TotalAmount'] > 0]
    return df

df = load_data()

# RFM Calculation
latest_date = df['InvoiceDate'].max()
df['Recency'] = df.groupby('CustomerID')['InvoiceDate'].transform(lambda x: (latest_date - x.max()).days)
df['Frequency'] = df.groupby('CustomerID')['InvoiceNo'].transform('nunique')
df['Monetary'] = df.groupby('CustomerID')['TotalAmount'].transform('sum')
rfm = df[['CustomerID', 'Recency', 'Frequency', 'Monetary']].drop_duplicates()

# Segment Customers
r_labels = range(4, 0, -1)
f_labels = range(1, 5)
m_labels = range(1, 5)

rfm['R_Quartile'] = pd.qcut(rfm['Recency'], q=4, labels=r_labels)
rfm['F_Quartile'] = pd.cut(df['Frequency'], bins=4, labels=f_labels, include_lowest=True)
rfm['M_Quartile'] = pd.qcut(rfm['Monetary'], q=4, labels=m_labels)
rfm['RFM_Score'] = rfm['R_Quartile'].astype(int) + rfm['F_Quartile'].astype(int) + rfm['M_Quartile'].astype(int)

def segment_customer(rfm_score):
    if rfm_score >= 10:
        return 'Gold'
    elif 6 <= rfm_score < 10:
        return 'Silver'
    else:
        return 'Bronze'

rfm['Segment'] = rfm['RFM_Score'].apply(segment_customer)

# Product Recommendation based on past purchases
def recommend_products(customer_id):
    customer_segment = rfm.loc[rfm['CustomerID'] == customer_id, 'Segment'].values
    if len(customer_segment) == 0:
        return "Customer not found."
    
    segment = customer_segment[0]
    segment_customers = rfm[rfm['Segment'] == segment]['CustomerID']
    segment_products = df[df['CustomerID'].isin(segment_customers)]['Description'].value_counts().head(5)
    return segment_products.index.tolist()

# Streamlit UI
st.title("Product Recommendation System")
customer_id = st.number_input("Enter Customer ID:", min_value=1, step=1)

if st.button("Recommend Products"):
    recommendations = recommend_products(customer_id)
    st.write("Recommended Products:")
    if isinstance(recommendations, list):
        for product in recommendations:
            st.write(f"- {product}")
    else:
        st.write(recommendations)
