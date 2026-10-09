"""
Dashboard simple del lakehouse de FilaYa.

Correr:
    streamlit run dashboard.py
"""

import duckdb
import streamlit as st

st.set_page_config(page_title="FilaYa - Análisis de eventos", layout="wide")
st.title("📊 FilaYa - Análisis de mercado")

con = duckdb.connect("warehouse.duckdb", read_only=True)

st.header("Eventos por nivel de riesgo de fila")
riesgo = con.execute("""
    SELECT riesgo_fila_estimado, COUNT(*) AS cantidad
    FROM gold.eventos_riesgo_fila
    GROUP BY 1
    ORDER BY 2 DESC
""").df()
st.bar_chart(riesgo.set_index("riesgo_fila_estimado"))

st.header("Próximos eventos de alto riesgo de fila")
proximos = con.execute("""
    SELECT fecha, artista, evento, venue, capacidad_venue
    FROM gold.eventos_riesgo_fila
    WHERE riesgo_fila_estimado = 'alto'
    ORDER BY fecha
""").df()
st.dataframe(proximos, use_container_width=True)

st.header("Todos los eventos (tabla completa)")
todos = con.execute("SELECT * FROM silver.eventos ORDER BY fecha").df()
st.dataframe(todos, use_container_width=True)

con.close()
