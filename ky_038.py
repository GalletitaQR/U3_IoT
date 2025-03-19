import network
import time
from machine import Pin, ADC
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
        print('Conectando a la red Wi-Fi...')
        wlan.connect(wifi_ssid, wifi_password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Conexión Wi-Fi exitosa:', wlan.ifconfig())

# Configuración del sensor KY-038
ANALOG_PIN = ADC(Pin(34))  # Pin analógico para el sensor de sonido
ANALOG_PIN.atten(ADC.ATTN_11DB)  # Configuración para leer un rango de 0-3.3V
DIGITAL_PIN = Pin(15, Pin.IN, Pin.PULL_UP)  # Pin digital para detección de sonido

# Conexión MQTT
def connect_mqtt():
    try:
        client = MQTTClient("sound_sensor_client", mqtt_broker, mqtt_port)
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        return None

# Enviar datos solo si el valor del sensor cambia
def publish_data(client, last_value):
    if client is None:
        print("Cliente MQTT no disponible, reintentando conexión...")
        return last_value
    
    try:
        analog_value = ANALOG_PIN.read()  # Leer valor analógico
        voltage_int = int((analog_value / 4095) * 1023)  # Convertir a entero (escala de 0 a 1023)
        digital_value = DIGITAL_PIN.value()  # Leer estado digital (si se detecta sonido)

        # Aquí decides si quieres enviar el valor analógico o digital como entero
        payload = voltage_int  # O puedes usar "payload = digital_value" si prefieres el estado digital
        
        # Si el valor ha cambiado, publicamos el mensaje
        if payload != last_value:  # Solo enviar si hay un cambio
            client.publish(mqtt_topic, str(payload))  # Enviar como un entero convertido a string
            print("Datos enviados:", payload)
            return payload  # Guardar nuevo estado
        return last_value
    except Exception as e:
        print("Error al leer el sensor o enviar datos:", e)
        return last_value

# Main
connect_wifi()
client = connect_mqtt()

last_value = None  # Inicializar como None (sin valor previo)

while True:
    last_value = publish_data(client, last_value)
    time.sleep(1)  # Espera de 1 segundo antes de la siguiente lectura
