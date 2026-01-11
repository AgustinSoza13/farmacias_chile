# from fastapi import FastAPI,HTTPException
# import uvicorn
# import cloudscraper
# import os
# from sqlmodel import SQLModel, Field

# from fastapi import Depends, FastAPI, HTTPException, status
# from fastapi.security import APIKeyHeader
# API_KEY = os.getenv("mi_clave_secreta_123")
# API_KEY_NAME = os.getenv("API_KEY_NAME")

# api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# app = FastAPI()

# def validar_api_key(api_key: str = Depends(api_key_header)):
#     if api_key != API_KEY:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="API Key inválida"
#         )

# @app.get("/farmacias_protegido")
# def farmacias_protegido(dep=Depends(validar_api_key)):
#     return {"mensaje": "Acceso permitido"}

# API_1 = os.getenv("API_1") # locales de turno
# API_2 = os.getenv("API_2") #locales existentes

# # Creamos el scraper que simula un navegador (Chrome en este caso)
# def scraper_minsal(API):
#     """scraper = cloudscraper.create_scraper(
#         browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
#     )
#     headers = {
#         "Referer": "https://midas.minsal.cl/",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
#     }
#     return scraper.get(API,headers=headers, timeout=15)"""
#     scraper = cloudscraper.create_scraper()
#     headers = {
#         "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
#         "Accept": "application/json",
#         "Accept-Language": "es-CL,es;q=0.9",
#         "Referer": "https://midas.minsal.cl/",
#         "Connection": "keep-alive"
#     }
#     return scraper.get(API, headers=headers, timeout=15)

# class Farmacia(SQLModel, table=True):
#     id: int|None = Field(default=None, primary_key=True)
#     local_nombre: str
#     local_direccion: str
#     comuna_nombre: str
#     local_lat: str
#     local_lng: str
#     local_telefono: str
#     #funcionamiento_hora_apertura: 
#     #funcionamiento_hora_cierre:

# def extraccion_data_relevante(data):
#     item = {
#             "nombre": data.get("local_nombre"),
#             "direccion": data.get("local_direccion"),
#             "comuna": data.get("comuna_nombre"),
#             "local_lat":data.get("local_lat"),
#             "local_lng":data.get("local_lng"),
#             "local_telefono":data.get("local_telefono"),
#             "funcionamiento_hora_apertura":data.get("funcionamiento_hora_apertura"),
#             "funcionamiento_hora_cierre":data.get("funcionamiento_hora_cierre")
#         }
#     return item

# @app.get("/getLocales")
# def get_fuente_uno(comuna: str = None, localidad: str = None):
#     try:
#         resp = scraper_minsal(API_2)
#         # Hacemos la petición
#         if resp.status_code==403:
#             for i in range(0,3):
#                 resp = scraper_minsal(API_2)
#                 if resp.status_code==200:
#                     break
#         if resp.status_code != 200:
#             print("STATUS:", resp.status_code)
#             print("HEADERS:", resp.headers)
#             print("BODY:", resp.text[:500])
#             raise HTTPException(
#                 status_code=resp.status_code, 
#                 detail=f"Cloudflare persiste en el bloqueo: {resp.status_code}"
#             )
            
#         else:
#             data = resp.json()

#         if comuna:
#             data = [f for f in data if comuna.upper() in f.get("comuna_nombre", "").upper()]
        
#         if localidad:
#             data = [f for f in data if localidad.upper() in f.get("localidad_nombre", "").upper()]
#         lista=[]
#         for d in data:
#             lista.append(extraccion_data_relevante(d))
#         return lista

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# @app.get("/getLocalesDeTurno")
# def get_fuente_dos(comuna: str = None, localidad: str = None):
#     try:
#         resp = scraper_minsal(API_1)
#         # Hacemos la petición
#         if resp.status_code==403:
#             for i in range(0,3):
#                 print("intento :",i)
#                 resp = scraper_minsal(API_2)
#                 if resp.status_code==200:
#                     break
#         if resp.status_code != 200:
#             print("STATUS:", resp.status_code)
#             print("HEADERS:", resp.headers)
#             print("BODY:", resp.text[:500])
#             raise HTTPException(
#                 status_code=resp.status_code, 
#                 detail=f"Cloudflare persiste en el bloqueo: {resp.status_code}"
#             )

#         data = resp.json()
#         if comuna:
#             data = [f for f in data if comuna.upper() in f.get("comuna_nombre", "").upper()]
        
#         if localidad:
#             data = [f for f in data if localidad.upper() in f.get("localidad_nombre", "").upper()]

#         return extraccion_data_relevante(data[0])

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

