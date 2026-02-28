from flask import Flask , render_template , request ,session, redirect,url_for
from flask_socketio import join_room , leave_room , send , SocketIO
import random
from string import ascii_uppercase
from datetime import datetime
import socket

app = Flask(__name__)
app.config["SECRET_KEY"] = "qwertydsuiop"
socketio = SocketIO(app)

rooms = {}
user_room_history = {}  

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        if code not in rooms:
            break

    return code
@app.route("/" , methods = ["POST" , "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join" , False)
        create = request.form.get("create" , False)
        rejoin = request.form.get("rejoin", False)
        
        if not name:
            return render_template("home.html" , error="Please enter a name" , code=code , name=name, active_rooms=get_active_rooms(), room_history=user_room_history.get(name, []))
        if join != False and not code:
            return render_template("home.html" , error="Please enter a room code.",code=code , name=name, active_rooms=get_active_rooms(), room_history=user_room_history.get(name, []))
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members":0 , "messages":[]}
        elif rejoin != False:
            if code not in rooms:
                return render_template("home.html", error="Room no longer exists.", code=code, name=name, active_rooms=get_active_rooms(), room_history=user_room_history.get(name, []))
            room = code
        elif code not in rooms:
            return render_template("home.html" , error="Room does not exist." , code=code , name=name, active_rooms=get_active_rooms(), room_history=user_room_history.get(name, []))
        
        session["room"] = room
        session["name"] = name
        
        # Track room history for user
        if name not in user_room_history:
            user_room_history[name] = []
        
        existing = next((r for r in user_room_history[name] if r["code"] == room), None)
        if existing:
            existing["last_active"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            user_room_history[name].append({
                "code": room,
                "joined_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "last_active": datetime.now().strftime("%Y-%m-%d %H:%M")
            })
        
        return redirect(url_for("room"))
        
    return render_template("home.html", active_rooms=get_active_rooms(), room_history=[])

def get_active_rooms():
    return [{"code": code, "members": data["members"]} for code, data in rooms.items() if data["members"] > 0]
@app.route("/chat-room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))
    
    return render_template("chat-room.html" , code = room , name = session.get("name") , messages = rooms[room]["messages"])
@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return
    
    msg_text = data.get("data", "").strip()
    if not msg_text or len(msg_text) > 500:
        return
    
    content = {"name":session.get("name") , "message":msg_text}
    send(content, to=room)
    rooms[room]["messages"].append(content)

@socketio.on("typing")
def typing():
    room = session.get("room")
    name = session.get("name")
    if room not in rooms:
        return
    send({"typing": name}, to=room, include_self=False)

@socketio.on("connect")
def connect(auth):
    name = session.get("name")
    room = session.get("room")
    
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    join_room(room)
    send({"name": name, "message": "has joined the room"} , to=room)
    rooms[room]["members"] += 1
    send({"members": rooms[room]["members"]} , to=room)
@socketio.on("disconnect")
def disconnect():
    name = session.get("name")
    room = session.get("room")
    if not room or not name:
        return
    if room in rooms:
        leave_room(room)
        rooms[room]["members"] -= 1

        if rooms[room]["members"] <= 0:
            del rooms[room]
        else:
            send({"name": name, "message": "has left the room"}, to=room)
            send({"members": rooms[room]["members"]}, to=room)
    
if __name__ == "__main__":
    import socket
    def get_wifi_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"
    
    local_ip = get_wifi_ip()
    print(f"\n{'='*40}")
    print(f"  Chat server running!")
    print(f"  Local:   http://localhost:5000")
    print(f"  Network: http://{local_ip}:5000")
    print(f"  Share the Network URL with others")
    print(f"  on the same WiFi to chat!")
    print(f"{'='*40}\n")
    socketio.run(app, host="0.0.0.0", port=5000, debug=False, allow_unsafe_werkzeug=True)