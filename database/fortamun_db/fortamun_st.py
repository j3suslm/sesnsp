import streamlit as st
import sqlite3

# --- Configuration (Same as before) ---
DATABASE_NAME = "gobierno_datos.db"
TABLE_NAME = "reporte_anual"

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

COLUMN_TYPES = {
    "AÑO": "INTEGER", "ID": "INTEGER", "CANTIDAD": "INTEGER", 
    "MONTO ANUAL ASIGNADO A SUBPROGRAMA": "REAL", "MONTO PAGADO EN 1ER TRIMESTRE": "REAL",
    "MONTO PAGADO EN 2DO TRIMESTRE": "REAL", "MONTO PAGADO EN 3ER TRIMESTRE": "REAL",
    "MONTO PAGADO EN 4TO TRIMESTRE": "REAL", "Monto FORTAMUN ANUAL Asignado al Municipio": "REAL",
    "MONTO DE RETENCIÓN": "REAL", "Monto Destinado a Seguridad Pública": "REAL",
    "SUMA DE MONTO PAGADO ANUAL": "REAL", "REINTEGROS": "REAL", "RENDIMIENTOS": "REAL",
    "ESTADO": "TEXT", "MUNICIPIO": "TEXT", "EJE ESTRATÉGICO": "TEXT", "PROGRAMA CON PRIORIDAD NACIONAL": "TEXT",
    "SUBPROGRAMA PPN": "TEXT", "BIENES Y/O SERVICIOS ADQUIRIDOS": "TEXT", "METAS (UNIDAD DE MEDIDA)": "TEXT",
    "ID DE BIEN O SERVICIO": "TEXT", "ELEMENTOS BENEFICIADOS POR SUBPROGRAMA": "TEXT", "FORMA DE GOBIERNO": "TEXT",
    "ESTADO DE FUERZA": "TEXT", "NÚMERO TELEFÓNICO DE EMERGENCIAS LOCAL": "TEXT", "911": "TEXT",
    "RETENCIONES DE LA S.H.C.P.": "TEXT", "RAZÓN DE LA RETENCIÓN": "TEXT"
}
# --- End Configuration ---

# --- Database Functions (Same as before) ---
@st.cache_resource
def setup_db():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        column_definitions = ", ".join(f'"{col}" {COLUMN_TYPES.get(col, "TEXT")}' for col in COLUMNS)
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            _PK_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            {column_definitions}
        );
        """
        cursor.execute(create_table_sql)
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error setting up database: {e}")

def save_data(data):
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        placeholders = ", ".join(["?"] * len(COLUMNS))
        column_names_sql = ", ".join(f'"{col}"' for col in COLUMNS)
        insert_sql = f"""
        INSERT INTO {TABLE_NAME} ({column_names_sql})
        VALUES ({placeholders})
        """
        cursor.execute(insert_sql, data)
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False
# --- End Database Functions ---

def main():
    st.set_page_config(layout="wide", page_title="Reporte Anual")
    st.header("Reporte Anual FORTAMUN")

    setup_db()

    # Create the Form
    with st.form(key='data_entry_form'):

        col1, col2, col3 = st.columns(3)
        
        # Dictionary to store the values from the form inputs
        form_data = {}
        
        # Populate the form inputs
        for i, col_name in enumerate(COLUMNS):
            if i % 3 == 0:
                current_col = col1
            elif i % 3 == 1:
                current_col = col2
            else: # Esto cubre el caso donde i % 3 == 2
                current_col = col3
            
            # Append "*" to the label to indicate a required field
            label = f"{col_name} *" 
            data_type = COLUMN_TYPES.get(col_name)
            
            if data_type == "INTEGER":
                form_data[col_name] = current_col.text_input(label, key=col_name, placeholder="Enter an integer number")
            elif data_type == "REAL":
                form_data[col_name] = current_col.text_input(label, key=col_name, placeholder="Enter a monetary value (e.g., 1000.50)")
            else:
                form_data[col_name] = current_col.text_input(label, key=col_name)

        st.markdown("---")
        submit_button = st.form_submit_button(label='Guardar')

        if submit_button:
            # 1. Start Validation Check
            missing_fields = []
            
            # Check for empty fields (or fields that only contain whitespace)
            for col_name, value in form_data.items():
                if not value or value.strip() == "":
                    # Special check for 'REAL' type fields where '0.0' might be the default 
                    # (Though here we use an empty value in text_input to enforce user input)
                    missing_fields.append(col_name)

            if missing_fields:
                st.error(f"🛑 Error: Los {len(missing_fields)} campos son obligatorios y deben requisitarse antes de guardar: **{', '.join(missing_fields[:3])}**... (and more).")
                # Stop processing if fields are missing
                st.stop()
            
            # 2. Proceed with Type Conversion and Save if no fields are missing
            data_list = []
            is_valid = True

            for col_name in COLUMNS:
                value = form_data[col_name]
                data_type = COLUMN_TYPES.get(col_name)
                
                try:
                    if data_type == "INTEGER":
                        data_list.append(int(value))
                    elif data_type == "REAL":
                        data_list.append(float(value))
                    else:
                        data_list.append(value)
                except ValueError:
                    st.error(f"❌ Error de Formato: El valor para **{col_name}** debe ser un número válido ({data_type.lower()}).")
                    is_valid = False
                    break
            
            if is_valid:
                if save_data(data_list):
                    st.success("✅ ¡Datos guardados exitosamente!")
                
if __name__ == "__main__":
    main()
