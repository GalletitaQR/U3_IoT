import network
import time
from machine import Pin, ADC
from umqtt.simple import MQTTClient

# Configuración de la red Wi-Fi
wifi_ssid = "vivoQR"  # Cambia por tu SSID
wifi_password = "73hgj3jg"  # Cambia por tu contraseña

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
        client = MQTTClient("ky039_heartbeat_sensor_client", mqtt_broker, mqtt_port, keepalive=60)  # 60 segundos de keepalive
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        return None

# Configuración del sensor KY-039 (Sensor de ritmo cardíaco)
ANALOG_PIN = ADC(Pin(34))  # Pin ADC para leer el valor analógico del sensor
ANALOG_PIN.atten(ADC.ATTN_11DB)  # Configuración para una mayor gama de voltajes (hasta 3.6V)

# Función para leer el valor del sensor de ritmo cardíaco y enviarlo por MQTT
def read_heartbeat_sensor(client):
    try:
        # Leer el valor analógico del sensor
        analog_value = ANALOG_PIN.read()

        # Convertir el valor bruto a milivoltios
        voltage = (analog_value / 4095) * 3300  # Conversión a mV
        print(f"Analog Value: {analog_value} | Voltage: {voltage:.2f} mV")  # Agregar impresión para depuración

        # Enviar solo el valor de voltaje como mensaje
        message = f"{voltage:.2f}"

        # Enviar el mensaje a través de MQTT
        client.publish(mqtt_topic, message)
        print(f"Message sent: {message}")

    except Exception as e:
        print("Error al leer o enviar estado del sensor de ritmo cardíaco:", e)

# Main
connect_wifi()
client = connect_mqtt()
if client:
    # Iniciamos el loop de lectura y envío de datos del sensor de ritmo cardíaco
    while True:
        try:
            if client:
                client.check_msg()  # Revisar si hay mensajes MQTT

            read_heartbeat_sensor(client)  # Leer el valor del sensor de ritmo cardíaco y enviarlo
            time.sleep(1)  # Esperar un segundo antes de la siguiente lectura

        except Exception as e:
            print("Error en la comunicación MQTT:", e)
            client = connect_mqtt()
            time.sleep(1)  # Reintentar conexión

    time.sleep(0.1)
