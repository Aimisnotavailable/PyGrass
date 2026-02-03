# PyGrass

A small experimental Python prototype demonstrating a networked grass simulation with separate **server** and **client** components. This repository is intended as a learning and prototyping project for simple multiplayer state synchronization and a minimal simulation of grass entities. Graphics and polish are intentionally minimal.

---

## Overview

**PyGrass** shows an authoritative-server style prototype where the server maintains simulation state and clients connect to receive updates and send simple input. The codebase separates networking, game logic, and entity simulation so you can iterate on rendering, networking, or game rules independently.

**Status**: experimental prototype — not production ready.

---

## Features

- **Authoritative server** that manages simulation state and client connections.  
- **Client examples** demonstrating basic connectivity and state handling.  
- **Modular design**: networking, game logic, and entity simulation are split into dedicated modules.  
- **Simple asset folder** for grass images to support basic rendering experiments.

---

## Requirements

- **Python 3.8+**  
- Standard library modules (sockets, threading, etc.) — no external packages required for the basic prototype.  
- Optional: **pygame** or another rendering library if you extend the client to show graphics.

---

## Quick Start

1. **Start the server** (run from the repository root):
```bash
python server.py
```

2. **Start a client** in another terminal or on another machine on the same network:
```bash
python client_grass.py
```

3. **Run a connectivity test**:
```bash
python client_test.py
```

**Notes**
- Edit host and port values in the client and server files if you need to bind to a specific interface or use a different port.
- Run server first, then start one or more clients.

---

## Configuration

- **Host and Port**: configurable in the top of `server.py` and client scripts. Adjust to match your network environment.  
- **Assets**: image assets are located under `data/images/grass`. Update paths in client code if you move assets.  
- **Logging**: sample logs may be present in `logs.txt`. Use or extend logging in the modules for debugging.

---

## Project Structure

```
PyGrass/
├─ server.py
├─ client_grass.py
├─ client_test.py
├─ server_grass.py
├─ grass.py
├─ gamehandler.py
├─ network_handler.py
├─ data/
│  └─ images/
│     └─ grass/
├─ scripts/
├─ logs.txt
```

- **server.py** — server entry point and main loop.  
- **client_grass.py** — example client with basic rendering hooks.  
- **client_test.py** — minimal client for connectivity testing.  
- **server_grass.py**, **grass.py** — simulation entities and rules.  
- **gamehandler.py** — game state management and update logic.  
- **network_handler.py** — socket handling and message parsing.  
- **data/images/grass** — image assets for client rendering.  
- **scripts/** — helper scripts and utilities.

---

## Development Notes

**Design choices**
- Clear separation between networking and game logic to make it easier to swap transport or rendering layers.  
- Prototype favors clarity and simplicity over performance and scalability.

**Suggested improvements**
- Add a `requirements.txt` and a minimal `setup` script.  
- Add a license file to clarify reuse terms.  
- Replace ad-hoc networking with a more robust protocol or use an existing library for serialization (e.g., `msgpack`, `protobuf`).  
- Improve rendering using `pygame`, `pyglet`, or a modern OpenGL wrapper.  
- Implement client-side prediction and interpolation for smoother visuals with higher latency.

**Caveats**
- Not hardened for untrusted networks. Use on local or trusted networks only.  
- No authentication or encryption implemented.

---

## Contributing

- Fork the repository, make changes on a branch, and open a pull request.  
- Good first contributions: add a `requirements.txt`, include a license, add a runnable demo with configurable host/port, or improve documentation and tests.  
- When contributing networking changes, include tests or a simple reproducible demo.

---

## License and Attribution

No license file is included in the repository. **Before reusing or redistributing code, add an appropriate license** (for example MIT, Apache 2.0) or contact the repository owner to confirm reuse terms.

---

## Contact

Refer to the repository owner on GitHub for questions, issues, or collaboration requests.
