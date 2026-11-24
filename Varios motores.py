from machine import Pin, PWM
import time

# Configura los pines GPIO que están conectados a los ESC de los motores
motor_pins = [
    PWM(Pin(12), freq=50),  # Motor 1
    PWM(Pin(13), freq=48),  # Motor 2
    PWM(Pin(14), freq=50),  # Motor 3
    PWM(Pin(15), freq=50)   # Motor 4
]

# Función para ajustar la velocidad de cada motor
def set_motor_speed(motor_index, speed_percent):
    min_duty = 40   # Valor mínimo del duty para armar el ESC (~1ms de pulso)
    max_duty = 80  # Valor máximo del duty (~2ms de pulso)

    # Calcular el valor de duty cycle para el porcentaje dado
    duty_value = int(min_duty + (max_duty - min_duty) * (speed_percent / 100))
    motor_pins[motor_index].duty(duty_value)

# Armar los ESC de cada motor
print("Armando los ESCs...")
for motor in motor_pins:
    motor.duty(0)  # Enviar señal de 0% para armar cada ESC
time.sleep(2)  # Esperar 2 segundos para armar

# Sincronización de motores
print("Sincronizando motores...")
for i in range(4):
    set_motor_speed(i, 0)  # Asegurarse de que todos los motores estén en 0% inicialmente

# Esperar un momento para asegurar que todos los motores están listos
time.sleep(1)

# Hacer girar todos los motores al 10% de la velocidad máxima al mismo tiempo
print("Motores girando al 10% de velocidad")
for i in range(4):
    set_motor_speed(i, 10)  # Establece el 10% de velocidad para cada motor

# Mantener los motores funcionando por 5 segundos
time.sleep(1)

# Detener todos los motores al mismo tiempo
print("Deteniendo los motores")
for i in range(4):
    set_motor_speed(i, 0)  # Detener cada motor

time.sleep(2)