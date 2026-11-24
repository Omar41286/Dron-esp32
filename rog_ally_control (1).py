import pygame
import socket

# Inicializar Pygame
pygame.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()

motores_encendidos = False

# Crear el socket para enviar datos al ESP32
server_ip = '192.168.43.57'  # IP del ESP32
server_port = 8080
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    pygame.event.pump()

    boton_arrancar = joystick.get_button(0)  # Botón "A"
    boton_apagar = joystick.get_button(1)    # Botón "B"

    if boton_arrancar and not motores_encendidos:
        message = "encender_motores"
        motores_encendidos = True
    elif boton_apagar:
        message = "detener"
        motores_encendidos = False
    elif motores_encendidos:
        eje_y = joystick.get_axis(1)
        if eje_y < -0.5:
            message = "mover_adelante"
        elif eje_y > 0.5:
            message = "mover_atras"
        else:
            message = ""  # No envía comando para mantener la velocidad actual
    else:
        message = ""  # No enviar mensajes innecesarios

    if message:  # Solo enviar si hay un comando válido
        s.sendto(message.encode(), (server_ip, server_port))
        print(f"Estado de los motores: {'Encendidos' if motores_encendidos else 'Apagados'}, Acción: {message}")

    pygame.time.delay(100)