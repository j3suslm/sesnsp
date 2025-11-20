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

# image and text
st.image('images/sesnsp.png', width=300)

# set title and subtitle
st.markdown("<h2><span style='color: #bc955c;'>Asignación del Fondo FASP</span></h2>",
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

# Sliders for weights 15 VARIABLES
with st.sidebar.expander('Bandas'):
    # presupuesto estimado widget
    presupuesto = st.number_input(
        'Fondo',
        value=9_941_162_915.0, placeholder='Monto del fondo', key='Presupuesto estimado', format="%.2f", 
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



# Sliders for weights
with st.sidebar.expander('Características Estatales'):
    # Categoria 1: categorias estatales
    w_pob = create_weight_input('Población (Alto=Bueno)', .6*.5)
    w_var_inc_del = create_weight_input('Incidencia delictiva (Alto=Bueno)', .6*.3)
    w_base = create_weight_input('Monto base', .6*.2)

    caracteristicas_sum = (
        w_pob + w_var_inc_del + w_base
    )
    formatted_caracteristicas = f"{caracteristicas_sum:.4f}"
    st.markdown(f'**Suma:** {formatted_caracteristicas}')

with st.sidebar.expander('Desempeño Institucional'):
    # Categoria 2: desempeño institucional
    w_tasa_policial = create_weight_input('Tasa policial (Alto=Bueno)', .24*.2)
    w_dig_salarial = create_weight_input('Dig salarial (Alto=Bueno)', .24*.2)
    w_profesionalizacion = create_weight_input('Profesionalización (Alto=Bueno)', .24*.15)
    w_ctrl_conf = create_weight_input('Ctrl confianza (Alto=Bueno)', .24*.1)
    w_disp_camaras = create_weight_input('Disp cámaras (Alto=Bueno)', .24*.15)
    w_disp_lectores_veh = create_weight_input('Disp lectores veh. (Alto=Bueno)', .24*.1)
    w_abandono_llamadas = create_weight_input('Tasa abandono llamadas (Alto=Malo)', .24*.1)
    w_cump_presup = create_weight_input('Cump. presup. (Alto=Bueno)', .01)
    w_sobrepob = create_weight_input('Sobrepob. penitenciaria (Alto=Malo)', .15*.1)
    w_proc_justicia = create_weight_input('Proc justicia (Alto=Malo)', .15*.1)
    w_servs_forenses = create_weight_input('Servs forenses (Alto=Bueno)', .15*.5)
    w_eficiencia_procesal = create_weight_input('Eficiencia procesal (Alto=Bueno)', .15*.3)

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
formatted_sum = f"{total_sum:.0%}"
st.sidebar.markdown(f'**Suma de ponderadores:** {formatted_sum}')


# Store all weights in a dictionary
weights = {
    'Pob': w_pob,
    'Inc_del': w_var_inc_del,
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
            title=md('Fondo para las Aportaciones de Seguridad Pública (FASP)'),
            subtitle=md('## Indicadores de Distribución')
            )
        .fmt_percent(columns=['Ponderación_categoría','Ponderación_subcategoría','Ponderación_indicador'], decimals=1).sub_zero(zero_text=md(''))
        .cols_width(cases={
                "Categoría": "20%",
                "Ponderación_categoría": "20%",
                "Subcategoría": "30%",
                "Indicador": "60%",
                "Ponderación_subcategoría": "20%",
                "Ponderación_indicador": "20%",
                })
        .cols_label(
            Categoría = md('**Categoría**'),
            Subcategoría = md('**Subcategoría**'),
            Ponderación_categoría = md('**Ponderación categoría**'),
            Ponderación_subcategoría = md('**Ponderación subcategoría**'),
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
    tab1, tab2, tab3 = st.tabs(['1.Indicadores','2.Asignación','3.Nota técnica',])


    with tab1:

        # header
        st.subheader('Indicadores Utilizados para la Asignación')
        st.markdown('''
        <div style="text-align: justify;">
        
        El **Fondo de Aportaciones para la Seguridad Pública** (FASP) es un fondo presupuestal previsto en
        la *Ley de Coordinación Fiscal* a través del cual se transfieren recursos a las entidades federativas
        para dar cumplimiento a estrategias nacionales en materia de seguridad pública.
        
        En la siguiente tabla, se listan los indicadores utilizados para la asignación de este fondo.
        
        </div>''',
         unsafe_allow_html=True)

        st.html(indicadores)
        st.caption('Tabla 1. Indicadores utilizados para la asignación de fondos y ponderaciones predeterminadas.')
        st.markdown('Para mayor información sobre el fondo, vísite la página [Fondo de Aportaciones para la Seguridad Pública (FASP) 2025](https://www.gob.mx/sesnsp/acciones-y-programas/fondo-de-aportaciones-para-la-seguridad-publica-fasp)')
        
        st.markdown('''
        ---
        *© Dirección General de Planeación*   
        *Elaborado por Jesús López Monroy*   
        ''')


    with tab2:
        #st.header('2. Cálculo de Asignación')
        st.markdown(f'''
            ## Escenarios de Asignación
            #### Fondo: *{presupuesto_formateado}*
        ''')
        st.subheader("Datos de Entrada")

        # --- Funciones de Cálculo del Índice proporcion directa (aplicando shift=mean(x)+stdev(x) al invertir alto=malo) ---
        def direct_proportion_normalize(series, direction='positive'):
            """
            Normaliza una serie de datos usando el método de Proporción Directa (Normalización a la Suma).
            Implementa un 'shift' para asegurar que todos los valores sean no negativos.
            
            - Si la dirección es 'positive' (Alto=Bueno), usa Proporción Directa.
            - Si la dirección es 'negative' (Alto=Malo), usa una Proporción Inversa Suavizada 
            (penalizando valores altos) basada en la fórmula R/(R+X) donde R es la media + std.
            """
            
            # Asegurar que el input es una Serie de Pandas
            if not isinstance(series, pd.Series):
                series = pd.Series(series)

            # 1. SHIFTING: Asegurar que el valor mínimo de la serie sea 0 o positivo.
            R = series.mean() + series.std()*3

            min_val = series.min()
            
            # Shift para que el mínimo sea exactamente 0 (si era negativo)
            if min_val < 0:
                # Corrimiento de prom + stdev.
                shifted_series = series + R 
            else:
                # No se necesita shift si el mínimo es 0 o positivo.
                shifted_series = series
            
            # --- Lógica de Normalización ---
            if direction == 'positive':
                # Alto=Bueno (Proporción Directa Estándar)
                total_sum = shifted_series.sum()
                
                if total_sum == 0:
                    # Caso extremo: si todos los valores son cero después del shift.
                    return pd.Series(1.0 / len(shifted_series), index=shifted_series.index)
                
                return shifted_series / total_sum
            
            elif direction == 'negative':
                
                # Alto=Malo: Proporción Inversa Suavizada (penalizando valores altos)
                # Un valor grande (Alto=Malo) dará un resultado penalizado (cercano a 0).
                penalized_series = 1 / shifted_series
                
                # 3. Normalizar la serie penalizada a la suma (Proporción Directa)
                total_sum_penalized = penalized_series.sum()
                
                if total_sum_penalized == 0:
                    # Si, por alguna razón, la suma es 0 después de la penalización (muy improbable con R>0)
                    return pd.Series(1.0 / len(shifted_series), index=shifted_series.index)
                    
                return penalized_series / total_sum_penalized
                

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
                'Inc_del': 'positive', 'Dig_salarial': 'positive', 
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
        data[['Inc_del','Dig_salarial','Disp_camaras','Disp_lectores_veh','Tasa_abandono_llamadas',
            'Cump_presup','Sobrepob_penitenciaria','Proc_justicia','Servs_forenses','Eficiencia_procesal',]] = (
        data[['Inc_del','Dig_salarial','Disp_camaras','Disp_lectores_veh','Tasa_abandono_llamadas',
            'Cump_presup','Sobrepob_penitenciaria','Proc_justicia','Servs_forenses','Eficiencia_procesal',]]*100
        )
        fasp_datos_entrada2 = (
            data.rename(columns={'Entidad': 'Entidad_Federativa'})
                .style.format({
                    'Pob': '{:,.0f}',
                    'Inc_del':'{:.2f}%',
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
        st.caption('Tabla 2. Variables utilizadas en el modelo para la asignación del fondo.')


        # --- Cálculo y Visualización ---
        # Calcular la asignación
        df_results = calculate_index(fasp_datos_entrada, weights, presupuesto)
        

        # Mostrar la tabla final de resultados
        st.subheader("Resultados Iniciales (sin bandas)")
        
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

        st.dataframe(df_end, width=600)
        st.caption('Tabla 3. Resultados iniciales sin bandas.')


        # --- Start of the iterative rebalance logic ---
        st.subheader('Rebalanceo de remanente (*iteración*)')
        st.markdown(f'''
        Se estableció una banda de control de **{lower_limit:.0%}** (inferior) y **{upper_limit:.0%}** (superior) para el importe asignado 2026 en relación
        al asignado 2025.
        El proceso de rebalanceo es iterativo hasta que **todas** las Entidades Federativas se encuentren dentro de este rango.
        ''')

        # Initial setup before the loop
        df_iterative = df_results.copy()
        
        # Start with the initial calculated allocation as the 'working' column
        df_iterative['Asignacion_Iterativa'] = df_iterative['Asignacion_Bruta']
        df_iterative['Asignacion_Final'] = df_iterative['Asignacion_Bruta'] # Final result column

        # Calculate Band Limits (Min and Max)
        df_iterative['Min'] = df_iterative['Asignacion_2025'] * (1 + lower_limit)
        df_iterative['Max'] = df_iterative['Asignacion_2025'] * (1 + upper_limit)

        # Iteration Control
        max_iterations = 20 # Safety limit
        current_iteration = 0
        remanente = 1.0 # Initialize to a non-zero value to start the loop
        total_remanente_acumulado = 0.0 # To track pooled funds across iterations

        # Use the original proportion for distribution base (it sums to 1.0)
        df_iterative['Base_Reparto_Original'] = df_iterative['Reparto'] 

        # --- ITERATIVE REALLOCATION LOOP ---
        while abs(remanente) > 0.01 and current_iteration < max_iterations: # Check if the remanente is significant
            
            current_iteration += 1
            
            # 1. Calculate Superavit and Deficit from the current 'Asignacion_Iterativa'    
            # Superavit: Funds exceeding the Max band (to be pooled)
            df_iterative['Superavit'] = np.where(df_iterative['Asignacion_Iterativa'] > df_iterative['Max'],
                                                df_iterative['Asignacion_Iterativa'] - df_iterative['Max'],
                                                0)
            # Deficit: Funds below the Min band (to be covered first)
            df_iterative['Deficit'] = np.where(df_iterative['Asignacion_Iterativa'] < df_iterative['Min'],
                                                df_iterative['Min'] - df_iterative['Asignacion_Iterativa'],
                                                0)

            # 2. Calculate the Net Remanente (Pooled Funds - Deficit Needed)
            total_superavit = df_iterative['Superavit'].sum()
            total_deficit = df_iterative['Deficit'].sum()
            
            # This is the net fund to be redistributed among "eligible" states
            remanente = total_superavit - total_deficit 
            
            if abs(remanente) < 0.01: # Check again if the remanente is negligible
                break
                
            total_remanente_acumulado += remanente

            # 3. Apply Caps and Floors (Interim Allocation)
            # The .clip() function sets the current working column to be within the bands
            df_iterative['Reasignacion'] = df_iterative['Asignacion_Iterativa'].clip(lower=df_iterative['Min'], upper=df_iterative['Max'])

            # 4. Identify Eligible States for Remanente Distribution
            # Eligible states are those not capped by the Max limit in this iteration
            # (i.e., their Reasignacion is < Max)
            df_iterative['Elegibles'] = np.where(df_iterative['Reasignacion'] < df_iterative['Max'], 1, 0)
            
            # New sum of the base proportions, only for the eligible states
            total_basis_share = df_iterative.loc[df_iterative['Elegibles'] == 1, 'Base_Reparto_Original'].sum()

            # 5. Distribute the Net Remanente among Eligible States
            if total_basis_share > 0:
                # Repartir el remanente usando la base de reparto original, solo entre elegibles
                df_iterative['Reparto_neto'] = np.where(df_iterative['Elegibles'] == 1, 
                                                    (df_iterative['Base_Reparto_Original'] / total_basis_share) * remanente,
                                                    0)
            else:
                # No eligible states, or division by zero. Should not happen if remanente is non-zero.
                df_iterative['Reparto_neto'] = 0

            # 6. Calculate the New Working Allocation for the next iteration
            # Sum the capped/floored allocation + the new proportional share of the remanente
            df_iterative['Asignacion_Iterativa'] = df_iterative['Reasignacion'] + df_iterative['Reparto_neto']
            
            # The final result is the working column after all iterations are done
            df_iterative['Asignacion_Final'] = df_iterative['Asignacion_Iterativa']

        # --- END OF ITERATIVE REALLOCATION LOOP ---
        st.success(f'Proceso de rebalanceo completado (*{current_iteration} iteraciones*).')

        # Final Calculation and Display
        # Replace the old final columns with the new iterative result
        df_results['Asignacion_ajustada'] = df_iterative['Asignacion_Final']
        df_results['Var%_ajustada'] = (df_results['Asignacion_ajustada'] - df_results['Asignacion_2025']) / df_results['Asignacion_2025']


        # Display Final Adjusted Allocation Table (Table 5)
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

        st.markdown('#### Asignación Ajustada Final')
        st.dataframe(df_reasignacion2, hide_index=True, width=750)
        st.caption('Tabla 4. asignación ajustada final dentro de la banda especificada.')


        # --- 2.5 Visualización de Asignación Ajustada Final ---
        st.subheader('Comparativo de Asignaciones')
        st.markdown('''
        En la siguiente gráfica se observa la diferencia entre el monto de referencia (2025), el monto inicial calculado por el modelo (2026 Inicial) y el monto final ajustado por las bandas de control (2026 Final Ajustada).
        ''')

        # 1. Preparar los datos para el gráfico agrupado (Unpivot/Melt)
        df_chart = df_results[['Entidad_Federativa', 'Asignacion_2025', 'Asignacion_2026', 'Asignacion_ajustada']].copy()

        df_melted = pd.melt(
            df_chart,
            id_vars='Entidad_Federativa',
            value_vars=['Asignacion_2025', 'Asignacion_2026', 'Asignacion_ajustada'],
            var_name='Tipo_Asignacion',
            value_name='Monto'
        )

        # 2. Renombrar las categorías para una mejor leyenda y display
        df_melted['Tipo_Asignacion'] = df_melted['Tipo_Asignacion'].map({
            'Asignacion_2025': 'Asignación 2025 (Referencia)',
            'Asignacion_2026': 'Asignación 2026 (Inicial)',
            'Asignacion_ajustada': 'Asignación 2026 (Final Ajustada)'
        })

        # 3. Definir el mapa de colores para la gráfica
        color_map = {
            'Asignación 2025 (Referencia)': '#ddc9a3',    # Neutral/Referencia
            'Asignación 2026 (Inicial)': '#9f2241',       # Inicial (puede estar fuera de bandas)
            'Asignación 2026 (Final Ajustada)': '#235b4e' # Final (dentro de bandas)
        }

        # 4. Crear el gráfico de barras agrupado con Plotly Express
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
            hover_data={
                'Monto':':,.2f',
                },
        )

        # 5. Configuración de Trazas y Layout
        fig_final.update_traces(
            textposition='outside',
            texttemplate='$%{text:,.0f}', # Muestra valores sin decimales, en millones
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
                orientation="h",
                yanchor="bottom",
                y=.99,
                xanchor="right",
                x=1
            )
        )

        fig_final.update_xaxes(
            showgrid=True,
            tickangle=-60,
            title_font=dict(size=16, family='Noto Sans', color='#28282b'),
            tickfont=dict(size=14, family='Noto Sans', color='#4f4f4f'),
        )

        fig_final.update_yaxes(
            tickprefix="$",
            tickformat=',.0f',
            showgrid=True,
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
    