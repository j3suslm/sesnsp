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

# set title and subtitle
st.markdown("<h1><span style='color: #691c32;'>Asignación del Fondo FOFISP</span></h1>",
    unsafe_allow_html=True)

# author, date
st.caption('Jesús LM')
st.caption('Octubre, 2025')


# authentication by password
password = os.getenv('MY_PASSWORD')
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

with st.sidebar.expander('Bandas'):
    # presupuesto estimado widget
    presupuesto = st.number_input(
        'Presupuesto estimado',
        value=1_155_443_263.97, placeholder='Monto del fondo', key='Presupuesto estimado', format="%f", 
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
        value=0.1, key='Limite inferior',
    )


# sliders for weights
# Los valores se limitan para que la suma siempre sea 1
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

    # asegurar que la suma sea 1.0 y ajustar el peso del último slider para cuadrar
    total_sum = w_pob + w_edo_fza + w_var_incidencia_del + w_academias
    #st.sidebar.markdown('---')
    formatted_sum = f"{total_sum:.0%}"
    st.markdown(f'Suma: {formatted_sum}')


    if total_sum != 1.0:
        # ajustar el peso más pequeño (o cualquier otro) para que sume 1
        w_pob = w_pob / total_sum
        w_edo_fza = w_edo_fza / total_sum
        w_var_incidencia_del = w_var_incidencia_del / total_sum
        w_academias = w_academias / total_sum
        # Redondeamos para fines de presentación, aunque los cálculos usan el valor exacto
        #st.markdown(f"**Suma Ajustada:** {w_pob:.2f} + {w_edo_fza:.2f} + {w_var_incidencia_del:.2f} + {w_academias:.2f} = 1.00")

weights = {
    'Población': w_pob,
    'Tasa_policial': w_edo_fza,
    'Var_incidencia_del': w_var_incidencia_del,
    'Academias': w_academias,
}


# upload final variables dataset
# widget para subir archivos
uploaded_file = st.file_uploader("", type=['csv'], )

if uploaded_file is None:
    st.text('Sube el archivo con las variables para la asignación del fondo en formato csv.')
