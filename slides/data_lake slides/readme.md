# The "Layered" Data Lake

This approach is often implemented using a tiered architecture, sometimes called a "medallion architecture" or "data lake layers."

-   **Bronze Layer (Raw Data)**

    This is your landing zone for the original, unprocessed data. Files are stored exactly as they were ingested (e.g., CSV, JSON). This layer is typically write-once and is used for long-term archival.

-   **Silver Layer (Transformed/Cleaned Data)**

    This is where you store your Parquet files. Data in this layer has been cleaned, transformed, and structured for efficient analysis. This is the layer your DuckDB queries will primarily interact with.

-   **Gold Layer (Curated Data)**

    This layer is for highly aggregated and enriched data, optimized for specific applications like business intelligence dashboards or machine learning model training.

By following this layered approach, you get the best of both worlds: the immutability and security of the raw data in the Bronze layer, and the performance and efficiency of the Parquet files in the Silver layer.

## Why Keep the Original Files?

The main reason to keep the original files is that they act as a "single source of truth" and an immutable copy of your raw data. This is crucial for several reasons:

-   **Auditability and Reproducibility**

    If you ever need to re-create a past analysis or debug an issue with your data processing pipeline, having the raw, unprocessed data is essential. It allows you to trace exactly where your processed data came from.

-   **Flexibility for Future Needs**

    As your project evolves, you may need to apply new transformations or extract different features from the data that you didn't anticipate. If you've only kept the Parquet files, which are already a transformed version of the data, you may have lost information. The original files give you the flexibility to go back and start over.

-   **Data Integrity**

    Data ingestion is often complex. If there's a corruption or a bug in your conversion process to Parquet, the original files are your safety net. You can simply re-process them to fix the issue, rather than trying to fix the Parquet files themselves.

## Code

