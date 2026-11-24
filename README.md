# Dron-esp32
Diseñar y programar la elaboración de un dron a base de un controlador esp32 utilizando diversos actuadores y sensores 

Características principales
 **Telemetría en tiempo real:** Lectura de sensores barométricos (BMP280), giroscopios/acelerómetros (MPU6050) y módulos GPS.
 **Control a distancia:** Servidor web implementado con Flask y MicroPython para el manejo remoto de motores.
 **Base de datos:** Integración con Firebase para el almacenamiento y sincronización de datos de vuelo.

Tecnologías utilizadas
 **Lenguaje:** Python (MicroPython) / HTML5
 **Framework:** Flask (Servidor web)
 **Base de datos / Nube:** Firebase
 **Hardware:** Módulos GPS, sensores barométricos y IMU, controladores de motores.

Estructura del proyecto
  Dron/ -> Scripts principales en Python para la lectura de sensores (BMP280, GPS, MPU6050).
  Dron/Servidor Flask para control a distancia/ -> Interfaz web y backend para el comando de motores a distancia.
