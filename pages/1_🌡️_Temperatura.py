import websocket
import threading
import json

# Função de callback quando receber nova mensagem
def on_message(ws, message):
    data = json.loads(message)

    
    # Log no console
    print(f"Mensagem recebida: {data}")

# Função de inicialização do WebSocket
def iniciar_websocket():
    ws = websocket.WebSocketApp("wss://d8c0-2804-14c-fc86-800f-d52c-c43-891c-2959.ngrok-free.app/ws/temperature",
                                on_message=on_message)
    ws.run_forever()


# Manter o script ativo
while True:
    pass
