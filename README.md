## CARelay

**__THIS IS ONLY A CONCEPT PROJECT! PLEASE DO NOT TRANSFER SENSITIVE INFORMATION THROUGH THIS PROGRAM!__**

**CARelay** is a Tor‑hidden, end‑to‑end encrypted, terminal‑style chat.

- Tor v3 onion service transport
- NaCl "box" crypto (Curve25519 + XSalsa20‑Poly1305)
- Fixed 512‑byte frames to hide message length
- ZERO logs on disk
- Works on Linux, macOS, WSL, and native Windows
- PufferPanel template for one‑click host install (Not using Docker, feel free to clone this and push a version that does)

---

## Quick host setup (PufferPanel)

1. Import `CArelay_template.json` in the PufferPanel web UI.  
2. Create a server from that template (no public port needed if using Tor only).  
3. Start the server – the installer will auto‑clone this repo, install dependencies, and run the relay on localhost:7331.  
4. Check `/var/lib/tor/carelay/hostname` for your `.onion` address.

---

## Client usage (Linux / macOS / WSL)

```bash
pip install -r requirements.txt
export CARELAY_ADDR="your.onion.address"
python3 car_client.py

Built by Collin Aguiar
https://github.com/CollinAguiar