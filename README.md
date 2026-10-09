# FilaYa Data Lakehouse (local)

Pipeline de datos para el análisis de mercado del proyecto FilaYa.
Arquitectura tipo lakehouse corriendo 100% en tu PC, sin costo de nube.

## Arquitectura

```
Scrapers → bronze (crudo) → silver (limpio) → gold (agregado) → dashboard
```

- **bronze/**: datos crudos tal cual vienen de cada fuente.
- **silver/**: datos limpios, tipados y deduplicados (Parquet).
- **gold/**: tablas listas para análisis (dentro de warehouse.duckdb).
- **warehouse.duckdb**: tu "data warehouse" local, consultable con SQL.

## Instalación

```bash
python -m venv venv
source venv/bin/activate        # en Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Uso (orden de ejecución)

1. **Scrapear eventos** (agrega CSVs nuevos a bronze/eventos/):
   ```bash
   cd scrapers
   python scraper_eventos.py
   ```

2. **Transformar a silver** (limpia y unifica):
   ```bash
   cd ../pipeline
   python transform_silver.py
   ```

3. **Transformar a gold** (clasifica riesgo de fila):
   ```bash
   python transform_gold.py
   ```

4. **Ver el dashboard**:
   ```bash
   cd ..
   streamlit run dashboard.py
   ```

5. **Consultar directo con SQL** (opcional, para explorar a mano):
   ```bash
   python -c "import duckdb; con = duckdb.connect('warehouse.duckdb'); print(con.execute('SELECT * FROM gold.eventos_riesgo_fila LIMIT 10').df())"
   ```

## Próximos pasos

- [ ] Agregar más venues (Luna Park, River, Vélez) duplicando scraper_eventos.py
      con su URL correspondiente.
- [ ] Sumar scraper_social.py para menciones de Twitter/Instagram sobre
      tiempo de fila real.
- [ ] Cruzar gold.eventos_riesgo_fila con datos de la encuesta de Google Forms.
- [ ] (Opcional) Automatizar la corrida diaria con un scheduler simple
      (cron en Linux/Mac, Task Scheduler en Windows, o Prefect/Airflow
      si querés ir más pro).