```{python}
import pandas as pd
import polars as pl
import duckdb as db
from pathlib import Path
import os

# 1. Define and create the data lake layers
# Use pathlib.Path for a robust, OS-agnostic way to manage file paths
# This creates the "Bronze", "Silver", and "Gold" layers

BASE_DIR = Path("data_lake")
RAW_LAYER = BASE_DIR / "bronze" / "raw"
PROCESSED_LAYER = BASE_DIR / "silver" / "processed"
CURATED_LAYER = BASE_DIR / "gold" / "curated"

# Create the directories if they don't exist

RAW_LAYER.mkdir(parents=True, exist_ok=True)
PROCESSED_LAYER.mkdir(parents=True, exist_ok=True)
CURATED_LAYER.mkdir(parents=True, exist_ok=True)

print(f"Bronze layer created at: {RAW_LAYER}")
print(f"Silver layer created at: {PROCESSED_LAYER}")
print(f"Gold layer created at: {CURATED_LAYER}\n")


# 2. Simulate data ingestion into the raw layer
# We'll create a dummy CSV file to represent incoming, unprocessed data.

raw_data = {
    'id': [1, 2, 3, 4],
    'product_name': ['Widget A', 'Widget B', 'Widget A', 'Widget C'],
    'price_usd_str': ['10.50', '25.99', '10.50', '4.99'], # Price is a string! This is a common raw data issue.
    'sale_date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04']
}
df_raw = pd.DataFrame(raw_data)
raw_file_path = RAW_LAYER / "sales_20230104.csv"
df_raw.to_csv(raw_file_path, index=False)

print(f"Raw data file created at: {raw_file_path}\n")


# 3. Process and promote data to the silver layer
# This function encapsulates the logic for transformation and storage.

def ingest_to_silver_layer(raw_path: Path, processed_dir: Path):
    """
    Reads a raw CSV file, cleans it, and saves it as a Parquet file.
    """
    print(f"Starting ingestion process for: {raw_path}")

    # Use Polars to read the data efficiently.
    # It will infer the schema, but we'll explicitly cast for our transformation.
    # The 'product_name' column will be used for our transformation logic.
    raw_df_polars = pl.read_csv(raw_path)

    # Clean the data:
    # 1. Convert the 'price_usd_str' column to a proper floating-point number.
    # 2. Add a new column 'sale_month' for better analytics.

    silver_df = raw_df_polars.with_columns(
        pl.col('price_usd_str').str.replace_all(',', '.').cast(pl.Float64).alias('price_usd'),
        pl.col('sale_date').str.to_date("%Y-%m-%d").dt.month().alias('sale_month')
    ).drop('price_usd_str') # Drop the old, unclean column.

    # Define the output file path using pathlib.
    # Change the file extension and place it in the processed directory.

    processed_file_path = processed_dir / f"{raw_path.stem}.parquet"
    
    # Write the cleaned data to a Parquet file.
    # Parquet is a columnar format, perfect for analytics and storage.

    silver_df.write_parquet(processed_file_path)

    print(f"Data successfully processed and saved to: {processed_file_path}\n")

    return processed_file_path


# 4. Create the Gold layer from the Silver layer
def create_gold_layer(silver_path: Path, gold_dir: Path):
    """
    Reads a Parquet file from the Silver layer, performs an aggregation,
    and saves the final, curated data as a Parquet file in the Gold layer.
    """
    print(f"Starting creation of Gold layer from: {silver_path}")
    con = duckdb.connect(':memory:')

    # Use DuckDB to read and aggregate the data directly from the Parquet file.
    
    query = f"""
    SELECT 
        sale_month, 
        SUM(price_usd) AS total_monthly_sales
    FROM '{silver_path}'
    GROUP BY 1
    ORDER BY 1;
    """
    
    gold_df = con.execute(query).fetchdf()

    # Define the output path for the Gold file.
        gold_file_path = gold_dir / "monthly_sales_report.parquet"
    
    # Write the aggregated data to the Gold layer.
    con.from_df(gold_df).write_parquet(gold_file_path)
    
    print(f"Gold layer file created at: {gold_file_path}\n")
    con.close()
    
    return gold_file_path


# 5. Verify the data using DuckDB
def verify_with_duckdb(parquet_file: Path):
    """
    Uses DuckDB to query the Parquet file directly to verify its contents.
    This demonstrates the "data lakehouse" concept.
    """
    print("Verifying data with DuckDB...")
    
    # DuckDB's magic: you can query a Parquet file directly without a server.
    # It treats the file as a table.
    con = duckdb.connect(':memory:')
    
    # Perform a simple aggregation query to prove the data is correct.
    # We'll calculate the total sales for each product.
    query = f"""
    SELECT 
        product_name, 
        SUM(price_usd) AS total_sales,
        CAST(COUNT(*) as INTEGER) AS total_units
    FROM '{parquet_file}'
    GROUP BY 1
    ORDER BY total_sales DESC;
    """
    
    results = con.execute(query).fetchdf()
    
    print("DuckDB Query Results:")
    print(results)
    
    con.close()
    
    print("\nVerification complete. Data lake pipeline is working!")


# Main execution block
if __name__ == "__main__":
    # Get a list of all raw files to process.
    raw_files_to_process = list(RAW_LAYER.glob("*.csv"))
    
    # Loop through each raw file and process it.
    for raw_file in raw_files_to_process:
        # Step 1: Ingest from Bronze to Silver
        processed_file = ingest_to_silver_layer(raw_file, PROCESSED_LAYER)
        
        # Step 2: Create a Gold layer report from the Silver layer
        gold_file = create_gold_layer(processed_file, CURATED_LAYER)

        # Step 3: Verify the Silver layer data
        verify_with_duckdb(processed_file)
        
        # Step 4: Verify the Gold layer data
        print("Verifying Gold layer data with DuckDB...")
        con = duckdb.connect(':memory:')
        gold_results = con.execute(f"SELECT * FROM '{gold_file}'").fetchdf()
        print("Gold Layer Results:")
        print(gold_results)
        con.close()
```

------------------------------------------------------------------------

# Data Lake

You can create a DuckDB data lake for diverse files, but you need to handle structured and unstructured data differently. For structured data like CSV, TXT, JSON, and GeoJSON, DuckDB can create a direct view on the raw files. For unstructured data like images, audio, and PDFs, you must first use other libraries to extract meaningful metadata or content and then store that extracted information in a structured format (like Parquet) for DuckDB to query.

