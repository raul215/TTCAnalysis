import dropbox
import pandas as pd
import streamlit as st
import io
import os
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode

# Initialize Dropbox client with your access token
ACCESS_TOKEN = st.secrets["dropbox"]["DROPBOX_ACCESS_TOKEN"]

# Initialize Dropbox client with your access token
if ACCESS_TOKEN:
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
else:
    st.error("Dropbox access token not found. Please set the environment variable.")


# Function to list subfolders and files
def list_dropbox_items(folder_path):
    try:
        response = dbx.files_list_folder(folder_path)
        subfolders = []
        files = []
        for entry in response.entries:
            if isinstance(entry, dropbox.files.FolderMetadata):
                subfolders.append(entry.name)
            elif isinstance(entry, dropbox.files.FileMetadata):
                files.append(entry.name)
        return subfolders, files
    except dropbox.exceptions.ApiError as e:
        st.error(f"Error accessing Dropbox folder: {e}")
        return [], []

# Function to load CSV from Dropbox
def load_dropbox_csv(file_path):
    try:
        _, res = dbx.files_download(file_path)
        return pd.read_csv(io.BytesIO(res.content))
    except Exception as e:
        st.error(f"Error loading CSV: {e}")
        return pd.DataFrame()

# Function to display AgGrid table
def display_table_with_features(df):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    gb.configure_side_bar()  # Adds a sidebar for filtering
    gb.configure_default_column(editable=True, sortable=True, filter=True)
    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        enable_enterprise_modules=True,
        height=600,
        fit_columns_on_grid_load=True,
        theme='streamlit',
        paginationPageSize=10,
    )

    filtered_data = grid_response['data']
    return pd.DataFrame(filtered_data)

# Function to visualize schema
def visualize_schema(df):
    st.subheader("Schema Visualization")
    st.write(df.dtypes)

    st.write("### Summary Statistics")
    st.write(df.describe(include='all'))

# Function to visualize top occurrences
def visualize_top_occurrences(df):
    st.subheader("Top Occurrences in a Column")
    selected_column = st.selectbox("Select a column to analyze", df.columns)
    
    if selected_column:
        top_n = st.number_input("Select number of top occurrences", min_value=1, max_value=100, value=10)
        top_occurrences = df[selected_column].value_counts().head(top_n)

        st.write(f"### Top {top_n} occurrences in '{selected_column}'")
        st.bar_chart(top_occurrences)

# Streamlit UI
def main():
    st.set_page_config(page_title="TTC Data Viewer", layout="wide")
    st.title("TTC Data Viewer")

    # Define your Dropbox "Dumps" folder path
    dump_folder = '/Dumps'  # Path to the main folder in Dropbox
    subfolders, _ = list_dropbox_items(dump_folder)

    if subfolders:
        selected_subfolder = st.selectbox("Select a subfolder", subfolders)

        if selected_subfolder:
            subfolder_path = f"{dump_folder}/{selected_subfolder}"
            _, files = list_dropbox_items(subfolder_path)

            # Filter only CSV files
            csv_files = [f for f in files if f.lower().endswith('.csv')]

            if csv_files:
                selected_file = st.selectbox("Select a CSV file", csv_files)

                if selected_file:
                    file_path = f"{subfolder_path}/{selected_file}"
                    st.write(f"Loading file from: {file_path}")

                    # Load CSV and display table
                    df = load_dropbox_csv(file_path)
                    if not df.empty:
                        filtered_df = display_table_with_features(df)

                        # Option to download filtered data
                        st.download_button(
                            label="Download filtered data as CSV",
                            data=filtered_df.to_csv(index=False, encoding='utf-8'),
                            file_name=f"filtered_{selected_file}",
                            mime='text/csv',
                        )

                        # Visualize schema
                        visualize_schema(df)

                        # Visualize top occurrences
                        visualize_top_occurrences(df)
            else:
                st.error("No CSV files found in the selected subfolder.")
    else:
        st.error("No subfolders found in the Dumps folder.")

if __name__ == "__main__":
    main()
