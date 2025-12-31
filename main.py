from fastapi import FastAPI,HTTPException
import requests 
import asyncio 
import uvicorn
import cloudscraper
import os
app = FastAPI()

API_1 = "https://midas.minsal.cl/farmacia_v2/WS/getLocalesTurnos.php" # locales de turno
API_2 = "https://midas.minsal.cl/farmacia_v2/WS/getLocales.php" #locales existentes

def extraccion_data_relevante(data):
    item = {
            "nombre": data.get("local_nombre"),
            "direccion": data.get("local_direccion"),
            "comuna": data.get("comuna_nombre"),
            "local_lat":data.get("local_lat"),
            "local_lng":data.get("local_lng")
        }
    return item

@app.get("/getLocales")
def get_fuente_uno(comuna: str = None, localidad: str = None):
    try:
        # Creamos el scraper que simula un navegador (Chrome en este caso)
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        resp = scraper.get(API_1, timeout=20)
        
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code, 
                detail=f"Cloudflare persiste en el bloqueo: {resp.status_code}"
            )

        data = resp.json()

        # Filtrado manual en Python (Minsal ignora los parámetros de la URL)
        if comuna:
            data = [f for f in data if comuna.upper() in f.get("comuna_nombre", "").upper()]
        
        if localidad:
            data = [f for f in data if localidad.upper() in f.get("localidad_nombre", "").upper()]
        
        return extraccion_data_relevante(data[0])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/getLocalesDeTurno")
def get_fuente_dos(comuna: str = None, localidad: str = None):
    try:
        # Creamos el scraper que simula un navegador (Chrome en este caso)
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        # Hacemos la petición
        resp = scraper.get(API_1, timeout=20)
        
        if resp.status_code != 200:
            # Si sigue dando 403, Cloudflare detectó el entorno de servidor
            raise HTTPException(
                status_code=resp.status_code, 
                detail=f"Cloudflare persiste en el bloqueo: {resp.status_code}"
            )

        data = resp.json()

        # Filtrado manual en Python (Minsal ignora los parámetros de la URL)
        if comuna:
            data = [f for f in data if comuna.upper() in f.get("comuna_nombre", "").upper()]
        
        if localidad:
            data = [f for f in data if localidad.upper() in f.get("localidad_nombre", "").upper()]

        return extraccion_data_relevante(data[0])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    port = int(os.getenv("PORT",8000))
    uvicorn.run(app, host="0.0.0.0", port=port)