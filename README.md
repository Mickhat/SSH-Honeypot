# Python SSH Honeypot

This is a simple SSH Honeypot script written in Python. It uses the `paramiko` library to create a fake SSH server that logs attempted logins.

When a client tries to connect to the server and sends a username and password, the server logs these credentials and sends them to a Discord channel using a webhook.

## Dependencies

This script depends on the following Python libraries:

- `paramiko`
- `threading`
- `datetime`
- `socket`
- `signal`
- `sys`
- `discord_webhook`

You can install these libraries using pip:

```bash
pip install paramiko discord_webhook
```

## Usage

Before running the script, make sure to replace the WEBHOOK_URL value with your Discord webhook URL.

You also need to have a SSH private key file named 'key' in the same directory. You can generate it using ssh-keygen:

```bash
ssh-keygen -t rsa -f key
```

Then you can run the script with Python:
```bash
python ssh_honeypot.py
```
The server will start and listen for incoming connections on port 2222.

## Output
The script will log any login attempts, along with the username, password, and client IP, to a file named credentials.log. It will also send this information to your Discord channel via the webhook.

If you stop the script (for example, by pressing Ctrl+C), it will close the server and exit.

## Warning
Please be aware that running a SSH Honeypot could attract unwanted attention to your network. Be sure to follow all relevant laws and regulations, and use this responsibly.
