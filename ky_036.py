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
mqtt_topic = "utng/roma"  # Nuevo tema

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
        client = MQTTClient("ky036_touch_sensor_client", mqtt_broker, mqtt_port, keepalive=60)  # 60 segundos de keepalive
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        return None

# Configuración del sensor KY-036 (Sensor táctil capacitivo)
ANALOG_PIN = ADC(Pin(33))  # Pin ADC para leer el valor analógico del sensor
ANALOG_PIN.atten(ADC.ATTN_11DB)  # Configuración para una mayor gama de voltajes (hasta 3.6V)
DIGITAL_PIN = Pin(15, Pin.IN, Pin.PULL_UP)  # Pin digital para la señal de toque

# Función para leer el valor del sensor táctil y enviarlo por MQTT
def read_touch_sensor(client):
    try:
        # Leer el valor analógico del sensor
        analog_value = ANALOG_PIN.read()

        # Convertir el valor bruto a milivoltios
        voltage = (analog_value / 4095) * 3300  # Conversión a mV

        # Leer el valor digital del sensor
        digital_value = DIGITAL_PIN.value()

        # Formatear el mensaje para que sea un texto adecuado y no cause errores en SQL
        # Enviar solo los valores numéricos, evitando el uso de palabras reservadas como "Voltage"
        message = f"{voltage:.2f}"

        # Enviar el mensaje a través de MQTT
        client.publish(mqtt_topic, message)
        print(f"Message sent: {message}")

    except Exception as e:
        print("Error al leer o enviar estado del sensor táctil:", e)

# Main
connect_wifi()
client = connect_mqtt()
if client:
    # Iniciamos el loop de lectura y envío de datos del sensor táctil
    while True:
        try:
            if client:
                client.check_msg()  # Revisar si hay mensajes MQTT

            read_touch_sensor(client)  # Leer el valor del sensor táctil y enviarlo
            time.sleep(1)  # Esperar un segundo antes de la siguiente lectura

        except Exception as e:
            print("Error en la comunicación MQTT:", e)
            client = connect_mqtt()
            time.sleep(1)  # Reintentar conexión

    time.sleep(0.1)
