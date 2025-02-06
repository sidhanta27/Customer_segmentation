import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from wordcloud import WordCloud

# Read and process the dataset
path="C:/Users/sidha/OneDrive/Desktop/project_X/Online Retail.xlsx"
df = pd.read_excel(path)
df = df.dropna(subset=['CustomerID'])
df = df.drop_duplicates()

# Data Cleaning and Preprocessing
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'], format="%d-%m-%Y %H:%M")
df['Month'] = df['InvoiceDate'].dt.month
df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
df = df[df['TotalAmount'] > 0]

# Calculate RFM
latest_date = df['InvoiceDate'].max()
df['Recency'] = df.groupby('CustomerID')['InvoiceDate'].transform(lambda x: (latest_date - x.max()).days)
df['Frequency'] = df.groupby('CustomerID')['InvoiceNo'].transform('nunique')
df['Monetary'] = df.groupby('CustomerID')['TotalAmount'].transform('sum')

# Create RFM DataFrame
rfm = df[['CustomerID', 'Recency', 'Frequency', 'Monetary']].drop_duplicates()

# Define quartile labels
r_labels = range(4, 0, -1)
f_labels = range(1, 5)
m_labels = range(1, 5)

df['R_Quartile'] = pd.qcut(df['Recency'], q=4, labels=r_labels)
df['F_Quartile'] = pd.cut(df['Frequency'], bins=4, labels=f_labels, include_lowest=True)
df['M_Quartile'] = pd.qcut(df['Monetary'], q=4, labels=m_labels)

# Combine RFM scores
df['RFM_Score'] = df['R_Quartile'].astype(str) + df['F_Quartile'].astype(str) + df['M_Quartile'].astype(str)

# Define Customer Segments
def segments(df):
    if df['RFM_Score'] > 9:
        return 'Gold'
    elif (df['RFM_Score'] > 5) and (df['RFM_Score'] <= 9):
        return 'Silver'
    else:
        return 'Bronze'

# Calculate RFM_Score numerically by converting quartiles to integers
df['RFM_Score'] = df['R_Quartile'].astype(int) + df['F_Quartile'].astype(int) + df['M_Quartile'].astype(int)

# Apply the segmentation function
df['General_Segment'] = df.apply(segments, axis=1)

# Streamlit UI
st.title('Customer Loyalty Program')

# Display customer segments
st.subheader('Customer Segmentation')
segment_counts = df['General_Segment'].value_counts()
st.bar_chart(segment_counts)

# Show Customer Loyalty Program Insights
st.subheader('Customer Insights')
customer_id = st.selectbox('Select Customer ID:', df['CustomerID'].unique())
customer_data = df[df['CustomerID'] == customer_id].iloc[0]

st.write(f"**Customer ID**: {customer_id}")
st.write(f"**Recency**: {customer_data['Recency']} days")
st.write(f"**Frequency**: {customer_data['Frequency']} purchases")
st.write(f"**Monetary**: £{customer_data['Monetary']:,.2f}")
st.write(f"**Segment**: {customer_data['General_Segment']}")

# Display Loyalty Points Based on RFM
loyalty_points = 0
if customer_data['General_Segment'] == 'Gold':
    loyalty_points = customer_data['Monetary'] * 0.1  # 10% of monetary value
elif customer_data['General_Segment'] == 'Silver':
    loyalty_points = customer_data['Monetary'] * 0.05  # 5% of monetary value
else:
    loyalty_points = customer_data['Monetary'] * 0.02  # 2% of monetary value

st.write(f"**Loyalty Points Awarded**: {loyalty_points:,.2f} points")

# Wordcloud Visualization of Product Descriptions
st.subheader('Word Cloud of Product Descriptions')
text = ' '.join(df['Description'].dropna())
wordcloud = WordCloud(background_color='white', width=800, height=800, max_words=30).generate(text)
plt.figure(figsize=(8, 8))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
st.pyplot(plt)

# Segment Characteristics (Heatmap)
st.subheader('Segment Characteristics')
fig, ax = plt.subplots(figsize=(8, 5))
sns.heatmap(df.groupby('General_Segment').agg({'Recency': 'mean', 'Frequency': 'mean', 'Monetary': 'mean'}),
            annot=True, fmt=".2f", cmap="YlGnBu", ax=ax)
st.pyplot(fig)

# Extra: Allow adjusting thresholds for loyalty points calculation (optional)
st.subheader('Adjust Loyalty Points Thresholds')
gold_multiplier = st.slider('Gold Multiplier', 0.01, 0.2, 0.1, step=0.01)
silver_multiplier = st.slider('Silver Multiplier', 0.01, 0.1, 0.05, step=0.01)
bronze_multiplier = st.slider('Bronze Multiplier', 0.01, 0.05, 0.02, step=0.01)

# Recalculate loyalty points with new multipliers
if customer_data['General_Segment'] == 'Gold':
    loyalty_points = customer_data['Monetary'] * gold_multiplier
elif customer_data['General_Segment'] == 'Silver':
    loyalty_points = customer_data['Monetary'] * silver_multiplier
else:
    loyalty_points = customer_data['Monetary'] * bronze_multiplier

st.write(f"**Updated Loyalty Points Awarded**: {loyalty_points:,.2f} points")
