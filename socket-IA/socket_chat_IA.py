import socket
import sys
import requests
import time
from decouple import Config, RepositoryEnv

# Cargar la configuración desde el archivo .env en la carpeta Env
config = Config(RepositoryEnv('C:/SeveBrains/Socket-chat/Env/.env'))


def get_messages():
    # Cargar la URL desde la variable de entorno
    url = config('API-WAI_URL')

    try:
        response = requests.get(url)

        if response.status_code == 200:
            messages_data = response.json()  # Asumiendo que la respuesta es JSON
            #print("Mensajes recibidos de la API:", messages_data)  # Imprime los mensajes en la consola
            return messages_data  # Retorna los datos para procesarlos

        else:
            print(f"Error {response.status_code}: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error en la petición: {e}")
        return None


def process_messages(messages):
    processed_data = []  # Lista para almacenar los mensajes procesados

    if messages:
        for item in messages:
            waid = item['waid']
            mensajes = item['mensajes']

            for mensaje in mensajes:
                textomensaje = mensaje['textomensaje']

                # Crear un nuevo diccionario con los datos requeridos
                message_dict = {
                    "telefono": waid,
                    "mensaje": textomensaje
                }

                processed_data.append(message_dict)  # Añadir a la lista

    return processed_data  # Retornar la lista de mensajes procesados


# Crear un socket TCP/IP
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Configurar el socket para reutilizar la dirección
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Asignar el socket a una dirección y puerto
server_address = ('localhost', 10001)
print(f'Iniciando en {server_address[0]} puerto {server_address[1]}')
sock.bind(server_address)

# Escuchar por conexiones entrantes
sock.listen(1)


def server_loop():
    while True:
        print("Realizando petición a la API...")
        messages = get_messages()
        processed_messages = process_messages(messages)  # Procesar los mensajes
        print("Mensajes procesados:", processed_messages)  # Imprimir los mensajes procesados

        # Esperar unos segundos antes de hacer otra petición
        time.sleep(10)  # Peticiones cada 10 segundos


if __name__ == '__main__':
    # Iniciar el ciclo de peticiones en paralelo
    import threading

    api_thread = threading.Thread(target=server_loop)
    api_thread.start()

    while True:
        # Esperar por una conexión
        print('Esperando una conexión...')
        connection, client_address = sock.accept()

        try:
            print('Conexión desde', client_address)

            # Recibir los datos del cliente (si es necesario)
            while True:
                data = connection.recv(16)
                if data:
                    print(f'Datos recibidos del cliente: {data}')
                    break
                else:
                    print(f'No hay datos desde el cliente {client_address}')
                    break

        finally:
            # Limpiar la conexión
            connection.close()