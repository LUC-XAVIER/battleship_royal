import time
#import struct
import socket
import threading
from datetime import datetime
from colorama import Fore, Style

class Logger:
    def __init__(self):
        pass
    
    def __log(self,
       severity,
       *values: object,
       sep = '',
       end = '\n',
       file = None,
       flush: bool = ...,
       ) -> None: 
        print(f"[{datetime.now()} {severity}] ", *values, sep=sep, end=end, file=file, flush=flush)
        
    def info(self, *values: object,
        sep = '',
        end = '\n',
        file = None,
        flush: bool = ...,):
        self.__log(Fore.LIGHTGREEN_EX + 'INFO' + Style.RESET_ALL, *values, sep=sep, end=end, file=file, flush=flush)
        
    def warn(self, *values: object,
        sep = '',
        end = '\n',
        file = None,
        flush: bool = ...,):
        self.__log(Fore.YELLOW + 'WARN'+ Style.RESET_ALL, *values, sep=sep, end=end, file=file, flush=flush)
        
    def error(self, *values: object,
        sep = '',
        end = '\n',
        file = None,
        flush: bool = ...,):
        self.__log(Fore.LIGHTRED_EX + 'ERROR' + Style.RESET_ALL, *values, sep=sep, end=end, file=file, flush=flush)
        
log = Logger()

class Server:
    def __init__(self, host="127.0.0.1", port=1234):
        self.host = host
        self.port = port
        
        self.kill = False
        self.thread_count = 0
        
        self.players = []
        
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
                    print('new connection: ', conn, addr)
                    if len(self.players) < 2:
                        self.players.append(conn)
                        #spawn listener task
                except socket.timeout:
                    continue
                time.sleep(0.01)
        self.thread_count -= 1
        log.info("Listening thread stopped")
        
        
    def await_kill(self):
        self.kill = True
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
            log.info("server stopped!")
            
            
            
if __name__ == "__main__":            
    Server().run()