import network
import time
import machine
import ubinascii
from umqtt.simple import MQTTClient

# Configuración WiFi
SSID = "vivoQR"
PASSWORD = "73hgj3jg"

# Configuración MQTT
MQTT_BROKER = "192.168.36.212"
MQTT_PORT = 1883
MQTT_TOPIC = "utng/knock"
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id()).decode()

# Sensor de golpes
KNOCK_SENSOR_PIN = machine.Pin(16, machine.Pin.IN, machine.Pin.PULL_UP)

# Conectar a WiFi
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)

    print("Conectando a WiFi...", end="")
    while not wlan.isconnected():
        time.sleep(1)
        print(".", end="")
    print("\n✅ Conectado a WiFi:", wlan.ifconfig())

# Conectar a MQTT
def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
    client.connect()
    print("✅ Conectado al broker MQTT:", MQTT_BROKER)
    return client

# Inicializar conexión
conectar_wifi()
mqtt_client = conectar_mqtt()

while True:
    if KNOCK_SENSOR_PIN.value() == 0:
        print("🔥 Golpe detectado!")
        mqtt_client.publish(MQTT_TOPIC, "Knock detected!")
        time.sleep(0.2)  # Pequeño retraso para evitar spam
    
    time.sleep(0.05)  # Sensibilidad de detección
