#!/usr/bin/env python3
"""
CARelay - Tor-hidden, encrypted chat relay.
Runs on localhost:7331 and is intended to be exposed as a Tor v3 hidden service.
"""

import socket
import threading
import nacl.utils
import nacl.public
from datetime import datetime

PORT = 7331
MAX_FRAME = 512  # fixed frame length
clients = {}     # socket -> (alias, pubkey)
rooms = {}       # room -> set(socket)
lock = threading.Lock()

BANNER = r"""
████████████████████████████████████████
█ ▄▄▄▄▄ █▀▄▄▀█ ▄▄  █ ▄ ▄ ▀█ ▄▄▄▄▄ █
█ █   █ █ ▀▀ █ ▀▀█ █ █▀█ █ █   █ █
█ █▄▄▄█ █ ▀▀▄█ ▀▀  █ ▀ █ █ █▄▄▄█ █
█▄▄▄▄▄▄▄█▄█▄██▄██▄█▄█▄█▄█▄▄▄▄▄▄▄█
          C  A  R  e  l  a  y
────────────────────────────────────
"""

def utc_stamp() -> str:
    return datetime.utcnow().strftime("%H:%M:%S")

def send_frame(sock, text: str):
    sock.send(text.encode()[:MAX_FRAME].ljust(MAX_FRAME, b" "))

def broadcast(room: str, origin, payload: bytes):
    with lock:
        for s in list(rooms.get(room, [])):
            if s is origin:
                continue
            try:
                s.send(payload)
            except Exception:
                rooms[room].discard(s)

def handle_client(sock: socket.socket, addr):
    try:
        pk_raw = sock.recv(32)
        alias = sock.recv(32).decode().strip() or f"user{addr[1]}"
    except Exception:
        sock.close()
        return

    client_pk = nacl.public.PublicKey(pk_raw)

    with lock:
        clients[sock] = (alias, client_pk)
        rooms.setdefault("lobby", set()).add(sock)
    broadcast("lobby", None,
              f"[{utc_stamp()}] * {alias} joined lobby\n".encode().ljust(MAX_FRAME))

    current_room = "lobby"

    while True:
        try:
            data = sock.recv(MAX_FRAME)
            if not data:
                raise ConnectionError
            text = data.decode(errors="ignore").rstrip()

            # slash commands are sent in clear inside frame
            if text.startswith("/"):
                parts = text.split(maxsplit=1)
                cmd = parts[0].lower()

                if cmd == "/nick" and len(parts) == 2:
                    new_alias = parts[1][:16]
                    with lock:
                        old_alias = clients[sock][0]
                        clients[sock] = (new_alias, client_pk)
                    broadcast(current_room, None,
                              f"[{utc_stamp()}] * {old_alias} -> {new_alias}\n".encode().ljust(MAX_FRAME))
                elif cmd == "/join" and len(parts) == 2:
                    new_room = parts[1]
                    with lock:
                        rooms[current_room].discard(sock)
                        rooms.setdefault(new_room, set()).add(sock)
                    current_room = new_room
                    send_frame(sock, f"Joined {new_room}\n")
                elif cmd == "/rooms":
                    with lock:
                        listing = ", ".join(f"{r}({len(s)})" for r, s in rooms.items())
                    send_frame(sock, listing + "\n")
                elif cmd == "/quit":
                    raise ConnectionError
                else:
                    send_frame(sock, "Unknown command\n")
                continue

            # regular encrypted frame
            broadcast(current_room, sock, data)

        except Exception:
            break

    # cleanup
    with lock:
        rooms[current_room].discard(sock)
        alias, _ = clients.pop(sock, ("unknown", None))
    broadcast(current_room, None,
              f"[{utc_stamp()}] * {alias} left\n".encode().ljust(MAX_FRAME))
    sock.close()

def main():
    print(BANNER)
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind(("127.0.0.1", PORT))
    srv.listen()
    print(f"Relay listening on 127.0.0.1:{PORT}")
    while True:
        s, a = srv.accept()
        threading.Thread(target=handle_client, args=(s, a), daemon=True).start()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down.")
