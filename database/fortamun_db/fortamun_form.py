import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# --- Configuration ---
DATABASE_NAME = "gobierno_datos.db"
TABLE_NAME = "reporte_anual"

# Column names from your prompt
COLUMNS = [
    "AÑO", "ESTADO", "MUNICIPIO", "EJE ESTRATÉGICO", "PROGRAMA CON PRIORIDAD NACIONAL",
    "SUBPROGRAMA PPN", "ID", "MONTO ANUAL ASIGNADO A SUBPROGRAMA", "MONTO PAGADO EN 1ER TRIMESTRE",
    "MONTO PAGADO EN 2DO TRIMESTRE", "MONTO PAGADO EN 3ER TRIMESTRE", "MONTO PAGADO EN 4TO TRIMESTRE",
    "BIENES Y/O SERVICIOS ADQUIRIDOS", "METAS (UNIDAD DE MEDIDA)", "CANTIDAD", "ID DE BIEN O SERVICIO",
    "ELEMENTOS BENEFICIADOS POR SUBPROGRAMA", "FORMA DE GOBIERNO", "ESTADO DE FUERZA",
    "NÚMERO TELEFÓNICO DE EMERGENCIAS LOCAL", "911", "Monto FORTAMUN ANUAL Asignado al Municipio",
    "RETENCIONES DE LA S.H.C.P.", "MONTO DE RETENCIÓN", "RAZÓN DE LA RETENCIÓN",
    "Monto Destinado a Seguridad Pública", "SUMA DE MONTO PAGADO ANUAL", "REINTEGROS", "RENDIMIENTOS"
]

# Simple mapping of column name to SQLite data type (adjust as necessary)
COLUMN_TYPES = {
    "AÑO": "INTEGER",
    "ESTADO": "TEXT",
    "MUNICIPIO": "TEXT",
    "EJE ESTRATÉGICO": "TEXT",
    "PROGRAMA CON PRIORIDAD NACIONAL": "TEXT",
    "SUBPROGRAMA PPN": "TEXT",
    "ID": "INTEGER", # Assuming ID is an integer
    "CANTIDAD": "INTEGER",
    "ID DE BIEN O SERVICIO": "TEXT",

    # Monetary/Numeric fields are typically REAL (float) or INTEGER
    "MONTO ANUAL ASIGNADO A SUBPROGRAMA": "REAL",
    "MONTO PAGADO EN 1ER TRIMESTRE": "REAL",
    "MONTO PAGADO EN 2DO TRIMESTRE": "REAL",
    "MONTO PAGADO EN 3ER TRIMESTRE": "REAL",
    "MONTO PAGADO EN 4TO TRIMESTRE": "REAL",
    "Monto FORTAMUN ANUAL Asignado al Municipio": "REAL",
    "MONTO DE RETENCIÓN": "REAL",
    "Monto Destinado a Seguridad Pública": "REAL",
    "SUMA DE MONTO PAGADO ANUAL": "REAL",
    "REINTEGROS": "REAL",
    "RENDIMIENTOS": "REAL",

    # Other text fields
    "BIENES Y/O SERVICIOS ADQUIRIDOS": "TEXT",
    "METAS (UNIDAD DE MEDIDA)": "TEXT",
    "ELEMENTOS BENEFICIADOS POR SUBPROGRAMA": "TEXT",
    "FORMA DE GOBIERNO": "TEXT",
    "ESTADO DE FUERZA": "TEXT",
    "NÚMERO TELEFÓNICO DE EMERGENCIAS LOCAL": "TEXT",
    "911": "TEXT",
    "RETENCIONES DE LA S.H.C.P.": "TEXT",
    "RAZÓN DE LA RETENCIÓN": "TEXT"
}

# --- Database Functions ---

def setup_db():
    """Initializes the SQLite database and creates the table if it doesn't exist."""
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Construct the SQL CREATE TABLE statement
        column_definitions = ", ".join(
            f'"{col}" {COLUMN_TYPES.get(col, "TEXT")}'
            for col in COLUMNS
        )
        # Adding a primary key for good measure
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            _PK_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            {column_definitions}
        );
        """
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()
        print("Database setup complete.")
    except Exception as e:
        messagebox.showerror("DB Error", f"Error setting up database: {e}")

def save_data():
    """Collects data from the form entries and inserts it into the SQLite table."""
    data = [entries[col].get() for col in COLUMNS]

    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()

        # Construct the INSERT statement
        placeholders = ", ".join(["?"] * len(COLUMNS))
        column_names_sql = ", ".join(f'"{col}"' for col in COLUMNS)
        insert_sql = f"""
        INSERT INTO {TABLE_NAME} ({column_names_sql})
        VALUES ({placeholders})
        """
        cursor.execute(insert_sql, data)
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Data saved successfully!")
        
        # Optional: Clear the form after successful submission
        for entry in entries.values():
            entry.delete(0, tk.END)

    except Exception as e:
        messagebox.showerror("DB Error", f"Error saving data: {e}")

# --- Tkinter GUI Setup ---

def create_form(root):
    """Creates the Tkinter form layout with all entry fields."""
    
    # Use a Canvas and Scrollbar because there are too many fields for one screen
    canvas = tk.Canvas(root)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion = canvas.bbox("all")))

    # Frame to hold all the form elements
    form_frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=form_frame, anchor="nw")

    # Dictionary to hold the entry widgets globally
    global entries
    entries = {}
    
    # Layout configuration
    row = 0
    column_count = 2 # Two columns of label/entry pairs

    for i, col_name in enumerate(COLUMNS):
        # Calculate grid position
        r = i // column_count
        c = (i % column_count) * 2

        # Label
        label = ttk.Label(form_frame, text=f"{col_name}:", anchor="w")
        label.grid(row=r, column=c, padx=5, pady=5, sticky="w")

        # Entry Field
        entry = ttk.Entry(form_frame, width=40)
        entry.grid(row=r, column=c+1, padx=5, pady=5, sticky="we")
        
        # Save entry reference
        entries[col_name] = entry
        
        row = r # Update row index for the next button/separator

    # Add a separator and the Save button
    separator = ttk.Separator(form_frame, orient='horizontal')
    separator.grid(row=r + 1, columnspan=column_count * 2, sticky="ew", pady=10)

    save_button = ttk.Button(form_frame, text="Guardar", command=save_data)
    # The button spans the entire width of the form frame
    save_button.grid(row=r + 2, columnspan=column_count * 2, pady=10)


def main():
    # 1. Setup Database
    setup_db()

    # 2. Setup Tkinter Root
    root = tk.Tk()
    root.title("Reporte Anual FORTAMUN")
    # Setting a minimum size for the main window
    root.geometry("1200x600")

    # 3. Create the Form
    create_form(root)

    # 4. Run the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
