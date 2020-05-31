import requests
import time
from math import sin,cos,atan2,sqrt,pi

# VARIABLES GLOBALES
TOKEN = 'BBFF-RY7bpMO28tnV2Vj2PUqbgNZOWW0BgA'
ETIQUETA = 'InternationalSpaceStation'
VARIABLE = "distancia"

URL_BASE = 'http://industrial.api.ubidots.com/api/v1.6/devices/'

# COORDENADAS
LAT = 37.894602
LONG = -4.803113

def get_iss_position():
    # POSICION ACTUAL ISS
    req_iss = requests.get('http://api.open-notify.org/iss-now.json')
    dict = req_iss.json()
    lat_lng = dict['iss_position']
    # GUARDAR LA POSICION ACTUAL
    lat_iss = float(lat_lng['latitude'])
    lng_iss = float(lat_lng['longitude'])
    return lat_iss, lng_iss

def grad2rad(grad):
    return grad * (pi/180)

def getDistance(lat_iss, lng_iss, lat, lng):
    R = 6371  # RADIO DE LA TIERRA EN KM
    dLat = grad2rad(lat-lat_iss)  
    dLng = grad2rad(lng-lng_iss)
    a = sin(dLat/2) * sin(dLat/2) + cos(grad2rad(lat_iss)) * \
        cos(grad2rad(lat)) * sin(dLng/2) * sin(dLng/2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = R * c  # DISTANCIA A LAS COORDENADAS EN KM
    return d

def build_payload(variable, value, lat_iss, lng_iss):
    # PAYLOAD A ENVIAR
    payload = {variable: value, "posicion": {
        "value": 1, "context": {"lat": lat_iss, "lng": lng_iss}}}
    return payload

def send_ubidots(etiqueta, payload):
    # HTTP REQUEST A UBIDOTS
    url = "{0}{1}/?token={2}".format(URL_BASE, etiqueta, TOKEN)
    status = 400
    attempts = 0

    while status >= 400 and attempts <= 5:
        req = requests.post(url, json=payload)
        status = req.status_code
        attempts += 1

    response = req.json()

    return response

def main(etiqueta, variable, lat, lng):
    lat_iss, lng_iss = get_iss_position()
    distance = getDistance(lat_iss, lng_iss, lat, lng)
    distance = round(distance, 1)
    payload = build_payload(variable, distance, lat_iss, lng_iss)
    response = send_ubidots(etiqueta, payload)

    return response

if __name__ == '__main__':
    while True:
        try:
            response = main(ETIQUETA, VARIABLE, LAT, LONG)
            print("Respuesta JSON desde el servidor: \n{0}".format(response))
        except:
            pass

        time.sleep(1)
