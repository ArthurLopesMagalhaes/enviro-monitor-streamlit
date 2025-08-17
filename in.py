import streamlit as st
import websocket
import threading
import queue
from streamlit.runtime.scriptrunner import add_script_run_ctx
import pandas as pd
import json
from datetime import datetime, timezone

st.set_page_config(layout="wide")

# Initialize session state variables
if "message_queue" not in st.session_state:
    st.session_state.message_queue = queue.Queue(maxsize=1000)

if "websocket_thread" not in st.session_state:
    print("WebSocket thread not found")
    st.session_state.websocket_thread = None

if "dataframe" not in st.session_state:
    utc_now = datetime.now(timezone.utc)
    st.session_state.dataframe = [
        {"symbol": "EURUSD", "time": utc_now, "bid": "000000.0000", "ask": "000000.0000", "mid": "000000.0000", "spread": 0, "h_spread" : 0, "l_spread" : 99999999 },
        {"symbol": "GBPUSD", "time": utc_now, "bid": "000000.0000", "ask": "000000.0000", "mid": "000000.0000", "spread": 0, "h_spread" : 0, "l_spread" : 99999999 },
        {"symbol": "NZDUSD", "time": utc_now, "bid": "000000.0000", "ask": "000000.0000", "mid": "000000.0000", "spread": 0, "h_spread" : 0, "l_spread" : 99999999 },
        {"symbol": "USDJPY", "time": utc_now, "bid": "000000.0000", "ask": "000000.0000", "mid": "000000.0000", "spread": 0, "h_spread" : 0, "l_spread" : 99999999 },
        {"symbol": "USDCHF", "time": utc_now, "bid": "000000.0000", "ask": "000000.0000", "mid": "000000.0000", "spread": 0, "h_spread" : 0, "l_spread" : 99999999 },
        {"symbol": "AUDUSD", "time": utc_now, "bid": "000000.0000", "ask": "000000.0000", "mid": "000000.0000", "spread": 0, "h_spread" : 0, "l_spread" : 99999999 },
        {"symbol": "USDCAD", "time": utc_now, "bid": "000000.0000", "ask": "000000.0000", "mid": "000000.0000", "spread": 0, "h_spread" : 0, "l_spread" : 99999999 },
        {"symbol": "USDNOK", "time": utc_now, "bid": "000000.0000", "ask": "000000.0000", "mid": "000000.0000", "spread": 0, "h_spread" : 0, "l_spread" : 99999999 },
        {"symbol": "USDSEK", "time": utc_now, "bid": "000000.0000", "ask": "000000.0000", "mid": "000000.0000", "spread": 0, "h_spread" : 0, "l_spread" : 99999999 },
    ]

# Streamlit UI setup
st.title("Real-Time WebSocket Client")
# placeholder = st.empty()  # Placeholder for displaying messages
df_placeholder = st.dataframe(pd.DataFrame(st.session_state.dataframe))

def on_message(ws, message):
    # if "message_queue" in st.session_state:
    st.session_state.message_queue.put(message)
    print(st.session_state.message_queue.qsize())
    # print(message)

def on_error(ws, error):
    print(f"WebSocket Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("WebSocket connection closed")

def on_open(ws):
    ws.send('{"userKey": "YOUR API KEY", "symbol":"EURUSD,GBPUSD,AUDUSD,NZDUSD,USDJPY,USDCHF,USDCAD,USDNOK,USDSEK"}')

def run_websocket():
    ws = websocket.WebSocketApp(
        "wss://marketdata.tradermade.com/feedadv",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever()
    print("WebSocket thread started")

def get_list_to_update_session_state(json_message_l, list_of_pairs):
    for index, value in enumerate(list_of_pairs):
        if value["symbol"] == json_message_l["symbol"]:
            epoch_seconds = int(json_message_l["ts"]) / 1000
            datetime_str = datetime.fromtimestamp(epoch_seconds, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            # print("index ----->", index)
            
            list_of_pairs[index]["time"] = datetime_str
            list_of_pairs[index]["bid"] = json_message_l["bid"]
            list_of_pairs[index]["ask"] = json_message_l["ask"]
            list_of_pairs[index]["mid"] = json_message_l["mid"]
            
            spread = float(json_message_l["ask"]) - float(json_message_l["bid"])
            
            if "JPY" in value["symbol"] or "NOK" in value["symbol"] or "SEK" in value["symbol"]:
                spread = round(spread * 100, 2)
            else:
                spread = round(spread * 10000, 2)
            
            list_of_pairs[index]["spread"] = str(spread) + ' pips'
            
            if list_of_pairs[index]["h_spread"] < spread:
                list_of_pairs[index]["h_spread"] = spread
            if list_of_pairs[index]["l_spread"] > spread:
                list_of_pairs[index]["l_spread"] = spread

            break
            
    return list_of_pairs


if st.session_state.websocket_thread is None or not st.session_state.websocket_thread.is_alive():
    print("Starting WebSocket connection...")
    websocket_thread = threading.Thread(target=run_websocket, daemon=True)
    add_script_run_ctx(websocket_thread)
    websocket_thread.start()
    st.session_state.websocket_thread = websocket_thread

# Process messages from the queue and update UI
if st.session_state.message_queue.empty():
    # placeholder.write("Waiting for messages...")
    print("Waiting for messages...")
else:
    pass

while True:
    while not st.session_state.message_queue.empty():
        message = st.session_state.message_queue.get()
        # placeholder.write(message)
        # print(message)
        try:
            json_message = json.loads(message)
            st.session_state.dataframe = get_list_to_update_session_state(json_message,st.session_state.dataframe)
            df_placeholder.dataframe(st.session_state.dataframe,
                                     # {"symbol": "EURUSD", "time": utc_now, "bid": "000000.0000", "ask": "000000.0000",
                                     #  "mid": "000000.0000", "spread": 0, "Highest Spread": 0, "Lowest Spread": 99999999}
                column_config={
                    "symbol": st.column_config.TextColumn(label="Symbol", width="small"),
                    "time": st.column_config.TextColumn(label="Time", width="medium"),
                    "bid": st.column_config.NumberColumn(label="Bid", width="small"),
                    "ask": st.column_config.NumberColumn(label="Ask", width="small"),
                    "mid": st.column_config.NumberColumn(label="Mid", width="small"),
                    "spread": st.column_config.TextColumn(label="Spread", width="small"),
                    "h_spread": st.column_config.NumberColumn(label="High", width="small"),
                    "l_spread": st.column_config.NumberColumn(label="Low", width="small"),
                },
                use_container_width=True)  # Optional: Makes the table fill the container width)
        except Exception as e:
            print(e)
            pass