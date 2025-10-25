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
st.set_page_config(layout="wide", page_title="FASP App", page_icon=im)

# set title and subtitle
st.markdown("<h1><span style='color: #691c32;'>Asignación del Fondo FASP</span></h1>",
    unsafe_allow_html=True)

# author, date
st.caption('Jesús LM')
st.caption('Octubre, 2025')


# authentication by password
password = os.getenv('PASSWORD')
# Initialize session state if not already set
if 'password_correct' not in st.session_state:
    st.session_state.password_correct = False

# if password is not correct, ask for it
if not st.session_state.password_correct:
    password_guess = st.text_input('¡Escribe el password para acceder!')
        
    if password_guess == password:
        st.session_state.password_correct = True
        st.rerun()
    else:
        st.stop()

# this code runs only when the password is correct
#st.success('¡Bienvenido!')

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

# Sliders for weights 15 VARIABLES
with st.sidebar.expander('Bandas'):
    # presupuesto estimado widget
    presupuesto = st.number_input(
        'Presupuesto estimado',
        value=9_951_114_029.0, placeholder='Monto del fondo', key='Presupuesto estimado', format="%.2f", 
    )
    presupuesto_formateado = f"${presupuesto:,.2f}"
    # presupuesto estimado widget
    upper_limit = st.number_input(
        'Banda superior',
        value=0.05, key='Limite superior',
    )
    # presupuesto estimado widget
    lower_limit = st.number_input(
        'Banda inferior',
        value=0.08, key='Limite inferior',
    )



# Sliders for weights
with st.sidebar.expander('Características Estatales'):
    # Categoria 1: categorias estatales
    w_pob = create_weight_input('Población (Alto=Bueno)', .3*.25)
    w_var_inc_del = create_weight_input('Var incidencia delictiva (Alto=Bueno)', .3*.7)
    w_base = create_weight_input('Monto base', .3*.05)

    caracteristicas_sum = (
        w_pob + w_var_inc_del + w_base
    )
    formatted_caracteristicas = f"{caracteristicas_sum:.4f}"
    st.markdown(f'**Suma:** {formatted_caracteristicas}')

with st.sidebar.expander('Desempeño Institucional'):
    # Categoria 2: desempeño institucional
    w_tasa_policial = create_weight_input('Tasa policial (Alto=Bueno)', .45*.1)
    w_dig_salarial = create_weight_input('Dig salarial (Alto=Bueno)', .45*.1)
    w_profesionalizacion = create_weight_input('Profesionalización (Alto=Bueno)', .45*.3)
    w_ctrl_conf = create_weight_input('Ctrl confianza (Alto=Bueno)', .45*.05)
    w_disp_camaras = create_weight_input('Disp cámaras (Alto=Bueno)', .45*.175)
    w_disp_lectores_veh = create_weight_input('Disp lectores veh. (Alto=Bueno)', .45*.175)
    w_abandono_llamadas = create_weight_input('Tasa abandono llamadas (Alto=Malo)', .45*.1)
    w_cump_presup = create_weight_input('Cump. presup. (Alto=Bueno)', .005)
    w_sobrepob = create_weight_input('Sobrepob. penitenciaria (Alto=Malo)', .245*.15)
    w_proc_justicia = create_weight_input('Proc justicia (Alto=Malo)', .245*.35)
    w_servs_forenses = create_weight_input('Servs forenses (Alto=Bueno)', .245*.15)
    w_eficiencia_procesal = create_weight_input('Eficiencia procesal (Alto=Bueno)', .245*.35)

    institucionales_sum = (
        w_tasa_policial + w_dig_salarial + w_profesionalizacion + w_ctrl_conf + w_disp_camaras +
        w_disp_lectores_veh + w_abandono_llamadas + + w_cump_presup + w_sobrepob +
        w_proc_justicia + w_servs_forenses + w_eficiencia_procesal
    )
    formatted_institucionales = f"{institucionales_sum:.4f}"
    st.markdown(f'**Suma:** {formatted_institucionales}')

# Total sum check and adjustment
total_sum = (
    w_pob + w_tasa_policial + w_var_inc_del + w_disp_camaras + w_disp_lectores_veh +
    w_abandono_llamadas + w_dig_salarial + w_profesionalizacion +
    w_ctrl_conf + w_sobrepob + w_proc_justicia + w_servs_forenses + 
    w_eficiencia_procesal + w_cump_presup + w_base
)
formatted_sum = f"{total_sum:.4f}"
st.sidebar.markdown(f'**Suma:** {formatted_sum}')


