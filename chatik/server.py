import socket
import threading

clients = []
clients_lock = threading.Lock()

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5001

def handle_client(client_socket, client_address):
    print(f'Подключился клиент: {client_address}')
    
    with clients_lock:
        clients.append(client_socket)
    
    welcome_message = "Добро пожаловать в чат!"
    client_socket.send(welcome_message.encode('utf-8'))
    
    with clients_lock:
        for client in clients:
            if client != client_socket:
                try:
                    msg = f"Новый участник присоединился к чату: {client_address}"
                    client.send(msg.encode('utf-8'))
                except:
                    pass
    
    try:
        while True:
            data = client_socket.recv(1024)
            
            if not data:
                break
            
            message = data.decode('utf-8')
            with clients_lock:
                for client in clients:
                    if client != client_socket:
                        try:
                            client.send(data)
                        except:
                            pass
            
            print(f'[{client_address}] {message}')
            
    except Exception as e:
        print(f'Ошибка с клиентом {client_address}: {e}')
    finally:
        with clients_lock:
            if client_socket in clients:
                clients.remove(client_socket)
        
        with clients_lock:
            for client in clients:
                try:
                    msg = f"Клиент {client_address} покинул чат"
                    client.send(msg.encode('utf-8'))
                except:
                    pass
        
        client_socket.close()
        print(f'Клиент {client_address} отключился')

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen()
    
    print(f'Сервер запущен на {SERVER_HOST}:{SERVER_PORT}')
    print('Сервер ждет подключений...')
    
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            
            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print('\nСервер останавливается...')
    finally:
        with clients_lock:
            for client in clients:
                client.close()
        server_socket.close()

if __name__ == '__main__':
    start_server()
