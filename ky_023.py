import network
import time
import machine
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración de la red Wi-Fi
wifi_ssid = "vivoQR"
wifi_password = "73hgj3jg"  # Cambia por tu contraseña

# Configuración del broker MQTT
mqtt_broker = "192.168.36.212"  # IP del broker
mqtt_port = 1883
mqtt_topic = "utng"

# Configuración del sensor KY-023
JOYSTICK_X = machine.ADC(machine.Pin(33))
JOYSTICK_Y = machine.ADC(machine.Pin(32))
BUTTON = machine.Pin(5, machine.Pin.IN, machine.Pin.PULL_UP)

JOYSTICK_X.atten(machine.ADC.ATTN_11DB)
JOYSTICK_Y.atten(machine.ADC.ATTN_11DB)

# Conexión Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(wifi_ssid, wifi_password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Conexión Wi-Fi exitosa:', wlan.ifconfig())

# Conexión MQTT
def connect_mqtt():
    try:
        client = MQTTClient("sensor_temp_client", mqtt_broker, mqtt_port)
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        return None

def leer_joyStick():
    x_value = JOYSTICK_X.read()
    y_value = JOYSTICK_Y.read()
    button_state = BUTTON.value()
    return("X:", x_value, "Y:", y_value, "Button:", "Not Pressed" if button_state else "Pressed")


def publish_data(client):
    if client is None:
        print("Cliente MQTT no disponible, reintentando conexión...")
        return
    
    try:
        lectura = leer_joyStick()
        if lectura is None:
            print("Error: valor no valido")
            return

        # Redondear la temperatura a un número entero
        payload = str(lectura)  # Convertir el valor redondeado a string
        print(f"Enviando datos: {payload} °C")  # Imprimir el payload antes de enviarlo
        client.publish(mqtt_topic, payload)
        print("Datos enviados:", payload, "°C")
    except Exception as e:
        print("Error al leer el sensor o enviar datos:", e)

# Main
connect_wifi()
client = connect_mqtt()

while True:
    publish_data(client)
    time.sleep(10)  # Esperar 10 segundos antes del próximo envío
