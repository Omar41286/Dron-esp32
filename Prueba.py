import machine
from time import sleep
from micropyGPS import MicropyGPS
from bmp280 import BMP280
import network
import urequests
import json

# Configuración Wi-Fi
SSID = "'Totalplay-2.4G-4730'"
PASSWORD = "He47PwKwSE2u73Hp" 

# Configuración de Firebase
FIREBASE_URL = "https://dron-esp32-default-rtdb.firebaseio.com/datos.json"

# Conexión a Wi-Fi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print("Conectado a Wi-Fi:", wlan.ifconfig())

# Enviar datos a Firebase
def send_data_to_firebase(temperature, pressure, gps_data):
    try:
        data = {
            "temperature": temperature,
            "pressure": pressure,
            "gps": gps_data
        }
        response = urequests.post(FIREBASE_URL, data=json.dumps(data))
        print("Datos enviados, respuesta de Firebase:", response.text)
        response.close()
    except Exception as e:
        print("Error al enviar datos a Firebase:", e)

# Configuración I2C y sensores
i2c = machine.I2C(1, scl=machine.Pin(22), sda=machine.Pin(21), freq=100000)
bmp = BMP280(i2c)
gps_serial = machine.UART(2, baudrate=9600, tx=17, rx=16)
my_gps = MicropyGPS()

# Conecta a Wi-Fi
connect_to_wifi(SSID, PASSWORD)

while True:
    try:
        # Leer datos del BMP280
        temperature = bmp.getTemp()
        pressure = bmp.getPress() / 100  # Esto debería funcionar si bmp.getPress() devuelve un número


        # Leer datos GPS
        gps_data = {}
        if gps_serial.any():
            data = gps_serial.read()
            for byte in data:
                my_gps.update(chr(byte))

            # Extraer información GPS si está disponible
            gps_data = {
                "latitude": my_gps.latitude_string() if my_gps.latitude else None,
                "longitude": my_gps.longitude_string() if my_gps.longitude else None,
                "altitude": my_gps.altitude,
                "satellites": my_gps.satellites_in_use,
                "timestamp": my_gps.timestamp
            }

        # Enviar datos a Firebase
        send_data_to_firebase(temperature, pressure, gps_data)

        sleep(5)  # Espera antes de enviar de nuevo
    
    except Exception as e:
        print("Error en el bucle principal:", e)
