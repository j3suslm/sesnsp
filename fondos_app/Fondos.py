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
import time


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
st.set_page_config(layout="wide", page_title="Fondos App", page_icon=im)

# image and text
st.image('images/sesnsp.png', width=300)

# set title and subtitle
st.markdown("<h1><span style='color: #691c32;'>Fondos Federales de Seguridad Pública</span></h1>",
    unsafe_allow_html=True)

# author, date
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


# tab layout
tab1, tab2 = st.tabs(['1.Introducción','2.Procedimiento',])

with tab1:
    st.markdown('''
        <div style="text-align: justify;">
                    
        ## ¿Cómo funciona esta aplicación?
            
        #### 1. Objetivo de la Aplicación
            
        Esta aplicación interactiva sirve como una herramienta de análisis de escenarios diseñada para simular la asignación de recursos de los Fondos
        para la Seguridad Pública: **FASP, FOFISP y FORTAMUN**.
            
        Su propósito es permitir a los tomadores de decisiones visualizar cómo diferentes prioridades de política pública —*expresadas a través de la asignación
        de ponderadores*— impactan directamente en la cantidad de fondos que recibe cada Entidad Federativa.
            
        Esta herramienta permite destacar las siguientes características:
            
        - **Transparencia**
            
            La lógica de asignación es visible y ajustable.
            
        - **Justificación**
            
            Las decisiones sobre la distribución de fondos se pueden respaldar con datos y escenarios explícitos.
            
        - **Facilidad de uso**
            
            El resultado final se recalcula automáticamente con cada ajuste hecho en la barra lateral.
            

        #### 2. El Corazón del cálculo
            
        - **El Índice Ponderado**
            
            La aplicación utiliza un sistema llamado Índice de Proporciones Directas Ponderadas para determinar el reparto de la mayor parte del presupuesto
            (el 94% restante, después de restar el monto base).
            
        - **Variables**
            
            Se utilizan 15 variables de desempeño y características estatales (Tasa Policial, Población, Incidencia Delictiva, etc).
            
        - **Normalización (La Medida de Necesidad)**
            
            Para cada variable, el desempeño de un estado se compara con el desempeño de todos los demás estados.
            
        - **Variables "Buenas" (Alto = Más fondos)**
            
            Si un estado tiene un alto nivel en una variable deseada (ej. Más Servicios Forenses), recibe una proporción mayor de los fondos de esa variable.
            
        - **Variables "Malas" (Alto = Menos fondos)**
            
            Si un estado tiene un alto nivel en una variable no deseada (ej. Más Sobrepoblación Penitenciaria), el modelo castiga ese valor, dándole una
            proporción menor de los fondos de esa variable.
            
        - **Ponderación (Prioridad)**
            
            Cada una de estas 15 variables tiene un "peso" asignado en la barra lateral (sliders).
            Este peso es su herramienta de política pública. 
            Si le da un peso de 0.50 a la Población, esa variable determinará la mitad del resultado.
            Si le da un peso de 0.01 a la Tasa Policial, esa variable tendrá un impacto marginal en el resultado.
            
            
        - **Asignación Inicial**
            
            El monto de la asignación inicial de cada estado es la suma de todas sus proporciones (la 'medida de necesidad') multiplicadas por los pesos
            definidos ('prioridades').
            
        #### 3. El Rebalanceo
            
        - **Aplicación de Bandas de Control**
            
            Una vez que el modelo calcula la asignación inicial (Asignación 2026 Inicial), esta debe pasar por un proceso de ajuste para cumplir con las
            Bandas de Control preestablecidas:
            
        - **Banda Superior**
            
            Es el porcentaje máximo en que la asignación de un estado puede crecer respecto al año anterior (2025).
            (Ej. Si se establece en 10%, ningún estado puede recibir más de un 10% adicional).
            
        - **Banda Inferior**
            
            Es el porcentaje mínimo en que la asignación de un estado puede crecer o decrecer respecto al año anterior (2025).
            (Ej. Si se establece en 0%, ningún estado puede recibir menos que el monto asignado en 2025).
            
        - **El Proceso Iterativo**
            
            La Asignación Inicial puede provocar que algunos estados queden por encima de la banda superior o por debajo de la banda inferior.
            Para corregir esto, la aplicación ejecuta un ciclo iterativo de reasignación:
            
        - **Superávit y Déficit**
            
            El sistema identifica los fondos excedentes de los estados que superaron el límite superior (supéravit) y los fondos faltantes para los
            estados que cayeron por debajo del límite inferior (déficit).
            
        - **Fondo Remanente**
            
            Los fondos excedentes se reúnen en un fondo común y, en primer lugar, se usan para cubrir los déficits.
            Lo que queda se llama remanente neto.
            
        - **Redistribución Continua**
            
            El remanente neto se reparte proporcionalmente entre sólo aquellos estados que no han sido "topados" por el límite superior.
            
        - **Repetición**
            
            Este proceso de topado, recolección y redistribución se repite automáticamente (*iteración*) hasta que el remanente por repartir es insignificante.
            Este método asegura que el monto total del Fondo no se altere, y que absolutamente todos los estados cumplan con los límites de variación definidos
            en la barra lateral, resultando en la Asignación 2026 Final Ajustada.
        </div>''',
        unsafe_allow_html=True)
            
    st.markdown('''
    ---
    *© Dirección General de Planeación*   
    *Elaborado por Jesús López Monroy*   
    ''')

with tab2:
    st.header('Procedimiento para la Asignacion de los Fondos')
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

    st.markdown('''
    ---
    *© Dirección General de Planeación*   
    *Elaborado por Jesús López Monroy*   
    ''')

