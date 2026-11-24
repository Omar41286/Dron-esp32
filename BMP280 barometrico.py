import machine
import time
from bmp280 import BMP280  # Asegúrate de que la clase esté en el mismo directorio o en el módulo correcto
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
def send_data_to_firebase(temperature, pressure):
    try:
        data = {
            "temperature": temperature,
            "pressure": pressure,
        }
        response = urequests.post(FIREBASE_URL, data=json.dumps(data))
        print("Datos enviados, respuesta de Firebase:", response.text)
        response.close()
    except Exception as e:
        print("Error al enviar datos a Firebase:", e)

# Configura el I2C
i2c = machine.I2C(1, scl=machine.Pin(22), sda=machine.Pin(21), freq=100000)

# Conecta a Wi-Fi
connect_to_wifi(SSID, PASSWORD)

# Inicializa el sensor BMP280
bmp = BMP280(i2c)

while True:
    # Obtener temperatura y presión
    temperature = bmp.getTemp()  # Temperatura en °C
    pressure = bmp.getPress() / 100  # Presión en hPa
    
     # Enviar datos a Firebase
    send_data_to_firebase(temperature, pressure)

    time.sleep(5)  # Espera antes de enviar de nuevo

    print('Temperatura: {:.2f} °C'.format(temperature))
    print('Presión: {:.2f} hPa'.format(pressure))
    print('Altitud: {:.2f} m'.format(bmp.getAltitude()))  # Altitud en metros
    print('--------------------')
    
    time.sleep(2)  # Esperar 2 segundos entre lecturas

