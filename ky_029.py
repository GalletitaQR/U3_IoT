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
mqtt_topic = "utng/led"  # Nuevo tema para el actuador KY-029

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
        client = MQTTClient("ky029_led_client", mqtt_broker, mqtt_port, keepalive=60)  # 60 segundos de keepalive
        client.connect()
        print("Conectado al broker MQTT")
        return client
    except Exception as e:
        print("Error al conectar con MQTT:", e)
        return None

# Configuración del actuador KY-029 (LED rojo y verde)
LED_RED_PIN = Pin(16, Pin.OUT)  # Pin del LED rojo
LED_GREEN_PIN = Pin(17, Pin.OUT)  # Pin del LED verde

# Función para controlar los LEDs y enviar el estado por MQTT
def control_leds(client):
    try:
        # Alternar LEDs
        LED_RED_PIN.on()
        LED_GREEN_PIN.off()
        print("LED Rojo ON")
        client.publish(mqtt_topic, "Red LED ON")  # Publicar mensaje para el LED rojo
        time.sleep(3)

        LED_RED_PIN.off()
        LED_GREEN_PIN.on()
        print("LED Verde ON")
        client.publish(mqtt_topic, "Green LED ON")  # Publicar mensaje para el LED verde
        time.sleep(3)

    except Exception as e:
        print("Error al controlar los LEDs:", e)

# Main
connect_wifi()
client = connect_mqtt()
if client:
    # Iniciamos el loop de control de LEDs
    while True:
        try:
            if client:
                client.check_msg()  # Revisar si hay mensajes MQTT

            control_leds(client)  # Controlar los LEDs y enviar los estados
        except Exception as e:
            print("Error en el loop principal:", e)
