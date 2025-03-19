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
MQTT_TOPIC = "utng/sound"
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id()).decode()

# Sensor de sonido
ANALOG_PIN = machine.ADC(machine.Pin(34))
ANALOG_PIN.atten(machine.ADC.ATTN_11DB)
DIGITAL_PIN = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)

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

ultimo_estado = None
while True:
    analog_value = ANALOG_PIN.read()
    voltage = (analog_value / 4095) * 3300  # Convertir a milivoltios
    digital_value = DIGITAL_PIN.value()

    estado_actual = "Sound Detected" if digital_value == 1 else "No Sound"

    # Enviar solo si hay cambios
    if estado_actual != ultimo_estado:
        mensaje = f"Voltage: {voltage:.2f} mV | {estado_actual}"
        print("📡 Enviando:", mensaje)
        mqtt_client.publish(MQTT_TOPIC, mensaje)
        ultimo_estado = estado_actual
    
    time.sleep(1)  # Leer cada segundo
