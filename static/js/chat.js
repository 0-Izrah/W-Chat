var socketio = io();

    const messages = document.getElementById("messages")
    const statusIndicator = document.getElementById("connection-status");

    socketio.on("connect", () => {
        statusIndicator.innerHTML = "🟢 Connected";
        statusIndicator.style.color = "lightgreen";
    });

    socketio.on("disconnect", () => {
        statusIndicator.innerHTML = "🔴 Disconnected - Reconnecting...";
        statusIndicator.style.color = "red";
    });

    socketio.on("connect_error", () => {
        statusIndicator.innerHTML = "⚠️ Connection error - Retrying...";
        statusIndicator.style.color = "orange";
    });

    const createMessage = (name, msg, currentUser) => {
        const isMyMessage = name === currentUser;
        const messageClass = isMyMessage ? "text my-message" : "text other-message";
        const content = `
        <div class="${messageClass}">
            <span class="muted">
                ${new Date().toLocaleString([], { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })}
            </span>
            <span>
                <strong>${name}</strong>: ${msg}
            </span>
        </div>
        `
        messages.innerHTML += content;
        messages.scrollTop = messages.scrollHeight;
    }

    socketio.on("message" , (data) =>{
        if(data.members){
            document.getElementById("member-count").innerHTML = 
            `${data.members} member${data.members !==1 ? "s" : ""} in the room.` ;
        }else if(data.typing){
            const typingIndicator = document.getElementById("typing-indicator");
            typingIndicator.innerHTML = `${data.typing} is typing...`;
            clearTimeout(window.typingTimeout);
            window.typingTimeout = setTimeout(() => {
                typingIndicator.innerHTML = "";
            }, 2000);
        }else if(data.name && data.message){
            createMessage(data.name , data.message , currentUsername)
        }
    })

    const sendMessage = () => {
        const message = document.getElementById("message")
        if ( message.value.trim() == "") return;
        if (!socketio.connected) {
            alert("Not connected to server. Please wait...");
            return;
        }
        socketio.emit("message", {data : message.value.trim()})
        message.value = "";
    }

    document.getElementById("message").addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
            sendMessage();
        }
    })

    let lastTypingTime = 0;
    document.getElementById("message").addEventListener("input", () => {
        const now = Date.now();
        if (now - lastTypingTime > 1000) {
            socketio.emit("typing");
            lastTypingTime = now;
        }
    })

    const leaveRoom = () => {
        socketio.disconnect();
        window.location.href = "/";
    }
