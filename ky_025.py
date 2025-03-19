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
MQTT_TOPIC = "utng/reed"
MQTT_CLIENT_ID = ubinascii.hexlify(machine.unique_id()).decode()

# Configurar sensores Reed
REED_SENSOR_ANALOG_PIN = machine.ADC(machine.Pin(36))
REED_SENSOR_ANALOG_PIN.atten(machine.ADC.ATTN_11DB)  # Máxima lectura de voltaje
REED_SENSOR_DIGITAL_PIN = machine.Pin(17, machine.Pin.IN, machine.Pin.PULL_UP)

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

ultimo_estado = REED_SENSOR_DIGITAL_PIN.value()

while True:
    analog_value = REED_SENSOR_ANALOG_PIN.read()  # Leer valor analógico
    digital_value = REED_SENSOR_DIGITAL_PIN.value()  # Leer estado digital

    # Enviar cada 1 segundo el valor analógico
    mqtt_client.publish(MQTT_TOPIC, f"Analog: {analog_value}")
    print(f"📡 Enviado MQTT: Analog: {analog_value}")

    # Enviar alerta solo si cambia el estado digital
    if digital_value != ultimo_estado:
        estado_texto = "Threshold Reached" if digital_value else "Not Reached"
        mqtt_client.publish(MQTT_TOPIC, f"Digital: {estado_texto}")
        print(f"📡 Enviado MQTT: Digital: {estado_texto}")
        ultimo_estado = digital_value

    time.sleep(1)  # Pequeña pausa para evitar saturar la red
