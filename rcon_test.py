#!/usr/bin/env python

# pip install mcipc
# https://github.com/coNQP/mcipc

# in the server.properties:
# enable-rcon=true
# rcon.port=25575
# rcon.password=12345

from mcipc.rcon import Client

HOST_NAME: str = "localhost"
PORT: int = 25575
PASSWORD: str = "12345"


def main() -> None:
    with Client(HOST_NAME, PORT) as c:
        c.login(PASSWORD)
        c.say("Hello from the RCON!")


if __name__ == "__main__":
    main()
