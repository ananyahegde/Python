let ws;
let myUsername = "";
let currentRoom = "";
let currentDMUser = "";
let typingClearTimers = {};
let lastTypingSent = 0;
let myRooms = [];
let myDMs = [];

function connect() {
    const input = document.getElementById("username-input");
    const username = input.value.trim();
    if (!username) return;
    myUsername = username;

    ws = new WebSocket("ws://localhost:8765");

    ws.onopen = () => {
        ws.send(JSON.stringify({ type: "register", username }));
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleMessage(data);
    };

    ws.onclose = () => {
        appendSystem("[ DISCONNECTED FROM SERVER ]");
    };

    ws.onerror = () => {
        appendSystem("[ CONNECTION ERROR — IS SERVER RUNNING? ]");
    };
}

function handleMessage(data) {
    switch (data.type) {
        case "registered":
            document.getElementById("login-screen").style.display = "none";
            document.getElementById("app").style.display = "flex";
            appendSystem(`[ CONNECTED AS ${data.username} ]`);
            searchRooms("");
            break;

        case "user_history":
            myRooms = data.rooms || [];
            myDMs = data.dms || [];
            renderSidebar();
            break;

        case "search_results":
            renderSearchResults(data.rooms);
            break;

        case "room_joined":
            currentDMUser = "";
            currentRoom = data.room;
            document.getElementById("room-title").textContent = data.room;
            document.getElementById("member-count").textContent = `${data.member_count} online`;
            document.getElementById("messages").innerHTML = "";
            data.history.forEach(m => appendMessage(m.sender, m.text, m.timestamp));
            appendSystem(`[ JOINED ${data.room} ]`);
            if (!myRooms.includes(data.room)) {
                myRooms.push(data.room);
            }
            renderSidebar();
            break;

        case "chat_message":
            if (currentRoom === data.room) {
                appendMessage(data.username, data.text, data.timestamp);
            }
            break;

        case "typing":
            if (currentRoom === data.room) {
                showTyping(data.username);
            }
            break;

        case "dm":
            const other = data.from === myUsername ? data.to : data.from;
            if (!myDMs.includes(other)) {
                myDMs.push(other);
                renderSidebar();
            }
            if (currentDMUser === other || (data.from === myUsername && currentDMUser === data.to)) {
                appendDM(data.from, data.to, data.text, data.timestamp);
            } else {
                appendSystem(`[ DM from ${data.from} — click their name to view ]`);
            }
            break;

        case "dm_history":
            document.getElementById("messages").innerHTML = "";
            document.getElementById("room-title").textContent = `[ DM ] ${data.with}`;
            document.getElementById("member-count").textContent = "";
            data.history.forEach(m => appendDM(m.sender, m.recipient, m.text, m.timestamp));
            break;

        case "user_joined":
            if (currentRoom === data.room) {
                appendSystem(`[ ${data.username} joined ${data.room} ]`);
            }
            break;

        case "user_left":
            if (currentRoom === data.room) {
                appendSystem(`[ ${data.username} left ${data.room} ]`);
            }
            break;

        case "presence_update":
            renderOnlineList(data.members);
            const count = data.members.filter(m => m.status === "online").length;
            document.getElementById("member-count").textContent = currentRoom ? `${count} online` : "";
            break;

        case "error":
            appendSystem(`[ ERROR: ${data.message} ]`);
            break;
    }
}

function renderSidebar() {
    const roomEl = document.getElementById("my-rooms");
    roomEl.innerHTML = "";
    myRooms.forEach(r => {
        const div = document.createElement("div");
        div.textContent = r;
        if (r === currentRoom) div.classList.add("active");
        div.onclick = () => joinRoom(r);
        roomEl.appendChild(div);
    });

    const dmEl = document.getElementById("my-dms");
    dmEl.innerHTML = "";
    myDMs.forEach(u => {
        const div = document.createElement("div");
        div.textContent = u;
        if (u === currentDMUser) div.classList.add("active");
        div.onclick = () => openDMWith(u);
        dmEl.appendChild(div);
    });
}

function joinRoom(name) {
    ws.send(JSON.stringify({ type: "join_room", room: name }));
}

function searchRooms(query) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "search_rooms", query }));
    }
}

