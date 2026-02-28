# W-Chat

A real-time multi-room chat application built with Flask and Socket.IO.

## Features
- Create and join chat rooms with unique codes
- Real-time messaging via WebSockets
- Typing indicators
- Message history
- Active rooms list
- Room history per user
- Connection status display
- Member count tracking

## Tech Stack
- **Backend:** Python, Flask, Flask-SocketIO
- **Frontend:** HTML, CSS, JavaScript, Socket.IO
- **Real-time:** WebSockets

## Setup

1. Clone the repo
```bash
git clone https://github.com/0-Izrah/W-Chat.git
cd W-Chat
```

2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Run the server
```bash
python app.py
```

5. Open browser to `http://localhost:5000`

## Local Network Usage
Run the server and share the Network URL with others on the same WiFi to chat!