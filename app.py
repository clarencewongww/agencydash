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
    df['Years of Service'] = 2022 - df['Year of Joining']
    df['Age'] = 2022 - df['Year of Birth']
    
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

min_doj, max_doj = df['Years of Service'].min(), df['Years of Service'].max()
doj_range = st.sidebar.slider("Select Years of Service Range (in 2022)", min_value=min_doj, max_value=max_doj, value=(min_doj, max_doj))

# Categorical filters
cat_filters = {}
for field in categorical_fields:
    options = df[field].unique()
    selected_options = st.sidebar.multiselect(f"Select {field}", options, default=options)
    cat_filters[field] = selected_options

# Filter the dataframe based on the selected year ranges
filtered_df = df[(df['Year of Birth'] >= dob_range[0]) & (df['Year of Birth'] <= dob_range[1]) & 
                 (df['Years of Service'] >= doj_range[0]) & (df['Years of Service'] <= doj_range[1])]

# Filter the dataframe based on selected categorical options
for field, selected_options in cat_filters.items():
    filtered_df = filtered_df[filtered_df[field].isin(selected_options)]

# Filter the dataframe based on selected agencies
filtered_df = filtered_df[filtered_df['Agency'].isin(agency_selected)]

# Create sections
instruction_summary_section = st.empty()
categorical_section = st.empty()
leave_section = st.empty()
comparison_section = st.empty()

# Instruction and Summary Section
with instruction_summary_section.container():
    col1, col2 = st.columns([3,2], gap = "medium")
    with col1:
        st.subheader("Instructions")
        st.write("""
        This dashboard allows you to filter and analyze staff data based on various criteria.
        Use the sidebar to select the agency, year ranges, and other categorical filters.
        The filtered data and visualizations will be displayed below.
                 
        Lastest data as of year 2022. 
        """)
    with col2:
        st.subheader("Summary Data")
        total_employees = len(filtered_df)
        avg_years_of_service = filtered_df['Years of Service'].mean()
        avg_leave_taken = filtered_df[int_fields[1]].mean()
        st.markdown(f"**Total Employees:** {total_employees}")
        st.markdown(f"**Average Years of Service:** {avg_years_of_service:.2f}")
        st.markdown(f"**Average Sick Leave Taken:** {avg_leave_taken:.2f}")

# Function to plot proportions
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

# Function to plot histogram
def plot_histogram(df, field):
    data = df[field]
    fig = px.histogram(data, x=field, nbins=20, title=f"Histogram of {field}", color_discrete_sequence=['skyblue'])
    return fig

# Function to plot boxplot
def plot_boxplot(df, field):
    data = df[field]
    fig = px.box(data, x=field, title=f"Box Plot of {field}", color_discrete_sequence=['lightgreen'])
    return fig

# Function to plot bar chart
def plot_bar_chart(df, field):
    avg_sick_leave = df.groupby('Agency')[field].mean().sort_values()
    fig = px.bar(avg_sick_leave, x=avg_sick_leave.values, y=avg_sick_leave.index, orientation='h',
                 title=f"Average {field} by Agency", color_discrete_sequence=['coral'],
                 labels={'x': 'Sick Leave Consumed (Days)', 'y': 'Agency'})
    return fig


# Function to plot scatter plot of average sick leave by years of service
def plot_scatter_avg_sick_leave(df, service_field, leave_field):
    avg_leave_by_service = df.groupby(service_field)[leave_field].mean().reset_index()
    fig = px.scatter(avg_leave_by_service, x=service_field, y=leave_field, 
                     title=f"Average Sick Leave by Years of Service", 
                     labels={service_field: "Years of Service", leave_field: "Average Sick Leave"}, 
                     color_discrete_sequence=['blue'])
    return fig

# Function to plot scatter plot of average sick leave by age
def plot_scatter_avg_sick_leave_age(df, age_field, leave_field):
    avg_leave_by_age = df.groupby(age_field)[leave_field].mean().reset_index()
    fig = px.scatter(avg_leave_by_age, x=age_field, y=leave_field, 
                     title=f"Average Sick Leave by Age", 
                     labels={age_field: "Age (in 2022)", leave_field: "Average Sick Leave"}, 
                     color_discrete_sequence=['green'])
    return fig

# Categorical Section
with categorical_section.container():
    st.subheader("Profile Data")
    col1, col2 = st.columns(2)
    for i, col_of_int in enumerate(categorical_fields):
        if i % 2 == 0:
            with col1:
                st.plotly_chart(plot_proportions(filtered_df, col_of_int))
        else:
            with col2:
                st.plotly_chart(plot_proportions(filtered_df, col_of_int))

# Leave Section
with leave_section.container():
    st.subheader("Leave Data")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_histogram(filtered_df, int_fields[1]))
        st.plotly_chart(plot_scatter_avg_sick_leave(filtered_df, 'Years of Service', int_fields[1]))
    with col2:
        st.plotly_chart(plot_boxplot(filtered_df, int_fields[1]))
        st.plotly_chart(plot_scatter_avg_sick_leave_age(filtered_df, 'Age', int_fields[1]))


# Comparison Section
with comparison_section.container():
    st.subheader("Referencing Between Agency Data")
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(plot_bar_chart(filtered_df, int_fields[1]))

# Display the filtered dataframe
st.subheader("Filtered Data")
st.write(filtered_df)
