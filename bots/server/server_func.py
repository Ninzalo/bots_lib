import asyncio
import pickle
from bots.bot.struct import Message_struct
from bots.bot.converters import dataclass_to_dict


async def send_to_server(message: Message_struct, local_ip: str, local_port: int):
    _, writer = await asyncio.open_connection(local_ip, local_port)

    message_dict = dataclass_to_dict(message)
    data = pickle.dumps(message_dict)
    writer.write(data)
    await writer.drain()
    writer.write_eof()
    writer.close()
