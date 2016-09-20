# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26

@author: Miquel Quetglas
@author: AMS
@version: 1.1 (25/05/2016)
"""

#Enviroment.
ENTORNO = 'PRO'

#VIEWS Connection String
#PRE
OPENDATA_CONEXION_BD_PRE="(DESCRIPTION=(LOAD_BALANCE=on)(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx))(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx))(CONNECT_DATA=(SERVICE_NAME=xxx)))"
#DES
OPENDATA_CONEXION_BD_DES="(DESCRIPTION=(LOAD_BALANCE=on)(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx))(CONNECT_DATA=(SERVICE_NAME=xxx)))"
#PRO
OPENDATA_CONEXION_BD="(DESCRIPTION=(LOAD_BALANCE=on)(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx))(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx))(CONNECT_DATA=(SERVICE_NAME=xxx)))"

#ORACLE Connection String  

if ENTORNO == 'DES':
	AST1_CONEXION_BD="(DESCRIPTION=(LOAD_BALANCE=on)(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx))(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx))(CONNECT_DATA=(SERVICE_NAME=pxxx)))"
	AST2_CONEXION_BD="(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx)))(CONNECT_DATA=(SERVER = DEDICATED)(SERVICE_NAME = xxx)))"
	AST_TURISMO="(DESCRIPTION =(ADDRESS_LIST =(ADDRESS =(PROTOCOL = TCP)(HOST = xxx)(PORT = xxx)))(CONNECT_DATA =(SERVER = DEDICATED)(SERVICE_NAME = xxx)))"
elif ENTORNO == 'PRE': 
	AST1_CONEXION_BD="(DESCRIPTION=(LOAD_BALANCE=on)(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx))(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx))(CONNECT_DATA=(SERVICE_NAME=xxx)))"
	AST2_CONEXION_BD="(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx)))(CONNECT_DATA=(SERVER = DEDICATED)(SERVICE_NAME = xxx)))"
	AST_TURISMO="(DESCRIPTION =(ADDRESS_LIST =(ADDRESS =(PROTOCOL = TCP)(HOST = xxx)(PORT = xxx)))(CONNECT_DATA =(SERVER = DEDICATED)(SERVICE_NAME = xxx)))"
elif ENTORNO == 'PRO':
	AST1_CONEXION_BD="(DESCRIPTION=(LOAD_BALANCE=on)(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx))(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx))(CONNECT_DATA=(SERVICE_NAME=xxx)))"
	AST2_CONEXION_BD="(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=47017)))(CONNECT_DATA=(SERVER=DEDICATED)(SERVICE_NAME=xxx)))"
	AST_TURISMO="(DESCRIPTION =(ADDRESS_LIST =(ADDRESS =(PROTOCOL = TCP)(HOST = xxx)(PORT = xxx)))(CONNECT_DATA = (SERVER = DEDICATED)(SERVICE_NAME = xxx)))"


CRA_CONEXION="(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(Port=xxx)))(CONNECT_DATA=(SID=xxx)))"
CRA_USR="xxxx"
CRA_PASS="xxxx"

#POSTGRESQL Connection String
AST3_CONEXION_BD = "host='xxx' dbname='xxx' port='xxx' user='xxx' password='xxx'"
OPENDATA_POSTGRE_CONEXION_BD="host='localhost' dbname='xxx'  port='xxx' user='xxx' password='xxx'"

#SQL_SERVER Connection String
AST4_CONEXION_BD = "host='xxx', user='xxx', password='xxx', database='xxx'"

AST5_CONEXION_BD="(DESCRIPTION=(LOAD_BALANCE=on)(ADDRESS=(PROTOCOL=TCP)(HOST=xxx)(PORT=xxx))(CONNECT_DATA=(SERVICE_NAME=xxx)))"

#Users
OPENDATA_USR="xxx"
OPENDATA_PASS="xxx"
OPENDATA="xxx"
AST_USR="xxx"
AST_PASS="xxx"
USR_ADMIN="xxx"

#Table or View with the list of Views
OPEN_VIEWS="OPENDATA.OPENDATA_V_VISTAS"

#Aplication path
APP_PATH="{path/to/our/aplication/}"

#Custom log of the aplication
CUSTOM_LOG="{path/to/our/aplication/}ga_od_core_custom.log"

#Number of records returned by the function "preview_vista"
NUM_REGISTROS=5000


#Debuf functions and DB depends of the enviroment.
if ENTORNO == 'DES':
    VIEWS_DB = 'des-opendata-oracle'
    DEBUG_VAR = True
elif ENTORNO == 'PRE':
    VIEWS_DB = 'pre-opendata-oracle'
    DEBUG_VAR = True
elif ENTORNO == 'PRO':
    VIEWS_DB = 'pro-opendata-oracle'
    DEBUG_VAR = True

#For google analytics
SERVICE_ACCOUNT_EMAIL='xxx@xxx'