function renderSearchResults(rooms) {
    const el = document.getElementById("search-results");
    el.innerHTML = "";
    const query = document.getElementById("search-input").value.trim();

    rooms.forEach(r => {
        const div = document.createElement("div");
        div.textContent = r.name;
        if (r.name === currentRoom) div.classList.add("active");
        div.onclick = () => {
            joinRoom(r.name);
            document.getElementById("search-input").value = "";
            el.innerHTML = "";
        };
        el.appendChild(div);
    });

    if (query) {
        const normalized = query.startsWith("#") ? query : "#" + query;
        const exists = rooms.find(r => r.name === normalized);
        if (!exists) {
            const div = document.createElement("div");
            div.textContent = `+ create ${normalized}`;
            div.style.color = "#555";
            div.onclick = () => {
                joinRoom(query);
                document.getElementById("search-input").value = "";
                el.innerHTML = "";
            };
            el.appendChild(div);
        }
    }
}

function renderOnlineList(members) {
    const el = document.getElementById("online-list");
    el.innerHTML = "";
    members.forEach(m => {
        const div = document.createElement("div");
        const dot = `<span class="status-dot status-${m.status}"></span>`;
        div.innerHTML = `${dot}${m.username}`;
        el.appendChild(div);
    });
}

function sendMessage() {
    const input = document.getElementById("msg-input");
    const text = input.value.trim();
    if (!text) return;

    if (currentDMUser) {
        ws.send(JSON.stringify({ type: "dm", to: currentDMUser, text }));
        input.value = "";
        return;
    }

    if (!currentRoom) {
        appendSystem("[ JOIN A ROOM FIRST ]");
        return;
    }

    ws.send(JSON.stringify({ type: "chat_message", room: currentRoom, text }));
    input.value = "";
}

function handleKey(e) {
    if (e.key === "Enter") sendMessage();
}

function sendTyping() {
    const now = Date.now();
    if (now - lastTypingSent > 2000 && currentRoom && !currentDMUser) {
        ws.send(JSON.stringify({ type: "typing", room: currentRoom }));
        lastTypingSent = now;
    }
}

function showTyping(username) {
    const el = document.getElementById("typing-indicator");
    el.textContent = `${username} is typing...`;
    clearTimeout(typingClearTimers[username]);
    typingClearTimers[username] = setTimeout(() => {
        el.textContent = "";
    }, 3000);
}

function openDM() {
    document.getElementById("dm-modal").style.display = "flex";
    document.getElementById("overlay").style.display = "block";
    document.getElementById("dm-to").value = "";
    document.getElementById("dm-text").value = "";
}

function openDMWith(username) {
    currentDMUser = username;
    currentRoom = "";
    document.getElementById("messages").innerHTML = "";
    document.getElementById("typing-indicator").textContent = "";
    renderSidebar();
    ws.send(JSON.stringify({ type: "dm_history", with: username }));
}

function closeDM() {
    document.getElementById("dm-modal").style.display = "none";
    document.getElementById("overlay").style.display = "none";
}

function sendDM() {
    const to = document.getElementById("dm-to").value.trim();
    const text = document.getElementById("dm-text").value.trim();
    if (!to || !text) {
        appendSystem("[ DM ERROR: FILL IN BOTH FIELDS ]");
        closeDM();
        return;
    }
    if (to === myUsername) {
        appendSystem("[ ERROR: CANNOT DM YOURSELF ]");
        closeDM();
        return;
    }
    ws.send(JSON.stringify({ type: "dm", to, text }));
    if (!myDMs.includes(to)) {
        myDMs.push(to);
        renderSidebar();
    }
    currentDMUser = to;
    currentRoom = "";
    document.getElementById("messages").innerHTML = "";
    document.getElementById("room-title").textContent = `[ DM ] ${to}`;
    document.getElementById("member-count").textContent = "";
    ws.send(JSON.stringify({ type: "dm_history", with: to }));
    closeDM();
}

function appendMessage(sender, text, timestamp) {
    const el = document.getElementById("messages");
    const div = document.createElement("div");
    div.className = "msg";
    div.innerHTML = `<span class="ts">[${timestamp}]</span><span class="sender">${sender}:</span>${escapeHtml(text)}`;
    el.appendChild(div);
    el.scrollTop = el.scrollHeight;
}

function appendDM(from, to, text, timestamp) {
    const el = document.getElementById("messages");
    const div = document.createElement("div");
    div.className = "msg dm-msg";
    div.innerHTML = `<span class="ts">[${timestamp}]</span><span class="sender">${from}:</span>${escapeHtml(text)}`;
    el.appendChild(div);
    el.scrollTop = el.scrollHeight;
}

function appendSystem(text) {
    const el = document.getElementById("messages");
    const div = document.createElement("div");
    div.className = "msg system-msg";
    div.textContent = text;
    el.appendChild(div);
    el.scrollTop = el.scrollHeight;
}

function escapeHtml(text) {
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}
