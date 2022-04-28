import json
import string
from contextlib import closing
import random
import socket
from typing import List

from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

from app.container_manager import MiniVContainerManager

app = FastAPI()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, endpoint_id: str, **kwargs):
        await websocket.accept()
        self.active_connections.append(websocket)
        MiniVContainerManager.get_instance().run_container(endpoint_id,
                                                           kwargs['external_port'],
                                                           kwargs['username'],
                                                           kwargs['password'],
                                                           kwargs['to_host'])

    def disconnect(self, websocket: WebSocket, endpoint_id: str):
        self.active_connections.remove(websocket)
        MiniVContainerManager.get_instance().stop_container(endpoint_id)

    async def send(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)


manager = ConnectionManager()


def get_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


@app.websocket("/cjrpc/{endpoint_id}")
async def websocket_endpoint(websocket: WebSocket, endpoint_id: str):
    host = '172.27.2.2'
    port = get_port()
    username = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    password = ''.join(random.choice(string.ascii_lowercase + string.digits + string.punctuation) for _ in range(23))
    await manager.connect(websocket, endpoint_id, external_port=port, username=username, password=password,
                          to_host=host)
    try:
        while True:
            result = json.dumps({
                'host': host,
                'ssh_username': username,
                'ssh_password': password,
                'external_port': port
            })
            await manager.send(result, websocket)
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, endpoint_id)
