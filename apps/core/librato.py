# This is kind of like StatsD, https://github.com/etsy/statsd
# Sends UDP-packets to our custom librato-collector, https://github.com/etsy/statsd
# Should perhaps be moved outside of Sherpa as a custom dependency

import socket
import json

IP = "127.0.0.1"
PORT = 38519
socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def increment(name):
    message = json.dumps({
        'name': name
    })
    send(message)

def send(message):
    socket.sendto(message, (IP, PORT))
