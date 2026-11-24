import pygame
import serial

# Inicializar Pygame para leer los controles
pygame.init()
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

# Configurar la conexión serial (ajusta 'COM3' al puerto correcto)
ser = serial.Serial('COM3', 115200, timeout=1)

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.JOYBUTTONDOWN:
                if joystick.get_button(0):  # Botón A
                    ser.write(b"LED_ON\n")
                    print("Comando enviado: Encender LED")
                elif joystick.get_button(1):  # Botón B
                    ser.write(b"LED_OFF\n")
                    print("Comando enviado: Apagar LED")
        
        pygame.time.wait(100)

except KeyboardInterrupt:
    print("Programa terminado")
finally:
    pygame.quit()
    ser.close()
