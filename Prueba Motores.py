from machine import Pin, PWM
import time

# Configura el pin GPIO que está conectado al ESC
motor_pin = PWM(Pin(12), freq=50)  # GPIO14, frecuencia de 50Hz (PWM estándar para ESC)


# Función para ajustar la velocidad del motor
# duty_cycle va de 0 a 1023, donde 1023 es 100% y 0 es 0%
def set_motor_speed(speed_percent):
    # Convertimos el porcentaje de velocidad (0-100%) al duty cycle de PWM (40-115 range)
    min_duty = 40   # Valor mínimo del duty para armar el ESC (~1ms de pulso)
    max_duty = 60  # Valor máximo del duty (~2ms de pulso)
    
    # Calcular el valor de duty cycle para el porcentaje dado
    duty_value = int(min_duty + (max_duty - min_duty) * (speed_percent / 100))
    motor_pin.duty(duty_value)
   

# Armando el ESC
print("Armando el ESC...")
set_motor_speed(0)  # Enviar señal de 0% para armar el ESC
time.sleep(2)       # Esperar 2 segundos para  armar

# Hacer girar el motor al 10% de la velocidad máxima
print("Motor girando al 10% de velocidad")
set_motor_speed(10)  # Establece el 10% de velocidad

# Mantener el motor funcionando por 5 segundos
time.sleep(2)

# Detener el motor
print("Deteniendo el motor")
set_motor_speed(0)  # Detener el motor
time.sleep(2)
