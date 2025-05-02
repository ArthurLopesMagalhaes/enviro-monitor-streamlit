import streamlit as st
import random
import pandas as pd
import time

st.set_page_config(layout="wide")
st.title("🌡️ Monitoramento de Temperatura")

placeholder = st.empty()
historico = []

for _ in range(100):
    valor = round(random.uniform(20, 30), 2)
    historico.append({"valor": valor, "tempo": pd.Timestamp.now()})
    if len(historico) > 50:
        historico.pop(0)

    df = pd.DataFrame(historico).set_index("tempo")

    with placeholder.container():
        st.subheader("📈 Gráfico de Linha")
        st.line_chart(df)

        st.subheader("📊 Gráfico de Barras")
        st.line_chart(df)

        st.subheader("🟫 Gráfico de Área")
        st.line_chart(df)

    time.sleep(1)
