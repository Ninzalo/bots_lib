import asyncio
from aiogram import types, executor, Dispatcher
from bots.bot.struct import Message_struct
from bots.bot.converters import str_to_dict
from bots.server.server_func import send_to_server


class Tg_client:
    def __init__(
        self, dispatcher: Dispatcher, local_ip: str, local_port: int
    ) -> None:
        self._dp = dispatcher
        self._local_ip = local_ip
        self._local_port = local_port
        self._dp.callback_query_handler()(self.callback_message_handler)
        self._dp.message_handler()(self.message_handler)
        self._started = False

    async def callback_message_handler(
        self,
        query: types.CallbackQuery,
    ) -> None:
        message_struct = Message_struct(
            user_id=query.from_user.id,
            messenger="tg",
            payload=str_to_dict(string=query.data),
        )
        await send_to_server(
            message=message_struct,
            local_ip=self._local_ip,
            local_port=self._local_port,
        )

    async def message_handler(self, message: types.Message) -> None:
        message_struct = Message_struct(
            user_id=message.from_id, messenger="tg", text=message.text
        )
        await send_to_server(
            message=message_struct,
            local_ip=self._local_ip,
            local_port=self._local_port,
        )

    async def test_messages_rate(self):
        self._started = True
        for num in range(30):
            message_struct = Message_struct(
                user_id=432672691, messenger="tg", text=f"{num}"
            )
            await send_to_server(
                message=message_struct,
                local_ip=self._local_ip,
                local_port=self._local_port,
            )

    def start_tg_client(self) -> None:
        if self._started:
            print(f"[ERROR] Ensure not to run test")
            return
        print(f"TG listening started")
        executor.start_polling(self._dp, skip_updates=True)

    def run_test(self) -> None:
        asyncio.run(self.test_messages_rate())


def start_tg_client(
    dispatcher: Dispatcher, handler_ip: str, handler_port: int
) -> None:
    tg_client = _get_tg_client(
        dispatcher=dispatcher, local_ip=handler_ip, local_port=handler_port
    )
    tg_client.start_tg_client()


def run_test(
    dispatcher: Dispatcher, handler_ip: str, handler_port: int
) -> None:
    tg_client = _get_tg_client(
        dispatcher=dispatcher, local_ip=handler_ip, local_port=handler_port
    )
    tg_client.run_test()


def _get_tg_client(
    dispatcher: Dispatcher, handler_ip: str, handler_port: int
) -> Tg_client:
    return Tg_client(
        dispatcher=dispatcher, local_ip=handler_ip, local_port=handler_port
    )
