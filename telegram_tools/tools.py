from telethon import TelegramClient, errors, types
import traceback
import asyncio
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl import functions
from telethon.tl.functions.channels import JoinChannelRequest
import os
import pickle


class Client(TelegramClient):
    def __init__(self, *args, **kwargs):
        TelegramClient.__init__(self, *args, **kwargs)
        _dir = "do_not_delete"
        os.makedirs(_dir, exist_ok=True)
        self._joins_list_file = f"{_dir}/{self.session.filename.split('/')[-1]}_joinslist"

    def _dump_to_file(self, file, obj: object):
        with open(file, "wb") as f:
            pickle.dump(obj, f)

    def _read_from_file(self, file) -> object:
        with open(file, "rb") as f:
            return pickle.load(f)

    def _have_joined_already(self, join_link: str) -> bool:
        if not os.path.exists(self._joins_list_file):
            return False
        joins_list = self._read_from_file(self._joins_list_file)
        return join_link in joins_list

    def _add_to_joinslist(self, join_link: str):
        joins_list = [join_link]
        if os.path.exists(self._joins_list_file):
            joins_list.extend(self._read_from_file(self._joins_list_file))
        self._dump_to_file(self._joins_list_file, joins_list)

    async def join_it(self, target_link: str, ignore_cache=False):
        if not ignore_cache:
            if self._have_joined_already(target_link):
                print(f"User have already joined {target_link}")
                self._add_to_joinslist(target_link)
                return await self.get_entity(target_link)
        try:
            # Join public group
            updates = await self(JoinChannelRequest(target_link))
        except (TypeError, ValueError):
            # The group is private so join private
            group_hash = target_link.split('/')[-1]
            try:
                updates = await self(ImportChatInviteRequest(group_hash))
            except errors.rpcerrorlist.UserAlreadyParticipantError:
                self._add_to_joinslist(target_link)
                return await self.get_entity(target_link)
        if isinstance(updates, list):
            updates = updates[0]
        self._add_to_joinslist(target_link)
        return updates

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
