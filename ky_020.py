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
MQTT_TOPIC = "utng/tilt"
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id()).decode()

# Configurar el sensor de inclinación
TILT_SWITCH_PIN = machine.Pin(4, machine.Pin.IN, machine.Pin.PULL_UP)

# Conectar a WiFi
def conectar_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    
    print("Conectando a WiFi...", end="")
    while not wlan.isconnected():
        time.sleep(1)
        print(".", end="")
    print("\nConectado a WiFi:", wlan.ifconfig())

# Conectar a MQTT
def conectar_mqtt():
    client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, MQTT_PORT)
    client.connect()
    print("Conectado al broker MQTT:", MQTT_BROKER)
    return client

# Inicializar conexión
conectar_wifi()
mqtt_client = conectar_mqtt()

ultimo_estado = TILT_SWITCH_PIN.value()

while True:
    estado_actual = TILT_SWITCH_PIN.value()

    if estado_actual == 0 and ultimo_estado == 1:  # Detectar cambio de estado
        print("⛔ ¡Inclinación detectada!")
        mqtt_client.publish(MQTT_TOPIC, "TILT DETECTED")  # Enviar alerta
        print("📡 Publicado en MQTT:", MQTT_TOPIC)
        time.sleep(1)  # Pequeña pausa para evitar spam

    ultimo_estado = estado_actual
    time.sleep(0.1)  # Pequeño retraso para evitar rebotes
