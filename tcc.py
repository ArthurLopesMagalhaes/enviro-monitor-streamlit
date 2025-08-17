import streamlit as st
import websocket
import threading
import queue
import time
import pandas as pd
from datetime import datetime
from streamlit.runtime.scriptrunner import add_script_run_ctx

# --- Configurações Iniciais do Streamlit ---
st.set_page_config(layout="wide")
st.title("Gráfico de Temperaturas em Tempo Real")

# --- Inicialização do Estado da Sessão ---
# Fila para as mensagens do WebSocket
if "message_queue" not in st.session_state:
    st.session_state.message_queue = queue.Queue(maxsize=100)

# Thread do WebSocket
if "websocket_thread" not in st.session_state:
    st.session_state.websocket_thread = None

# DataFrame para armazenar os dados do gráfico
if "temperature_data" not in st.session_state:
    st.session_state.temperature_data = pd.DataFrame(columns=['time', 'temperature']).set_index('time')

# --- Funções do WebSocket ---
def on_message(ws, message):
    st.session_state.message_queue.put(message)

def on_error(ws, error):
    print(f"Erro do WebSocket: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Conexão WebSocket fechada")

def on_open(ws):
    print("Conexão aberta e mensagem de subscrição enviada.")

def run_websocket():
    ws = websocket.WebSocketApp(
        "ws://localhost:8000/ws/temperature",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()

# --- Lógica de Inicialização da Thread ---
if st.session_state.websocket_thread is None or not st.session_state.websocket_thread.is_alive():
    print("Iniciando thread do WebSocket...")
    websocket_thread = threading.Thread(target=run_websocket, daemon=True)
    add_script_run_ctx(websocket_thread)
    websocket_thread.start()
    st.session_state.websocket_thread = websocket_thread
else:
    print("Thread do WebSocket já está rodando.")

# --- Interface e Loop de Atualização ---
# Placeholder para o gráfico
chart_placeholder = st.empty()

while True:
    if not st.session_state.message_queue.empty():
        try:
            message = st.session_state.message_queue.get()
            temperature = float(message)  # Converte a string da mensagem para float
            
            # Cria um novo ponto de dado com o timestamp atual
            new_data = pd.DataFrame(
                [{'time': datetime.now(), 'temperature': temperature}]
            ).set_index('time')

            # Anexa o novo dado ao DataFrame existente
            st.session_state.temperature_data = pd.concat(
                [st.session_state.temperature_data, new_data]
            )

            # Opcional: limita o DataFrame aos últimos 50 pontos para manter a performance
            st.session_state.temperature_data = st.session_state.temperature_data.tail(50)
            
            # Atualiza o gráfico com os dados mais recentes
            chart_placeholder.line_chart(st.session_state.temperature_data)
            
        except ValueError:
            print(f"Mensagem inválida recebida: {message}")
        
    time.sleep(0.1) # Pausa curta para evitar sobrecarga