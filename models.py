from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime
from database import Base

#tabela koja ce nam pamtiti podatke koi su vec prikupljeni
class EnergyConsumption(Base):
    __tablename__ = 'energy_consumption'
    
    id = Column(Integer, primary_key=True, index=True)
    datetime = Column(DateTime, index=True)
    building_id = Column(Integer, index=True)
    consumption = Column(Float)
    
#tabela koja ce pamtiti podatke nakon predvidjanja
class Prediction(Base):
    __tablename__ = 'predictions'
    
    id = Column(Integer, primary_key=True, index=True)
    building_id = Column(Integer, index=True)
    datetime = Column(DateTime, index=True)
    predicted_value = Column(Float)
    