## Handling Structured and Semi-structured Files

DuckDB's strength lies in its ability to directly read and query structured and semi-structured files without needing to import the data.

-  **CSV & TXT**

    You can use the read_csv_auto() function. TXT files can be treated as a special case of CSV, often with a different delimiter.

-  **JSON & GeoJSON**

    Use read_json_auto(). Since GeoJSON is just a specialized JSON format, DuckDB can handle it. You might need to use DuckDB's geospatial extension for advanced operations, but basic queries work out of the box.

### Using views

The main reason is that CREATE VIEW does not physically copy or store the data inside the DuckDB database. Instead, it creates a virtual table that is essentially a saved query. When you run a query against the users view, DuckDB goes directly to the users.csv file, reads the data, and returns the result. This means your data remains in its original files, which is a core principle of a data lake.

Here's a quick breakdown of why this is beneficial:

-   **No data duplication**

    You aren't creating a separate copy of your CSV, JSON, or Excel data. This saves disk space and simplifies your data architecture.

-   **Always up-to-date**

    If you modify users.csv, the users view will reflect those changes immediately the next time you query it. A table created with CREATE TABLE would be a static snapshot and wouldn't update automatically.

-   **Flexibility**

    You can define views for different purposes on the same raw files without having to transform and save multiple physical tables.

You would use CREATE TABLE if you wanted to physically import and store the data inside the DuckDB file, creating a more traditional *data warehouse*. This might be useful for performance optimizations or if you needed to create a permanent, non-volatile snapshot of the data.

### Parquet files (raw)

Yes, you absolutely should create Parquet files and then build your views on top of them. This is a common and highly recommended best practice for building an efficient data lake.

While DuckDB can read CSV, JSON, and Excel files, the Parquet format is significantly more performant and efficient for analytics. Here's why:

-   **Columnar Storage**

    Parquet is a columnar data format, meaning it stores data by column rather than by row. DuckDB is also a columnar database. When you run a query that only needs a few columns, DuckDB can read just those columns from the Parquet file, which is much faster than scanning an entire CSV or JSON file.

-   **Optimal Compression**

    Parquet files are highly compressed, saving you a significant amount of disk space.

-   **Schema Awareness**

    Parquet files have a built-in schema, which helps prevent data type issues and makes data loading much more reliable.

By converting to Parquet, you're building a more robust and performant data lake architecture. The original files can be considered your "raw" layer, and the Parquet files become your "processed" or "curated" layer, which is optimized for fast, analytical queries.

## Handling Unstructured Files

For files like images, audio, and PDFs, DuckDB cannot directly "read" or "understand" the file content itself. To query these, you must follow a two-step process:

-   **Pre-processing**

    Use a Python library to open each file and extract relevant metadata.

-   **PDFs**

    Use a library like PyMuPDF (imported as fitz) to get the number of pages, creation date, author, or even the full text content.

-   **Images**

    Use Pillow to get dimensions (width, height), format, and other EXIF data.

-   **Audio**

    Use a library like mutagen to extract duration, bit rate, artist, and album information.

-   **Structuring and Ingesting**

    Store this extracted metadata in a structured format like a Parquet file. This Parquet file acts as an index for your unstructured data lake. DuckDB can then query this index to find information about your files. The actual image, audio, or PDF file remains untouched.

Here is a Python script that demonstrates this dual approach, creating a data lake from a CSV file, a JSON file, and a PDF file. The script first extracts metadata from the PDF and then uses DuckDB to query all three data sources.

This script gives you a flexible and scalable pattern. You can easily extend this to other file types by adding a pre-processing step using the appropriate library and then writing the results to a Parquet file that DuckDB can query. This way, you create a powerful, unified view of both your structured and unstructured data.


