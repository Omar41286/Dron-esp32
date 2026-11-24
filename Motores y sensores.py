import machine
from machine import Pin, PWM, I2C
from time import sleep
import network
import socket
import urequests
import json
from bmp280 import BMP280
from micropyGPS import MicropyGPS

# Configuración Wi-Fi
SSID = "'Totalplay-2.4G-4730'"
PASSWORD = "He47PwKwSE2u73Hp"

# Configuración de Firebase
FIREBASE_URL = "https://dron-esp32-default-rtdb.firebaseio.com/datos.json"

# Pines GPIO para los ESCs
esc_pins = [12, 13, 14, 15]  # Ajusta estos números según tus conexiones
pwm_freq = 50  # Frecuencia PWM (en Hz)
led = Pin(2, Pin.OUT)

# Instanciar el objeto micropyGPS
my_gps = MicropyGPS()

# Crear objetos PWM para cada ESC
escs = [PWM(Pin(pin), freq=pwm_freq, duty=0) for pin in esc_pins]

# Offsets individuales para cada ESC (ajusta estos valores si es necesario)
esc_offsets = [0, 0, 0, 0]

# Conexión a Wi-Fi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        pass
    print("Conectado a Wi-Fi:", wlan.ifconfig())
    return wlan

# Enviar datos a Firebase
def send_data_to_firebase(temperature, pressure, latitude, longitude):
    try:
        data = {
            "temperature": temperature,
            "pressure": pressure,
            "latitude": latitude,
            "longitude": longitude,
        }
        response = urequests.post(FIREBASE_URL, data=json.dumps(data))
        print("Datos enviados, respuesta de Firebase:", response.text)
        response.close()
    except Exception as e:
        print("Error al enviar datos a Firebase:", e)

# Mapeo de valores de velocidad
def map_value(value, in_min, in_max, out_min, out_max):
    return int((value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

# Inicializar los ESCs
def init_escs():
    print("Iniciando ESCs...")
    for esc in escs:
        esc.duty(0)
    sleep(2)
    print("ESCs inicializados")

# Calibrar los ESCs
def calibrate_escs():
    print("Iniciando calibración...")
    set_all_speeds(100)
    set_all_speeds(0)
    sleep(2)
    print("Calibración completada.")

# Armando los ESCs
def arm_escs():
    print("Armando los ESCs...")
    set_all_speeds(0)
    sleep(2)
    print("ESCs armados")
    led.value(1)
    sleep(5)
    led.value(0)

# Establece la velocidad de un ESC específico
def set_individual_speed(esc_index, speed):
    if 0 <= speed <= 100 and 0 <= esc_index < len(escs):
        adjusted_speed = speed + esc_offsets[esc_index]
        adjusted_speed = max(0, min(100, adjusted_speed))
        duty = map_value(adjusted_speed, 0, 100, 51, 102)  # Mapea de 1000µs a 2000µs
        escs[esc_index].duty(duty)
        print(f"ESC {esc_index} velocidad: {adjusted_speed}%")
    else:
        print("Índice de ESC o velocidad inválidos")

# Establece la misma velocidad para todos los ESCs
def set_all_speeds(speed):
    for i in range(len(escs)):
        set_individual_speed(i, speed)

# Configuración principal
wlan = connect_to_wifi(SSID, PASSWORD)
i2c = I2C(1, scl=Pin(22), sda=Pin(21), freq=100000)
gps_serial = machine.UART(2, baudrate=9600, tx=17, rx=16)
bmp = BMP280(i2c)

init_escs()
calibrate_escs()
arm_escs()

# Crear un socket UDP para recibir datos
addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(addr)

print("Esperando datos UDP...")
led.value(1)

# Bucle principal
while True:
    # Leer datos del sensor BMP280
    temperature = bmp.getTemp()
    pressure = bmp.getPress() / 100  # Convertir presión a hPa
    altitude = bmp.getAltitude()

    # Leer datos del GPS
    latitude, longitude = None, None
    while gps_serial.any():
        data = gps_serial.read()
        for byte in data:
            stat = my_gps.update(chr(byte))
            if stat is not None:
                # Verificar si el GPS tiene datos válidos (latitud y longitud)
                if my_gps.latitude != 0 and my_gps.longitude != 0:
                    latitude = my_gps.latitude_string()
                    longitude = my_gps.longitude_string()
                    print('Latitud:', latitude)
                    print('Longitud:', longitude)
                    break  # Salir cuando tengamos datos válidos

    # Enviar datos a Firebase incluso si el GPS no está listo
    send_data_to_firebase(temperature, pressure, latitude, longitude)

    print('Temperatura: {:.2f} °C'.format(temperature))
    print('Presión: {:.2f} hPa'.format(pressure))
    print('Altitud: {:.2f} m'.format(altitude))
    print('Latitud:', latitude if latitude else 'Esperando GPS...')
    print('Longitud:', longitude if longitude else 'Esperando GPS...')
    print('--------------------')
    
    # Comprobar si hay comandos UDP
    s.setblocking(False)
    try:
        data, addr = s.recvfrom(1024)
        comando = data.decode().strip()
        print(f"Comando recibido: {comando}")

        if comando == "mover_adelante":
            print("Motores adelante")
            set_all_speeds(70)
        elif comando == "mover_atras":
            print("Motores atrás")
            set_all_speeds(70)
        elif comando == "Iniciar motores":
            print("Iniciando los motores")
            set_all_speeds(10)
        elif comando == "Detener":
            print("Deteniendo los motores")
            set_all_speeds(0)
        elif comando.startswith("velocidad:"):
            try:
                velocidad = int(comando.split(":")[1])
                print(f"Ajustando velocidad a {velocidad}%")
                set_all_speeds(velocidad)
            except ValueError:
                print("Error al interpretar la velocidad")
        else:
            print("Comando no reconocido")
    except:
        pass

    s.setblocking(True)
    sleep(2)  # Esperar 2 segundos entre lecturas y comandos
