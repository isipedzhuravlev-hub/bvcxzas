import socket
import threading

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5001

class ChatClient:
    def __init__(self):
        self.client_socket = None
        self.running = True
        
    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((SERVER_HOST, SERVER_PORT))
            print(f'Подключено к серверу {SERVER_HOST}:{SERVER_PORT}')
            return True
        except ConnectionRefusedError:
            print('Ошибка: не удалось подключиться к серверу. Убедитесь, что сервер запущен.')
            return False
        except Exception as e:
            print(f'Ошибка подключения: {e}')
            return False
    
    def receive_messages(self):
        while self.running:
            try:
                data = self.client_socket.recv(1024)
                if not data:
                    print('\nСоединение с сервером разорвано')
                    self.running = False
                    break
                
                message = data.decode('utf-8')
                print(f'\n{message}\n> ', end='')
            except ConnectionResetError:
                print('\nСоединение с сервером разорвано')
                self.running = False
                break
            except Exception as e:
                if self.running:
                    print(f'Ошибка получения сообщения: {e}')
                break
    
    def send_messages(self):
        while self.running:
            try:
                message = input('> ')
                if message.lower() in ['exit', 'quit', 'выход', 'вых']:
                    self.running = False
                    break
                
                if message:
                    self.client_socket.send(message.encode('utf-8'))
            except Exception as e:
                if self.running:
                    print(f'Ошибка отправки сообщения: {e}')
                break
    
    def start(self):
        if not self.connect():
            return
        
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()
        
        self.send_messages()
        
        receive_thread.join(timeout=1)
        
        if self.client_socket:
            self.client_socket.close()
        print('Клиент остановлен')
    
    def stop(self):
        self.running = False

def main():
    client = ChatClient()
    
    try:
        client.start()
    except KeyboardInterrupt:
        print('\nОтключаемся...')
    finally:
        client.stop()

if __name__ == '__main__':
    main()
