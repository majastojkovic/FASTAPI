from fastapi import FastAPI, UploadFile, File, HTTPException, Query, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Annotated
from typing import List
import os
#import asyncpg
import pandas as pd
from datetime import datetime
from database import SessionLocal, engine
from pydantic import BaseModel
import models
from fastapi.middleware.cors import CORSMiddleware
from notebook_executor import run_notebook
from notebook_script import main as run_analysis_building1
#from notebook_script_building2 import main as run_analysis_building2
#from notebook_script_building3 import main as run_analysis_building3
#from notebook_script_building4 import main as run_analysis_building4
import requests

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

class EnergyConsumption(BaseModel):
    
    id:int
    datetime:datetime
    building_id: int
    consumption:float
    
    
class Prediction(BaseModel):
    
    id:int
    datetime:datetime
    building_id: int
    predicted_value:float
    

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Zavistnost za sesiju baze podataka
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create directory for static files if it doesn't exist
if not os.path.exists('static'):
    os.makedirs('static')

# Helper function to connect to the database
#async def get_db_connection():
 #   conn = await asyncpg.connect(get_db())
  #  return conn

#JUPYTER_TOKEN='16ec85d737877cf84a4fa90bb3f59f22fedace7e4e446ab9'
JUPYTER_TOKEN='2bbe8b646003e0ccb0a1eaa85d5ee04ec21762a9d8eac72e'
import json

@app.get("/run-notebook")
def run_notebook_endpoint(notebook_url: str):
    try:
       # Prilagodite URL da ukaže na API i uključite token
        api_url = notebook_url.replace('/notebooks/', '/api/contents/')
        if '?' in api_url:
            api_url += f"&token={JUPYTER_TOKEN}"
        else:
            api_url += f"?token={JUPYTER_TOKEN}"
        
        # Pošaljite zahtev za dobijanje sadržaja beležnice
        response = requests.get(api_url)
        response.raise_for_status()
        notebook_content = response.json()
        if not notebook_content or 'content' not in notebook_content:
            raise HTTPException(status_code=500, detail="Nije moguće dobiti sadržaj beležnice.")
    
        # Dodavanje logovanja za proveru sadržaja
        print("Sadržaj beležnice:", json.dumps(notebook_content, indent=2))
    
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Neuspelo preuzimanje beležnice: {e}")

    result = run_notebook(notebook_content['content'])
    return {"result": result}

db_dependency = Annotated[Session, Depends(get_db)]

""""building_id: Parametar koji specificira ID zgrade za koju se traže podaci.
db: Session = Depends(get_db): Inicijalizuje sesiju prema bazi podataka.
db.query(EnergyConsumption).filter(EnergyConsumption.building_id == building_id).all(): Izvlači sve zapise o potrošnji energije za zgradu sa zadatim ID-jem iz baze podataka.
if not consumption_data: Proverava da li postoje podaci za zadatu zgradu. Ako ne, vraća HTTP 404 grešku.
return consumption_data: Vraća podatke o potrošnji energije."""

@app.get("/consumption/{building_id}")
def get_consumption(building_id: int, db: db_dependency):
    consumption_data = db.query(EnergyConsumption).filter(EnergyConsumption.building_id == building_id).all()
    if not consumption_data:
        raise HTTPException(status_code=404, detail="Data not found")
    return consumption_data

"""building_id: Parametar koji specificira ID zgrade za koju se traže predikcije.
start_date i end_date: Parametri koji specificiraju početni i krajnji datum za period predikcija.
db: Session = Depends(get_db): Inicijalizuje sesiju prema bazi podataka.
if start_date < datetime.now() or end_date < datetime.now() or start_date > end_date: Proverava validnost vremenskog opsega. Ako je opseg nevažeći, vraća HTTP 400 grešku.
db.query(Prediction).filter(Prediction.building_id == building_id, Prediction.datetime >= start_date, Prediction.datetime <= end_date).all(): Izvlači sve predikcije za zgradu sa zadatim ID-jem u zadatom vremenskom periodu iz baze podataka.
return predictions: Vraća predikcije."""
@app.get("/predictions/{building_id}")
def get_predictions(building_id: int, start_date: datetime, end_date: datetime, db: db_dependency):
    if start_date < datetime.now() or end_date < datetime.now() or start_date > end_date:
        raise HTTPException(status_code=400, detail="Invalid date range")
    
    predictions = db.query(Prediction).filter(
        Prediction.building_id == building_id,
        Prediction.datetime >= start_date,
        Prediction.datetime <= end_date
    ).all()

    return predictions
# Run the server with uvicorn main:app --reload


"""
Tok rada
Korisnik šalje zahtev: Korisnik putem frontend aplikacije šalje HTTP GET zahtev ka odgovarajućem endpointu.
FastAPI prima zahtev: FastAPI endpoint prima zahtev i koristi zadate parametre (building_id, start_date, end_date) za pretragu baze podataka.
Pristup bazi podataka: Korišćenjem SQLAlchemy ORM-a, endpoint pristupa TimescaleDB bazi podataka i izvršava upit za dobijanje traženih podataka.
Validacija podataka: Endpoint proverava validnost unetih parametara i postojanje podataka u bazi. Ako su podaci validni, vraća ih korisniku.
Vraćanje odgovora: Endpoint vraća JSON odgovor sa traženim podacima o potrošnji ili predikcijama.
"""