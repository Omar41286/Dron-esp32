import network
import socket
import time
from machine import Pin
import esp
import gc
import camera
import urequests  # Necesitarás esta librería para hacer las solicitudes HTTP

# Disable the watchdog timer
esp.osdebug(None)

# Free up memory
gc.collect()

# Wi-Fi credentials
SSID = 'Totalplay-2.4G-4730'
PASSWORD = 'He47PwKwSE2u73Hp'

# Connect to Wi-Fi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(SSID, PASSWORD)

# Wait for connection
while not wlan.isconnected():
    time.sleep(1)

print('Connected to Wi-Fi:', wlan.ifconfig())

# Camera setup
try:
    camera.deinit()  # Deinitialize the camera first
    camera.init(0, format=camera.JPEG, framesize=camera.FRAME_VGA)
    print("Camera initialized successfully")
except Exception as e:
    print("Camera initialization failed:", str(e))

# Dirección del servidor Flask
FLASK_SERVER_URL = 'http://192.168.100.8:5000/upload'  # Cambia esto a la IP de tu servidor Flask

# Función para capturar la imagen y enviarla a Flask
def capture_and_send_to_flask():
    try:
        img = camera.capture()  # Captura la imagen en formato JPEG
        headers = {'Content-Type': 'image/jpeg'}
        response = urequests.post(FLASK_SERVER_URL, data=img, headers=headers)
        print("Imagen enviada al servidor Flask. Respuesta:", response.text)
        response.close()
    except Exception as e:
        print("Error al enviar la imagen:", str(e))

# Crear un socket para manejar la solicitud HTTP básica
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 80))
s.listen(1)

print('Listening on', wlan.ifconfig()[0], 'port 80')

def web_page():
    return """<!DOCTYPE html>
<html>
<head>
    <title>ESP32-CAM Stream</title>
</head>
<body>
    <h1>Live Stream from ESP32-CAM</h1>
    <img src="/stream" />
</body>
</html>
"""

def stream():
    while True:
        try:
            img = camera.capture()  # Captura una imagen
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n')
            capture_and_send_to_flask()  # Enviar la imagen al servidor Flask
        except Exception as e:
            print("Error capturing image:", str(e))
            time.sleep(1)

while True:
    try:
        cl, addr = s.accept()
        print('Client connected from', addr)
        request = cl.recv(1024)
        request = str(request)
        
        if '/stream' in request:
            cl.send(b'HTTP/1.1 200 OK\r\n')
            cl.send(b'Content-Type: multipart/x-mixed-replace; boundary=frame\r\n\r\n')
            for frame in stream():
                cl.send(frame)
        else:
            response = web_page()
            cl.send('HTTP/1.1 200 OK\r\n')
            cl.send('Content-Type: text/html\r\n')
            cl.send('Connection: close\r\n\n')
            cl.sendall(response)
    except Exception as e:
        print("Error handling client:", str(e))
    finally:
        cl.close()

