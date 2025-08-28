import streamlit as st
import pandas as pd
import plotly.express as px

# Page config
st.set_page_config(page_title="Ambition Box Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    return pd.read_csv('merged.csv')

df = load_data()

# Title
st.title("🏢 Company Dashboard")

# Sidebar filters
st.sidebar.header("Filters")

location = st.sidebar.selectbox(
    "Location", 
    ["All"] + sorted(df['location'].unique().tolist())
)

industry = st.sidebar.selectbox(
    "Industry",
    ["All"] + sorted(df['industry'].unique().tolist())
)

company_type = st.sidebar.selectbox(
    "Type",
    ["All"] + sorted(df['type'].unique().tolist())
)

rating_filter = st.sidebar.slider(
    "Minimum Rating",
    min_value=0.0,
    max_value=5.0,
    value=0.0,
    step=0.1
)

# Filter data
filtered_df = df.copy()

if location != "All":
    filtered_df = filtered_df[filtered_df['location'] == location]
    
if industry != "All":
    filtered_df = filtered_df[filtered_df['industry'] == industry]
    
if company_type != "All":
    filtered_df = filtered_df[filtered_df['type'] == company_type]

if rating_filter > 0:
    filtered_df = filtered_df[filtered_df['company_rating'] >= rating_filter]

# Display metrics
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Companies", len(filtered_df))
with col2:
    st.metric("Average Rating", f"{filtered_df['company_rating'].mean():.1f}")
with col3:
    st.metric("Top Rating", f"{filtered_df['company_rating'].max():.1f}")

# Charts
if len(filtered_df) > 0:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top 10 Companies by Rating")
        top_companies = filtered_df.nlargest(10, 'company_rating')
        fig1 = px.bar(
            top_companies, 
            x='company_rating', 
            y='company_name',
            orientation='h',
            color='company_rating',
            color_continuous_scale='viridis'
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("📊 Rating Distribution")
        fig2 = px.histogram(
            filtered_df, 
            x='company_rating',
            nbins=15,
            color_discrete_sequence=['#667eea']
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    col3, col4 = st.columns(2)
    
    with col3:
        st.subheader("🏭 Companies by Industry")
        industry_counts = filtered_df['industry'].value_counts().head(8)
        fig3 = px.pie(
            values=industry_counts.values,
            names=industry_counts.index,
            hole=0.4
        )
        st.plotly_chart(fig3, use_container_width=True)
    
    with col4:
        st.subheader("🏢 Company Size Distribution")
        size_counts = filtered_df['size'].value_counts()
        fig4 = px.bar(
            x=size_counts.index,
            y=size_counts.values,
            color=size_counts.values,
            color_continuous_scale='plasma'
        )
        st.plotly_chart(fig4, use_container_width=True)
    
    # Data table
    st.subheader("📋 Company Data")
    st.dataframe(filtered_df, use_container_width=True)
    
else:
    st.warning("No data found matching your criteria.")