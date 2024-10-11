import os
import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
import matplotlib.pyplot as plt

def load_csv(filepath):
    return pd.read_csv(filepath, encoding='utf-8')  # Ensure the CSV is read with UTF-8 encoding

def display_table_with_features(df):
    # Streamlit AgGrid integration for interactive tables
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)  # Pagination
    gb.configure_side_bar()  # Adds a sidebar for filtering
    gb.configure_default_column(editable=True, sortable=True, filter=True)  # Enable sorting and filtering

    grid_options = gb.build()

    grid_response = AgGrid(
        df,
        gridOptions=grid_options,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        update_mode=GridUpdateMode.MODEL_CHANGED,
        enable_enterprise_modules=True,
        height=600,
        fit_columns_on_grid_load=True,
        theme='streamlit',  # You can choose between 'streamlit', 'alpine', 'balham', etc.
        paginationPageSize=10,  # Specify the number of rows per page
    )

    # Extract filtered and sorted data
    filtered_data = grid_response['data']
    return pd.DataFrame(filtered_data)  # Return filtered dataframe

def visualize_schema(df):
    st.subheader("Schema Visualization")
    st.write(df.dtypes)  # Display the data types of the columns

    # Display summary statistics
    st.write("### Summary Statistics")
    st.write(df.describe(include='all'))

def visualize_top_occurrences(df):
    st.subheader("Top Occurrences in a Column")
    selected_column = st.selectbox("Select a column to analyze", df.columns)
    
    if selected_column:
        top_n = st.number_input("Select number of top occurrences", min_value=1, max_value=100, value=10)
        top_occurrences = df[selected_column].value_counts().head(top_n)

        # Create a bar chart for the top occurrences
        st.write(f"### Top {top_n} occurrences in '{selected_column}'")
        st.bar_chart(top_occurrences)

def main():
    # Set the page configuration for a wide layout
    st.set_page_config(page_title="DB2 Library CSV Viewer", layout="wide")

    st.title("DB2 Library CSV Viewer TTC")

    # Input field to enter DB2 library folder path
    folder_selected = st.text_input("Enter the path of DB2 Library folder", "")

    if folder_selected and os.path.isdir(folder_selected):
        # List all CSV files in the selected folder
        tables = [f for f in os.listdir(folder_selected) if f.endswith('.csv')]

        # Dropdown to select a specific CSV table
        selected_table = st.selectbox("Select a table", tables)
        if selected_table:
            # Load the selected table as a DataFrame
            df = load_csv(os.path.join(folder_selected, selected_table))

            # Display a message for Japanese text support
            st.markdown("### Japanese Text Support Test")
            st.markdown("例: こんにちは, さようなら, 日本語をサポートしています")  # Example Japanese text

            # Search bar to search within the table
            search_term = st.text_input("Search within the table")

            if search_term:
                # Filter rows based on search term (simple text match across all columns)
                df = df[df.apply(lambda row: row.astype(str).str.contains(search_term, case=False).any(), axis=1)]

            # Display table with sorting, filtering, and pagination
            filtered_df = display_table_with_features(df)

            # Option to download the filtered data
            st.download_button(
                label="Download filtered data as CSV",
                data=filtered_df.to_csv(index=False, encoding='utf-8'),  # Ensure download is UTF-8 encoded
                file_name=f"filtered_{selected_table}",
                mime='text/csv',
            )

            # Visualize schema
            visualize_schema(df)

            # Analyze top occurrences
            visualize_top_occurrences(df)

            # Translation feature (commented out)
            st.subheader("Translate Text")
            text_to_translate = st.text_area("Enter text to translate (Japanese or any text)", "")
            target_language = st.selectbox("Select target language", ["en", "ja", "es", "fr", "de"], format_func=lambda x: {
                'en': 'English',
                'ja': 'Japanese',
                'es': 'Spanish',
                'fr': 'French',
                'de': 'German',
            }[x])

            if st.button("Translate"):
                if text_to_translate:
                    translated_text = translate_text(text_to_translate, target_language)
                    st.success(f"Translated Text: {translated_text}")
                else:
                    st.error("Please enter text to translate.")

if __name__ == "__main__":
    main()
