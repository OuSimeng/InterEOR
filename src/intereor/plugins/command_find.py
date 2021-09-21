from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

from .data_source import data

_find = on_command('find', priority=5)

@_find.handle()
async def handle_find(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if not args:
        await _find.finish('未输入物品名称！')
    result = data.find_items(args)
    msg = f"[{args}]的查询结果：\n\n" + "\n".join([i.name for i in result])
    await _find.finish(msg)
