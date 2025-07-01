#!/usr/bin/env python3
import nacl.public, base64
sk = nacl.public.PrivateKey.generate()
print("Private:", base64.b64encode(sk.encode()).decode())
print("Public :", base64.b64encode(sk.public_key.encode()).decode())
