from logging import Logger
from telethon import TelegramClient
from telethon.events import CallbackQuery, NewMessage

from .config import Config

from abc import ABC
from re import match


async def _get_users(client: TelegramClient, group_id: int, author_id: int) -> list[ABC]:
    members = []

    async for user in client.iter_participants(group_id):
        if not user.deleted:
            members.append(user)

    return list(filter(lambda member: member.id not in (client._self_id, author_id), members))


class TelegramBot:
    def __init__(self, logger: Logger, config: Config) -> None:
        self.logger = logger
        self.config = config

        self.client = TelegramClient(
            'bot', 
            self.config["tech"]["api_id"], 
            self.config["tech"]["api_hash"]
        )

    async def handlers(self) -> None:
        self.me = await self.client.get_me()

        @self.client.on(NewMessage(incoming=True, func=lambda c: c.is_private))
        async def empty_message(event) -> None:
            if not (match("^/help*", event.message.text) or match("^/start*", event.message.text)):
                await event.client.send_message(
                    event.chat_id,
                    "Для взаимодействия используйте команды /start и /help."
                )
                
        @self.client.on(NewMessage(pattern="^/all$", incoming=True, func=lambda c: c.is_group))
        @self.client.on(NewMessage(pattern=f"^/all@{self.me.username}", incoming=True, func=lambda c: c.is_group))
        async def all_tag(event: CallbackQuery) -> None:
            tag_text = str()
            users = await _get_users(self.client, event.chat_id, event.message.from_id.user_id)

            if len(users) > 199:
                return await event.reply(
                    "К сожалению я пока не могу упоминать всех участников группового чата, " +
                    "если их число превышает 200 человек. Следите за новостями, функционал бота постоянно расширяется!"
                )

            for user in users:
                tag_text += f"@{user.username} "

            await event.reply(tag_text)

        @self.client.on(NewMessage(pattern="^/start$", incoming=True))
        @self.client.on(NewMessage(pattern=f"^/start@{self.me.username}", incoming=True))
        async def start_command(event) -> None:
            await event.client.send_message(
                event.chat_id,
                """Привет, я позволяю реализовать функционал тега /all в групповых чатах Telegram. 
Добавь меня в группу и начни пользоваться всеми функциями.

Для инструкций используйте /help."""
            )
        
        @self.client.on(NewMessage(pattern="^/help$", incoming=True))
        @self.client.on(NewMessage(pattern=f"^/help@{self.me.username}", incoming=True))
        async def help_command(event) -> None:
            await event.client.send_message(
                event.chat_id,
                """Используйте команду `/all` чтобы упомянуть всех участников в любом групповом чате."""
            )

    async def run(self) -> None:
        self.logger.info("Bot starts his work.")
        await self.client.run_until_disconnected()
