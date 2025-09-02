import streamlit as st
from streamlit_gsheets import GSheetsConnection


# Credentials Constant
CREDENTIALS_COLUMN_INDEX = 0
CREDENTIALS_ROW_COUNT = 2
CREDENTIAL_CELL_ROW = 0
CREDENTIAL_CELL_COL = 0
SHEET_CREDENCIALES = "960299724"
TIME_TO_REFRESH = 0 


def validate_token(input_token):

    conn = st.connection("gsheets", type=GSheetsConnection)

    credentials_sheet = conn.read(
        worksheet=SHEET_CREDENCIALES,  
        ttl=TIME_TO_REFRESH,
        usecols=[CREDENTIALS_COLUMN_INDEX], # Se limita a la primera columna
        nrows=CREDENTIALS_ROW_COUNT # Se limita a las dos primeras filas
    )

    stored_token = credentials_sheet.iloc[CREDENTIAL_CELL_ROW, CREDENTIAL_CELL_COL] # Accede la celda donde está la credencial

    stored_token = stored_token.strip()
    input_token = input_token.strip()

    if input_token != stored_token:
        return False

    return True


    