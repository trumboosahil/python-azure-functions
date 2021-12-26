import logging
import jsonpickle
import azure.functions as func
import numpy as np
import json
from typing import List
from json import JSONEncoder
import urllib3
from datetime import datetime
import numpy as np
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    location = req.params.get('locations')
    if not location:
        try:
            req_body = req.get_body()          
            requestjson = jsonpickle.decode(req_body)
            loc = requestjson['locations']
            resp = getRouteMatrix(loc)
            print(resp)
            respdata = json.loads(resp)
            dict = respdata["matrix"]["distances"]
            data = list(dict)
            matrix = np.array(data)
            matrix[np.isnan(matrix)] = 0
            matrix = matrix[~np.isnan(matrix)]          
            count =len(loc)
            newshape = matrix.reshape(count,-1)
            dm = np.array(newshape)             
        except ValueError:
            pass
    

    if location:
        return func.HttpResponse(f"Hello, {dm}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
def getRouteMatrix(location):
    http = urllib3.PoolManager()
    matrixAttributes = ['travelTimes']
    rootobject = root(location,[],regionDefinitions("world"),None,None,None,matrixAttributes)
    encoded_data = jsonpickle.encode(rootobject, unpicklable=False)

    resp = http.request(
        'POST',
        'https://matrix.router.hereapi.com/v8/matrix',
        body=encoded_data,
        headers={'Content-Type': 'application/json'}
    )
    return resp.data
class origin(object): 
    def __init__(self, lat: float, lng: float): 
        self.lat = lat 
        self.lng = lng
class regionDefinitions(object):
     def __init__(self, type: str): 
        self.type = type 
class root(object):
    def __init__(self,origins: List[origin],destinations: List[origin],regionDefinition: regionDefinitions,
         departureTime: str,transportMode: str,routingMode: str,matrixAttributes: List[str]):
         self.origins = origins
         self.destinations = None
         self.regionDefinition = regionDefinition
         self.departureTime = departureTime
         self.transportMode = transportMode
         self.routingMode = routingMode
         self.profile = "carFast"
         self.matrixAttributes = matrixAttributes
class networkcentroidRequest(object):
     def __init__(self,locations: List[origin],numberofcentroid: int):
         self.locations = locations
         self.numberofcentroid = numberofcentroid
