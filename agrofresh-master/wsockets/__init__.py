import asyncio
import json
from  django.core.serializers.json import DjangoJSONEncoder

connected_clients = set()

async def broadcast(message):
    if connected_clients:  # asyncio.wait doesn't accept an empty list
        message = {
            'type': 'websocket.send',
            'text': json.dumps(message, cls=DjangoJSONEncoder, allow_nan=False)
        }
        # TODO handle errors
        await asyncio.wait([client_send(message) for client_send in connected_clients])


async def websocket_application(scope, receive, send):
    while True:
        event = await receive()
        if event['type'] == 'websocket.disconnect':
            connected_clients.remove(send)
            break

        if event['type'] == 'websocket.connect':
            await send({'type': 'websocket.accept'})
            connected_clients.add(send)
            continue

        if event['type'] != 'websocket.receive':
            # TODO websocket writes instead of REST API?
            continue

        if event['text'] == 'ping':
            await send({
                'type': 'websocket.send',
                'text': 'pong!'
            })
            continue
