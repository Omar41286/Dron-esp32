from flask import Flask, render_template, request, Response
import socket
import cv2
import numpy as np
import threading
import time

app = Flask(__name__)

# Configuración del socket para enviar datos al ESP32
latest_frame = None
frame_lock = threading.Lock()
server_ip = '192.168.43.57'  # IP del ESP32
server_port = 8080
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def generate_frames():
    global latest_frame
    while True:
        with frame_lock:
            if latest_frame is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + latest_frame + b'\r\n')
        time.sleep(0.1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    global latest_frame
    if 'image/jpeg' in request.headers.get('Content-Type', ''):
        with frame_lock:
            latest_frame = request.data
        return 'OK', 200
    return 'Bad Request', 400

@app.route('/control', methods=['POST'])
def control():
    action = request.form.get('action')
    
    # Enviar el mensaje al ESP32
    s.sendto(action.encode(), (server_ip, server_port))

    return '', 204  # No content

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,threaded=True)