import paramiko
import threading
import datetime
import socket
import signal
import requests
import json
import sys
from discord_webhook import DiscordWebhook, DiscordEmbed

WEBHOOK_URL = "URL"

def log_credentials(username, password, ip):

    #get geolocation of the client IP
    request_url = 'https://geolocation-db.com/jsonp/' + ip
    response = requests.get(request_url)
    result = response.content.decode()
    result = result.split("(")[1].strip(")")
    result  = json.loads(result)
    #print(result)

    timestamp = datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')
    with open('credentials.log', 'a') as f:
        f.write(f'Timestamp: {timestamp}\n')
        f.write(f'Username: {username}\n')
        f.write(f'Password: {password}\n')
        f.write(f'IP: {ip}\n')
        f.write(f'Geolocation: {result}\n')
        f.write('\n')

    # Send credentials and IP to Discord webhook
    webhook = DiscordWebhook(url=WEBHOOK_URL)
    embed = DiscordEmbed(title="SSH Honeypot | New SSH login attempt:", description=f"**Timestamp:** {timestamp}\n**Username:** {username}\n**Password:** {password}\n**IP:** {ip}\n**Password:** {password}\n**Geolocation:** {result['country_name']}")
    embed.set_footer(text="Coded by Mickhat#1337")
    webhook.add_embed(embed)
    webhook.execute()

class FakeSSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        client_ip = self.event.client_address[0] if self.event.client_address else "Unknown IP"
        log_credentials(username, password, client_ip)
        print(f"Login attempt - Username: {username}, Password: {password}, IP: {client_ip}")
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

def signal_handler(sig, frame):
    print("KeyboardInterrupt: Closing SSH server...")
    server_socket.close()
    sys.exit(0)

def start_honeypot():
    # Create a socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to a specific IP address and port
    server_socket.bind(('0.0.0.0', 2222))

    # Listen for incoming connections
    server_socket.listen(5)
    print("Honeypot started. Listening for connections...")

    signal.signal(signal.SIGINT, signal_handler)

    try:
        while True:
            # Accept a client connection
            client_socket, address = server_socket.accept()
            print(f"Incoming connection from: {address[0]}:{address[1]}")

            # Start a new thread to handle the connection
            transport = paramiko.Transport(client_socket)
            transport.add_server_key(paramiko.RSAKey(filename='key'))
            transport.local_version = "SSH-2.0-OpenSSH_7.2p2 Ubuntu-4ubuntu2.10"

            server = FakeSSHServer()
            server.event.client_address = address

            try:
                transport.start_server(server=server)
            except (paramiko.SSHException, EOFError) as e:
                print(f"SSH negotiation failed: {str(e)}")
                continue

            channel = transport.accept()
            if channel is not None:
                channel.close()

            # Close the transport and client socket
            transport.close()
            client_socket.close()
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

#start
start_honeypot()