# if __name__ == "__main__":
#     port = int(os.getenv("PORT",8000))
#     uvicorn.run(app, host="0.0.0.0", port=port)

"""from DrissionPage import ChromiumPage, ChromiumOptions
import json
import time
def extraccion_data_relevante(data):
    item = {
            "nombre": data.get("local_nombre"),
            "direccion": data.get("local_direccion"),
            "comuna": data.get("comuna_nombre"),
            "local_lat":data.get("local_lat"),
            "local_lng":data.get("local_lng")
        }
    return item

def get_farmacia(API_URL,comuna=None,localidad=None):
    # Configuración del navegador
    co = ChromiumOptions()
    co.set_argument('--headless') # si necesitar que se muestre el navegador comentar esta linea 
    co.set_user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    try:
        page = ChromiumPage(co)    
        page.get(API_URL)
        time.sleep(5) 
        html = page.html
        inicio = html.find('<body>') + len('<body>')
        fin = html.find('</body>')
        json_text = html[inicio:fin].strip()
        data = json.loads(json_text)
        if comuna:
            data = [f for f in data if comuna.upper() in f.get("comuna_nombre", "").upper()]
        
        if localidad:
            data = [f for f in data if localidad.upper() in f.get("localidad_nombre", "").upper()]
        lista=[]
        for d in data:
            lista.append(extraccion_data_relevante(d))
        return lista
    except Exception as e:
        print(f"Ocurrió un error: {e}")
    
if __name__ == "__main__":
    API_URL_TURNOS="https://midas.minsal.cl/farmacia_v2/WS/getLocalesTurnos.php"
    API_URL="https://midas.minsal.cl/farmacia_v2/WS/getLocales.php"

    data_local=get_farmacia(API_URL_TURNOS,comuna="Linares",localidad="Linares")
    data_general=get_farmacia(API_URL,comuna="Talca")
    print(data_local)
    print(data_general)

    #podemos almanecenar con un cron en un archivo y que itere una sola vez al dia para no saturar el servidor
    #para esto debemos realizar ambas peticiones sin filtros para tener toda la data del dia 
    #esto lo haremos si es que te funciona
   
    with open("farmacias_turnos.json", "w", encoding="utf-8") as f:
        json.dump(data_local, f, ensure_ascii=False, indent=4)

    with open("farmacias_turnos.json", "w", encoding="utf-8") as f:
        json.dump(data_general, f, ensure_ascii=False, indent=4)
   
"""


from fastapi import FastAPI, Query
from DrissionPage import ChromiumPage, ChromiumOptions
import json
import time

app = FastAPI()


def extraccion_data_relevante(data: dict) -> dict:
    item = {
        "nombre": data.get("local_nombre"),
        "direccion": data.get("local_direccion"),
        "comuna": data.get("comuna_nombre"),
        "local_lat": data.get("local_lat"),
        "local_lng": data.get("local_lng"),
    }
    return item


def get_farmacia(API_URL: str, comuna: str | None = None, localidad: str | None = None):
    co = ChromiumOptions()
    co.set_argument("--headless")  # si quieres ver el navegador, comenta esta línea
    co.set_user_agent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    try:
        page = ChromiumPage(co)
        page.get(API_URL)
        time.sleep(5)

        html = page.html
        inicio = html.find("<body>") + len("<body>")
        fin = html.find("</body>")
        json_text = html[inicio:fin].strip()
        data = json.loads(json_text)

        if comuna:
            data = [f for f in data if comuna.upper() in f.get("comuna_nombre", "").upper()]

        if localidad:
            data = [f for f in data if localidad.upper() in f.get("localidad_nombre", "").upper()]

        return [extraccion_data_relevante(d) for d in data]

    except Exception as e:
        # en FastAPI es mejor lanzar una excepción HTTP, pero para simplificar:
        return {"error": str(e)}


API_URL_TURNOS = "https://midas.minsal.cl/farmacia_v2/WS/getLocalesTurnos.php"
API_URL = "https://midas.minsal.cl/farmacia_v2/WS/getLocales.php"


@app.get("/farmacias/turno")
def farmacias_turno(
    comuna: str | None = Query(default=None),
    localidad: str | None = Query(default=None),
):
    """
    Ejemplo:
    /farmacias/turno?comuna=Linares&localidad=Linares
    """
    return get_farmacia(API_URL_TURNOS, comuna=comuna, localidad=localidad)


@app.get("/farmacias")
def farmacias(
    comuna: str | None = Query(default=None),
    localidad: str | None = Query(default=None),
):
    """
    Ejemplo:
    /farmacias?comuna=Talca
    """
    return get_farmacia(API_URL, comuna=comuna, localidad=localidad)
