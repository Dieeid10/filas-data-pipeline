"""
Silver -> Gold
--------------
Genera la tabla final "eventos_riesgo_fila": clasifica cada evento
según su probabilidad de generar fila física relevante, cruzando
capacidad del venue y (cuando exista) datos de menciones sociales.

Correr desde la carpeta pipeline/:
    python transform_gold.py
"""

import duckdb

DB_PATH = "../warehouse.duckdb"


def main():
    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS gold")

    # Regla simple de clasificación de "riesgo de fila" en base a capacidad.
    # Se puede sofisticar más adelante sumando velocidad de venta,
    # menciones en redes, etc.
    con.execute("""
        CREATE OR REPLACE TABLE gold.eventos_riesgo_fila AS
        SELECT
            fecha,
            anio,
            artista,
            evento,
            venue,
            capacidad_venue,
            CASE
                WHEN capacidad_venue >= 10000 THEN 'alto'
                WHEN capacidad_venue >= 3000  THEN 'medio'
                ELSE 'bajo'
            END AS riesgo_fila_estimado
        FROM silver.eventos
        ORDER BY fecha
    """)

    resumen = con.execute("""
        SELECT riesgo_fila_estimado, COUNT(*) AS cantidad_eventos
        FROM gold.eventos_riesgo_fila
        GROUP BY 1
        ORDER BY 2 DESC
    """).df()

    con.close()
    print("Gold actualizado. Resumen por nivel de riesgo:")
    print(resumen)


if __name__ == "__main__":
    main()