else:
    data = pd.read_csv(io.BytesIO(uploaded_file.getvalue()))    

    # tabla de indicadores
    indicadores_fofisp = pd.read_csv('data/indicadores_fofisp.csv')
    indicadores_fofisp['Categoría'] = indicadores_fofisp['Categoría'].fillna('')
    indicadores_fofisp['Ponderación_categoría'] = indicadores_fofisp['Ponderación_categoría'].fillna(0)

    # tabla formateada
    indicadores = (
        GT(indicadores_fofisp)
        .cols_hide(columns='Monto_asignado')
        .tab_stub()
        .tab_header(
            title=md('Fondo para el Fortalecimiento de las Instituciones de Seguridad Pública'),
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
        A continuación se enlistan los indicadores subyacentes para la asignación del <b>Fondo para el Fortalecimiento
        de las Instituciones de Seguridad Pública</b> (FOFISP) <b>2026</b>.
        </div>''',
         unsafe_allow_html=True)

        st.html(indicadores)
        st.caption('Tabla 1. Indicadores utilizados para la asignación de fondos y ponderaciones predeterminadas.')

        st.markdown('''
        ##### ¿Cómo funciona esta aplicación?
        ''')

        st.markdown('''
        <div style="text-align: justify;">
        Esta aplicación interactiva sirve como una herramienta de análisis de escenarios que utiliza un <i>Índice de Asignación de Seguridad Pública Normalizado</i>.
        
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

        [Fondo para el Fortalecimiento de las Instituciones de Seguridad Pública (FOFISP) 2025](https://www.gob.mx/sesnsp/acciones-y-programas/fondo-para-el-fortalecimiento-de-las-instituciones-de-seguridad-publica-fofisp?state=published)
        
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

        
        # --- Funciones de Cálculo del Índice ---
        def min_max_normalize(series, direction='positive'):
            """
            Normaliza una serie de datos entre 0 y 1 usando el método Min-Max.
            Si la dirección es 'negativa', se invierte (Alto = Malo se convierte en Alto = Bueno).
            """
            min_val = series.min()
            max_val = series.max()

            if max_val == min_val:
                return pd.Series(0.5, index=series.index) # Retorna 0.5 si todos los valores son iguales

            if direction == 'positive':
                # (X - Min) / (Max - Min) -> Un valor más alto resulta en una puntuación más alta
                return (series - min_val) / (max_val - min_val)
            elif direction == 'negative':
                # (Max - X) / (Max - Min) -> Un valor más bajo (mejor) resulta en una puntuación más alta
                return (max_val - series) / (max_val - min_val)
            else:
                raise ValueError("La dirección debe ser 'positiva' o 'negativa'")

        def calculate_index(df, weights):
            """Calcula el Índice Compuesto Normalizado."""

            # 1. Normalización de Variables
            # variables positivas
            df['Pob_norm'] = min_max_normalize(df['Población'], direction='positive')
            df['Tasa_policial_norm'] = min_max_normalize(df['Tasa_policial'], direction='positive')
            df['Academias_norm'] = min_max_normalize(df['Academias'], direction='positive')

            # variables negativas (menos es mejor, por lo tanto, se invierte)
            df['Var_incidencia_del_norm'] = min_max_normalize(df['Var_incidencia_del'], direction='negative')

            # 2. Aplicación de Ponderadores
            df['Indice Normalizado'] = (
                df['Pob_norm'] * weights['Población'] +
                df['Tasa_policial_norm'] * weights['Tasa_policial'] +
                df['Var_incidencia_del_norm'] * weights['Var_incidencia_del'] +
                df['Academias_norm'] * weights['Academias']
            )

            # El índice final también se normaliza a un rango de 0 a 1 para asegurar comparabilidad
            df['Indice Final (0-1)'] = min_max_normalize(df['Indice Normalizado'], direction='positive')
            epsilon = 0.01
            df['Indice Final (Corrimiento)'] = (df['Indice Final (0-1)'] * (1 - epsilon)) + epsilon

            return df

        

        # change index to start at 1, must specify last limit
        fofisp_datos_entrada = data.copy()
        data.index = pd.RangeIndex(start=1, stop=33, step=1)
        data['Var_incidencia_del'] = data['Var_incidencia_del']*100
        fofisp_datos_entrada2 = (
            data
                .style.format({
                    'Población': '{:,.2f}',
                    'Var_incidencia_del':'{:.2f}%',
                    'Tasa_policial':'{:.2f}',
                    'Asignacion_2025': '${:,.2f}',
                    })
                )

        st.dataframe(fofisp_datos_entrada2, use_container_width=True)
        st.caption('Tabla 2. Variables utilizadas en el modelo para la asignación de fondos.')


                # --- Cálculo y Visualización ---
        # Calcular el índice
        df_results = calculate_index(fofisp_datos_entrada, weights)
        
        # Mostrar la tabla final de resultados
        st.subheader("2.2 Resultados")
        # reckon end allocated amount
        # sum final index
        total_indice = df_results['Indice Final (Corrimiento)'].sum()
        # create share weights
        df_results['Reparto'] = df_results['Indice Final (Corrimiento)'] / total_indice
        # Var%funds
        df_results['Asignacion_2026'] = df_results['Reparto'] * presupuesto
        # validate allocated budget
        #stVar%dataframe(df_results[['Asignacion_2026']].sum()) -Var%    

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

        # Gráfico de barras de asignacion de fondos
        fig = px.bar(
            df_results,
            x='Entidad_Federativa',
            y='Asignacion_2026',
            text='Asignacion_2026',
            title=f"Población={w_pob*100:.0f}%, Tasa policial={w_edo_fza*100:.0f}%, Incidencia delictiva={w_var_incidencia_del*100:.0f}%, Academias={w_academias*100:.0f}%",
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
        Se estableció una banda de ±10% para el importe asignado 2026 en relación al asignado 2025.
        
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
        st.caption('Tabla 3. Entidades Federativas por encima/debajo de la banda de ±10%')

        st.markdown('''
        En la siguiente tabla, se resume el superavit y deficit totales, respecto a la banda de 10% y el remanente a repartir.
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
        total_basis = df_results['Elegibles'].sum()
        # 2. Calculate the proportional share of the net fund
        if total_basis > 0:
            df_results['Reparto_neto'] = (df_results['Elegibles'] / total_basis) * remanente
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
        st.caption('Tabla 5. Reasignación de Remanente por Entidad Federativa con banda de ±10%')

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
            title=f"Reasignación de Fondos por Entidad Federativa después de Remanente de la banda de ±10%",
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
        fig2.show()
        st.plotly_chart(fig2, use_container_width=True)

        
        st.markdown('---')
        st.markdown('*© Dirección General de Planeación*')


    with tab3:
        st.header('3. Nota metodológica')
        st.markdown("""
        1. **Normalización:** Todos los indicadores se escalan al rango [0, 1].
        2. **Agregación:** Se aplica la suma ponderada de las variables normalizadas.
        3. **Corrimiento estadístico:** Se suma un valor epsilon para evitar coeficientes nulos.
        4. **Repartición:** Se reparte el presupuesto entre las Entidades Federativas según el valor de las ponderaciones de los indicadores.
        """)

        st.subheader('3.1 Normalización')
        st.latex(r'''
        V_{i,j} = \frac{X_{i,j} - X_{i, \min}}{X_{i, \max} - X_{i, \min}}\\
        \text{ }\\
        \text{donde:}\\
        \text{ }\\
        V_{i,j} = \text{Valor normalizado del indicador i para la Entidad Federativa j}\\
        X_{i,j} = \text{Indicador i de la Entidad Federativa j}\\
        ''')
        st.markdown('`Inversión: Las variables negativas se invierten para que una tasa baja resulte en un valor normalizado alto (cercano a 1).`')
        
        st.subheader('3.2 Agregación del Índice')
        st.latex(r'''
        I_j = \sum_{i=1}^{n}( V_{i,j} \times W_i)\\
        \text{ }\\
        \text{donde:}\\
        \text{ }\\
        I_j = \text{Índice de asignación de fondos para la Entidad Federativa j}\\
        V_{i,j} = \text{Valor normalizado del indicador i para la Entidad Federativa j}\\
        W_i = \text{Ponderación del indicador i}\\
        ''')
        st.markdown('`Re-escalado: El índice final se re-escala [0, 1] para facilitar la interpretación del rendimiento relativo.`')

        st.subheader('3.3 Corrimiento Estadístico')
        st.markdown('''
        La fórmula opera sobre el índice normalizado (con rango [0,1]) usando una constante pequeña y positiva, ϵ.

        ##### 3.3.1  Compresión del Rango: (indice_normalizado * (1−ϵ))

        **Objetivo: Comprimir el rango de los valores normalizados.**

        - Multiplicar por un factor ligeramente menor que 1, como (1−0.0001)=0.9999.
        - El rango original [0,1] se convierte en [0,1−ϵ].
        - El valor mínimo (0) se mantiene en 0×(1−ϵ)=0.
        - El valor máximo (1) se reduce a 1×(1−ϵ)=1−ϵ.
        
        ##### 3.3.2 Corrimiento hacia arriba (Shift): +ϵ

        **Objetivo: Desplazar todo el conjunto de datos hacia arriba por la cantidad ϵ.**

        Se suma ϵ al resultado del paso anterior.

        - El mínimo, que era 0, ahora es 0+ϵ=ϵ.
        - El máximo, que era 1−ϵ, ahora es (1−ϵ)+ϵ=1.
        
        
        |Indice normalizado|Transformación|Valor Final|
        |:---:|:---:|:---:|
        |0 (mínimo)|(0 * (1−ϵ)) + ϵ|ϵ|
        |1 (máximo)|(1 * (1−ϵ)) + ϵ|1|

        ''')

        st.subheader('3.4 Repartición del Presupuesto')
        st.markdown('''
        Se calcula la participación porcentual de cada Entidad Federativa en el índice total
        y se distribuye el fondo total entre cada una de acuerdo a su participación porcentual.
        ''')
        
        st.subheader('3.5 Repartición del Remanente')
        st.markdown('''
        <div style="text-align: justify;">
        Se aplican bandas del ±10% respecto al importe asignado del ejercicio anterior inmediato y se obtiene 
        el total de importe sobrante y faltante aplicando estas bandas.
        Posteriormente, se reparte este remanente entre las diversas Entidades Federativas para que ninguna rebase
        las bandas del ±10%.
        </div>''',
        unsafe_allow_html=True)

        st.markdown('---')
        st.markdown('*© Dirección General de Planeación*')

        # Inject custom CSS to left-align KaTeX elements
        st.markdown(
            """
            <style>
            .katex-html {
                text-align: left;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    with tab4:

        st.header('4. Nota técnica')
        st.markdown("""
        En este apartado, se muestra la sábana de datos con todos las fases del cálculo de asignación de fondos,
        incluyendo las bandas y reasignación del remanente.

        Por otra parte, se anexa hoja de cálculo en formato xlsx (Excel) con el desarrollo mencionado.
        """)

        st.dataframe(df_results)

        st.markdown("[Hoja de cálculo](https://sspcgob-my.sharepoint.com/:x:/g/personal/oscar_avila_sspc_gob_mx/ESy9dnRh6AdJgNEwSx5-udMBcKgLhTP29mnxWhgDvYF6WA?e=l1O8Xl)")
        
        st.markdown('---')
        st.markdown('*© Dirección General de Planeación*')
