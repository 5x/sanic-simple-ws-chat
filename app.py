import os

from sanic import Sanic
from sanic import response
from websockets.exceptions import ConnectionClosed


class Room:
    def __init__(self):
        self.clients = []

    def join(self, client):
        self.clients.append(client)

    def leave(self, client):
        try:
            self.clients.remove(client)
        except ValueError:
            pass  # already removed

    async def send_message(self, message):
        for receiver in self.clients:
            try:
                await receiver.send(message)
            except ConnectionClosed:
                self.leave(receiver)

    def __len__(self):
        return len(self.clients)


app = Sanic(__name__)
global_room = Room()


@app.listener('before_server_start')
async def before_server_start(app, loop):
    app.chat_room = Room()


@app.route("/")
async def test(request):
        return await response.file('./static/index.html')


@app.websocket('/chat')
async def feed(request, ws):
    app.chat_room.join(ws)
    while True:
        try:
            message = await ws.recv()
        except ConnectionClosed:
            app.chat_room.leave(ws)
            break
        else:
            await app.chat_room.send_message(message)


app.static('/', './static')


if __name__ == "__main__":
    port=int(os.environ.get('PORT', 8000))
    app.run(host="0.0.0.0", port=port)
