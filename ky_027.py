import network
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

# Configuración del sensor KY-027 y LED
sensor = Pin(15, Pin.IN)  # GPIO del sensor de vibración
led = Pin(4, Pin.OUT)  # LED del ESP32 (puedes cambiarlo)
contador = 0  # Contador de vibraciones
client = None  # Cliente MQTT

# Conexión Wi-Fi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a la red Wi-Fi...')
        wlan.connect(wifi_ssid, wifi_password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Conexión Wi-Fi exitosa:', wlan.ifconfig())

# Conexión MQTT
def connect_mqtt():
    global client
    try:
        client = MQTTClient("shock_sensor_client", mqtt_broker, mqtt_port)
        client.connect()
        print("Conectado al broker MQTT")
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        client = None

# Función para enviar datos al broker MQTT
def publish_data():
    global contador, client
    time.sleep_ms(50)  # Pequeño debounce
    if sensor.value() == 1:  # Si se detecta vibración
        contador += 1
        mensaje = f"1{contador}"
        print(mensaje)

        # Encender LED brevemente
        led.value(1)
        time.sleep(0.2)
        led.value(0)

        # Enviar mensaje por MQTT
        if client:
            try:
                client.publish(mqtt_topic, mensaje)
                print("Datos enviados a MQTT")
            except Exception as e:
                print("Error al enviar datos MQTT:", e)

# Configurar interrupción en el sensor de vibración
sensor.irq(trigger=Pin.IRQ_RISING, handler=lambda pin: publish_data())

# Main
connect_wifi()
connect_mqtt()

print("Esperando vibraciones...")
while True:
    time.sleep(1)  # Mantener el programa corriendo
