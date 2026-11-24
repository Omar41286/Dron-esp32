from machine import Pin, PWM
from time import sleep
import time
import network
import socket
import urequests
import json

# Configuración de WiFi
SSID = 'Totalplay-2.4G-4730'
PASSWORD = 'He47PwKwSE2u73Hp'

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

while not wlan.isconnected():
    pass

print("Conectado a la red WiFi")
print("IP del ESP32:", wlan.ifconfig()[0])  # Muestra la IP asignada

# Pines GPIO para los ESCs
esc_pins = [12, 13, 14, 15]  # Ajusta estos números según tus conexiones
pwm_freq = 50  # Frecuencia PWM (en Hz)
led = Pin(2, Pin.OUT)

# Crear objetos PWM para cada ESC
escs = [PWM(Pin(pin), freq=pwm_freq, duty=0) for pin in esc_pins]

# Offsets individuales para cada ESC (ajusta estos valores si es necesario)
esc_offsets = [0, 0, 0, 0]

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
    led.value(1)  # Encender el LED (HIGH)
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

# Recibir los comandos UDP
while True:
    data, addr = s.recvfrom(1024)
    comando = data.decode().strip()
    print(f"Comando recibido: {comando}")

    # Controlar la velocidad de los motores según el comando recibido
    if comando == "mover_adelante":
        print("Motores adelante")
        set_all_speeds(10)  # Ajusta la velocidad según lo necesites
    elif comando == "mover_atras":
        print("Motores atrás")
        set_all_speeds(10)  # Puedes cambiar el comportamiento si deseas
    elif comando == "Detener":
        print("Deteniendo los motores")
        set_all_speeds(0)
    
