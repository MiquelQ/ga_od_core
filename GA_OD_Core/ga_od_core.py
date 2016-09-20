# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26

@author: Miquel Quetglas
@author: AMS
@version: 1.1 (25/05/2016)
"""
import conf as configuracion
import sys
sys.path.insert(0, configuracion.APP_PATH)
import conexiones
import json
import sys
import os
os.environ["NLS_LANG"] = "SPANISH_SPAIN.AL32UTF8"
import cgi
from flask import make_response
from flask import jsonify
import dicttoxml
dicttoxml.set_debug(False)
import sustCaracter as sustCaracter
import logging
import logging.handlers
from flask import request

# Remove all handlers associated with the root logger object.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
    

#Added for google analytics
import argparse

from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials

import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import urllib2
import urlparse

#LOG_DEBUG = If is True will write logs with the deb() function
LOG_DEBUG = configuracion.DEBUG_VAR


#FORMAT='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#Creation of rotative log (5MB max size) file with personalized format.
FORMAT='%(asctime)s - %(levelname)s - %(message)s'
my_logger=logging.getLogger("MyLogger")
if LOG_DEBUG is True:
    my_logger.setLevel(logging.DEBUG)
else:
    my_logger.setLevel(logging.ERROR)
fh=logging.handlers.RotatingFileHandler(configuracion.CUSTOM_LOG, maxBytes=5000000, backupCount=5)
if LOG_DEBUG is True:
    fh.setLevel(logging.DEBUG)
else:
    fh.setLevel(logging.ERROR)
fh.setFormatter(logging.Formatter(FORMAT))
my_logger.addHandler(fh)
dicttoxml.set_debug(False)



def deb(msg):
    """
    If LOG_DEBUG is True, will write in log file.
    """
    if LOG_DEBUG is True:
        my_logger.info(msg)
        #print msg


def views(user):
    """
    Views
        Args:
           user(String): user logged in Opendata Portal (CKAN).
        Returns: 
            resultados(Array): Array with all available views returned in indented JSON
    """
    db = conexiones.conexion(configuracion.VIEWS_DB).cadena
    cursor = db.cursor()
    if user == 'admin' or user is None:
        sentencia = "SELECT id_vista, nombre FROM opendata.opendata_v_vistas order by id_vista"
    else:
        sentencia = "SELECT * FROM opendata.opendata_v_listadoVistas where usuario='" + user + "' order by id_vista"
    cursor.execute(sentencia)
    rows = cursor.fetchall()
    resultado = []    

    for row in rows:
        resultado.append(row)    
    
    cursor.close()
    resultados = json.dumps(resultado,ensure_ascii=False,indent=4)
    return resultados  


def show_columns(view_id):
    """
    Show Columns
    Args:    
        view_id(Integer): ID of the View to query
    Returns:
        resultados(Array): Array with information about the columns and data types
    """
    try:    
        #Connect to the database according to environment
        db = conexiones.conexion(configuracion.VIEWS_DB).cadena
        cursor = db.cursor()
        cursor.execute("SELECT SUBSTR(NOMBREREAL,INSTR(NOMBREREAL,'.',-1)+1),BASEDATOS from " + configuracion.OPEN_VIEWS + " WHERE ID_VISTA = '"+ str(view_id) + "'")
        rows = cursor.fetchall()
        resultado = []
        
        #Keep Fields 'NOMBRE'(from ';' to the end) and field 'BASEDEDATOS'  
        for i in rows:
            deb("--------------------")        
            deb("<Seleccionamos vista: " + i[0])
            nombre_vista = i[0]
            tipo_vista = i[1]
            resultado.append(i)
    
        cursor.close()    
        
        #Query to the View according to environment
        db = conexiones.conexion(tipo_vista).cadena  
        deb("--------------------")
        deb("CADENA DE CONEXION: " + str(db))
        deb("--------------------")
 
        #Obtain the type of Database (oracle, mysql, postge o sqlserver) according to environment
        tipo = conexiones.conexion(tipo_vista).tipo
        deb("TIPO DE BASE DE DATOS: " + str(tipo))
        
        #If the View is google_analytics type we store name and dataType to match views database
        if tipo == 'google_analytics':
            resultado = []
            col = devuelve_rows(view_id,None,None)[1]
            for n in range(len(col)):
                resultado.append(dict(columnName=str(col[n]['name']),dataType=str(col[n]['dataType'])))
        else:
            cursor = db.cursor()
            
            #Query according the type of Database
            if tipo == 'oracle':
                cursor.execute("select COLUMN_NAME,DATA_TYPE from ALL_TAB_COLUMNS where TABLE_NAME = UPPER('" + nombre_vista + "')")
            elif tipo == 'postgre':
                cursor.execute("SELECT column_name,data_type FROM information_schema.columns WHERE table_name   = '"+ nombre_vista+"'")
            elif tipo == 'sqlserver':
                cursor.execute("SELECT column_name,data_type FROM information_schema.columns WHERE table_name   = '"+ nombre_vista+"'")
            elif tipo == 'mysql' and view_id == '104':
                '''
                Hack for database name problem in list of our views.
                '''
                cursor.execute("SELECT COLUMN_NAME,DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'open_poligonos'")       
            elif tipo == 'mysql' and not view_id == '104':
                cursor.execute("SELECT COLUMN_NAME,DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '"+ nombre_vista+"'")
            else:
                deb("UNKNOWN TYPE OF DATABSE !!!!!")
            
            rows = cursor.fetchall()
            resultado = []
            
            #Insert results in a ( { key : value } ) dictionary
            columns = [column[0] for column in cursor.description]
            for row in rows:
                resultado.append(dict(zip(columns, row)))
            cursor.close() 

        resultados = json.dumps(resultado, ensure_ascii=False,sort_keys=True,indent=4) 
        return resultados
    except Exception,e:
        my_logger.error(e) 

    
def devuelve_rows(view_id,select_sql,filter_sql):
    """
    Devuelve Rows
    Args:    
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve. If are more than one,separate them by a coma (SQL Format)
        filro_sql(String): String with filters to add to the query (SQL Format)
    Returns:
        resultados(Array): Array with records requested in the query
        columns(Array): Array with the name of the Fields
    """
    try:          
        deb("*********************view_id: " + str(view_id))
        deb("*********************select_sql: " + str(select_sql))
        deb("*********************filter_sql: " + str(filter_sql))
        
        #Query to the View according to environment
        db_v = conexiones.conexion(configuracion.VIEWS_DB).cadena
        
        cursor_v = db_v.cursor()
        cursor_v.execute("SELECT NOMBREREAL,BASEDATOS from " + configuracion.OPEN_VIEWS + " WHERE ID_VISTA = '"+ str(view_id) + "'")    
        rows = cursor_v.fetchall()
        
        #Keep Fields 'NOMBRE' and 'BASEDEDATOS'  
        for i in rows:
            deb("--------------------")  
            deb("Seleccionamos vista: " + i[0])
            nombre_vista = i[0]
            tipo_vista = i[1]
        cursor_v.close()


        deb("**tipo_vista: " + str(tipo_vista))
        db = conexiones.conexion(tipo_vista).cadena

        deb("--------------------")
        deb("CADENA DE CONEXION: " + str(db))
        deb("--------------------")
       
        #Obtain the type of Database (oracle, mysql, postge o sqlserver) according to environment    
        tipo = conexiones.conexion(tipo_vista).tipo
        deb("1-TIPO DE BASE DE DATOS: " + str(tipo))
        
        if tipo == 'google_analytics':
            url = nombre_vista.replace("'","")
            parsed = urlparse.urlparse(url)
            profile = str(urlparse.parse_qs(parsed.query)['profile'][0])
            start_date = str(urlparse.parse_qs(parsed.query)['start_date'][0])
            end_date = str(urlparse.parse_qs(parsed.query)['end_date'][0])
            metrics = str(urlparse.parse_qs(parsed.query)['metrics'][0])    
            try:
                dimensions = str(urlparse.parse_qs(parsed.query)['dimensions'][0])
            except Exception, e:
                dimensions = None
    
            try:
                filters = str(urlparse.parse_qs(parsed.query)['filters'][0])
            except Exception, e:
                filters = None
            
            try:
                include_empty_rows = str(urlparse.parse_qs(parsed.query)['include_empty_rows'][0])
            except Exception, e:
                include_empty_rows = None
            
            try:
                max_results = str(urlparse.parse_qs(parsed.query)['max_results'][0])
            except Exception, e:
                max_results = None

            try:
                output = str(urlparse.parse_qs(parsed.query)['output'][0])
            except Exception, e:
                output = None

            try:
                samplingLevel = str(urlparse.parse_qs(parsed.query)['samplingLevel'][0])
            except Exception, e:
                samplingLevel = None

            try:
                segment = str(urlparse.parse_qs(parsed.query)['segment'][0])
            except Exception, e:
                segment = None

            try:
                sort = str(urlparse.parse_qs(parsed.query)['sort'][0])
            except Exception, e:
                sort = None

            try:
                start_index = str(urlparse.parse_qs(parsed.query)['start_index'][0])
            except Exception, e:
                start_index = None
            
            try:
                fields = str(urlparse.parse_qs(parsed.query)['fields'][0])
            except Exception, e:
                fields = None

            response = google_analytics(profile,start_date,end_date,metrics,dimensions,filters,include_empty_rows,max_results,output,samplingLevel,segment,sort,start_index,fields)  

            columns = []
            resultados = json.loads(response)

            for n in range(len(resultados['columnHeaders'])):
                columns.append(resultados['columnHeaders'][n])
            resultados = resultados['rows']
        else:
            cursor = db.cursor()
            
            #If GET[select_sql] is empty select all (*)
            if select_sql is None:
                select_sql = '*'
        
            #Hack for fix a wrong name in database       
            if nombre_vista == 'BD_WEBIAF':
                nombre_vista = 'open_poligonos'
            sentencia = "select " + str(select_sql) + " from " + str(nombre_vista)
            
            #If GET[filter_sql] is empty don't apply filters to the Query
            if filter_sql is None:
                filter_sql = "" 
            else:
                sentencia = str(sentencia) +  " " + str(filter_sql).replace("\"","\'")
            deb("sentencia: " + str(sentencia))
            
            cursor.execute(sentencia)
            rows = cursor.fetchall()
            resultados = rows
            
            #Hack to replace characters that cause errors         
            if tipo == 'mysql' or tipo == 'sqlserver' or nombre_vista[0:6] == 'ARABUS':
                resultados = []
                r = []
                for r in rows:
                    longitud = len(r)
                    arrayTupla = []
                    for i in range(longitud):
                        try:                
                            arrayTupla.append(sustCaracter.sustitucionCaracter(r[i]))
                        except Exception,e: 
                            arrayTupla.append(r[i])
                    resultados.append(arrayTupla)
            columns = [column[0] for column in cursor.description]
        return resultados,columns
    except Exception,e:
        my_logger.error(e)
        
 
def preview(view_id,select_sql,filter_sql):
    """
    Preview
    Args:
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve. If are more than one,separate them by a coma (SQL Format)
        filro_sql(String): String with filters to add to the query (SQL Format)
    Returns:
        resultados(Array): Array with records requested in the query. Allways is like SELECT {select_sql} from {nombre_vista} where {filter_sql}
    """
    try:
        #Query to the View according to environment
        db_v = conexiones.conexion(configuracion.VIEWS_DB).cadena
        cursor_v = db_v.cursor()
        cursor_v.execute("SELECT NOMBREREAL,BASEDATOS from " + configuracion.OPEN_VIEWS + " WHERE ID_VISTA = '"+ str(view_id) + "'")    
        rows = cursor_v.fetchall()
        
        for i in rows:
            deb("--------------------")  
            deb("Seleccionamos vista: " + i[0])
            nombre_vista = i[0]
            tipo_vista = i[1]
        cursor_v.close()    
       
        #Obtain the type of Database (oracle, mysql, postge o sqlserver) according to environment    
        tipo = conexiones.conexion(tipo_vista).tipo    
        
        #Limit the amount of records we will return , because without are many fails get 500
        num_reg = configuracion.NUM_REGISTROS
        deb("-->  tipo_vista es: " + str(tipo))  
       
        if filter_sql == None or filter_sql is None:
            if tipo == 'oracle':
                filter_sql = " WHERE ROWNUM< " + str(num_reg)
            elif tipo == 'sqlserver':
                filter_sql = ""
            elif tipo == 'postgre' or tipo == 'mysql':
                filter_sql = " LIMIT " + str(num_reg)
        else:
            if tipo == 'oracle':
                filter_sql = " WHERE " + str(filter_sql) + " AND ROWNUM< " + str(num_reg)
            elif tipo == 'sqlserver':
                filter_sql = " WHERE " + str(filter_sql)
            elif tipo == 'postgre' or tipo == 'mysql':
                filter_sql = " WHERE " + str(filter_sql) + " LIMIT " + str(num_reg)          
               
        deb("-->  filter_sql es: " + str(filter_sql))
       
        #Obtain registers and columns        
        rows = devuelve_rows(view_id,select_sql,filter_sql)[0]
        col = devuelve_rows(view_id,select_sql,filter_sql)[1]

        if tipo == 'google_analytics':
            columns = []
            for n in range(len(col)):
                columns.append(col[n]['name'])
        else:
            columns = col

        resultado = []
        resultado.append(columns)
        for row in rows:
            resultado.append(row)

        #This way format to use on opendata.aragon.es      
        d_string = json.dumps(resultado,default=date_handler,ensure_ascii=False,sort_keys=True,indent=4)
        return d_string 
    except Exception,e: 
        my_logger.error(e)

           
def download(view_id,select_sql,filter_sql,formato):
    """
    Download
    Args:
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve. If are more than one,separate them by a coma (SQL Format)
        filro_sql(String): String with filters to add to the query (SQL Format)
        formato(String): String with the format of the document to download, can be JSON, CSV or XML
    Returns:
        {nombre}.{formato} (File): A file with the format requested
    """ 
    db_v = conexiones.conexion(configuracion.VIEWS_DB).cadena
    cursor_v = db_v.cursor()
    cursor_v.execute("SELECT NOMBREREAL,BASEDATOS from " + configuracion.OPEN_VIEWS + " WHERE ID_VISTA = '"+ str(view_id) + "'")    
    rows = cursor_v.fetchall()
    
    for i in rows:
        deb("--------------------")  
        deb("Seleccionamos vista: " + i[0])
        nombre_vista = i[0]
        tipo_vista = i[1]
    cursor_v.close()

    #Obtain the type of Database (oracle, mysql, postge o sqlserver) according to environment   
    tipo = conexiones.conexion(tipo_vista).tipo

    if filter_sql != None or filter_sql is not None:
        filter_sql = " WHERE " + str(filter_sql)
    #Differentiate format
    if formato.upper() == "JSON":
        resultado = []    
        resultado = create_JSON_array(view_id,select_sql,filter_sql,tipo)  
    elif formato.upper() == 'XML':
        obj = create_XML_array(view_id,select_sql,filter_sql,tipo)
        resultado = dicttoxml.dicttoxml(obj,attr_type=False)
    elif formato.upper() == 'CSV':
        resultado = ""
        resultado = create_CSV(view_id,select_sql,filter_sql,tipo)      
    else:
        resultado = "Must enter the parameter <b>format</b>. (XML, JSON o CSV)"
    return resultado    


def create_JSON_array(view_id,select_sql,filter_sql,tipo):
    """
    Create JSON Array
    Args:
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve .
        filro_sql(String): String with filters to add to the query (SQL Format)
    Returns:
        reultados(Array):Array in JSON format
    """            
    resultado = []    
    rows = devuelve_rows(view_id,select_sql,filter_sql)[0]
    if tipo == 'google_analytics':
        col = devuelve_rows(view_id,select_sql,filter_sql)[1]
        columns = []
        for n in range(len(col)):
            columns.append(col[n]['name'])
    else:
        columns = devuelve_rows(view_id,select_sql,filter_sql)[1]
    resultado.append(columns)
    for row in rows:
        resultado.append(row)
    d_string = json.dumps(resultado, default=date_handler, ensure_ascii=False,sort_keys=True,indent=4)    
    return d_string


def create_XML_array(view_id,select_sql,filter_sql,tipo):
    """
    Create XML Array
    Args:
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve .
        filro_sql(String): String with filters to add to the query (SQL Format)
    Returns:
        reultados(Dictionary): Array in dictionary format.
    """            
    resultado = []    
    rows = devuelve_rows(view_id,select_sql,filter_sql)[0]
    if tipo == 'google_analytics':
        col = devuelve_rows(view_id,select_sql,filter_sql)[1]
        columns = []
        for n in range(len(col)):
            columns.append(col[n]['name'])
    else:
        columns = devuelve_rows(view_id,select_sql,filter_sql)[1]
    for row in rows:
        resultado.append(dict(zip(columns, row)))
    return resultado


def create_CSV(view_id,select_sql,filter_sql,tipo):
    """
    Create CSV
    Args:
        view_id(Integer): ID of the View to query
        select_sql(String): String fields you want to retrieve. If are more than one,separate them by a coma (SQL Format)
        filro_sql(String): String with filters to add to the query (SQL Format)
    Returns:
        reultados(String): String in csv format.
    """    
    rows = devuelve_rows(view_id,select_sql,filter_sql)[0]
    if tipo == 'google_analytics':
        col = devuelve_rows(view_id,select_sql,filter_sql)[1]
        columns = []
        for n in range(len(col)):
            columns.append(col[n]['name'])
    else:
        columns = devuelve_rows(view_id,select_sql,filter_sql)[1]

    #Creating csv with ';' as separator
    out = ""
    for row in columns:
        out = out + row
        out = out + ";"
    out = out + '\n'
    for row in rows:
        for column in row:
            out = out + str(column)
            out = out + ";"
        out = out + '\n'
    return out.encode('utf-8')


def get_view_id(resource_id):
    """
    Gets the Id of the View (VISTA) in opendata_v_resourceVista table knowing the Id of the resource (ID_RESOURCEVISTA)
    """
    db_v = conexiones.conexion(configuracion.VIEWS_DB).cadena
    cursor_v = db_v.cursor()
    cursor_v.execute("SELECT VISTA from opendata_v_resourceVista WHERE ID_RESOURCEVISTA = "+ str(resource_id))   
    rows = cursor_v.fetchall()
    for i in rows:
        view_id = i[0]
    cursor_v.close()
    return view_id    
 

def date_handler(obj):
    """
    For date format in json.dumps()
    """    
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj


def google_analytics(profile,start_date,end_date,metrics,dimensions,filters,include_empty_rows,max_results,output,samplingLevel,segment,sort,start_index,fields):
    """Returns a query to google analytics API.
    https://developers.google.com/apis-explorer/#p/analytics/v3/
    Using:
    https://developers.google.com/apis-explorer/#p/analytics/v3/analytics.data.ga.get
     Args:
        start_date(String): Requests can specify a start date formatted as YYYY-MM-DD, or as a relative date (e.g., today, yesterday, or 7daysAgo). The default value is 7daysAgo. (string)
        end_date(String): Requests can specify a start date formatted as YYYY-MM-DD, or as a relative date (e.g., today, yesterday, or 7daysAgo). The default value is 7daysAgo. (string)
        metrics(String): A comma-separated list of Analytics metrics. E.g., 'ga:sessions,ga:pageviews'. At least one metric must be specified. (string)
        dimensions(String):A comma-separated list of Analytics dimensions. E.g., 'ga:browser,ga:city'.
        filters(String):A comma-separated list of dimension or metric filters to be applied to Analytics data. 
        include-empty-rows(Boolean):The response will include empty rows if this parameter is set to true, the default is true 
        max-results(Integer):The maximum number of entries to include in this feed. 
        output(String):The selected format for the response. Default format is JSON. 
        samplingLevel(String):The desired sampling level. 
        segment(String):An Analytics segment to be applied to data. 
        sort(String):A comma-separated list of dimensions or metrics that determine the sort order for Analytics data. 
        start-index(integer, 1+):An index of the first entity to retrieve. Use this parameter as a pagination mechanism along with the max-results parameter. 
        fields:Selector specifying which fields to include in a partial response.
    Returns:
        reultados(Dictionary): Array in dictionary format.
    """            
    # Use the Analytics Service Object to query the Core Reporting API
    service_account_email = configuracion.SERVICE_ACCOUNT_EMAIL
    
    #key_file_location = 'client_secrets.p12'
    key_file_location = configuracion.APP_PATH + '/client_secrets.p12'

    # Define the auth scopes to request.
    scope = ['https://www.googleapis.com/auth/analytics.readonly']
    
    service = get_service('analytics', 'v3', scope, key_file_location, service_account_email)
 
    resultado = service.data().ga().get(
        ids='ga:' + profile,
        start_date=start_date,
        end_date=end_date,
        metrics=metrics,
        dimensions=dimensions,
        filters=filters,
        include_empty_rows=include_empty_rows,
        max_results=max_results,
        output=output,
        samplingLevel=samplingLevel,
        segment=segment,
        sort=sort,
        start_index=start_index,
        fields=fields
        ).execute()

    #Return  results in JSON format indented.
    return json.dumps(resultado,ensure_ascii=False,sort_keys=True,indent=1) 


def get_service(api_name, api_version, scope, key_file_location,
                service_account_email):
  """Get a service that communicates to a Google API.

  Args:
    api_name: The name of the api to connect to.
    api_version: The api version to connect to.
    scope: A list auth scopes to authorize for the application.
    key_file_location: The path to a valid service account p12 key file.
    service_account_email: The service account email address.

  Returns:
    A service that is connected to the specified API.
  """

  f = open(key_file_location, 'rb')
  key = f.read()
  f.close()

  credentials = SignedJwtAssertionCredentials(service_account_email, key,scope=scope)

  http = credentials.authorize(httplib2.Http())

  # Build the service object.
  service = build(api_name, api_version, http=http)
  return service
