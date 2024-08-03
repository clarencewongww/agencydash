import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns

# Define a color palette for categorical data
plotly_palette = px.colors.qualitative.Plotly  # Plotly color palette

st.set_page_config(page_title="Agency Dashboard", layout="wide")

st.header("Agency Dashboard")

# Function to load data and cache it
@st.cache_data
def load_data():
    return pd.read_excel("Data for Task A.xlsx")

# Load the data
df = load_data()


# Get column names and unique agencies
col_names = df.columns
agency_list = df.Agency.unique()  # length = 8 


# Define categorical and date fields (ensure indices are correct)
date_fields = col_names[[2, 5]]  
categorical_fields = col_names[[3, 4, 6, 7, 8]]
int_fields = col_names[[1, 9]]  # Integer fields


# Convert date columns to year
df['Year of Birth'] = pd.to_datetime(df[date_fields[0]]).dt.year
df['Year of Joining'] = pd.to_datetime(df[date_fields[1]]).dt.year


# Sidebar for selecting agency and date ranges
agency_selected = st.sidebar.selectbox("Select Agency", agency_list)

# Year sliders
min_dob, max_dob = df['Year of Birth'].min(), df['Year of Birth'].max()
dob_range = st.sidebar.slider("Select Year of Birth Range", min_value=min_dob, max_value=max_dob, value=(min_dob, max_dob))

min_doj, max_doj = df['Year of Joining'].min(), df['Year of Joining'].max()
doj_range = st.sidebar.slider("Select Year of Joining Range", min_value=min_doj, max_value=max_doj, value=(min_doj, max_doj))

# Filter the dataframe based on the selected year ranges
filtered_df = df[(df['Year of Birth'] >= dob_range[0]) & (df['Year of Birth'] <= dob_range[1]) & 
                 (df['Year of Joining'] >= doj_range[0]) & (df['Year of Joining'] <= doj_range[1])]

# Create a dictionary of filtered dataframes for each agency
agency_dfs = {agency: filtered_df[filtered_df["Agency"] == agency] for agency in agency_list}

def plot_proportions(agency, indicator):
    # Calculate the percentage of each unique value in the column for the selected agency
    percentage_of = agency_dfs[agency][indicator].value_counts(normalize=True) * 100
    absolute_counts = agency_dfs[agency][indicator].value_counts()

    # Create Plotly pie chart
    fig = px.pie(values=absolute_counts, names=absolute_counts.index, title=f"Proportion of {indicator}",
                 color_discrete_sequence=plotly_palette, 
                 labels={'values': 'Count', 'names': indicator})
    fig.update_traces(textinfo='label+percent+value')
    fig.update_layout(showlegend=False)
    return fig

def plot_histogram(agency, field):
    data = agency_dfs[agency][field]
    fig = px.histogram(data, x=field, nbins=20, title=f"Histogram of {field}", color_discrete_sequence=['skyblue'])
    return fig

def plot_boxplot(agency, field):
    data = agency_dfs[agency][field]
    fig = px.box(data, x=field, title=f"Box Plot of {field}", color_discrete_sequence=['lightgreen'])
    return fig

def plot_bar_chart(df, field):
    avg_sick_leave = df.groupby('Agency')[field].mean().sort_values()
    fig = px.bar(avg_sick_leave, x=avg_sick_leave.values, y=avg_sick_leave.index, orientation='h',
                 title=f"Average {field} by Agency", color_discrete_sequence=['coral'])
    return fig

# Create two columns
col1, col2 = st.columns(2)

# Display the plots for all categorical indicators
for i, col_of_int in enumerate(categorical_fields):
    if i % 2 == 0:
        with col1:
            st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
            st.plotly_chart(plot_proportions(agency_selected, col_of_int))
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        with col2:
            st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
            st.plotly_chart(plot_proportions(agency_selected, col_of_int))
            st.markdown('</div>', unsafe_allow_html=True)

# Display the histogram for the integer field
with col1:
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    st.plotly_chart(plot_histogram(agency_selected, int_fields[1]))
    st.markdown('</div>', unsafe_allow_html=True)

# Display the box plot for the integer field
with col2:
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    st.plotly_chart(plot_boxplot(agency_selected, int_fields[1]))
    st.markdown('</div>', unsafe_allow_html=True)

# Display the bar chart for the integer field
with col1:
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    st.plotly_chart(plot_bar_chart(df, int_fields[1]))
    st.markdown('</div>', unsafe_allow_html=True)


# Update Streamlit theme
st.markdown("""
    <style>
        .reportview-container {
            background-color: #f0f0f0;
        }
        .sidebar .sidebar-content {
            background-color: #ffffff;
        }
        .css-18e3th9 {
            color: #333333;
        }
        .stButton>button {
            background-color: #007BFF;
            color: white;
            border-radius: 5px;
        }
    </style>
    """, unsafe_allow_html=True)
