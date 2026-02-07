import time
import pickle
import socket
import threading
from logging import Logger
from shared import *

log = Logger()


class Server:
    def __init__(self, host="127.0.0.1", port=1234):
        self.host = host
        self.port = port

        self.kill = False
        self.thread_count = 0

        self.players = []
        self.rooms = []

    def connection_listener_loop(self):
        self.thread_count += 1
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
            s.bind((self.host, self.port))

            log.warn("this server waiting for connection ", self.thread_count)

            while not self.kill:
                s.settimeout(1)
                s.listen()
                try:
                    conn, addr = s.accept()
                    conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
                    conn.settimeout(1)

                    # Keep the player connection and address
                    new_player = Player(conn, addr, "", "blue")
                    self.players.append(new_player)

                    log.info('new connection: ', conn, addr)
                    # spawn listener task
                    thread = threading.Thread(target=self.listen, args=(new_player,))
                    thread.start()

                except socket.timeout:
                    continue
                time.sleep(0.01)
        self.thread_count -= 1
        log.info("Listening thread stopped")

    def listen(self, player: Player):
        log.debug(f'Listener started for connection {player}. Awaiting client message...')
        # While the connection is open
        while True:
            try:
                data = receive(player.sock)

                if data.type == 'PLAYER_INFO':
                    log.debug("data received: ", data)
                    player.name = data.name
                    send(player.sock, player.to_data())

            except socket.timeout:
                continue
            except BlockingIOError:
                continue
            except KeyboardInterrupt:
                break
            except ConnectionResetError:
                log.error("Connection closed by client: ", player)
                break
        player.sock.close()

    def await_kill(self):
        self.kill = True
        for player in self.players:
            player.sock.close()
        while self.thread_count:
            time.sleep(0.01)
        log.info("all threads killed")

    def run(self):
        connection_listener_thread = threading.Thread(target=self.connection_listener_loop)
        connection_listener_thread.start()
        log.info("the connection listener is running on thread: ", connection_listener_thread.name)
        try:
            log.info("Server started...")
            while True:
                time.sleep(0.05)
        except KeyboardInterrupt:
            self.await_kill()
            log.error("server stopped!")


if __name__ == "__main__":
    Server().run()
