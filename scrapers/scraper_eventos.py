"""
Scraper de eventos - Movistar Arena (Buenos Aires)
----------------------------------------------------
Extrae el historial de eventos desde la tabla de Wikipedia y lo guarda
en un CSV listo para cruzar con datos de redes sociales / encuestas.

Requisitos:
    pip install requests beautifulsoup4 pandas --break-system-packages

Correr:
    python scraper_eventos.py

Output:
    eventos_movistar_arena.csv  con columnas:
    fecha, anio, artista, evento, venue, capacidad_venue
"""

import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

URL = "https://en.wikipedia.org/wiki/Movistar_Arena_(Buenos_Aires)"
VENUE = "Movistar Arena"
CAPACIDAD = 15000  # capacidad fija y pública del venue

MESES = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12,
}


def obtener_html(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; FilaYaBot/1.0; +https://example.com)"}
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.text


def parsear_eventos(html: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    # Buscamos todas las tablas wikitable, que es donde Wikipedia guarda
    # el calendario de eventos por año.
    tablas = soup.find_all("table", {"class": "wikitable"})

    filas = []
    anio_actual = None

    for tabla in tablas:
        for tr in tabla.find_all("tr"):
            celdas = tr.find_all(["td", "th"])
            textos = [c.get_text(strip=True) for c in celdas]

            if not textos:
                continue

            # Detectar filas que son solo el año (ej: "2023")
            if len(textos) == 1 and re.fullmatch(r"20\d{2}", textos[0]):
                anio_actual = int(textos[0])
                continue

            # Filas de evento: [fecha, artista, evento] o [fecha, artista]
            if len(textos) >= 2:
                fecha_texto = textos[0]
                artista = textos[1]
                evento = textos[2] if len(textos) > 2 else ""

                # Intentar parsear "1 November" -> día 1, mes November
                match = re.match(r"(\d{1,2})\s+([A-Za-z]+)", fecha_texto)
                if match and anio_actual:
                    dia = int(match.group(1))
                    mes_nombre = match.group(2)
                    mes = MESES.get(mes_nombre)
                    if mes:
                        fecha_iso = f"{anio_actual}-{mes:02d}-{dia:02d}"
                        filas.append({
                            "fecha": fecha_iso,
                            "anio": anio_actual,
                            "artista": artista,
                            "evento": evento,
                            "venue": VENUE,
                            "capacidad_venue": CAPACIDAD,
                        })

    df = pd.DataFrame(filas)
    df = df.drop_duplicates(subset=["fecha", "artista", "evento"])
    df = df.sort_values("fecha")
    return df


def main():
    print("Descargando página...")
    html = obtener_html(URL)
    print("Parseando eventos...")
    df = parsear_eventos(html)
    df["fuente"] = "wikipedia_movistar_arena"
    df["scrapeado_en"] = pd.Timestamp.now().isoformat()

    salida = "../bronze/eventos/movistar_arena.csv"
    df.to_csv(salida, index=False, encoding="utf-8-sig")
    print(f"Listo. {len(df)} eventos guardados en {salida}")
    print(df.tail(10))


if __name__ == "__main__":
    main()
