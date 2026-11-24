import network
import socket
import machine
import time

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

# Configura los pines GPIO para los motores
motor1 = machine.PWM(machine.Pin(12), freq=50)
motor2 = machine.PWM(machine.Pin(13), freq=50)
motor3 = machine.PWM(machine.Pin(14), freq=50)
motor4 = machine.PWM(machine.Pin(15), freq=50)

# Función para ajustar la velocidad del motor
def set_motor_speed(motor, speed_percent):
    min_duty = 40   # Valor mínimo del duty (~1ms de pulso)
    max_duty = 60  # Valor máximo del duty (~2ms de pulso)
    
    # Calcular el valor de duty cycle para el porcentaje dado
    duty_value = int(min_duty + (max_duty - min_duty) * (speed_percent / 100))
    motor.duty(duty_value)

# Armando los ESCs
print("Armando los ESCs...")
set_motor_speed(motor1, 100)  # Enviar señal de 0% para armar el ESC
set_motor_speed(motor2, 100)
set_motor_speed(motor3, 100)
set_motor_speed(motor4, 100)
time.sleep(5)  # Esperar 2 segundos para armar los ESC

# Crear un socket UDP para recibir datos
addr = socket.getaddrinfo('0.0.0.0', 8080)[0][-1]
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(addr)

print('Esperando datos...')

# Recibir los comandos UDP
while True:
    data, addr = s.recvfrom(1024)  # Tamaño máximo de mensaje
    print(f'Dato recibido: {data.decode()}')

    # Procesar los datos recibidos y controlar la velocidad de los motores
    if data.decode() == "mover_adelante":
        print("Motores adelante")
        set_motor_speed(motor1, 30)
        set_motor_speed(motor2, 30)
        set_motor_speed(motor3, 30)
        set_motor_speed(motor4, 30)
    elif data.decode() == "mover_atras":
        print("Motores atrás")
        set_motor_speed(motor1, 30)
        set_motor_speed(motor2, 30)
        set_motor_speed(motor3, 30)
        set_motor_speed(motor4, 30)
    elif data.decode() == "detener":
        print("Deteniendo los motores")
        set_motor_speed(motor1, 0)
        set_motor_speed(motor2, 0)
        set_motor_speed(motor3, 0)
        set_motor_speed(motor4, 0)
