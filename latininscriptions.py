import streamlit as st
import pandas as pd

# Configure the page
st.set_page_config(
    page_title="Latin Inscriptions Dashboard",
    page_icon="📜",
    layout="wide"
)

# Title
st.title("📜 Latin Inscriptions Dashboard")
st.markdown("---")

# Sidebar
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio("Choose a page:", ["🏠 Overview", "🔍 Search", "📊 Statistics"])

# Sample data creator (replace this with your real data later)
@st.cache_data
def load_sample_data():
    """Creates sample data - replace this with your actual data loading"""
    data = {
        'person_id': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'name': ['Marcus Aurelius', 'Julia Felix', 'Gaius Julius', 'Claudia Severa', 
                 'Titus Flavius', 'Cornelia Prima', 'Lucius Vorenus', 'Antonia Minor',
                 'Quintus Sertorius', 'Livia Drusilla'],
        'gender': ['Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female', 'Male', 'Female'],
        'age_category': ['Adult', 'Adult', 'Child', 'Adult', 'Elder', 'Adult', 'Adult', 'Elder', 'Adult', 'Adult'],
        'year': [120, 150, 80, 200, 170, 140, 90, 180, 110, 160],
        'case': ['Nominative', 'Genitive', 'Accusative', 'Dative', 'Nominative', 'Ablative', 'Nominative', 'Genitive', 'Dative', 'Nominative'],
        'inscription_type': ['Funerary', 'Honorary', 'Votive', 'Funerary', 'Building', 'Funerary', 'Military', 'Honorary', 'Votive', 'Funerary']
    }
    return pd.DataFrame(data)

# Load data
try:
    # Try to load your real data first
    data = pd.read_csv("inscriptions_data.csv")
    st.sidebar.success("✅ Real data loaded!")
except:
    # If it fails, use sample data
    data = load_sample_data()
    st.sidebar.warning("⚠️ Using sample data. Upload your CSV to see real data.")

# File uploader in sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("📁 Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
if uploaded_file is not None:
    data = pd.read_csv(uploaded_file)
    st.sidebar.success("✅ File uploaded successfully!")

# ========================================
# OVERVIEW PAGE
# ========================================
if page == "🏠 Overview":
    st.header("Overview")
    
    # Metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📚 Total Inscriptions",
            value=len(data)
        )
    
    with col2:
        st.metric(
            label="👥 Unique People",
            value=data['person_id'].nunique()
        )
    
    with col3:
        st.metric(
            label="👨 Male",
            value=len(data[data['gender'] == 'Male'])
        )
    
    with col4:
        st.metric(
            label="👩 Female",
            value=len(data[data['gender'] == 'Female'])
        )
    
    st.markdown("---")
    
    # Timeline (simple bar chart)
    st.subheader("📅 Inscriptions Over Time")
    year_counts = data['year'].value_counts().sort_index()
    st.bar_chart(year_counts)
    
    st.markdown("---")
    
    # Recent inscriptions table
    st.subheader("🆕 Recent Inscriptions")
    st.dataframe(
        data.sort_values('year', ascending=False).head(10),
        use_container_width=True,
        hide_index=True
    )

# ========================================
# SEARCH PAGE
# ========================================
elif page == "🔍 Search":
    st.header("Search Inscriptions")
    
    # Search filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        name_search = st.text_input("🔤 Search by name:", "")
    
    with col2:
        gender_filter = st.selectbox("⚥ Gender:", ["All", "Male", "Female"])
    
    with col3:
        age_filter = st.selectbox("👶 Age Category:", 
                                  ["All"] + list(data['age_category'].unique()))
    
    # Apply filters
    filtered_data = data.copy()
    
    if name_search:
        filtered_data = filtered_data[
            filtered_data['name'].str.contains(name_search, case=False, na=False)
        ]
    
    if gender_filter != "All":
        filtered_data = filtered_data[filtered_data['gender'] == gender_filter]
    
    if age_filter != "All":
        filtered_data = filtered_data[filtered_data['age_category'] == age_filter]
    
    # Display results
    st.markdown("---")
    st.info(f"📊 Found **{len(filtered_data)}** results")
    
    if len(filtered_data) > 0:
        st.dataframe(
            filtered_data,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="📥 Download Results as CSV",
            data=csv,
            file_name="filtered_inscriptions.csv",
            mime="text/csv"
        )
    else:
        st.warning("No results found. Try different filters.")

# ========================================
# STATISTICS PAGE
# ========================================
elif page == "📊 Statistics":
    st.header("Statistics & Analysis")
    
    # Gender distribution
    st.subheader("⚥ Gender Distribution")
    gender_counts = data['gender'].value_counts()
    st.bar_chart(gender_counts)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("👨 Male", gender_counts.get('Male', 0))
    with col2:
        st.metric("👩 Female", gender_counts.get('Female', 0))
    
    st.markdown("---")
    
    # Age category distribution
    st.subheader("👶 Age Categories")
    age_counts = data['age_category'].value_counts()
    st.bar_chart(age_counts)
    
    st.markdown("---")
    
    # Inscription types
    st.subheader("📜 Inscription Types")
    type_counts = data['inscription_type'].value_counts()
    st.bar_chart(type_counts)
    
    st.markdown("---")
    
    # Grammatical case distribution
    st.subheader("📖 Grammatical Cases")
    case_counts = data['case'].value_counts()
    st.bar_chart(case_counts)
    
    st.markdown("---")
    
    # Summary statistics
    st.subheader("📈 Summary Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info(f"**Earliest Year:** {data['year'].min()}")
    with col2:
        st.info(f"**Latest Year:** {data['year'].max()}")
    with col3:
        st.info(f"**Year Range:** {data['year'].max() - data['year'].min()} years")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Latin Inscriptions Dashboard | Data from Zenodo</p>
    <p>Built with Streamlit 🎈</p>
</div>
""", unsafe_allow_html=True)
