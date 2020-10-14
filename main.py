import os
import socketio
import uvicorn
import redis
import asyncio
import concurrent.futures
from random import random
from hashlib import sha1
from fastapi import FastAPI
from rich.console import Console
from firebase_admin import db, credentials, initialize_app


ping_freq, ping_wait = 25, 60
player_limit = 1


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

# r = redis.StrictRedis(host="localhost", db=0, decode_responses=True)
r = redis.from_url(os.environ.get("REDIS_URL"))
room_id = sha1((str(random()) + str(random())).encode("utf8")).hexdigest()
r.set("n_player", 0)
r.set("room_id", room_id)

executor = concurrent.futures.ThreadPoolExecutor(max_workers=20)

cred = credentials.Certificate(
    os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"))
initialize_app(cred, {"databaseURL": os.environ.get("FIREBASE_URL")})
ref = db.reference("/")


def save_data(sid, message):
    ref.child(sid).push().set(str(message))


@sio.on("start_wait")
async def wait_handler(sid, message):
    console.print(message, sid, style="bold blue")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)
    n_player = int(r.get("n_player"))
    room_id = r.get("room_id")
    console.print(
        "Player joining wait. current player count is",
        n_player, style="bold blue"
    )
    if n_player < player_limit:
        await sio.emit("wait_data",
                       {"rm_id": room_id, "p_id": n_player}, room=sid)
        r.incrby("n_player", 1)
        if n_player + 1 == player_limit:
            room_id = sha1((str(random()) +
                            str(random())).encode("utf8")).hexdigest()
            r.set("room_id", room_id)
            console.print(
                "Starting game. player count in waiting room is.",
                n_player + 1,
                style="bold blue",
            )
            await sio.emit("start_game", {"msg_code": 1}, room=sid)
            r.set("n_player", 0)


@sio.on("start_game")
async def start_game_handler(sid, message):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)


@sio.on("end_game")
async def end_game_handler(sid, message):
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)


@sio.on("player_move")
async def player_movement_handler(sid, message):
    console.print(message, sid, style="bold blue")
    await sio.emit("player_move", message, room=sid)
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)


@sio.on("rescue_attempt")
async def rescue_attempt_handler(sid, message):
    console.print(message, sid, style="bold blue")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)


@sio.on("rescue_success")
async def rescue_success_handler(sid, message):
    console.print(message, sid, style="bold blue")
    loop = asyncio.get_event_loop()
    loop.run_in_executor(executor, save_data, sid, message)


@sio.on("connect")
async def connect_handler(sid, environ):
    console.print("CONNECTED", sid, style="bold magenta")
    await sio.emit("welcome", {"data": "Connected"}, room=sid)


@sio.on("disconnect")
async def disconnect_handler(sid):
    console.print("DISCONNECTED", sid, style="bold red")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