# Store all weights in a dictionary
weights = {
    'Pob': w_pob,
    'Var_inc_del': w_var_inc_del,
    'Tasa_policial': w_tasa_policial,
    'Dig_salarial': w_dig_salarial,
    'Profesionalizacion': w_profesionalizacion,
    'Ctrl_conf': w_ctrl_conf,
    'Disp_camaras': w_disp_camaras,
    'Disp_lectores_veh': w_disp_lectores_veh,
    'Tasa_abandono_llamadas': w_abandono_llamadas,
    'Cump_presup': w_cump_presup,
    'Sobrepob_penitenciaria': w_sobrepob,
    'Proc_justicia': w_proc_justicia,
    'Servs_forenses': w_servs_forenses,
    'Eficiencia_procesal': w_eficiencia_procesal,
    'Monto base': w_base,
}


# widget para subir archivos
uploaded_file = st.file_uploader("", type=['csv'], )

if uploaded_file is None:
    st.text('Sube el archivo con las variables para la asignación del fondo en formato csv.')
else:
    data = pd.read_csv(io.BytesIO(uploaded_file.getvalue()))    

    # --- UPDATED INDICADORES ---
    # Create a structure for the new 15 indicators (placeholders)
    try:
        indicadores_fasp = pd.read_csv('fasp_indicadores.csv')
    except FileNotFoundError:
        st.error("Archivo 'fasp_indicadores.csv' no encontrado.")
        st.stop()
    
    # Format GT table (rest of the GT configuration is the same)
    indicadores = (
        GT(indicadores_fasp)
        .tab_stub()
        .tab_header(
            title=md('Fondo para las Aportaciones de Seguridad Pública'),
            subtitle=md('## Indicadores de Distribución')
            )
        .fmt_percent(columns=['Ponderación_categoría','Ponderación_indicador'], decimals=1).sub_zero(zero_text=md(''))
        .cols_width(cases={
                "Categoría": "26%",
                "Ponderación_categoría": "22%",
                "Indicador": "30%",
                "Ponderación_indicador": "22%",
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
    tab1, tab2, tab3, tab4 = st.tabs(['1.Introducción', '2.Cálculo', '3.Nota metodológica', '4.Nota técnica'])

    with tab1:

        # header
        st.subheader('1. Introducción')
        st.markdown('''
        <div style="text-align: justify;">
        A continuación se enlistan los indicadores subyacentes para la asignación del <b>Fondo de Aportaciones para la 
        Seguridad Pública</b> (FASP) <b>2026</b>.
        </div>''',
         unsafe_allow_html=True)

        st.html(indicadores)
        st.caption('Tabla 1. Indicadores utilizados para la asignación de fondos y ponderaciones predeterminadas.')

        st.markdown('''
        ##### ¿Cómo funciona esta aplicación?
        ''')

        st.markdown('''
        <div style="text-align: justify;">
        Esta aplicación interactiva sirve como una herramienta de análisis de escenarios que utiliza un <i>Índice de Asignación de Proporciones Directas</i>.
        
        El corazón de la aplicación es la ponderación.
        Al usar los controles deslizantes en la barra lateral, se pueden simular diferentes prioridades de política pública.
        
        Al ajustar estas ponderaciones, la aplicación recalcula el índice en tiempo real, permitiéndo ver cómo los
        supuestos de ponderación impactan la clasificación final de las Entidades Federativas.
        Esto proporciona una base objetiva para discutir y justificar las decisiones de asignación de fondos,
        asegurando que los recursos se dirijan donde son más necesarios o donde generarán el mayor impacto.
        </div>''',
        unsafe_allow_html=True)
        
        st.markdown('''
        ##### Referencias

        [Fondo de Aportaciones para la Seguridad Pública (FASP) 2025](https://www.gob.mx/sesnsp/acciones-y-programas/fondo-de-aportaciones-para-la-seguridad-publica-fasp)
        
        ---

        *© Dirección General de Planeación*
        ''')


    with tab2:
        #st.header('2. Cálculo de Asignación')
        st.markdown(f'''
            ## 2. Escenarios de Asignación
            #### Cálculo con un Fondo Estimado de: *{presupuesto_formateado}*
        ''')
        st.subheader("2.1 Datos de Entrada")

        
        # --- Funciones de Cálculo del Índice (MODIFICADAS PARA PROPORCIÓN DIRECTA Y MONTO POR VARIABLE) ---
        def direct_proportion_normalize(series, direction='positive'):
            """
            Normaliza una serie de datos usando el método de Proporción Directa (Normalización a la Suma).
            Implementa un 'shift' para evitar valores negativos en la serie.
            Si la dirección es 'negative', se usa Proporción Inversa Normalizada sobre la serie shiftada.
            """
            
            # 1. SHIFTING: Asegurar que el valor mínimo de la serie sea 0 o positivo.
            min_val = series.min()
            if min_val < 0:
                # Sumar el valor absoluto del mínimo a toda la serie.
                shifted_series = series + abs(min_val)
            else:
                # No se necesita shift si el mínimo es 0 o positivo.
                shifted_series = series
            
            total_sum = shifted_series.sum()

            if total_sum == 0:
                # Caso extremo: si todos los valores son iguales a cero después del shift (o eran idénticos antes).
                return pd.Series(1.0 / len(shifted_series), index=shifted_series.index)

            if direction == 'positive':
                # Alto=Bueno
                return shifted_series / total_sum
            
            elif direction == 'negative':
                # Alto=Malo: Proporción Inversa Normalizada.
                # Primero, encontrar la Inversa de la serie shiftada (penalizando valores pequeños de la inversa).
                # 1. Aplicar un pequeño "epsilon" (un número muy pequeño) para evitar división por cero si shifted_series tiene ceros.
                # Esto es crucial para la inversa.
                epsilon = 1e-6
                safe_inverse_series = 1 / (shifted_series + epsilon) 
                
                # 2. Normalizar la inversa a la suma (esta es la proporción a asignar).
                return safe_inverse_series / safe_inverse_series.sum()
            
            else:
                raise ValueError("La dirección debe ser 'positive' o 'negative'")


        def calculate_index(df, weights, presupuesto):
            """
            Calcula la Asignación de Fondo Ponderada (Reparto Directo) y la contribución monetaria por variable.
            """
            
            # 1. Fondo restante a repartir por variables (94% del fondo)
            #w_remaining_fund_percent = 1 - weights['Monto base']
            #w_remaining_fund = presupuesto * w_remaining_fund_percent
            
            # Diccionario para almacenar las contribuciones monetarias de cada variable
            contributions = {}

            # --- Definiciones de Normalización y Cálculo de Monto (94% del fondo) ---    
            # Mapping of variable names to their properties
            variable_map = {
                'Pob': 'positive', 'Tasa_policial': 'positive', 'Profesionalizacion': 'positive', 
                'Ctrl_conf': 'positive', 'Disp_camaras': 'positive', 'Disp_lectores_veh': 'positive',
                'Cump_presup': 'positive', 'Servs_forenses': 'positive', 'Eficiencia_procesal': 'positive',
                'Var_inc_del': 'positive', 'Dig_salarial': 'positive', 
                'Tasa_abandono_llamadas': 'negative', 'Sobrepob_penitenciaria': 'negative', 
                'Proc_justicia': 'negative'
            }

            for var_name, direction in variable_map.items():
                # 1. Normalización
                df[f'{var_name}_prop'] = direct_proportion_normalize(df[var_name], direction=direction)
                
                # 2. Cálculo de la Contribución Monetaria Ponderada
                # (Proporción * Peso de la variable * Fondo restante)
                contribution_col_name = f'Monto_{var_name}'
                contributions[contribution_col_name] = df[f'{var_name}_prop'] * weights[var_name] * presupuesto

            # --- Cálculo del Monto Base (6% del fondo) ---
            w_base_amount = presupuesto * weights['Monto base']
            base_share = w_base_amount / len(df)
            
            # sumamos el monto base constante para cada fila
            contributions['Monto_Base'] = pd.Series(base_share, index=df.index) 

            # --- 3. Cálculo de la Asignación Bruta y Reparto Final ---
            # Sumar todas las contribuciones. (Esto incluye las 14 Series de variables + la Serie de Monto Base)
            # Al ser todas Series, la suma es vectorial (fila por fila).
            df['Asignacion_Bruta'] = sum(contributions.values())
            
            # Combinar todas las contribuciones (Monto_X) con el DF principal
            df = pd.concat([df, pd.DataFrame(contributions)], axis=1)
            
            # Para el resto del código (remanente) se necesita una columna que sume 1.00 y represente el reparto:
            df['Reparto'] = df['Asignacion_Bruta'] / df['Asignacion_Bruta'].sum()
            
            return df            
        
        
        # Adjust data for display
        fasp_datos_entrada = data.copy()
        data.index = pd.RangeIndex(start=1, stop=len(data)+1, step=1)
        # Apply formatting to relevant columns
        data[['Var_inc_del','Dig_salarial','Disp_camaras','Disp_lectores_veh','Tasa_abandono_llamadas',
            'Cump_presup','Sobrepob_penitenciaria','Proc_justicia','Servs_forenses','Eficiencia_procesal',]] = (
        data[['Var_inc_del','Dig_salarial','Disp_camaras','Disp_lectores_veh','Tasa_abandono_llamadas',
            'Cump_presup','Sobrepob_penitenciaria','Proc_justicia','Servs_forenses','Eficiencia_procesal',]]*100
        )
        fasp_datos_entrada2 = (
            data.rename(columns={'Entidad': 'Entidad_Federativa'})
                .style.format({
                    'Pob': '{:,.0f}',
                    'Var_inc_del':'{:.2f}%',
                    'Tasa_policial':'{:.2f}',
                    'Dig_salarial':'{:.2f}%',
                    'Profesionalizacion':'{:.0f}',
                    'Ctrl_conf':'{:.2f}',
                    'Disp_camaras':'{:.2f}%',
                    'Disp_lectores_veh':'{:.2f}%',
                    'Tasa_abandono_llamadas':'{:.2f}%',
                    'Cump_presup':'{:.2f}%',
                    'Sobrepob_penitenciaria':'{:.2f}%',
                    'Proc_justicia':'{:.2f}%',
                    'Servs_forenses':'{:.2f}%',
                    'Eficiencia_procesal':'{:.2f}%',
                    'Asignacion_2025': '${:,.2f}',
                    })
                )

        st.dataframe(fasp_datos_entrada2, use_container_width=True)
        st.caption('Tabla 2. Variables utilizadas en el modelo para la asignación de fondos.')


        # --- Cálculo y Visualización ---
        # Calcular la asignación
        df_results = calculate_index(fasp_datos_entrada, weights, presupuesto)
        

        # Mostrar la tabla final de resultados
        st.subheader("2.2 Resultados")
        
        # El reparto ya está en la columna 'Asignacion_Bruta' (sin bandas)
        df_results['Asignacion_2026'] = df_results['Asignacion_Bruta']
        
        # create diff amount and percentage
        df_results['Var%'] = df_results['Asignacion_2026'] / df_results['Asignacion_2025'] -1

        df_end = (
            df_results[['Entidad_Federativa','Asignacion_2026','Asignacion_2025','Var%']]
                .style
                .format({
                        'Asignacion_2026': '${:,.2f}',
                        'Asignacion_2025': '${:,.2f}',
                        'Var%': '{:.2%}',
                        })
        )

        st.dataframe(df_end)

        # Gráfico de barras de asignacion de fondos (Simplified Title)
        fig = px.bar(
            df_results,
            x='Entidad_Federativa',
            y='Asignacion_2026',
            text='Asignacion_2026',
            title="Asignación de Fondos 2026 (Según Ponderadores Aplicados)",
            template='ggplot2',
            hover_data={
                'Entidad_Federativa':False,
                'Asignacion_2026':':$,.2f', # customize hover for column of y attribute
                'Var%':':.2%',
                },
            labels={
                'Entidad_Federativa':'Entidad Federativa',
                'Asignacion_2026':'Asignación 2026',
                'Var%':'Variación',
                },
        )
            
        fig.update_traces(
            textposition='outside',
            marker_color='#235b4e',
            opacity=0.9,
            marker_line_color='#6f7271',
            marker_line_width=1.2,
            texttemplate='$%{text:,.2f}',
            textfont_size=20,
            )

        fig.update_layout(
            uniformtext_minsize=8, uniformtext_mode='hide',
            hovermode="x unified",
            autosize=True,
            height=600,
            xaxis_title='',
            yaxis_title='Asignacion 2026',
            hoverlabel=dict(
                bgcolor="#fff",
                font_size=16,
                font_family="Noto Sans",
                )
            )

        fig.update_xaxes(
            showgrid=True,
            title_font=dict(size=18, family='Noto Sans', color='#691c32'),  # X-axis title font size
            tickfont=dict(size=15, family='Noto Sans', color='#4f4f4f'),  # X-axis tick label font size
            tickangle=-75,
            )

        fig.update_yaxes(
            tickprefix="$",
            tickformat=',.0f',
            showgrid=True,
            title_font=dict(size=16, family='Noto Sans', color='#28282b'),
            tickfont=dict(size=15, family='Noto Sans', color='#4f4f4f'),
            tickangle=0,
            )
            
        st.plotly_chart(fig, use_container_width=True)


        # Gráfico de barras de variación de asignacion de fondos respecto al año anterior
        # create positive and negative colors using if and list comprehension
        var_color = ['#235b4e' if v > 0 else '#9f2241' for v in df_results['Var%']]

        fig_var = px.bar(
            df_results,
            x='Entidad_Federativa',
            y='Var%',
            text='Var%',
            title=f"Variación en la Asignación de Fondos con respecto al Ejercicio Anterior",
            template='ggplot2',
            hover_data={
                'Entidad_Federativa':False,
                'Var%':':.2%',
                },
            labels={
                'Entidad_Federativa':'Entidad Federativa',
                'Var%':'Variación',
                },
        )
            
        fig_var.update_traces(
            textposition='outside',
            marker_color=var_color,
            opacity=0.9,
            marker_line_color='#6f7271',
            marker_line_width=1.2,
            texttemplate='%{text:.2%}',
            textfont_size=20,
            )

        fig_var.update_layout(
            uniformtext_minsize=8, uniformtext_mode='hide',
            hovermode="x unified",
            autosize=True,
            height=600,
            xaxis_title='',
            yaxis_title='Variación %',
            hoverlabel=dict(
                bgcolor="#fff",
                font_size=16,
                font_family="Noto Sans",
                )
            )

        fig_var.update_xaxes(
            showgrid=True,
            title_font=dict(size=18, family='Noto Sans', color='#bc955c'),  # X-axis title font size
            tickfont=dict(size=15, family='Noto Sans', color='#4f4f4f'),  # X-axis tick label font size
            tickangle=-75,
        )

        fig_var.update_yaxes(
            tickformat='.0%',
            showgrid=True,
            title_font=dict(size=16, family='Noto Sans', color='#28282b'),
            tickfont=dict(size=15, family='Noto Sans', color='#4f4f4f'),
            tickangle=0,
            )
            
        st.plotly_chart(fig_var, use_container_width=True)


        st.subheader('2.3 Rebalanceo de remanente')
        st.markdown('''
        Se estableció una banda de control para el importe asignado 2026 en relación al asignado 2025.
        
        A continuación, podemos observar la aplicación de estas bandas a las Entidades Federativas en la asignación 2026.
        ''')

        # Define the tolerance level
        # Calculate Allocation Band (Min and Max)
        df_results['Min'] = df_results['Asignacion_2025'] * (1 - lower_limit)
        df_results['Max'] = df_results['Asignacion_2025'] * (1 + upper_limit)
        
        # Calculate Funds to Pool (from allocations > Max)
        # These are the funds we cap and re-claim
        df_results['Superavit'] = np.where(df_results['Asignacion_2026'] > df_results['Max'],
                                        df_results['Asignacion_2026'] - df_results['Max'],
                                        0)

        # Calculate Deficit to Cover (for allocations < Min)
        # These are the funds we must first cover from the pool
        df_results['Deficit'] = np.where(df_results['Asignacion_2026'] < df_results['Min'],
                                        df_results['Min'] - df_results['Asignacion_2026'],
                                        0)

        # PHASE 2: Calculate Net Exceeding Fund and Interim Allocation

        # Calculate the Net Exceeding Fund (Total Pooled Funds - Total Deficit Needed)
        total_superavit = df_results['Superavit'].sum()
        total_deficit = df_results['Deficit'].sum()
        remanente = total_superavit - total_deficit
        
        # Define the data structure: a list of dictionaries, where each dict is a row
        summary_data = [
            {'Concepto': 'Superávit total', 'Importe': total_superavit},
            {'Concepto': 'Déficit total', 'Importe': total_deficit},
            {'Concepto': 'Remanente', 'Importe': remanente}
        ]

        # Create the new DataFrame
        df_summary = pd.DataFrame(summary_data)

        # show results and band limits
        df_bandas = df_results.copy()
        df_bandas['Var%'] = df_bandas['Var%']*100

        # highlighting zeros
        def highlight_zeros_yellow(value):
            if value != 0:
                return 'background-color: #ddc9a3'
            return ''

        # Apply the styling
        df_bandas = (
            df_bandas[['Entidad_Federativa','Asignacion_2025','Asignacion_2026','Var%','Min','Max','Superavit','Deficit']]
            .style.format({
                'Asignacion_2025': '${:,.2f}',
                'Asignacion_2026': '${:,.2f}',
                'Var%':'{:.2f}%',
                'Min': '${:,.2f}',
                'Max': '${:,.2f}',
                'Superavit': '${:,.2f}',
                'Deficit': '${:,.2f}',
                })
            .applymap(
            highlight_zeros_yellow,
                subset=['Superavit','Deficit']
            )
        )

        st.dataframe(df_bandas, hide_index=True)
        st.caption('Tabla 3. Entidades Federativas por encima/debajo de la banda de control')

        st.markdown('''
        En la siguiente tabla, se resume el superavit y deficit totales, respecto a la banda de control y el remanente a repartir.
        ''')

        
        df_summary2 = (
            df_summary
                .style.format({
                    'Importe': '${:,.2f}',
                    })
            )
        st.dataframe(df_summary2, hide_index=True, width=300)
        st.caption('Tabla 4. Resumen del remante')


        # Determine Interim Allocation: Apply the caps and floors
        # The .clip() function is perfect for this: setting min=TMin and max=TMax
        df_results['Reasignacion'] = df_results['Asignacion_2026'].clip(lower=df_results['Min'], upper=df_results['Max'])
        df_results['Elegibles'] = np.where(df_results['Reasignacion'] < df_results['Max'],
                                            1,
                                            0)
        # Use the raw assignment proportion as the basis for reallocation
        # The sum of 'Reparto' is already 1.00, so it's a valid basis for a new share.
        df_results['Base_Reparto'] = df_results['Reparto']

        total_basis_share = df_results.loc[df_results['Elegibles'] == 1, 'Base_Reparto'].sum()
        
        # 2. Calculate the proportional share of the net fund
        if total_basis_share > 0:
            # Repartir el remanente usando la base de reparto original, solo entre elegibles
            df_results['Reparto_neto'] = np.where(df_results['Elegibles'] == 1, 
                                                (df_results['Base_Reparto'] / total_basis_share) * remanente,
                                                0)
        else:
            df_results['Reparto_neto'] = 0

        # 3. Calculate Final Adjusted Allocation
        df_results['Asignacion_ajustada'] = df_results['Reasignacion'] + df_results['Reparto_neto']
        # Calculate the final percentage change to confirm all are within the target band
        df_results['Var%_ajustada'] = (df_results['Asignacion_ajustada'] - df_results['Asignacion_2025']) / df_results['Asignacion_2025']
        
        df_reasignacion = df_results.copy()
        # create percentages
        df_reasignacion['Var%'] = df_reasignacion['Var%']*100
        df_reasignacion['Var%_ajustada'] = df_reasignacion['Var%_ajustada']*100

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

        st.markdown('''
            En esta tabla se muestra el importe reasignado así como la variación ajustada.
        ''')


        st.dataframe(df_reasignacion2, hide_index=True)
        # validar que la suma de reasignacion ajustada sea igual al presupuesto inicial 2026
        #st.dataframe(pd.Series(df_results['Asignacion_ajustada'].sum()))
        st.caption('Tabla 5. Reasignación de Remanente por Entidad Federativa con banda de control')

        st.dataframe(df_results[['Asignacion_ajustada']].sum(), width=200, hide_index=True,
            column_config={
                '0': st.column_config.NumberColumn(
                    'Importe total asignado',
                    format='dollar',
                )
            }
        )

        # grafico2
        # Gráfico de barras de reasignacion de remanente 2026 vs 2025
        fig2 = go.Figure(data=[
            go.Bar(name='Ejercicio 2025',
                x=df_results['Entidad_Federativa'],
                y=df_results['Asignacion_2025'],
                marker_color='#bc955c',
                ),
            go.Bar(name='Ejercicio 2026',
                x=df_results['Entidad_Federativa'],
                y=df_results['Asignacion_ajustada'],
                marker_color='#691c32',
                ),
            ])

        # Update layout to group bars
        fig2.update_traces(
            textposition='outside',
            opacity=0.9,
            marker_line_color='#6f7271',
            marker_line_width=1.2,
            texttemplate='$%{text:,.2f}',
            textfont_size=20,
            )

        fig2.update_layout(
            barmode='group',
            title=f"Reasignación de Fondos por Entidad Federativa después de Remanente de la banda de control",
            template='ggplot2',
            uniformtext_minsize=8, uniformtext_mode='hide',
            hovermode="x unified",
            autosize=True,
            height=600,
            xaxis_title='',
            yaxis_title='Asignacion 2026',
            hoverlabel=dict(
                bgcolor="#fff",
                font_size=16,
                font_family="Noto Sans",
                )
            )

        fig2.update_xaxes(
            showgrid=True,
            title_font=dict(size=18, family='Noto Sans', color='#691c32'),  # X-axis title font size
            tickfont=dict(size=15, family='Noto Sans', color='#4f4f4f'),  # X-axis tick label font size
            tickangle=-75,
            )

        fig2.update_yaxes(
            tickprefix="$",
            tickformat=',.0f',
            showgrid=True,
            title_font=dict(size=16, family='Noto Sans', color='#28282b'),
            tickfont=dict(size=15, family='Noto Sans', color='#4f4f4f'),
            tickangle=0,
            )
        # fig2.show() # Removed as it's not needed in Streamlit
        st.plotly_chart(fig2, use_container_width=True)

        

        # --- NUEVA TABLA: Contribución Monetaria por Variable ---
        st.subheader("2.4 Contribución Monetaria por Indicador")
        st.markdown(f'''
            La siguiente tabla desglosa la contribución monetaria de cada uno de los 15 indicadores
            a la asignación bruta (sin rebalanceo) del **Fondo Estimado de {presupuesto_formateado}**.
        ''')

        contribution_cols = [f'Monto_{col}' for col in weights.keys() if col != 'Monto base'] + ['Monto_Base']

        # DataFrame for display
        df_contributions = df_results[['Entidad_Federativa'] + contribution_cols].copy()
        
        # Add the 'Total Bruto' for verification
        df_contributions['Asignacion Bruta'] = df_results['Asignacion_Bruta']
        
        # Prepare the DataFrame for display formatting
        st.dataframe(
            df_contributions.style.format({col: '${:,.2f}' for col in contribution_cols + ['Asignacion Bruta']}),
            hide_index=True,
            use_container_width=True
        )
        st.caption('Tabla 6. Contribución monetaria de cada indicador a la asignación bruta por Entidad Federativa.')

        st.markdown('---')
        st.markdown('*© Dirección General de Planeación*')


    with tab3:
        st.markdown('## 3. Nota metodológica')

        st.markdown('''    
        #### 1. Estandarización de Variables (Proporciones)

        Primero, calculamos la proporción que representa cada estado en cada variable:

        - Proporción de Población (Pi​):
        
            `Pi​ = Población del Estado i​ / Población Total`

        - Proporción de Delitos (Di​):
        
            `Di ​= Delitos del Estado i​ / Total de Delitos`

        #### 2. Cálculo del Factor de Asignación Ponderado

        Luego, combina estas dos proporciones para cada estado (i) usando las ponderaciones (WP​=0.60 y WD​=0.40).

        - Factor Ponderado (Fi​):
        
            `Fi ​= (Pi​*0.60)+(Di​*0.40)`

        El resultado Fi​ es el porcentaje total del fondo que le corresponde al Estado i. 
        
        `Nota: La suma de todos los Fi​ para todos los estados debe ser igual a 1.00 (100%).`

        #### 3. Asignación Final del Fondo

        Finalmente, multiplica el Factor Ponderado por el Fondo Total (FT):

        - Asignación al Estado i:
        
            `A_i​ = Fi * FT`
    ''')

    with tab4:

        st.header('4. Nota técnica')
        st.markdown("""
        En este apartado, se muestra la sábana de datos con todos las fases del cálculo de asignación de fondos,
        incluyendo las bandas y reasignación del remanente.

        Por otra parte, se anexa hoja de cálculo en formato xlsx (Excel) con el desarrollo mencionado.
        """)

        st.dataframe(df_results, use_container_width=True)

        st.markdown("[Hoja de cálculo](https://sspcgob-my.sharepoint.com/:x:/g/personal/oscar_avila_sspc_gob_mx/ESy9dnRh6AdJgNEwSx5-udMBcKgLhTP29mnxWhgDvYF6WA?e=l1O8Xl)")
        
        st.markdown('---')
        st.markdown('*© Dirección General de Planeación*')
