import network
import time
from machine import Pin
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
        client = MQTTClient("ky040_rotary_encoder_client", mqtt_broker, mqtt_port, keepalive=60)  # 60 segundos de keepalive
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        return None

# Configuración del codificador rotatorio KY-040
CLK_PIN = Pin(18, Pin.IN, Pin.PULL_UP)  # Pin CLK
DT_PIN = Pin(19, Pin.IN, Pin.PULL_UP)   # Pin DT
SW_PIN = Pin(21, Pin.IN, Pin.PULL_UP)   # Pin SW (Botón)

counter = 0
last_state_clk = CLK_PIN.value()

# Función para leer el estado del codificador rotatorio y enviar el valor por MQTT
def read_rotary_encoder(client):
    global counter, last_state_clk

    try:
        current_state_clk = CLK_PIN.value()
        if current_state_clk != last_state_clk:
            if DT_PIN.value() != current_state_clk:
                counter += 1  # Sentido horario
            else:
                counter -= 1  # Sentido antihorario

            print("Posición:", counter)
            # Enviar la posición del codificador rotatorio como un valor
            client.publish(mqtt_topic, str(counter))

        last_state_clk = current_state_clk

        # Detectar si el botón está presionado
        if SW_PIN.value() == 0:
            print("Botón presionado")
            # Enviar el estado del botón por MQTT
            client.publish(mqtt_topic, "button_pressed")
            time.sleep(0.1)  # Evitar múltiples lecturas

    except Exception as e:
        print("Error al leer o enviar el estado del codificador rotatorio:", e)

# Main
connect_wifi()
client = connect_mqtt()
if client:
    # Iniciamos el loop de lectura y envío de datos del codificador rotatorio
    while True:
        try:
            if client:
                client.check_msg()  # Revisar si hay mensajes MQTT

            read_rotary_encoder(client)  # Leer el estado del codificador rotatorio y enviar
            time.sleep(0.05)  # Esperar un poco antes de la siguiente lectura

        except Exception as e:
            print("Error en la comunicación MQTT:", e)
            client = connect_mqtt()
            time.sleep(1)  # Reintentar conexión

    time.sleep(0.1)
