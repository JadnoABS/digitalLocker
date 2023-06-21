# try:
#   import usocket as socket
# except:
import socket
from machine import Pin, PWM
import network
import esp
import gc


class ESPServer:
    def __init__(self):
        esp.osdebug(None)
        gc.collect()
        self.station = network.WLAN(network.STA_IF)
        self.station.active(True)
        self.locker_state = "OFF"
    def connect(self, ssid, password):
        self.station.connect(ssid, password)
        while self.station.isconnected() == False:
          pass
        print('Connection successful')
        print(self.station.ifconfig())
    def web_page(self):
        html = """<html><head> <title>Digital Locker</title> <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="icon" href="data:,"> <style>html{font-family: Helvetica; display:inline-block; margin: 0px auto; text-align: center;}
        h1{color: #0F3376; padding: 2vh;}p{font-size: 1.5rem;}.button{display: inline-block; background-color: #e7bd3b; border: none; 
        border-radius: 4px; color: white; padding: 16px 40px; text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}
        .button2{background-color: #4286f4;}</style></head><body> <h1>Digital Locker</h1> 
        <p>Locker state: <strong>""" + self.locker_state  + """</strong></p><p><a href="/?locker=on"><button class="button">ON</button></a></p>
        <p><a href="/?locker=off"><button class="button button2">OFF</button></a></p></body></html>"""
        return html
    def start(self):
        # Inicialização do pino de saida para o servo motor
        p25 = Pin(25, Pin.OUT)
        motor = PWM(p25, freq=50)
        motor.duty(40)
        locker_state = "OFF"
        # Inicialização do socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', 3000))
        s.listen(2)
        while True:
            conn, addr = s.accept()
            print('Got a connection from %s' % str(addr))
            request = conn.recv(1024)
            request = str(request)
            print('Content = %s' % request)
            locker_on = request.find('/?locker=on')
            locker_off = request.find('/?locker=off')
            if locker_on == 6:
                print('LOCKER ON')
                motor.duty(110)
                self.locker_state = "ON"
            if locker_off == 6:
                print('LOCKER OFF')
                motor.duty(40)
                self.locker_state = "OFF"
            response = self.web_page()
            conn.send('HTTP/1.1 200 OK\n')
            conn.send('Content-Type: text/html\n')
            conn.send('Connection: close\n\n')
            conn.sendall(response)
            conn.close()


server = ESPServer()
server.connect("REDE", "SENHA")
server.start()
