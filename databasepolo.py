# -*- coding: utf-8 -*-
#refactorizar
from os import path
from sqlalchemy import create_engine,Table, Column,ForeignKey, Integer, Binary,DateTime,String, MetaData
from sqlalchemy.sql import text, select 
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker as SM
from datetime import datetime as DT

engine          = create_engine('sqlite:///polodb.db', echo=True)
conn            = engine.connect()
session_factory = SM(bind=engine)
session         = session_factory()

if not path.exists('//polodb.db'):
    meta   = MetaData()
    prenda =    Table('prenda', meta, 
                Column('id_prenda', Integer, primary_key=True),
                Column('fecha',DateTime),
                Column('estado', Integer),
                Column('op',String, unique=True,nullable=False),
                Column('id_color',Integer),
                Column('cant_total',Integer),
                Column('referencia', String),)
                    
    color   =   Table('color',meta,
                Column('id_color', Integer, primary_key=True),
                Column('nom_color', String),
                Column('num_color',Integer),)
                
    talla   =  Table('talla',meta,
                Column('id_talla' ,Integer,primary_key=True),
                Column('nom_talla', String),)         
    #operacion lista
    Book   =  Table('book',meta,
                Column('title' ,Integer))         
    #operacion lista
    operacion = Table('operacion',meta,Column('id_operacion', Integer,primary_key=True),
                Column('fecha', DateTime),
                Column('id_prenda',Integer),
                Column('id_talla',Integer),
                Column('can_terminada',Integer))
    meta.create_all(engine)    
else:pass