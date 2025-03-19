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
        client = MQTTClient("ky035_magnetic_sensor_client", mqtt_broker, mqtt_port, keepalive=60)  # 60 segundos de keepalive
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        return None

# Configuración del sensor KY-035 (Sensor de campo magnético)
SENSOR_PIN = ADC(Pin(33))  # Pin ADC para leer el valor analógico del sensor
SENSOR_PIN.atten(ADC.ATTN_11DB)  # Configuración para una mayor gama de voltajes (hasta 3.6V)

# Función para leer el valor del sensor de campo magnético y enviarlo por MQTT
def read_magnetic_field(client):
    try:
        # Leer el valor bruto del sensor
        raw_value = SENSOR_PIN.read()

        # Convertir el valor bruto a milivoltios
        voltage = (raw_value / 4095) * 3300  # Conversión a mV

        # Enviar el valor de voltaje del campo magnético como un mensaje MQTT
        client.publish(mqtt_topic, str(voltage))
        print(f"Campo magnético: {voltage} mV")

    except Exception as e:
        print("Error al leer o enviar estado del sensor de campo magnético:", e)

# Main
connect_wifi()
client = connect_mqtt()
if client:
    # Iniciamos el loop de lectura y envío de datos del sensor de campo magnético
    while True:
        try:
            if client:
                client.check_msg()  # Revisar si hay mensajes MQTT

            read_magnetic_field(client)  # Leer el valor del campo magnético y enviarlo
            time.sleep(1)  # Esperar un segundo antes de la siguiente lectura

        except Exception as e:
            print("Error en la comunicación MQTT:", e)
            client = connect_mqtt()
            time.sleep(1)  # Reintentar conexión

    time.sleep(0.1)
