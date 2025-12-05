import streamlit as st
import sqlite3
import pandas as pd
import io

# --- Configuration and Initialization ---
# Assume the database file is named 'chinook.db' and is in the same directory.
DATABASE_FILE = "chinook.db"

st.set_page_config(
    page_title="Chinook Database Explorer",
    layout="wide"
)

# --- Database Functions ---
#@st.cache_resource
def get_db_connection(db_file):
    """
    Establishes and caches the database connection.
    Caches the connection object across rerun to avoid reconnecting.
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
        st.stop()
        return None

#@st.cache_data
def get_table_names(conn):
    """Fetches a list of all table names in the database."""
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    df = pd.read_sql_query(query, conn)
    return df['name'].tolist()

#@st.cache_data(show_spinner="Loading data...")
def get_table_data(conn, table_name):
    """Fetches all data for a given table name."""
    query = f"SELECT * FROM \"{table_name}\""
    df = pd.read_sql_query(query, conn)
    return df

# --- CSV Handling Function ---
def convert_df_to_csv(df):
    """Converts a pandas DataFrame to a CSV string encoded in UTF-8."""
    # Use io.StringIO for in-memory string buffer for efficient CSV conversion
    csv_buffer = io.StringIO()
    # index=False ensures the row numbers are not included in the CSV file
    df.to_csv(csv_buffer, index=False)
    # Get the value and encode it for the download button
    return csv_buffer.getvalue().encode('utf-8')


# --- Streamlit App Layout ---
def main():
    st.title("📀 Chinook SQLite Database Explorer")
    st.markdown("Use the sidebar to select a table and view its contents. You can then download the data as a CSV file.")

    # 1. Connect to the database
    conn = get_db_connection(DATABASE_FILE)
    if conn is None:
        return

    # 2. Get table names
    table_names = get_table_names(conn)

    if not table_names:
        st.warning(f"No tables found in the database file: '{DATABASE_FILE}'. Please ensure the file exists and is a valid SQLite database.")
        return

    # 3. Sidebar for selection
    st.sidebar.header("Table Selection")
    selected_table = st.sidebar.selectbox(
        "Choose a table to explore:",
        options=table_names,
        index=0 # Default to the first table
    )

    # 4. Display data in the main area
    if selected_table:
        st.header(f"Table: `{selected_table}`")
        
        # Fetch data for the selected table
        df_table = get_table_data(conn, selected_table)

        if not df_table.empty:
            st.dataframe(df_table, use_container_width=True)
            st.markdown(f"*Displaying {len(df_table)} rows and {len(df_table.columns)} columns*")

        else:
            st.warning(f"The table '{selected_table}' is empty.")

if __name__ == "__main__":
    main()
