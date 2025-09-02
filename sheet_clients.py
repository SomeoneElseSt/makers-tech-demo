import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Constantes
SHEET_INVENTARIO = "0"
TIME_TO_REFRESH = 0 

def inventory_sheet_client():
    conn = st.connection("gsheets", type=GSheetsConnection) # Establece una conexion con una Google Sheet con tal que esta sea publica y tenga permisos de read

    return conn.read( # Lee la informacion de la Google Sheet
    worksheet=SHEET_INVENTARIO, # Se va a la primera Sheet, el Inventario
    ttl=TIME_TO_REFRESH # Desactiva el caching con un time de refresh de 0para que siempre obtenga los datos mas recientes de la Sheet
    )