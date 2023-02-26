import asyncio
from datetime import datetime
import pickle
from bots.bot.converters import dataclass_from_dict
from bots.bot.returns.message import Return
from bots.bot.struct import Message_struct
from bots.bot.throttlers import ThrottledResource
from bots.bot.reply.reply_division import Messengers_division
from bots.bot.transitions.transitions import Transitions
from bots.message_handler.message_handler import Message_handler


class Server:
    def __init__(
        self,
        messengers: Messengers_division,
        message_reply_rate: int | float,
        transitions: Transitions,
        message_handler: Message_handler,
    ) -> None:
        self._messengers = messengers
        self._message_reply_rate = message_reply_rate
        self._transitions = transitions
        self._message_handler = message_handler
        self._check_errors()

    def _check_errors(self) -> None:
        if not self._messengers._compiled:
            raise RuntimeError(f"Messengers aren't compiled")
        if not self._transitions._compiled:
            raise RuntimeError(f"Transitions aren't compiled")

    async def handle_echo(
        self,
        reader: asyncio.streams.StreamReader,
        writer: asyncio.streams.StreamWriter,
        throttler: ThrottledResource,
    ) -> None:
        tasks = []
        while True:
            data = await reader.read()
            if not data:
                break
            message = pickle.loads(data)
            message_cls = dataclass_from_dict(
                struct=Message_struct, dictionary=message
            )
            # return_cls = Returns()
            # await return_cls.add_return(
            #     user_id=message_cls.user_id,
            #     user_messenger=message_cls.messenger,
            #     text=f"Answer to '{message_cls.text}'",
            # )
            return_cls = await self._message_handler.get(
                message_class=message_cls
            )
            for answer in return_cls.returns:
                task = asyncio.create_task(throttler.query(answer))
                tasks.append(task)
        addr = writer.get_extra_info("peername")
        print(f"Received {message_cls!r} from {addr!r}")
        await asyncio.gather(*tasks)
        writer.close()

    async def replier(self, return_cls: Return):
        await self._messengers.get_func(
            messenger=return_cls.user_messenger, return_cls=return_cls
        )
        request = (
            f"{'='*10}"
            f"\nTime: {datetime.now()}\nUser_id: {return_cls.user_id}"
            f"\nMessage: {return_cls}"
            f"\n{'='*10}"
        )
        print(request)

    async def main(self, local_ip: str, local_port: int) -> None:
        _throttler = ThrottledResource(
            delay=1.0 / self._message_reply_rate, func_to_throttle=self.replier
        )
        _throttler.start()
        server = await asyncio.start_server(
            lambda reader, writer: self.handle_echo(
                reader=reader, writer=writer, throttler=_throttler
            ),
            local_ip,
            local_port,
        )

        addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
        print(f"Serving on {addrs}")

        async with server:
            await server.serve_forever()

    def start_server(self, local_ip: str, local_port: int) -> None:
        asyncio.run(self.main(local_ip=local_ip, local_port=local_port))


def run_server(
    messengers: Messengers_division,
    message_reply_rate: int | float,
    transitions: Transitions,
    message_handler: Message_handler,
    local_ip: str,
    local_port: int,
) -> None:
    server = Server(
        messengers=messengers,
        message_reply_rate=message_reply_rate,
        transitions=transitions,
        message_handler=message_handler
    )
    server.start_server(local_ip=local_ip, local_port=local_port)
