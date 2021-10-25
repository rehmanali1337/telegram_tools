from telethon import TelegramClient, errors, types
import traceback
import asyncio
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl import functions
from telethon.tl.functions.channels import JoinChannelRequest


class Client(TelegramClient):
    def __init__(self, *args, **kwargs):
        TelegramClient.__init__(self, *args, **kwargs)

    async def join_it(self, target_link: str):
        try:
            # Join public group
            updates = await self(JoinChannelRequest(target_link))
        except ValueError:
            # The group is private so join private
            group_hash = target_link.split('/')[-1]
            try:
                updates = await self(ImportChatInviteRequest(group_hash))
            except errors.rpcerrorlist.UserAlreadyParticipantError:
                pass
            except Exception as e:
                traceback.print_exc()

    async def delete_all_schedule_messages(self, target_group: types.Dialog):
        history = await self.client(functions.messages.GetScheduledHistoryRequest(
            target_group, 0))
        ids = []
        for message in history.messages:
            ids.append(message.id)
        await self.client(functions.messages.DeleteScheduledMessagesRequest(
            peer=target_group,
            id=ids
        ))
