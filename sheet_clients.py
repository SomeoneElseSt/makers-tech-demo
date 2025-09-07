import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Constantes
SHEET_INVENTARIO = "0"
TIME_TO_REFRESH = 0 

def inventory_sheet_client():
    """
    Establece conexión con Google Sheets y obtiene los datos del inventario sin configuración de pandas.
    
    Returns:
        DataFrame: Los datos del inventario desde Google Sheets
    """
    conn = st.connection("gsheets", type=GSheetsConnection) # Establece una conexion con una Google Sheet con tal que esta sea publica y tenga permisos de read

    return conn.read( # Lee la informacion de la Google Sheet
    worksheet=SHEET_INVENTARIO, # Se va a la primera Sheet, el Inventario
    ttl=TIME_TO_REFRESH # Desactiva el caching con un time de refresh de 0para que siempre obtenga los datos mas recientes de la Sheet
    )

def configure_pandas_display():
    """
    Configura las opciones de display de pandas para que el agente pueda leer 
    el texto completo en las columnas y filas del DataFrame.
    """
    pd.set_option('display.max_colwidth', None) # Importante: Hay que expandir el DF manualmente para que el Agente pueda leer el texto en las columnas y filas completo
    pd.set_option('display.max_columns', None) # Tanto en las columnas
    pd.set_option('display.max_rows', None) # Como en las filas

def get_configured_inventory_dataframe():
    """
    Obtiene el DataFrame del inventario y configura pandas para una visualización completa.
    Esta función combina la obtención de datos y la configuración de pandas.
    
    Returns:
        DataFrame: DataFrame del inventario configurado para visualización completa
    """
    # Configura pandas antes de obtener los datos
    configure_pandas_display()
    
    # Obtiene los datos del inventario
    df = inventory_sheet_client()
    
    return df