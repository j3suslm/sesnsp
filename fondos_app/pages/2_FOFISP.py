# libraries
import streamlit as st
import numpy as np
import pandas as pd
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
from great_tables import GT, md
import os
import io
from dotenv import load_dotenv
load_dotenv('.env')


# --- app settings ---
# blog home link
st.markdown('<a href="https://tinyurl.com/sesnsp-dgp-blog" target="_self">Home</a>', unsafe_allow_html=True)

# hide streamlit logo and footer
hide_default_format = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """

# load icon image
im = Image.open('images/logo.png')

# page layout config and add image
st.set_page_config(layout="wide", page_title="FOFISP App", page_icon=im)

# image and text
st.image('images/sesnsp.png', width=300)

# set title and subtitle
st.markdown("<h2><span style='color: #bc955c;'>Asignación del Fondo FOFISP</span></h2>",
    unsafe_allow_html=True)

# date
st.caption('Noviembre, 2025')

column1, column2 = st.columns([2,1])

with column1:
    # authentication by password
    password = os.getenv('FONDOS_PASSWORD')
    # Initialize session state if not already set
    if 'password_correct' not in st.session_state:
        st.session_state.password_correct = False

    # if password is not correct, ask for it
    if not st.session_state.password_correct:
        password_guess = st.text_input('¡Escribe el password para acceder!', type="password")
            
        if password_guess == password:
            st.session_state.password_correct = True
            st.rerun()
        else:
            st.stop()
with column2:
    pass

        
# customize color of sidebar and text
st.markdown(hide_default_format, unsafe_allow_html=True)
st.markdown("""
    <style>
        /* 1. Target the main content area background */
        [data-testid="stAppViewBlockContainer"] {
            background-color: #f6f6f6;
        }
        /* Sidebar background */
        [data-testid=stSidebar] {
            background-color: #f6f6f6;
            color: #28282b;
        }
        /* Target all text elements within the sidebar (labels, markdown, sliders, etc.) */
        [data-testid="stSidebar"] * {
            color: #28282b !important;
        }
    </style>
    """, unsafe_allow_html=True)


# --- sidebar ---
# sidebar image and text
st.sidebar.image('images/sesnsp.png')

# Function to create a weight slider/input
def create_weight_input(label, default_value):
    return st.number_input(
        label,
        min_value=0.0, max_value=1.0, value=default_value, step=0.001, key=label, format="%.4f",
    )

# Sliders for weights 05 VARIABLES
with st.sidebar.expander('Bandas'):
    # presupuesto estimado widget
    presupuesto = st.number_input(
        'Fondo',
        value=1_154_918_909.69, placeholder='Monto del fondo', key='Presupuesto estimado', format="%.2f", 
    )
    presupuesto_formateado = f"${presupuesto:,.2f}"
    # presupuesto estimado widget
    upper_limit = st.number_input(
        'Banda superior',
        value=0.1, key='Limite superior',
    )
    # presupuesto estimado widget
    lower_limit = st.number_input(
        'Banda inferior',
        value=0.0, key='Limite inferior',
    )

# --- NEW Simplified Weights Expander ---
with st.sidebar.expander('Ponderadores'):
    w_pob = st.number_input(
        'Población (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.70, step=0.01, key='Población', 
    )
    w_edo_fza = st.number_input(
        'Tasa policial (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.15, step=0.01, key='Tasa policial'
    )
    w_var_incidencia_del = st.number_input(
        'Variación incidencia delictiva (Alto=Malo)',
        min_value=0.0, max_value=1.0, value=0.10, step=0.01, key='Variación incidencia delictiva'
    )
    w_academias = st.number_input(
        'Academias (Alto=Bueno)',
        min_value=0.0, max_value=1.0, value=0.05, step=0.01, key='Academias'
    )
    
    # Total sum check
    total_sum = (
        w_pob + w_var_incidencia_del + w_edo_fza + w_academias
    )
    formatted_sum = f"{total_sum:.0%}"
    st.markdown(f'**Suma de ponderadores:** {formatted_sum}')
    
    if abs(total_sum - 1.0) > 0.001:
        st.warning('¡La suma de ponderadores debe ser 100%!')

# Store all weights in a dictionary
weights = {
    'Población': w_pob,
    'Var_incidencia_del': w_var_incidencia_del,
    'Tasa_policial': w_edo_fza,
    'Academias': w_academias,
}

formatted_sum = f"{total_sum:.0%}"
st.sidebar.markdown(f'**Suma de ponderadores:** {formatted_sum}')


# upload final variables dataset
# widget para subir archivos
uploaded_file = st.file_uploader("", type=['csv'], )

if uploaded_file is None:
    st.text('Sube el archivo con las variables para la asignación del fondo en formato csv.')
    st.stop()
else:
    data = pd.read_csv(io.BytesIO(uploaded_file.getvalue()))    

    # --- LOAD INDICADORES TABLE (Placeholder) ---
    try:
        indicadores_fofisp = pd.read_csv('fofisp_indicadores.csv')
    except FileNotFoundError:
        st.error("Archivo 'fofisp_indicadores.csv' no encontrado.")
        st.stop()

    # tabla de indicadores
    indicadores_fofisp = pd.read_csv('fofisp_indicadores.csv')
    indicadores_fofisp['Categoría'] = indicadores_fofisp['Categoría'].fillna('')
    indicadores_fofisp['Ponderación_categoría'] = indicadores_fofisp['Ponderación_categoría'].fillna(0)

    # Format GT table (rest of the GT configuration is the same)
    indicadores = (
        GT(indicadores_fofisp)
        .tab_stub()
        .tab_header(
            title=md('Fondo para el Fortalecimiento de las Instituciones de Seguridad Pública (FOFISP)'),
            subtitle=md('## Indicadores de Distribución')
            )
        .fmt_percent(columns=['Ponderación_categoría','Ponderación_subcategoría','Ponderación_indicador'], decimals=1).sub_zero(zero_text=md(''))
        .cols_width(cases={
                "Categoría": "20%",
                "Ponderación_categoría": "20%",
                "Indicador": "60%",
                "Ponderación_indicador": "20%",
                })
        .cols_label(
            Categoría = md('**Categoría**'),
            Ponderación_categoría = md('**Ponderación categoría**'),
            Indicador = md('**Indicador**'),
            Ponderación_indicador = md('**Ponderación indicador**'),
        )
        .cols_align(align='center', columns=['Ponderación_categoría','Ponderación_indicador'])
        .tab_options(
            container_width="100%",
            container_height="100%",
            heading_background_color="#691c32",
            column_labels_background_color="#ddc9a3",
            source_notes_background_color="#ddc9a3",
            row_striping_include_table_body=True,
            row_striping_background_color='#f8f8f8',
        )
        .tab_source_note(
            source_note=md("Fuente: *Secretariado Ejecutivo del Sistema Nacional de Seguridad Pública*")
        )
    )


# tab layout
tab1, tab2, tab3 = st.tabs(['1.Indicadores', '2.Asignación', '3.Nota técnica'])

# --- TAB 1: INDICADORES ---
with tab1:
    st.subheader('Indicadores Utilizados para la Asignación')
    st.markdown('''
    <div style="text-align: justify;">
    El <b>Fondo para el Fortalecimiento de las Instituciones de Seguridad Pública</b> (FOFISP) transfiere recursos a las entidades federativas 
    para atender las políticas de seguridad pública.
    En la siguiente tabla, se listan los indicadores utilizados.
    </div>''', unsafe_allow_html=True)

    st.html(indicadores)    
    st.caption('Tabla 1. Indicadores utilizados para la asignación de fondos y ponderaciones predeterminadas.')
    st.markdown('Para mayor información sobre el fondo, vísite la página [Fondo para el Fortalecimiento de las Instituciones de Seguridad Pública (FOFISP) 2025](https://www.gob.mx/sesnsp/acciones-y-programas/fondo-de-aportaciones-para-la-seguridad-publica-fasp)')
    st.markdown('''
        ---
        *© Dirección General de Planeación*   
        *Elaborado por Jesús López Monroy*   
    ''')


# --- TAB 2: ASIGNACIÓN ---
with tab2:
    st.markdown(f'''
        ## Escenarios de Asignación
        #### Fondo: *{presupuesto_formateado}*
    ''')
    st.subheader("Datos de Entrada")

    # --- Funciones de Cálculo del Índice (Direct Proportion Normalization) ---
    def direct_proportion_normalize(series, direction='positive'):
        """
        Normaliza una serie de datos.
        - 'positive' (Alto=Bueno): Proporción directa.
        - 'negative' (Alto=Malo): Proporción inversa (1/X) suavizada.
        """
        if not isinstance(series, pd.Series):
            series = pd.Series(series)
            
        # Corrimiento (Shift) para manejar valores no positivos en la proporción inversa
        # R = shift factor to avoid division by zero or negative values
        R = series.abs().max() * 0.01 + 1e-6 # Simple shift factor
        
        # 1. Base Series (Always positive for calculation)
        shifted_series = series + R
        
        # 2. Inversion for negative direction
        if direction == 'negative':
            normalized_base = 1 / shifted_series
        else:
            normalized_base = shifted_series

        # 3. Normalization to sum
        total_sum = normalized_base.sum()
        
        if total_sum == 0:
            return pd.Series(1.0 / len(normalized_base), index=normalized_base.index)
        
        return normalized_base / total_sum
        

    def calculate_index(df, weights, presupuesto):
        """
        Calcula la Asignación de Fondo Ponderado
        """
        contributions = {}
        df['Entidad_Federativa'] = df['Entidad_Federativa'].astype(str) # Ensure string for merge/display

        # Map the 4 variables to their calculation direction
        variable_map = {
            'Población': 'positive', 
            'Var_incidencia_del': 'negative', 
            'Tasa_policial': 'positive', 
            'Academias': 'positive',
        }
        
        # --- Normalization and Weighted Monetary Contribution (for 85% of the fund) ---
        for var_name, direction in variable_map.items():
            # 1. Normalization
            df[f'{var_name}_prop'] = direct_proportion_normalize(df[var_name], direction=direction)
            
            # 2. Calculate the Weighted Monetary Contribution
            contribution_col_name = f'Monto_{var_name}'
            contributions[contribution_col_name] = df[f'{var_name}_prop'] * weights[var_name] * presupuesto

        
        # --- 3. Calculation of the Gross Allocation (Asignacion_Bruta) ---
        # Sum all contributions (4 variables + Base)
        df['Asignacion_Bruta'] = sum(contributions.values())
        
        # Combine all contributions (Monto_X) with the main DF
        df = pd.concat([df, pd.DataFrame(contributions)], axis=1)
        
        # Calculate the proportional share (sums to 1.0)
        df['Reparto'] = df['Asignacion_Bruta'] / df['Asignacion_Bruta'].sum()
        
        return df

    # --- DATA DISPLAY (INPUT) ---
    fofisp_datos_entrada = data.copy()
    fofisp_datos_entrada.rename(columns={'Entidad': 'Entidad_Federativa'}, inplace=True)
    fofisp_datos_entrada.index = pd.RangeIndex(start=1, stop=len(fofisp_datos_entrada)+1, step=1)
    
    # Apply formatting for display purposes (assuming Var_incidencia_del, Tasa_policial, Academias are ratios/percentages or simple numbers)
    fofisp_datos_entrada_display = (
        fofisp_datos_entrada[['Entidad_Federativa', 'Población', 'Var_incidencia_del', 'Tasa_policial', 'Academias', 'Asignacion_2025']]
        .style.format({
            'Población': '{:,.0f}',
            'Var_incidencia_del':'{:.2f}', # Assumed a number/ratio
            'Tasa_policial':'{:.2f}',
            'Academias':'{:.0f}', # Assumed a count/integer
            'Asignacion_2025': '${:,.2f}',
            })
        )

    st.dataframe(fofisp_datos_entrada_display, use_container_width=True)
    st.caption('Tabla 2. Variables utilizadas en el modelo para la asignación del fondo.')


    # --- Calculation and Visualization ---
    df_results = calculate_index(fofisp_datos_entrada, weights, presupuesto)
    
    # --- RESULTS (WITHOUT BANDS) ---
    st.subheader("Resultados Iniciales (sin bandas)")
    df_results['Asignacion_2026'] = df_results['Asignacion_Bruta']
    df_results['Var%'] = df_results['Asignacion_2026'] / df_results['Asignacion_2025'] - 1

    df_end = (
        df_results[['Entidad_Federativa','Asignacion_2026','Asignacion_2025','Var%']]
        .style
        .format({
            'Asignacion_2026': '${:,.2f}',
            'Asignacion_2025': '${:,.2f}',
            'Var%': '{:.2%}',
            })
    )

    st.dataframe(df_end, width=600)
    st.caption('Tabla 3. Resultados iniciales sin bandas.')


    # --- ITERATIVE REBALANCE LOGIC (Bands) ---
    st.subheader('Rebalanceo de remanente (*iteración*)')
    st.markdown(f'''
    Se estableció una banda de control de **{lower_limit:.0%}** (inferior) y **+{upper_limit:.0%}** (superior) para el importe asignado 2026 en relación 
    al asignado 2025.
    El proceso de rebalanceo es iterativo hasta que **todas** las Entidades Federativas se encuentren dentro de este rango.
    ''')

    # Initial setup before the loop
    df_iterative = df_results.copy()
    
    df_iterative['Asignacion_Iterativa'] = df_iterative['Asignacion_Bruta']
    df_iterative['Asignacion_Final'] = df_iterative['Asignacion_Bruta']

    # Calculate Band Limits (Min and Max)
    df_iterative['Min'] = df_iterative['Asignacion_2025'] * (1 + lower_limit)
    df_iterative['Max'] = df_iterative['Asignacion_2025'] * (1 + upper_limit)

    # Iteration Control
    max_iterations = 20
    current_iteration = 0
    remanente = 1.0
    total_remanente_acumulado = 0.0

    df_iterative['Base_Reparto_Original'] = df_iterative['Reparto']

    # --- ITERATIVE REALLOCATION LOOP ---
    while abs(remanente) > 0.01 and current_iteration < max_iterations:
        
        current_iteration += 1
        
        # 1. Calculate Superavit and Deficit from the current 'Asignacion_Iterativa'   
        df_iterative['Superavit'] = np.where(df_iterative['Asignacion_Iterativa'] > df_iterative['Max'],
                                             df_iterative['Asignacion_Iterativa'] - df_iterative['Max'],
                                             0)
        df_iterative['Deficit'] = np.where(df_iterative['Asignacion_Iterativa'] < df_iterative['Min'],
                                             df_iterative['Min'] - df_iterative['Asignacion_Iterativa'],
                                             0)

        # 2. Calculate the Net Remanente (Pooled Funds - Deficit Needed)
        total_superavit = df_iterative['Superavit'].sum()
        total_deficit = df_iterative['Deficit'].sum()
        remanente = total_superavit - total_deficit
        
        if abs(remanente) < 0.01:
            break
            
        total_remanente_acumulado += remanente

        # 3. Apply Caps and Floors (Interim Allocation)
        df_iterative['Reasignacion'] = df_iterative['Asignacion_Iterativa'].clip(lower=df_iterative['Min'], upper=df_iterative['Max'])

        # 4. Identify Eligible States for Remanente Distribution
        df_iterative['Elegibles'] = np.where(df_iterative['Reasignacion'] < df_iterative['Max'], 1, 0)
        
        # New sum of the base proportions, only for the eligible states
        total_basis_share = df_iterative.loc[df_iterative['Elegibles'] == 1, 'Base_Reparto_Original'].sum()

        # 5. Distribute the Net Remanente among Eligible States
        if total_basis_share > 0:
            df_iterative['Reparto_neto'] = np.where(df_iterative['Elegibles'] == 1, 
                                                    (df_iterative['Base_Reparto_Original'] / total_basis_share) * remanente,
                                                    0)
        else:
            df_iterative['Reparto_neto'] = 0

        # 6. Calculate the New Working Allocation for the next iteration
        df_iterative['Asignacion_Iterativa'] = df_iterative['Reasignacion'] + df_iterative['Reparto_neto']
        
        df_iterative['Asignacion_Final'] = df_iterative['Asignacion_Iterativa']

    # --- END OF ITERATIVE REALLOCATION LOOP ---
    st.success(f'Proceso de rebalanceo completado (*{current_iteration} iteraciones*).')

    # Final Calculation and Display
    df_results['Asignacion_ajustada'] = df_iterative['Asignacion_Final']
    df_results['Var%_ajustada'] = (df_results['Asignacion_ajustada'] - df_results['Asignacion_2025']) / df_results['Asignacion_2025']

    # Display Final Adjusted Allocation Table (Table 4)
    df_reasignacion = df_results.copy()
    df_reasignacion['Var%'] = df_reasignacion['Var%'] * 100
    df_reasignacion['Var%_ajustada'] = df_reasignacion['Var%_ajustada'] * 100

    df_reasignacion2 = (
        df_reasignacion[['Entidad_Federativa','Asignacion_2025','Asignacion_2026','Var%','Asignacion_ajustada','Var%_ajustada']]
        .style.format({
            'Asignacion_2025': '${:,.2f}',
            'Asignacion_2026': '${:,.2f}',
            'Var%':'{:.2f}%',
            'Asignacion_ajustada': '${:,.2f}',
            'Var%_ajustada':'{:.2f}%',
            })
    )

    st.markdown('#### Asignación Ajustada Final')
    st.dataframe(df_reasignacion2, hide_index=True, width=750)
    st.caption('Tabla 4. asignación ajustada final dentro de la banda especificada.')


    # --- VISUALIZATION ---
    st.subheader('Comparativo de Asignaciones')

    # 1. Prepare data for the grouped chart (Unpivot/Melt)
    df_chart = df_results[['Entidad_Federativa', 'Asignacion_2025', 'Asignacion_2026', 'Asignacion_ajustada']].copy()

    df_melted = pd.melt(
        df_chart,
        id_vars='Entidad_Federativa',
        value_vars=['Asignacion_2025', 'Asignacion_2026', 'Asignacion_ajustada'],
        var_name='Tipo_Asignacion',
        value_name='Monto'
    )

    # 2. Rename categories
    df_melted['Tipo_Asignacion'] = df_melted['Tipo_Asignacion'].map({
        'Asignacion_2025': 'Asignación 2025 (Referencia)',
        'Asignacion_2026': 'Asignación 2026 (Inicial)',
        'Asignacion_ajustada': 'Asignación 2026 (Final Ajustada)'
    })

    # 3. Define color map
    color_map = {
        'Asignación 2025 (Referencia)': '#ddc9a3',
        'Asignación 2026 (Inicial)': '#9f2241',
        'Asignación 2026 (Final Ajustada)': '#235b4e'
    }

    # 4. Create the grouped bar chart with Plotly Express
    fig_final = px.bar(
        df_melted,
        x='Entidad_Federativa',
        y='Monto',
        color='Tipo_Asignacion',
        barmode='group',
        text='Monto',
        title=f"Comparativo de Asignaciones de Fondos (Bandas [{lower_limit:.0%}, +{upper_limit:.0%}])",
        template='ggplot2',
        color_discrete_map=color_map,
        labels={
            'Entidad_Federativa': 'Entidad Federativa',
            'Monto': 'Monto Asignado',
            'Tipo_Asignacion': 'Tipo de Asignación'
        },
        hover_data={'Monto':':,.2f'},
    )

    # 5. Configure Traces and Layout (Same as original)
    fig_final.update_traces(
        textposition='outside',
        texttemplate='$%{text:,.0f}',
        textfont_size=12,
        opacity=0.9,
        marker_line_color='black',
        marker_line_width=0.5,
    )

    fig_final.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        hovermode="x unified",
        autosize=True,
        height=700,
        xaxis_title='',
        yaxis_title='Monto asignado',
        legend_title='Tipo de Monto',
        legend=dict(
            orientation="h", yanchor="bottom", y=.99, xanchor="right", x=1
        )
    )

    fig_final.update_xaxes(
        showgrid=True, tickangle=-60,
        title_font=dict(size=16, family='Noto Sans', color='#28282b'),
        tickfont=dict(size=14, family='Noto Sans', color='#4f4f4f'),
    )

    fig_final.update_yaxes(
        tickprefix="$", tickformat=',.0f', showgrid=True,
        title_font=dict(size=16, family='Noto Sans', color='#28282b'),
        tickfont=dict(size=14, family='Noto Sans', color='#4f4f4f'),
        tickangle=0,
    )

    st.plotly_chart(fig_final, use_container_width=True)

    st.caption('''Figura 1. Comparativo de la Asignación 2025 (referencia), la Asignación 2026 Inicial (sin bandas) y
    la Asignación 2026 Final Ajustada.''')

    st.markdown('''
    ---
    *© Dirección General de Planeación*   
    *Elaborado por Jesús López Monroy*   
    ''')
    

with tab3:

        st.header('Sábana de Datos')
        st.markdown("""
        En este apartado, se muestra la sábana de datos con todos las fases del cálculo de asignación de fondos,
        incluyendo las bandas y reasignación del remanente.
        """)

        st.dataframe(df_results, use_container_width=True)

        st.markdown('Por otra parte, se anexa hoja de cálculo (Excel) con el procedimiento aplicado para la asignación final.')
        
        st.markdown("[Hoja de cálculo](https://sspcgob-my.sharepoint.com/:x:/g/personal/jesus_lopez_sspc_gob_mx/EVMYdkSmoR5FqM3VSG85RBEBCE3Lk4JFgfWOXZG2EuwS6Q?e=AOY1iJ)")
        
        st.markdown('''
        ---
        *© Dirección General de Planeación*   
        *Elaborado por Jesús López Monroy*   
        ''')
