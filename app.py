import streamlit as st
import pandas as pd
import plotly.express as px

# Define a color palette for categorical data
plotly_palette = px.colors.qualitative.Plotly  # Plotly color palette

st.set_page_config(page_title="Agency Staff Dashboard", layout="wide")

st.header("Agency Staff Dashboard")

# Function to load and process data
@st.cache_data
def load_and_process_data():
    # Load the data
    df = pd.read_excel("Data for Task A.xlsx")
    
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
    
    return df, agency_list, categorical_fields, int_fields

# Load and process the data
df, agency_list, categorical_fields, int_fields = load_and_process_data()

# Sidebar for selecting agency and date ranges
st.sidebar.header("Filter Options")

# Checkboxes for each agency, default to only "Agency A"
agency_selected = []
default_agency = "Agency A"
for agency in agency_list:
    if st.sidebar.checkbox(agency, value=(agency == default_agency)):
        agency_selected.append(agency)

# Year sliders
min_dob, max_dob = df['Year of Birth'].min(), df['Year of Birth'].max()
dob_range = st.sidebar.slider("Select Year of Birth Range", min_value=min_dob, max_value=max_dob, value=(min_dob, max_dob))

min_doj, max_doj = df['Year of Joining'].min(), df['Year of Joining'].max()
doj_range = st.sidebar.slider("Select Year of Joining Range", min_value=min_doj, max_value=max_doj, value=(min_doj, max_doj))

# Categorical filters
cat_filters = {}
for field in categorical_fields:
    options = df[field].unique()
    selected_options = st.sidebar.multiselect(f"Select {field}", options, default=options)
    cat_filters[field] = selected_options

# Filter the dataframe based on the selected year ranges
filtered_df = df[(df['Year of Birth'] >= dob_range[0]) & (df['Year of Birth'] <= dob_range[1]) & 
                 (df['Year of Joining'] >= doj_range[0]) & (df['Year of Joining'] <= doj_range[1])]

# Filter the dataframe based on selected categorical options
for field, selected_options in cat_filters.items():
    filtered_df = filtered_df[filtered_df[field].isin(selected_options)]

# Filter the dataframe based on selected agencies
filtered_df = filtered_df[filtered_df['Agency'].isin(agency_selected)]

def plot_proportions(df, indicator):
    # Calculate the percentage of each unique value in the column for the selected agency
    percentage_of = df[indicator].value_counts(normalize=True) * 100
    absolute_counts = df[indicator].value_counts()
    
    # Create Plotly pie chart
    fig = px.pie(values=absolute_counts, names=absolute_counts.index, title=f"Proportion of {indicator}",
                 color_discrete_sequence=plotly_palette, 
                 labels={'values': 'Count', 'names': indicator})
    fig.update_traces(textinfo='label+percent+value')
    fig.update_layout(showlegend=False)
    return fig

def plot_histogram(df, field):
    data = df[field]
    fig = px.histogram(data, x=field, nbins=20, title=f"Histogram of {field}", color_discrete_sequence=['skyblue'])
    return fig

def plot_boxplot(df, field):
    data = df[field]
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
            st.plotly_chart(plot_proportions(filtered_df, col_of_int))
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        with col2:
            st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
            st.plotly_chart(plot_proportions(filtered_df, col_of_int))
            st.markdown('</div>', unsafe_allow_html=True)

# Display the histogram for the integer field
with col1:
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    st.plotly_chart(plot_histogram(filtered_df, int_fields[1]))
    st.markdown('</div>', unsafe_allow_html=True)

# Display the box plot for the integer field
with col2:
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    st.plotly_chart(plot_boxplot(filtered_df, int_fields[1]))
    st.markdown('</div>', unsafe_allow_html=True)

# Display the bar chart for the integer field
with col1:
    st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)
    st.plotly_chart(plot_bar_chart(filtered_df, int_fields[1]))
    st.markdown('</div>', unsafe_allow_html=True)

# Create an empty container at the bottom and display the filtered dataframe
st.markdown('<div style="text-align: center;">', unsafe_allow_html=True)

# Reorder the columns such that the 3rd column from the back becomes the 3rd column from the front
cols = filtered_df.columns.tolist()
cols.insert(2, cols.pop(-3))
filtered_df_sorted = filtered_df[cols].sort_values(by=int_fields[1], ascending=False)

st.write(filtered_df_sorted)
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
