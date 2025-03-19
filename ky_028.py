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

# Configuración del sensor KY-028
TEMP_SENSOR_ANALOG_PIN = ADC(Pin(34))  # Sensor analógico (ADC) en el pin 36
TEMP_SENSOR_ANALOG_PIN.atten(ADC.ATTN_11DB)  # Rango de 0 a 3.3V
TEMP_SENSOR_DIGITAL_PIN = Pin(17, Pin.IN, Pin.PULL_UP)  # Salida digital del sensor
LED_PIN = Pin(16, Pin.OUT)  # LED indicador

# Conexión MQTT
def connect_mqtt():
    try:
        client = MQTTClient("ky028_sensor_client", mqtt_broker, mqtt_port)
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
        analog_value = TEMP_SENSOR_ANALOG_PIN.read()  # Leer valor analógico (0-4095)
        digital_value = TEMP_SENSOR_DIGITAL_PIN.value()  # Leer estado digital (umbral)

        # Encender LED si el umbral se ha superado
        if digital_value:
            LED_PIN.on()
            print(f"Temperatura alta - Analógico: {analog_value}")
        else:
            LED_PIN.off()
            print(f"Temperatura normal - Analógico: {analog_value}")

        # Enviar solo el valor analógico como INT si ha cambiado
        if analog_value != last_value:
            client.publish(mqtt_topic, str(analog_value))  # Enviar solo el entero
            print("Datos enviados:", analog_value)
            return analog_value  # Guardar nuevo estado
        
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
