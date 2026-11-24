import machine
from machine import Pin, PWM, I2C
import time
import network
import socket
from time import sleep
from bmp180 import BMP180
import urequests
import json
from mpu6050 import MPU6050
import math

# Configuración de WiFi
SSID = 'Totalplay-2.4G-4730'
PASSWORD = 'He47PwKwSE2u73Hp'

# Configuración de Firebase
FIREBASE_URL = "https://dron-esp32-default-rtdb.firebaseio.com/datos.json"

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

MAX_RETRIES = 30
retries = 0

while not wlan.isconnected():
    print("Intentando conectar al WiFi...")
    time.sleep(1)
    retries += 1
    if retries >= MAX_RETRIES:
        print("No se pudo conectar al WiFi. Reiniciando...")
        machine.reset()

print("Conectado a la red WiFi")
print("IP del ESP32:", wlan.ifconfig()[0])  # Muestra la IP asignada

# Pines GPIO para los ESCs
esc_pins = [12, 13, 14, 15]               # Conexiones para los motores
pwm_freq = 50                             # Frecuencia PWM (en Hz)
led = Pin(2, Pin.OUT)                     # Inicializar led
i2c = I2C(1, scl=Pin(22), sda=Pin(21))    # Configuración de pines I2C

servo_pin = Pin(4)
servo = PWM(servo_pin)
servo.freq(50)  # La mayoría de los servos funcionan a 50 Hz

# Crear objetos PWM para cada ESC
escs = [PWM(Pin(pin), freq=pwm_freq, duty=0) for pin in esc_pins]

# Offsets individuales para cada ESC (ajusta estos valores si es necesario)
esc_offsets = [0, 0, 0, 0]

# Inicializar el sensor BMP180
bmp = BMP180(i2c)
bmp.oversample_sett = 2  # Configuración de sobremuestreo
bmp.sea_level_pressure = 101325  # Presión a nivel del mar (en Pa)

mpu = MPU6050(i2c)

# Enviar datos a Firebase
def send_data_to_firebase(temperature, pressure, altitude, roll, pitch):
    try:
        data = {
            "temperature": temperature,
            "pressure": pressure,
            "altitude": altitude,
             "orientation": {
                "roll": roll,
                "pitch": pitch
                }
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
    time.sleep(2)
    print("ESCs inicializados")

# Calibrar los ESCs
def calibrate_escs():
    print("Iniciando calibración...")
    
    # Señal máxima
    set_all_speeds(100)
    led.value(1)  # Encender el LED (HIGH)
    sleep(5)
    led.value(0)
    
    # Señal mínima
    set_all_speeds(0)
    time.sleep(2)
    print("Calibración completada.")

# Armando los ESCs
def arm_escs():
    print("Armando los ESCs...")
    set_all_speeds(0)
    time.sleep(2)
    print("ESCs armados")

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
        
def calculate_roll_pitch(accel_data):
    ax = accel_data['AcX']
    ay = accel_data['AcY']
    az = accel_data['AcZ']

    roll = math.atan2(ay, az) * (180 / math.pi)  # Convertir a grados
    pitch = math.atan2(-ax, math.sqrt(ay**2 + az**2)) * (180 / math.pi)  # Convertir a grados

    return roll, pitch

# Función para mover el servo a un ángulo específico
def move_servo(angle):
    # Mapear el ángulo a un rango de ciclo útil (duty cycle)
    min_duty = 26  # Ciclo útil para 0° (puedes ajustarlo según el servo)
    max_duty = 123  # Ciclo útil para 180° (ajústalo según el servo)
    duty = int(min_duty + (angle / 180) * (max_duty - min_duty))
    servo.duty(duty)

# Inicializar y calibrar los ESCs
init_escs()
calibrate_escs()
arm_escs()

# Crear un socket UDP para recibir datos
addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(addr)

print("Esperando datos UDP...")
led.value(1)

# Agregar una variable para el estado de los motores y velocidad mínima
motores_encendidos = False

# Recepción de comandos UDP
while True:
    temperature = bmp.temperature()   # Obtiene la temperatura en °C
    pressure = bmp.pressure()         # Obtiene la presión en Pa
    altitude = bmp.altitude()         # Calcula la altitud en metros
    
     # Leer datos del MPU6050
    accel_gyro_data = mpu.read_accel_gyro()
    
    # Calcular Roll y Pitch
    roll, pitch = calculate_roll_pitch(accel_gyro_data)
    
     # Enviar datos a Firebase
    send_data_to_firebase(temperature, pressure, altitude, roll, pitch)
    
    data, addr = s.recvfrom(1024)
    comando = data.decode().strip()
    print(f"Comando recibido: {comando}")

    if comando == "encender_motores":
        if not motores_encendidos:
            print("Encendiendo motores a velocidad mínima (10%)")
            set_all_speeds(10)
            motores_encendidos = True
        else:
            print("Los motores ya están encendidos")
    elif comando == "mover_adelante" and motores_encendidos:
        print("Acelerando motores hacia adelante al 30%")
        set_all_speeds(30)
    elif comando == "mover_atras" and motores_encendidos:
        print("Acelerando motores hacia atrás al 30%")
        set_all_speeds(30)
    elif comando == "detener":
        print("Deteniendo los motores")
        set_all_speeds(0)
        motores_encendidos = False
    elif comando.startswith("velocidad:") and motores_encendidos:
        try:
            velocidad = int(comando.split(":")[1])
            if 10 <= velocidad <= 30:
                print(f"Ajustando velocidad a {velocidad}%")
                set_all_speeds(velocidad)
            else:
                print("Velocidad fuera de rango (10-30%)")
        except ValueError:
            print("Error al interpretar la velocidad")
    elif comando.startswith("servo:"):
        try:
            angle = int(comando.split(":")[1])
            if 0 <= angle <= 180:
                print(f"Moviendo servo a {angle}°")
                move_servo(angle)
            else:
                print("Ángulo fuera de rango (0-180°)")
        except ValueError:
            print("Error al interpretar el ángulo del servo")
    else:
        print("Comando no reconocido o motores apagados")
        
        # Liberar memoria
    gc.collect()
    time.sleep(0.1)