"""
Bronze -> Silver
----------------
Lee todos los CSVs crudos de bronze/eventos/*.csv (pueden venir de
distintos venues/scrapers), los unifica, limpia y guarda como Parquet
en silver/, y también los deja disponibles como tabla en el warehouse
DuckDB para consultar con SQL.

Correr desde la carpeta pipeline/:
    python transform_silver.py
"""

import glob
import duckdb
import pandas as pd

DB_PATH = "../warehouse.duckdb"


def cargar_eventos_bronze() -> pd.DataFrame:
    archivos = glob.glob("../bronze/eventos/*.csv")
    if not archivos:
        raise FileNotFoundError(
            "No hay CSVs en bronze/eventos/. Corré antes el scraper correspondiente."
        )

    dfs = [pd.read_csv(f) for f in archivos]
    df = pd.concat(dfs, ignore_index=True)

    # Limpieza básica
    df["fecha"] = pd.to_datetime(df["fecha"], errors="coerce")
    df = df.dropna(subset=["fecha"])
    df["artista"] = df["artista"].str.strip()
    df["venue"] = df["venue"].str.strip()
    df = df.drop_duplicates(subset=["fecha", "artista", "venue"])

    return df


def guardar_silver(df: pd.DataFrame):
    df.to_parquet("../silver/eventos.parquet", index=False)

    con = duckdb.connect(DB_PATH)
    con.execute("CREATE SCHEMA IF NOT EXISTS silver")
    con.execute("""
        CREATE OR REPLACE TABLE silver.eventos AS
        SELECT * FROM read_parquet('../silver/eventos.parquet')
    """)
    con.close()


def main():
    df = cargar_eventos_bronze()
    guardar_silver(df)
    print(f"Silver actualizado: {len(df)} eventos únicos.")
    print(df.head())


if __name__ == "__main__":
    main()
