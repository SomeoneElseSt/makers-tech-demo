import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from credentials import validate_token, TIME_TO_REFRESH
from admin_vizualizations import per_product_quantity_vizualization, per_product_brand_vizualization, per_product_price_vizualization
from sheet_clients import inventory_sheet_client
from agent_client import create_inventory_agent, build_conversation_history, create_enhanced_prompt, get_agent_response

### RECS

#Plataforma: Makers Tech

#Presentacion: Chat Interface

#Funcion: Responder preguntas sobre inventario, caracteristicas, precios.

#Modo Administrador: Ver DB de inventario, vizualizaciones, etc.

### COMO LOCALHOST

# Debes tener lo siguiente:

# Primero crea un virtual environment con uv venv si usas uv o con Python python -m venv .venv y activalo con source .venv/bin/activate en Mac o .\.venv\Scripts\activate

# Instala las dependencias con uv pip install -r requirements.txt    # o simplemente: pip install -r requirements.txt

# Un archivo secrets.toml debajo del siquiente directorio: root/.streamlit.secrets.toml

# El root es el directorio donde abriste app.py

# En secrets.toml debes tener una GEMINI_API_KEY=str primero

# Despues debes tener un header [connections.gsheets] y una variable spreadsheet=str con el link de una Google Sheet que tenga view-permissions y que sea publica

# CONSTANTES
SHEET_INVENTARIO = "0"

# Revisamos si la Gemini API key esta en el secrets.toml y si no lo esta le hacemos saber al usario que hay un error
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

if not GEMINI_API_KEY or GEMINI_API_KEY.strip() == "":
    st.error("El servicio de Chatbot no esta disponible. Contacta al administrador de la pagina.")
    st.stop()

# Revisamos si la Google Sheet esta en el secrets.toml y si no lo esta le hacemos saber al usario que hay un error
GSHEETS_SPREADSHEET = st.secrets["connections"]["gsheets"]["spreadsheet"]

if not GSHEETS_SPREADSHEET or GSHEETS_SPREADSHEET.strip() == "":
    st.error("El servicio de inventario no esta disponible. Contacta al administrador de la pagina.")
    st.stop()


### STREAMLIT CONFIG
st.set_page_config(
    initial_sidebar_state="collapsed", #Mantiene la Sidebar Collapsada por Default
    layout="wide",
    page_title="My Inventario",
    page_icon="📝"
)

st.title("Makers Tech | Inventario Interactivo")
st.header("¡Hola! 👋")
st.write("Bienvenido al inventario de Makers Tech. Abajo puedes preguntarle a un bot lo que quieras sobre el inventario de Makers Tech.")
st.write("De igual manera, si eres administrador, presiona el botón de abajo e ingresa la credencial en la segunda página de Google Sheets.")

### GOOGLE SHEETS CONFIG PARA DB MANAGEMENT USANDO GSHEETSCONNECTION

df = inventory_sheet_client()

pd.set_option('display.max_colwidth', None) # Importante: Hay que expandir el DF manualmente para que el Agente pueda leer el texto en las columnas y filas completo
pd.set_option('display.max_columns', None) # Tanto en las columnas
pd.set_option('display.max_rows', None) # Como en las filas

### DF DEBUGGING PRINTS

#print(df)
#st.dataframe(df) #Esto hace el DF aparecer en el front-end, para testing

### ADMIN PANEL CONFIG

# Toggle para mostrar la sección de administrador
if "show_admin" not in st.session_state:
    st.session_state.show_admin = False

# Sección de administrador solo visible tras presionar el botón
if not st.session_state.show_admin:
    if st.button("👨‍💻Modo Administrador", key="open_admin"):
        st.session_state.show_admin = True
        st.rerun()
# Si el boton de Modo Administrador ya se presiono hay un button para cerrar el modo de administracion de completo
else:
    if st.button("💻 Cerrar Modo Administrador", key="close_admin"):
        st.session_state.show_admin = False
        st.rerun()

def display_admin_dashboard(df):
    input_token = st.text_input("Aquí va tu credencial:", type="password")

    if not input_token:
        st.info("Ingresa el token para acceder al panel de administrador")
        return #
    
    validation_result = validate_token(input_token)

    if not validation_result:
        st.error("Token incorrecto")
        return

    st.success("Acceso concedido")
    st.dataframe(df)

    # Visualizamos el numero de cada producto
    st.write("### Cantidad por producto")
    per_product_quantity_vizualization(df)

    # Visualizamos el numero de productos por marca
    st.write("### Cantidad total por marca")
    per_product_brand_vizualization(df)

    # Visualizamos la distribucion de productos por precio
    st.write("### Distribucion de productos por precio")
    per_product_price_vizualization(df)

if st.session_state.show_admin:
    display_admin_dashboard(df)

### CHATBOT CONFIG

agent = create_inventory_agent(GEMINI_API_KEY, df)

### CHATBOT UI

# Empezamos una lista vacia de mensajes si no existe
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostramos cada mensaje en la session_state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Una casilla para que el usuario escriba su pregunta
if prompt := st.chat_input("Preguntale al bot sobre que tenemos en inventario, precios, y recomendaciones de productos."):
    # Anadimos el mensaje del usuario a la session_state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Mostramos el mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)

    # Para que el modelo tenga memoria, creamos una historia de conversacion en base a los ultimos mensajes
    conversation_history = build_conversation_history(st.session_state.messages)

    # Se crea un prompt dandole al modelo los ultimos mensajes y el DF para que no pierda contexto
    enhanced_prompt = create_enhanced_prompt(conversation_history, df)

    # Se envia al agente el enhanced_prompt con
    with st.chat_message("assistant"):
        full_response = get_agent_response(agent, enhanced_prompt)

    # Mostramos la respuesta del agente
    st.session_state.messages.append({"role": "assistant", "content": full_response})
