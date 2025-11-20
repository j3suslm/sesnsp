# libraries
import streamlit as st
import numpy as np
import pandas as pd
import polars as pl
import io
import zipfile
from PIL import Image
import os
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
st.set_page_config(layout="wide", page_title="FORTAMUN App", page_icon=im)

# image and text
st.image('images/sesnsp.png', width=300)

# set title and subtitle
st.markdown("<h2><span style='color: #bc955c;'>Asignación del Fondo FORTAMUN</span></h2>",
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

    
# paso 1
#st.markdown("<h3><span style='color: #bc955c;'>Sube el archivo</span></h3>",
#    unsafe_allow_html=True)
    
# sidebar image and text
st.sidebar.image('images/sesnsp.png')
st.sidebar.markdown('''
    # Instrucciones   
    - Sube el archivo Excel
    - Calcula los 247 municipios
    - Descarga los resultados
''')
    

# widget para subir archivos
uploaded_file = st.file_uploader("", type='xlsx')

if uploaded_file is None:
    st.text('Sube el archivo con las variables para la asignación del fondo en formato csv.')
else: 
    st.text('Sube el archivo con las variables para la asignación del fondo en formato xlsx.')
    data = pl.read_excel(io.BytesIO(uploaded_file.getvalue()))
    st.success("Archivo cargado!")
    
    # data transformation
    data = data.rename({
                'CLAVE': 'Clave',
                'NOM_ENT': 'Estado',
                'CVE_MUN': 'Clave_mun',
                'NOM_MUN': 'Mun',
                'ASIGNACIÓN FORTAMUN ESTATAL': 'Asignacion_estatal',
                'POB_TOTAL': 'Pob',
                'TOTAL DE VIVIENDAS HABITADAS': 'Viviendas',
                'Municipios que informaron haber destinado recursos del FORTAMUN a la atención de necesidades directamente vinculadas con la seguridad pública': 'seg_pub',
                'Asignación municipal (Gacetas estatales)': 'Asignacion_municipal',
                'INCIDENCIA DELICTIVA DE ALTO IMPACTO': 'Incidencia_delictiva',
                '56 Municipios prioritarios': 'prioritarios',
            }).with_columns(
                (pl.col('Estado') + ', ' + pl.col('Mun')).alias('municipio'),
                (pl.col('Asignacion_municipal')*0.2).alias('seg_pub_20%'),
                pl.when(
                    (pl.col('seg_pub')==1)
                    & (pl.col('Asignacion_municipal') > pl.mean('Asignacion_municipal'))
            )
            .then(1)
            .otherwise(0)
            .alias('mayor_prom_nacl_mun')
        )

                    
    # calculo prom
    prom_alto_impacto_asignacion_mayor_media = (
        data.filter(
            (pl.col("seg_pub") == 1) & (pl.col("mayor_prom_nacl_mun") == 1)
        )
        .select(
            pl.col("Incidencia_delictiva").mean()
        )
        .item() # Use .item() to get the scalar result
    )

                    
    # data2
    data2 = data.with_columns(
        pl.when(
            (pl.col('Incidencia_delictiva') > prom_alto_impacto_asignacion_mayor_media)
            & (pl.col('seg_pub')==1)
        )
        .then(1)
        .otherwise(0)
        .alias('mayor_prom_inc_del'),
    ).with_columns(
        pl.when(
            (pl.col('mayor_prom_inc_del')==1)
            | (pl.col('prioritarios')==1)
        )
        .then(1)
        .otherwise(0)
        .alias('criterio_adicional1'),
        (pl.col('Incidencia_delictiva') - prom_alto_impacto_asignacion_mayor_media)
        .alias('dif_prom_nacl_inc_del'),  
    )
            
            
    # parametro
    def df_247(parameter: float, data_frame: pl.DataFrame) -> pl.DataFrame:
        df = data_frame.with_columns(
                pl.when(
                    (pl.col('seg_pub') == 0)
                    & (pl.col('mayor_prom_nacl_mun') == 0)
                    & (pl.col('mayor_prom_inc_del') == 0)
                    )
                .then(pl.lit(0))
                .when((pl.col('prioritarios') == 1) | (pl.col('criterio_adicional1') == 1))
                .then(pl.lit(1))
                .when((pl.col('criterio_adicional1') == 0) & (pl.col('dif_prom_nacl_inc_del') >= -parameter)) # iterate
                .then(pl.lit(1))
                .otherwise(pl.lit(0))
                .alias('prom_criterio_inc_del')
                ).filter(
                    pl.col('prom_criterio_inc_del')==1
                )
        return df

            
    # paso 2
    # info widget
    st.markdown("<h3><span style='color: #bc955c;'>Cálcula la muestra</span></h3>",
        unsafe_allow_html=True)
    #st.write("Selecciona un número para ajustar el `parametro` y obtener los 247 municipios requeridos.")
    # Create a slider for the 'parameter'
    # Adjust min_value, max_value, and value based on your data's 'dif_prom_nacl_inc_del' range
    parameter_value = st.number_input(
        min_value=0,
        max_value=2_000,
        value=int(-data2['dif_prom_nacl_inc_del'].mean()), # Default value
        label="Selecciona un valor",
        width=200,)
            

    # Run the filtering function with the slider's value
    municipios = df_247(parameter_value, data2)
    num_municipios = municipios.shape[0]

    # Display feedback based on the number of municipalities
    if num_municipios == 247:
        st.success(f'🎉 ¡Felicidades! La muestra contiene **{num_municipios}** municipios')
    elif num_municipios <= 246:
        st.info(f'El resultado contiene **{num_municipios}** municipios. Captura un número mayor en el slider para aumentar la muestra.')
    elif num_municipios >= 248:
        st.warning(f'El resultado contiene **{num_municipios}** municipios. Captura un número menor en el slider para reducir la muestra.')

    # paso 3
    # descargar archivo municipios
    st.markdown("<h3><span style='color: #bc955c;'>Descarga los resultados</span></h3>",
        unsafe_allow_html=True)
            
    # new dataframe results
    # resultados listado 247 municipios
    resultados = (
        municipios.select(['Clave','Estado','Clave_mun','Mun','Pob'])
        .rename({
            'Estado':'Entidad Federativa',
            'Mun':'Municipio',
            'Pob':'Población',
        })
    )
    # resumen
    estados = (
        municipios.select('Estado','Mun','Asignacion_estatal')
            .group_by('Estado', maintain_order=True)
                .agg(pl.col('Mun').count(),
                    pl.col('Asignacion_estatal').first())
    )

    municipios_por_estado = (
        data.select({'Estado','Mun'})
            .group_by('Estado', maintain_order=True).agg(pl.col('Mun').count())
    )

    resumen = (
        estados.join(municipios_por_estado, on='Estado')
            .rename({
                'Estado':'Entidad Federativa',
                'Mun':'Municipios seleccionados',
                'Asignacion_estatal':'FORTAMUN',
                'Mun_right':'Total de Municipios',
            })
            .select(['Entidad Federativa','Total de Municipios','FORTAMUN','Municipios seleccionados'])
    )
            

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "x") as csv_zip:
        resultados_csv_string = resultados.write_csv(file=None)
        resumen_csv_string = resumen.write_csv(file=None)
        csv_zip.writestr("resultados.csv", resultados_csv_string.encode('latin1'))
        csv_zip.writestr("resumen.csv", resumen_csv_string.encode('latin1'))

    # download button
    st.download_button(
        label="Resultados.zip",
        data=buf.getvalue(),
        file_name="fortamun_muestra_resultados.zip",
        mime="application/zip",
    )
    
        
    st.markdown('''
        ---
        *© Dirección General de Planeación*   
        *Elaborado por Jesús López Monroy*   
    ''')
