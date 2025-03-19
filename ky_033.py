import network
import time
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración de la red Wi-Fi
wifi_ssid = "vivoQR"  # Cambia por tu SSID
wifi_password = "73hgj7jg"  # Cambia por tu contraseña

# Configuración del broker MQTT
mqtt_broker = "192.168.36.212"  # Nueva IP del broker
mqtt_port = 1883
mqtt_topic = "utng"  # Nuevo tema

# Conexión Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("Conectando a la red Wi-Fi...")
        wlan.connect(wifi_ssid, wifi_password)
        start_time = time.time()
        while not wlan.isconnected():
            time.sleep(1)
            if time.time() - start_time > 10:  # Tiempo de espera máximo de 10 segundos
                print("No se pudo conectar a la red Wi-Fi")
                return False
        print("Conexión Wi-Fi exitosa:", wlan.ifconfig())
    return True

def connect_mqtt():
    try:
        client = MQTTClient("ky033_line_sensor_client", mqtt_broker, mqtt_port, keepalive=60)  # 60 segundos de keepalive
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        return None

# Configuración del sensor KY-033 (Sensor de línea)
SENSOR_PIN = Pin(16, Pin.IN, Pin.PULL_UP)  # Configuramos el pin como entrada con pull-up

# Función para leer el estado del sensor de línea y enviar el valor por MQTT
def read_line_sensor(client):
    try:
        # Si el sensor detecta una línea, su valor será 1, si no, 0
        line_detected = 1 if SENSOR_PIN.value() == 1 else 0
        
        # Enviar el estado del sensor como un valor binario (1 o 0)
        client.publish(mqtt_topic, str(line_detected))
        print(f"Estado del sensor de línea enviado: {line_detected}")
    except Exception as e:
        print("Error al leer o enviar estado del sensor de línea:", e)

# Main
connect_wifi()
client = connect_mqtt()
if client:
    # Iniciamos el loop de lectura y envío de datos del sensor de línea
    while True:
        try:
            if client:
                client.check_msg()  # Revisar si hay mensajes MQTT

            read_line_sensor(client)  # Leer el estado del sensor de línea y enviar
            time.sleep(1)  # Esperar un segundo antes de la siguiente lectura

        except Exception as e:
            print("Error en la comunicación MQTT:", e)
            client = connect_mqtt()
            time.sleep(1)  # Reintentar conexión

    time.sleep(0.1)
