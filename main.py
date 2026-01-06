from fastapi import FastAPI,HTTPException
from fastapi.concurrency import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import uvicorn
import cloudscraper
from sqlmodel import delete
import os
from sqlmodel import SQLModel, Field, Session, create_engine, select

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import APIKeyHeader
API_KEY = "mi_clave_secreta_123"
API_KEY_NAME = "X-API-KEY"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
app = FastAPI()

def validar_api_key(api_key: str = Depends(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key inválida"
        )
@app.get("/farmacias_protegido")
def farmacias_protegido(dep=Depends(validar_api_key)):
    return {"mensaje": "Acceso permitido"}

API_1 = "https://midas.minsal.cl/farmacia_v2/WS/getLocalesTurnos.php" # locales de turno
API_2 = "https://midas.minsal.cl/farmacia_v2/WS/getLocales.php" #locales existentes

sqlite_file_name = "farmacias.db"

sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url)
# Creamos el scraper que simula un navegador (Chrome en este caso)
def scraper_minsal(API):
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'firefox', 'platform': 'windows', 'desktop': True,'mobile': False}
    )
    return scraper.get(API,headers={'Referer': 'https://www.minsal.cl/'}, timeout=3)

class Farmacia(SQLModel, table=True):
    id: int|None = Field(default=None, primary_key=True)
    local_nombre: str
    local_direccion: str
    comuna_nombre: str
    local_lat: str
    local_lng: str

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
        resp = scraper_minsal(API_2)
        if resp.status_code != 200:
            #with Session(engine) as session:
            #    farmacias = session.exec(select(Farmacia)).all()
            #    data = [f.model_dump() for f in farmacias]
                #TODO revisar en algun momento para los casos que este el documento
            print("STATUS:", resp.status_code)
            print("HEADERS:", resp.headers)
            print("BODY:", resp.text[:500])
            raise HTTPException(
                status_code=resp.status_code, 
                detail=f"Cloudflare persiste en el bloqueo: {resp.status_code}"
            )
            
        else:
            data = resp.json()

        if comuna:
            data = [f for f in data if comuna.upper() in f.get("comuna_nombre", "").upper()]
        
        if localidad:
            data = [f for f in data if localidad.upper() in f.get("localidad_nombre", "").upper()]
        lista=[]
        for d in data:
            lista.append(extraccion_data_relevante(d))
        return lista

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/getLocalesDeTurno")
def get_fuente_dos(comuna: str = None, localidad: str = None):
    try:
        # Hacemos la petición
        resp = scraper_minsal(API_1)
        
        if resp.status_code != 200:
            # Si sigue dando 403, Cloudflare detectó el entorno de servidor
            print("STATUS:", resp.status_code)
            print("HEADERS:", resp.headers)
            print("BODY:", resp.text[:500])
            raise HTTPException(
                status_code=resp.status_code, 
                detail=f"Cloudflare persiste en el bloqueo: {resp.status_code}"
            )

        data = resp.json()
        if comuna:
            data = [f for f in data if comuna.upper() in f.get("comuna_nombre", "").upper()]
        
        if localidad:
            data = [f for f in data if localidad.upper() in f.get("localidad_nombre", "").upper()]

        return extraccion_data_relevante(data[0])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    


def tarea_actualizar_farmacias():
    """Función que ejecuta el cron para actualizar la DB"""
    print("Iniciando actualización diaria de farmacias...")
    data_raw = scraper_minsal(API_2)
    
    if not data_raw:
        print("No se pudo obtener data del Minsal")
        return
    with Session(engine) as session:
        # Opcional: Limpiar tabla antes de actualizar para no duplicar
        
        session.exec(delete(Farmacia))
        session.commit()

        for d in data_raw:
            nueva_farmacia = Farmacia(
                nombre=d.get("local_nombre"),
                direccion=d.get("local_direccion"),
                comuna=d.get("comuna_nombre"),
                local_lat=d.get("local_lat"),
                local_lng=d.get("local_lng")
            )
            session.add(nueva_farmacia)
        
        session.commit()
        print(f"Éxito: {len(data_raw)} farmacias almacenadas.")



@asynccontextmanager
async def lifespan(app: FastAPI):
    # Crear tablas si no existen
    SQLModel.metadata.create_all(engine)
    
    # Configurar Cron
    scheduler = AsyncIOScheduler()
    # Todos los días a la 1:00 AM
    #scheduler.add_job(tarea_actualizar_farmacias, "cron", hour=1, minute=0)
    scheduler.add_job(tarea_actualizar_farmacias, "interval", seconds=2)
    scheduler.start()
    
    yield
    scheduler.shutdown()

#app = FastAPI(lifespan=lifespan)
if __name__ == "__main__":
    port = int(os.getenv("PORT",8000))
    uvicorn.run(app, host="0.0.0.0", port=port)