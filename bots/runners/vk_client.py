import json
from vkbottle import GroupEventType
from vkbottle.bot import Message, MessageEvent, Bot
from bots.bot.struct import Message_struct
from bots.server.server_func import send_to_server


class Vk_client:
    def __init__(self, handler: Bot, local_ip: str, local_port: int) -> None:
        self._bot = handler
        self._local_ip = local_ip
        self._local_port = local_port
        self._bot.on.raw_event(
            GroupEventType.MESSAGE_EVENT, dataclass=MessageEvent
        )(self.handle_callback_event)
        self._bot.on.message()(self.handle_message_event)

    async def handle_callback_event(self, event: MessageEvent):
        user_id = int(event.object.user_id)
        payload = event.object.payload
        message = Message_struct(
            user_id=user_id, messenger="vk", payload=payload
        )
        await send_to_server(
            message=message,
            local_ip=self._local_ip,
            local_port=self._local_port,
        )

    async def handle_message_event(self, event: Message):
        if event.payload:
            payload = json.loads(event.payload)
        else:
            payload = None
        message = Message_struct(
            user_id=int(event.from_id),
            messenger="vk",
            text=event.text,
            payload=payload,
        )
        await send_to_server(
            message=message,
            local_ip=self._local_ip,
            local_port=self._local_port,
        )

    def start_vk_bot(self):
        print(f"VK listening started")
        self._bot.run_forever()


def start_vk_client(handler: Bot, handler_ip: str, handler_port: int):
    vk_client = Vk_client(
        handler=handler, local_ip=handler_ip, local_port=handler_port
    )
    vk_client.start_vk_bot()
