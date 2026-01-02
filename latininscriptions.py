import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Latin Inscriptions Dashboard",
    page_icon="📜",
    layout="wide"
)

# Custom CSS for better look
st.markdown("""
    <style>
    .main {background-color: #f5f5f5;}
    .stMetric {background-color: white; padding: 15px; border-radius: 5px;}
    </style>
    """, unsafe_allow_html=True)

# Load data with error handling
@st.cache_data
def load_data():
    try:
        # Try to load your data - adjust the filename if needed!
        data = pd.read_csv("inscriptions_data.csv")
        return data
    except FileNotFoundError:
        st.error("⚠️ Data file not found! Please make sure 'inscriptions_data.csv' is in the same folder.")
        return None
    except Exception as e:
        st.error(f"⚠️ Error loading data: {e}")
        return None

# Load data
data = load_data()

# Only proceed if data loaded successfully
if data is not None:
    
    # Sidebar
    st.sidebar.title("📜 Navigation")
    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Choose a page:",
        ["🏠 Overview", "🔍 Search", "📊 Statistics", "ℹ️ About"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("**Data Source:**\nLatin Inscriptions from Zenodo")
    
    # ============================================
    # OVERVIEW PAGE
    # ============================================
    if page == "🏠 Overview":
        st.title("📜 Latin Inscriptions Dashboard")
        st.markdown("### Explore ancient Latin inscriptions and their linguistic features")
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="📖 Total Inscriptions",
                value=f"{len(data):,}"
            )
        
        with col2:
            if 'person_id' in data.columns:
                st.metric(
                    label="👥 Unique People",
                    value=f"{data['person_id'].nunique():,}"
                )
            else:
                st.metric(label="👥 Unique People", value="N/A")
        
        with col3:
            if 'year' in data.columns:
                year_range = f"{int(data['year'].min())} - {int(data['year'].max())}"
                st.metric(label="📅 Time Span", value=year_range)
            else:
                st.metric(label="📅 Time Span", value="N/A")
        
        with col4:
            if 'gender' in data.columns:
                most_common = data['gender'].mode()[0] if len(data['gender'].mode()) > 0 else "N/A"
                st.metric(label="⚧ Most Common Gender", value=most_common)
            else:
                st.metric(label="⚧ Gender Data", value="N/A")
        
        st.markdown("---")
        
        # Show first few columns of data
        st.subheader("📋 Data Preview")
        st.dataframe(data.head(100), use_container_width=True)
        
        # Show available columns
        with st.expander("🔍 Click to see all available data columns"):
            st.write("Your dataset contains these columns:")
            cols_df = pd.DataFrame({
                'Column Name': data.columns,
                'Data Type': data.dtypes.astype(str),
                'Non-Null Count': data.count().values
            })
            st.dataframe(cols_df, use_container_width=True)
        
        # Timeline if year column exists
        if 'year' in data.columns:
            st.markdown("---")
            st.subheader("📈 Timeline of Inscriptions")
            
            fig = px.histogram(
                data,
                x="year",
                title="Distribution of Inscriptions Over Time",
                labels={'year': 'Year', 'count': 'Number of Inscriptions'},
                color_discrete_sequence=['#3498db']
            )
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Count",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # ============================================
    # SEARCH PAGE
    # ============================================
    elif page == "🔍 Search":
        st.title("🔍 Search Inscriptions")
        st.markdown("Filter and explore the inscription database")
        
        # Search filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_text = st.text_input("🔤 Search any text:", "")
        
        with col2:
            if 'gender' in data.columns:
                genders = ["All"] + sorted(data['gender'].dropna().unique().tolist())
                gender_filter = st.selectbox("⚧ Gender:", genders)
            else:
                gender_filter = "All"
        
        with col3:
            if 'age_category' in data.columns:
                ages = ["All"] + sorted(data['age_category'].dropna().unique().tolist())
                age_filter = st.selectbox("👶 Age Category:", ages)
            else:
                age_filter = "All"
        
        # Apply filters
        filtered_data = data.copy()
        
        if search_text:
            # Search across all text columns
            mask = filtered_data.astype(str).apply(
                lambda row: row.str.contains(search_text, case=False, na=False).any(),
                axis=1
            )
            filtered_data = filtered_data[mask]
        
        if gender_filter != "All" and 'gender' in data.columns:
            filtered_data = filtered_data[filtered_data['gender'] == gender_filter]
        
        if age_filter != "All" and 'age_category' in data.columns:
            filtered_data = filtered_data[filtered_data['age_category'] == age_filter]
        
        # Results
        st.markdown("---")
        st.info(f"📊 Found **{len(filtered_data):,}** results out of {len(data):,} total inscriptions")
        
        if len(filtered_data) > 0:
            st.dataframe(filtered_data, use_container_width=True, height=600)
            
            # Download button
            csv = filtered_data.to_csv(index=False)
            st.download_button(
                label="⬇️ Download Results as CSV",
                data=csv,
                file_name="filtered_inscriptions.csv",
                mime="text/csv"
            )
        else:
            st.warning("No results found. Try adjusting your filters.")
    
    # ============================================
    # STATISTICS PAGE
    # ============================================
    elif page == "📊 Statistics":
        st.title("📊 Statistical Analysis")
        
        tab1, tab2, tab3 = st.tabs(["📈 Demographics", "🔤 Linguistic", "📍 Geographic"])
        
        with tab1:
            st.subheader("Demographic Statistics")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if 'gender' in data.columns:
                    st.markdown("#### Gender Distribution")
                    gender_counts = data['gender'].value_counts()
                    fig = px.pie(
                        values=gender_counts.values,
                        names=gender_counts.index,
                        title="Gender Distribution",
                        color_discrete_sequence=px.colors.qualitative.Set3
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No gender data available")
            
            with col2:
                if 'age_category' in data.columns:
                    st.markdown("#### Age Categories")
                    age_counts = data['age_category'].value_counts().sort_index()
                    fig = px.bar(
                        x=age_counts.index,
                        y=age_counts.values,
                        title="Age Category Distribution",
                        labels={'x': 'Age Category', 'y': 'Count'},
                        color_discrete_sequence=['#e74c3c']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No age data available")
        
        with tab2:
            st.subheader("Linguistic Features")
            
            if 'case' in data.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Grammatical Cases")
                    case_counts = data['case'].value_counts()
                    fig = px.bar(
                        x=case_counts.index,
                        y=case_counts.values,
                        title="Distribution of Grammatical Cases",
                        color_discrete_sequence=['#9b59b6']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Show case distribution table
                    st.markdown("#### Case Statistics")
                    case_df = pd.DataFrame({
                        'Case': case_counts.index,
                        'Count': case_counts.values,
                        'Percentage': (case_counts.values / len(data) * 100).round(2)
                    })
                    st.dataframe(case_df, use_container_width=True)
            else:
                st.info("No linguistic case data available")
        
        with tab3:
            st.subheader("Geographic Distribution")
            st.info("Geographic visualization would go here if location data is available")
            
            # Show any location-related columns if they exist
            location_cols = [col for col in data.columns if any(word in col.lower() for word in ['location', 'place', 'region', 'city'])]
            if location_cols:
                st.write("Available location fields:", location_cols)
                for col in location_cols:
                    st.write(f"**{col}:** {data[col].nunique()} unique values")
    
    # ============================================
    # ABOUT PAGE
    # ============================================
    elif page == "ℹ️ About":
        st.title("ℹ️ About This Dashboard")
        
        st.markdown("""
        ### Latin Inscriptions Explorer
        
        This dashboard allows you to explore and analyze ancient Latin inscriptions
        with their linguistic and demographic features.
        
        #### 📚 Data Sources
        - [Zenodo Dataset 10473706](https://zenodo.org/records/10473706)
        - [Zenodo Dataset 8431452](https://zenodo.org/records/8431452)
        
        #### 🔧 Technology Stack
        - **Python** for data processing
        - **Streamlit** for web interface
        - **Plotly** for interactive visualizations
        - **Pandas** for data manipulation
        
        #### 📊 Features
        - Real-time search and filtering
        - Interactive visualizations
        - Statistical analysis
        - Data export capabilities
        
        #### 👩‍💻 Development
        Built with love for digital humanities and classical studies.
        
        ---
        
        **Dataset Information:**
        """)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Records", f"{len(data):,}")
            st.metric("Columns", len(data.columns))
        with col2:
            st.metric("Memory Usage", f"{data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
            st.metric("Date Range", "Ancient Rome" if 'year' not in data.columns else f"{int(data['year'].min())} - {int(data['year'].max())}")

else:
    st.error("❌ Could not load data. Please check the data file location.")
    st.info("""
    ### How to fix this:
    
    1. Make sure your CSV file is in the same folder as this app.py file
    2. The file should be named `inscriptions_data.csv`
    3. Or update the filename in the code to match your actual file name
    
    **Current working directory:** You're running the app from wherever you opened Terminal.
    """)
