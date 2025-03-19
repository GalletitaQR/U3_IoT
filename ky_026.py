from machine import Pin, ADC
import time
import network
from umqtt.simple import MQTTClient

# Configuración de pines del KY-026
sensor_digital = Pin(17, Pin.IN)  # Salida digital (0 = llama detectada, 1 = sin llama)
sensor_analogico = ADC(Pin(35))  # Salida analógica (intensidad de la llama)
sensor_analogico.atten(ADC.ATTN_11DB)  # Rango de 0 a 3.3V

# Configuración WiFi
WIFI_SSID = "vivoQR"
WIFI_PASSWORD = "73hgj3jg"

# Configuración MQTT
MQTT_CLIENT_ID = "esp32_ky026_llama"
MQTT_BROKER = "192.168.36.212"  # Cambia esto por la IP de tu broker MQTT
MQTT_PORT = 1883
MQTT_TOPIC_PUB_ESTADO = "utng/roma"  # Topic MQTT para el estado de la llama
MQTT_TOPIC_PUB_INTENSIDAD = "utng/roma"  # Topic MQTT para la intensidad de la llama

# Variables de control
ultimo_estado = None  # Estado anterior del sensor digital
ultimo_nivel = None   # Última intensidad medida
umbral_cambio = 100   # Diferencia mínima en intensidad para enviar
tiempo_ping = time.time()  # Control del tiempo para mantener MQTT activo

# Función para conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.3)
    print("\nWiFi Conectada!")

# Conectar a WiFi
conectar_wifi()

# Función para conectar a MQTT
def conectar_mqtt():
    global client
    try:
        print("Conectando a MQTT...")
        client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)
        client.connect()
        print(f"Conectado a {MQTT_BROKER}")
    except OSError as e:
        print(f"Error al conectar a MQTT: {e}")
        time.sleep(5)
        conectar_mqtt()

# Conectar a MQTT
conectar_mqtt()

# Bucle principal
while True:
    try:
        # Leer el estado del sensor digital (0 = llama detectada, 1 = sin llama)
        estado = sensor_digital.value()
        
        # Publicar SIEMPRE el estado de la llama si cambia
        if estado != ultimo_estado:
            print(f"Publicando estado: {estado}")
            try:
                client.publish(MQTT_TOPIC_PUB_ESTADO, bytes([estado]))  # Enviar como byte
            except OSError:
                print("[ERROR] Fallo al publicar estado. Reintentando conexión...")
                conectar_mqtt()
            ultimo_estado = estado  # Actualizamos el estado para la próxima iteración

        # Leer la intensidad de la llama (valor analógico)
        nivel = sensor_analogico.read()
        
        # Publicar solo si la intensidad cambia significativamente
        if ultimo_nivel is None or abs(nivel - ultimo_nivel) > umbral_cambio:
            print(f"Publicando intensidad: {nivel}")
            try:
                client.publish(MQTT_TOPIC_PUB_INTENSIDAD, str(nivel).encode())  # Enviar como bytes
            except OSError:
                print("[ERROR] Fallo al publicar intensidad. Reintentando conexión...")
                conectar_mqtt()
            ultimo_nivel = nivel  # Guardamos el último nivel leído

        # Mantener la conexión activa enviando un ping cada 30 segundos
        if time.time() - tiempo_ping > 30:
            try:
                client.ping()
                print("[INFO] Ping MQTT enviado")
            except OSError:
                print("[ERROR] Ping fallido. Reintentando conexión MQTT...")
                conectar_mqtt()
            tiempo_ping = time.time()

    except OSError as e:
        print(f"Error al leer el sensor: {e}")
        conectar_mqtt()  # Intentar reconectar en caso de error

    time.sleep(1)  # Leer cada 1 segundo
