import asyncio
import websockets
import json
import uuid
import datetime
from database import (
        init_db, 
        get_or_create_user, 
        get_or_create_room, 
        search_rooms, 
        save_message, 
        get_room_history, 
        get_dm_history, 
        get_user_rooms, 
        get_user_dms
    )

connected_users = {}
rooms = {}

async def broadcast_to_room(room_name, message, exclude_session=None):
    if room_name not in rooms:
        return
    dead = set()
    for sid in list(rooms[room_name]):
        if sid == exclude_session:
            continue
        user = connected_users.get(sid)
        if user:
            try:
                await user["websocket"].send(json.dumps(message))
            except:
                dead.add(sid)
    for sid in dead:
        rooms[room_name].discard(sid)

async def send_to_user(username, message):
    for sid, user in connected_users.items():
        if user["username"] == username:
            try:
                await user["websocket"].send(json.dumps(message))
                return True
            except:
                return False
    return False

async def broadcast_presence(room_name):
    if room_name not in rooms:
        return
    members = []
    for sid in rooms[room_name]:
        user = connected_users.get(sid)
        if user:
            members.append({"username": user["username"], "status": user["status"]})
    await broadcast_to_room(room_name, {"type": "presence_update", "members": members})

async def handler(websocket):
    session_id = str(uuid.uuid4())[:6]
    current_room = None
    username = None

    try:
        async for raw in websocket:
            data = json.loads(raw)
            msg_type = data.get("type")

            if msg_type == "register":
                username = data["username"]
                await get_or_create_user(username)
                connected_users[session_id] = {
                    "username": username,
                    "websocket": websocket,
                    "status": "online",
                    "room": None
                }

                print(f"[INFO] User \"{username}\" connected (session: {session_id})")
                await websocket.send(json.dumps({
                    "type": "registered",
                    "username": username,
                    "session_id": session_id
                }))

                user_rooms = await get_user_rooms(username)
                user_dms = await get_user_dms(username)
                await websocket.send(json.dumps({
                    "type": "user_history",
                    "rooms": user_rooms,
                    "dms": user_dms
                }))

            elif msg_type == "search_rooms":
                query = data.get("query", "")
                results = await search_rooms(query)
                await websocket.send(json.dumps({"type": "search_results", "rooms": results}))

            elif msg_type == "join_room":
                room_name = data["room"]
                if not room_name.startswith("#"):
                    room_name = "#" + room_name

                if current_room and current_room in rooms:
                    rooms[current_room].discard(session_id)
                    await broadcast_to_room(current_room, {
                        "type": "user_left",
                        "username": username,
                        "room": current_room
                    })
                    await broadcast_presence(current_room)

                current_room = room_name
                connected_users[session_id]["room"] = room_name
                await get_or_create_room(room_name, username)

                if room_name not in rooms:
                    rooms[room_name] = set()
                rooms[room_name].add(session_id)

                history = await get_room_history(room_name)
                await websocket.send(json.dumps({
                    "type": "room_joined",
                    "room": room_name,
                    "history": history,
                    "member_count": len(rooms[room_name])
                }))

                await broadcast_to_room(room_name, {
                    "type": "user_joined",
                    "username": username,
                    "room": room_name
                }, exclude_session=session_id)

                await broadcast_presence(room_name)
                print(f"[INFO] {username} joined room {room_name}")

            elif msg_type == "chat_message":
                if not current_room:
                    await websocket.send(json.dumps({"type": "error", "message": "Join a room first."}))
                    continue
                text = data["text"]

                ts = datetime.datetime.now().strftime("%H:%M:%S")
                await save_message(sender=username, text=text, room=current_room)
                await broadcast_to_room(current_room, {
                    "type": "chat_message",
                    "username": username,
                    "text": text,
                    "room": current_room,
                    "timestamp": ts
                })

            elif msg_type == "typing":
                if current_room:
                    await broadcast_to_room(current_room, {
                        "type": "typing",
                        "username": username,
                        "room": current_room
                    }, exclude_session=session_id)

            elif msg_type == "dm":
                to = data["to"]
                text = data["text"]
                import datetime
                ts = datetime.datetime.now().strftime("%H:%M:%S")

                # check if user exists
                target_exists = any(u["username"] == to for u in connected_users.values())
                if not target_exists:
                    # check db
                    from database import user_exists
                    if not await user_exists(to):
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": f"User '{to}' does not exist."
                        }))
                        continue

                await save_message(sender=username, text=text, recipient=to)
                payload = {
                    "type": "dm",
                    "from": username,
                    "to": to,
                    "text": text,
                    "timestamp": ts
                }
                await send_to_user(to, payload)
                await websocket.send(json.dumps(payload))

            elif msg_type == "dm_history":
                other = data["with"]
                history = await get_dm_history(username, other)
                await websocket.send(json.dumps({"type": "dm_history", "with": other, "history": history}))

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if session_id in connected_users:
            del connected_users[session_id]
        if current_room and current_room in rooms:
            rooms[current_room].discard(session_id)
            await broadcast_to_room(current_room, {
                "type": "user_left",
                "username": username,
                "room": current_room
            })
            await broadcast_presence(current_room)
        if username:
            print(f"[INFO] User \"{username}\" disconnected")

async def main():
    await init_db()
    print("=== Server Log ===")
    print("[INFO] Chat server started on ws://0.0.0.0:8765")
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
