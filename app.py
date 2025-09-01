import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection
from agno.agent import Agent
from agno.models.google import Gemini
from credentials import validate_token, TIME_TO_REFRESH

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
GEMINI_MODEL = "gemini-2.0-flash"
MAX_CONVERSATION_HISTORY = 10

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

conn = st.connection("gsheets", type=GSheetsConnection) # Establece una conexion con una Google Sheet con tal que esta sea publica y tenga permisos de read

df = conn.read( # Lee la informacion de la Google Sheet
    worksheet=SHEET_INVENTARIO, # Se va a la primera Sheet, el Inventario
    ttl=TIME_TO_REFRESH # Desactiva el caching con un time de refresh de 0para que siempre obtenga los datos mas recientes de la Sheet
)

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

def display_admin_dashboard(conn, df):
    input_token = st.text_input("Aquí va tu credencial:", type="password")

    if not input_token:
        st.info("Ingresa el token para acceder al panel de administrador")
        return #
    
    validation_result = validate_token(input_token, conn, df, st)

    if not validation_result:
        st.error("Token incorrecto")
        return

    st.success("Acceso concedido")
    st.dataframe(df)

    # Visualizamos el numero de cada producto
    st.write("### Cantidad por producto")
    vizualizador_productos_df = df.set_index("Producto")["Cantidad"]
    st.bar_chart(vizualizador_productos_df)

    # Visualizamos el numero de productos por marca
    st.write("### Cantidad total por marca")
    vizualizador_por_marca_df = df.set_index("Marca")["Cantidad"]
    st.bar_chart(vizualizador_por_marca_df, x_label="Marca", y_label="Cantidad")

    # Visualizamos la distribucion de productos por precio
    st.write("### Distribucion de productos por precio")
    vizualizador_por_precio = df.set_index("Precio")["Cantidad"]
    st.bar_chart(vizualizador_por_precio, x_label="Precios", y_label="Cantidad")

if st.session_state.show_admin:
    display_admin_dashboard(conn, df)

### CHATBOT CONFIG

agent = Agent(
    model=Gemini(GEMINI_MODEL, api_key=GEMINI_API_KEY),
    instructions=f"""
    Apenas el usuario envíe el primer mensaje, diles lo siguiente: Hola, bienvenido al inventario de Makers Tech. ¿Con qué te puedo ayudar? y si el primer mensaje del usuario es una pregunta, di el anterior mensaje sin preguntarles con que los puedes ayudar y responde su pregunta.
    
    Eres un manager de inventario y recomendador de productos experto. Respondes en castellano cordial al usuario.

    Estas a cargo de informa a usuarios de Makers Tech sobre el inventario de la Empresa. 
    
    Obtendras preguntas como:

    1. Cuantas computadoras hay disponibles actualmente?
    2. Puedes contarme mas sobre la computadora de la marca Apple?
    3. Cual es el precio de la computadora de la marca Apple?

    Ofrece la informacion de manera directa, clara, y sucinta.
    
    Si tu ussario hace una pregunta no relacionada al inventario de Makers Tech, pidele que aclare su intencion/pregunta. Si la repite, dile que no lo puedes ayudar.  

    Debes responder de acuerdo a la informacion que tienes disponible aqui: {df}

    """,
    markdown=True,
)

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
    conversation_history = ""
    for msg in st.session_state.messages[-MAX_CONVERSATION_HISTORY:]:  # Solo damos los ultimos 10 mensajes del usuario
        role = "Usuario" if msg["role"] == "user" else "Asistente"
        conversation_history += f"{role}: {msg['content']}\n\n"

    # Se crea un prompt dandole al modelo los ultimos mensajes y el DF para que no pierda contexto
    enhanced_prompt = f"""
    Historial de la conversación:
    {conversation_history}

    Responde a la última consulta del usuario basándote en el contexto de la conversación. Ofrece leading questions y recomendaciones como sea aplicable.
    
    Recuerda que tienes la siguiente informacion disponible: {df} mas que no lo menciones al usuario.
    """

    # Se envia al agente el enhanced_prompt con
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""

        response_stream = agent.run( # El metodo .run activa el agente con la libreria Agno
            message=enhanced_prompt,
            stream=True
        )

        for chunk in response_stream:
            full_response += chunk.content
            placeholder.write(full_response) # Mostramos la respuesta del agente conforme llega en ves de esperar a que termine

    # Mostramos la respuesta del agente
    st.session_state.messages.append({"role": "assistant", "content": full_response})
