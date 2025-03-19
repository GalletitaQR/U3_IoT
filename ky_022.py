3import network
import time
from machine import Pin
from umqtt.simple import MQTTClient

# Configuración de la red Wi-Fi
wifi_ssid = "vivoQR"  # Cambia por tu SSID
wifi_password = "73hgj3jg"  # Cambia por tu contraseña

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
        retries = 0
        while not wlan.isconnected() and retries < 10:
            time.sleep(1)
            retries += 1
            print(f"Reintentando conexión Wi-Fi... {retries}/10")
        if retries == 10:
            print("No se pudo conectar a Wi-Fi después de varios intentos")
        else:
            print("Conexión Wi-Fi exitosa:", wlan.ifconfig())

def connect_mqtt():
    try:
        client = MQTTClient("ky022_ir_client", mqtt_broker, mqtt_port)
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        return None

# Configuración del sensor IR KY-022
IR_PIN = Pin(17, Pin.IN)  # Cambia el número de pin si es necesario

# Función de interrupción que se ejecutará cuando se detecte una señal IR
def ir_callback(pin):
    print("Señal IR detectada")
    send_mqtt_message(client, '1')  # Enviar mensaje "1" al broker cuando se detecta la señal IR

# Configuración de la interrupción en el pin IR
IR_PIN.irq(trigger=Pin.IRQ_FALLING, handler=ir_callback)

# Función para enviar mensajes al broker MQTT
def send_mqtt_message(client, message):
    try:
        client.publish(mqtt_topic, message)
        print(f"Mensaje enviado al broker: {message}")
    except Exception as e:
        print(f"Error al enviar mensaje MQTT: {e}")

# Main
connect_wifi()
client = connect_mqtt()
if client:
    while True:
        time.sleep(1)  # El bucle sigue corriendo esperando interrupciones IR
