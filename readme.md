
---





# <img src="https://user-images.githubusercontent.com/25181517/187070862-03888f18-2e63-4332-95fb-3ba4f2708e59.png" alt="websocket icon" width="5%" /> WebSocket Agent for IoT Applications

## Introduction
This project implements a **WebSocket agent** that enables secure and efficient communication between IoT devices and external servers. It addresses the challenges posed by limited device capabilities by allowing seamless data exchange without the overhead of traditional SSL/TLS connections.

## Features
- **Bidirectional Communication**: Facilitates real-time data exchange between IoT devices and servers.
- **Flexible Security Options**: Support for both SSL and non-SSL configurations to accommodate various use cases.
- **Easy Integration**: Designed for straightforward integration with existing IoT applications.

## Prerequisites
Before you begin, ensure that you have the following installed on your system:
- **Python**: Version 3.6 or newer.
- **pip**: Python package installer.

## Setup Instructions

### 1. Create a Virtual Environment
To create an isolated Python environment for this project, follow these steps:

1. **Install `virtualenv`** if you haven't already:
   ```bash
   pip install virtualenv
   ```

2. **Create a new virtual environment**:
   ```bash
   virtualenv venv
   ```

3. **Activate the virtual environment**:
   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - On **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```

### 2. Install Required Libraries
Once the virtual environment is activated, install the required libraries by running:
```bash
pip install websockets logging
```

### 3. Create the Configuration File
Create a configuration file named `config.conf` in the same directory as `main.py`. Below is an example configuration:

```ini
[server]
use_ssl = false
ssl_cert = path/to/cert.pem
ssl_key = path/to/key.pem
server1_url = localhost:8765
server2_url = localhost:8766

[auth]
valid_token = key
```

*Note*: Ensure that the specified server addresses are valid, and that each server is on a different network to optimize connectivity and performance for your end devices and external services.

### 4. Run the WebSocket Agent
To run the WebSocket agent, execute the following command in the terminal:
```bash
python main.py
```

## Conclusion
This WebSocket agent is designed to enhance communication capabilities for IoT applications, allowing for flexible configurations and efficient data transfer, catering to the needs of various devices with limited capabilities.

---

