import asyncio
import concurrent.futures
import datetime
import os
import sys
from hashlib import sha1
from random import random
from urllib.parse import urlparse

import redis
import socketio
import uvicorn
from fastapi import FastAPI
from firebase_admin import credentials, db, initialize_app
from rich.console import Console

ping_freq, ping_wait = 25, 60
player_limit = 2


console = Console()
app = FastAPI()
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins="*",
    ping_interval=ping_freq,
    ping_timeout=ping_wait
    # async_handlers=True
)

socket_app = socketio.ASGIApp(sio)
app.mount("/", socket_app)

console.print(f"ARGS PASSED: {sys.argv}", style="dark_orange3")

if sys.argv[1] == "local":
    r = redis.Redis(host="localhost", port=6379, db=0)
else:
    url = urlparse(os.environ.get("REDIS_URL"))
    r = redis.Redis(
        host=url.hostname,
        port=url.port,
        username=url.username,
        password=url.password,
        ssl=True,
        ssl_cert_reqs=None,
    )

room_id = sha1((str(random()) + str(random())).encode("utf8")).hexdigest()
r.set("n_player", 0)
r.set("room_id", room_id)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)

cred = credentials.Certificate(os.environ["FIREBASE_AUTH"])
initialize_app(cred, {"databaseURL": os.environ["FIREBASE_URL"]})
ref = db.reference("/")


def save_data(sid, message):
    message["socket_id"] = sid
    ref.child(sid).push().set(str(message))


@sio.on("start_wait")
async def wait_handler(sid, message):
    console.print(message, sid, style="bold blue")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)
    room_id = r.get("room_id").decode()
    console.print(
        "Player joining wait. current player count is", int(r.get("n_player")), style="bold blue"
    )
    r.set(sid, room_id)
    sio.enter_room(sid, room_id)
    await sio.emit("wait_data", {"rm_id": room_id, "p_id": int(r.get("n_player"))}, room=sid)
    r.incrby("n_player", 1)
    r.lpush(room_id, sid)
    if int(r.get("n_player")) == player_limit:
        players_list = r.lrange(room_id, 0, -1)
        r.set("room_id", sha1((str(random()) + str(random())).encode("utf8")).hexdigest())
        console.print(
            "Starting game. player count in waiting room is.",
            int(r.get("n_player")),
            room_id,
            style="bold blue",
        )
        r.set("n_player", 0)
        await sio.emit(
            "start_game", {"players_list": players_list, "rm_id": room_id}, room=room_id
        )


@sio.on("game_info")
async def game_info_handler(sid, message):
    console.print(message, sid, style="bold blue")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)


@sio.on("start_game")
async def start_game_handler(sid, message):
    console.print(message, sid, style="bold blue")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)


@sio.on("end_game")
async def end_game_handler(sid, message):
    console.print(message, sid, style="bold blue")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)


@sio.on("feedback")
async def end_game_handler(sid, message):
    console.print(message, sid, style="bold blue")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)


@sio.on("player_move")
async def player_movement_handler(sid, message):
    console.print(message, sid, style="bold blue")
    await sio.emit("player_move_success", message, room=message["rm_id"])


@sio.on("player_move_displayed")
async def player_movement_displayed_handler(sid, message):
    console.print(message, sid, style="bold blue")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)


@sio.on("rescue_attempt")
async def rescue_attempt_handler(sid, message):
    console.print(message, sid, style="bold blue")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)


@sio.on("rescue")
async def rescue_handler(sid, message):
    console.print(message, sid, style="bold blue")
    await sio.emit("rescue_success", message, room=message["rm_id"])


@sio.on("rescue_displayed")
async def rescue_displayed_handler(sid, message):
    console.print(message, sid, style="bold blue")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)


@sio.on("connect")
async def connect_handler(sid, environ):
    console.print("CONNECTED", sid, style="bold magenta")
    await sio.emit("welcome", {"data": "Connected", "socket_id": sid}, room=sid)
    loop = asyncio.get_event_loop()
    loop.run_in_executor(
        executor, save_data, sid, {"event": "connect", "time": str(datetime.datetime.utcnow())}
    )


@sio.on("game_config")
async def game_config_handler(sid, message):
    console.print("GAME CONFIG", sid, style="bold red")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)


@sio.on("disconnect")
async def disconnect_handler(sid):
    console.print("DISCONNECTED", sid, style="bold red")
    loop = asyncio.get_event_loop()
    room_id = r.get(sid).decode()
    sio.leave_room(sid, room_id)
    loop.run_in_executor(
        executor, save_data, sid, {"event": "disconnect", "time": str(datetime.datetime.utcnow())}
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