``` python
# Hybrid DuckDB Data Lake Script
# 8 Aug, 14:02
# Extract metadata from unstructured files and create a structured index
print("\nExtracting metadata from PDF and creating a Parquet index file...")

# Get PDF metadata using PyMuPDF (fitz)
pdf_info = fitz.open(pdf_file)
metadata = {
    'filename': pdf_file,
    'page_count': pdf_info.page_count,
    'creation_date': pdf_info.metadata.get('creationDate', 'N/A'),
    'title': pdf_info.metadata.get('title', 'N/A')
}
pdf_info.close()

# Store metadata in a pandas DataFrame
metadata_df = pd.DataFrame([metadata])

# Use DuckDB to save the DataFrame to a Parquet file
con = duckdb.connect(database=':memory:')
metadata_parquet_file = "pdf_metadata.parquet"
con.from_df(metadata_df).to_parquet(metadata_parquet_file)
```

## Notes

`To update database views automatically, you have to update parquet files not flat files!`


### Reference code (to follow later from Gemini)

``` python
# hybrid_duckdb_datalake.py
import duckdb
import pandas as pd
import os
import json
import csv
import fitz # PyMuPDF library for handling PDFs

# --- Step 1: Create sample data files ---
print("Creating sample data files...")

# Create a sample CSV file
csv_file = "user_demographics.csv"
with open(csv_file, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['user_id', 'age', 'city'])
    writer.writerow([101, 30, 'New York'])
    writer.writerow([102, 25, 'Los Angeles'])

# Create a sample JSON file (acting as a GeoJSON)
geojson_file = "city_locations.json"
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {"city": "New York", "population": 8400000},
            "geometry": {"type": "Point", "coordinates": [-74.006, 40.712]}
        },
        {
            "type": "Feature",
            "properties": {"city": "Los Angeles", "population": 3900000},
            "geometry": {"type": "Point", "coordinates": [-118.243, 34.052]}
        }
    ]
}
with open(geojson_file, 'w') as f:
    json.dump(geojson_data, f)

# Create a dummy PDF file for metadata extraction
pdf_file = "sample_report.pdf"
doc = fitz.open()
page = doc.new_page()
page.insert_text((72, 72), "This is a sample PDF report.")
doc.save(pdf_file)
doc.close()

# --- Step 2: Extract metadata from unstructured files and create a structured index ---
print("\nExtracting metadata from PDF and creating a Parquet index file...")

# Get PDF metadata using PyMuPDF (fitz)
pdf_info = fitz.open(pdf_file)
metadata = {
    'filename': pdf_file,
    'page_count': pdf_info.page_count,
    'creation_date': pdf_info.metadata.get('creationDate', 'N/A'),
    'title': pdf_info.metadata.get('title', 'N/A')
}
pdf_info.close()

# Store metadata in a pandas DataFrame
metadata_df = pd.DataFrame([metadata])

# Use DuckDB to save the DataFrame to a Parquet file
con = duckdb.connect(database=':memory:')
metadata_parquet_file = "pdf_metadata.parquet"
con.from_df(metadata_df).to_parquet(metadata_parquet_file)

# --- Step 3: Create relations (views) on all files (raw and indexed) ---
print("Creating views on the data lake files...")

# Create a view on the raw CSV file
con.execute(f"CREATE OR REPLACE VIEW users AS SELECT * FROM read_csv_auto('{csv_file}')")

# Create a view on the raw GeoJSON file
con.execute(f"CREATE OR REPLACE VIEW locations AS SELECT properties.city AS city, properties.population AS population FROM read_json_auto('{geojson_file}')")

# Create a view on the Parquet index file for the PDFs
con.execute(f"CREATE OR REPLACE VIEW documents AS SELECT * FROM read_parquet('{metadata_parquet_file}')")

# --- Step 4: Query the data lake ---
print("\nExecuting a multi-source SQL query...")
# This query joins the structured demographic data with location data
# and displays metadata from the unstructured documents.
query = f"""
    SELECT
        u.user_id,
        u.age,
        u.city,
        l.population,
        d.filename,
        d.page_count
    FROM
        users u
    JOIN
        locations l ON u.city = l.city
    CROSS JOIN
        documents d
    ORDER BY
        u.age DESC;
"""

result = con.execute(query).fetchdf()
print("Query Result:")
print(result)

# --- Step 5: Clean up ---
print("\nCleaning up temporary files...")
con.close()
os.remove(csv_file)
os.remove(geojson_file)
os.remove(pdf_file)
os.remove(metadata_parquet_file)
print("Cleanup complete.")
```
