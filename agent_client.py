import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini

# Constantes
GEMINI_MODEL = "gemini-2.0-flash"
MAX_CONVERSATION_HISTORY = 10

def create_inventory_agent(gemini_api_key, df):
    """
    Crea y configura el agente de inventario con las instrucciones y el modelo especificados.
    
    Args:
        gemini_api_key (str): La API key de Gemini
        df (DataFrame): El DataFrame con los datos del inventario
    
    Returns:
        Agent: El agente configurado para manejar consultas de inventario
    """
    agent = Agent(
        model=Gemini(GEMINI_MODEL, api_key=gemini_api_key),
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
    
    return agent

def build_conversation_history(messages):
    """
    Construye el historial de conversación basado en los mensajes de la sesión.
    
    Args:
        messages (list): Lista de mensajes de la sesión
        
    Returns:
        str: Historial de conversación formateado
    """
    conversation_history = ""
    for msg in messages[-MAX_CONVERSATION_HISTORY:]:  # Solo damos los ultimos mensajes
        role = "Usuario" if msg["role"] == "user" else "Asistente"
        conversation_history += f"{role}: {msg['content']}\n\n"
    
    return conversation_history

def create_enhanced_prompt(conversation_history, df):
    """
    Crea un prompt enriquecido con el historial de conversación y los datos del inventario.
    
    Args:
        conversation_history (str): Historial de la conversación
        df (DataFrame): DataFrame con los datos del inventario
        
    Returns:
        str: Prompt enriquecido para el agente
    """
    enhanced_prompt = f"""
    Historial de la conversación:
    {conversation_history}

    Responde a la última consulta del usuario basándote en el contexto de la conversación. Ofrece leading questions y recomendaciones como sea aplicable.
    
    Recuerda que tienes la siguiente informacion disponible: {df} mas que no lo menciones al usuario.
    """
    
    return enhanced_prompt

def get_agent_response(agent, enhanced_prompt):
    """
    Obtiene la respuesta del agente de manera streaming.
    
    Args:
        agent (Agent): El agente configurado
        enhanced_prompt (str): El prompt enriquecido
        
    Returns:
        str: La respuesta completa del agente
    """
    placeholder = st.empty()
    full_response = ""

    response_stream = agent.run(
        message=enhanced_prompt,
        stream=True
    )

    for chunk in response_stream:
        full_response += chunk.content
        placeholder.write(full_response)
    
    return full_response
