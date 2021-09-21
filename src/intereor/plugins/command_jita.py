import httpx
import asyncio

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import MessageSegment

from .data_source import data, number, Item


_jita = on_command("jita", priority=5)
result = []


async def price_get(item: Item):
    url = f"https://www.ceve-market.org/api/market/region/10000002/type/{item.typeID}.json"
    headers = {'X-Auth': 'from-client'}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        resp = response.json()
        if resp['sell']['min'] != 0:
            item.sell = number(resp['sell']['min'])
            item.buy = number(resp['buy']['max'])
            result.append(item)


@_jita.handle()
async def handle_jita(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if not args:
        await _jita.finish(
                "未输入关键词！",
                at_sender=True
                )

    try:
        key = data.find_abbreviation(args)["物品名称"]
        items = data.find_items(key)[0:5]
    except:
        try:
            items = data.find_items(args)[0:5]
        except:
            items = data.find_items(args)

    if not items:
        await _jita.finish(
                "物品不存在！",
                at_sender=True
                )

    task_list = []

    for i in items:
        if "图" not in args and "图" in i.name:
            continue
        request = price_get(i)
        task = asyncio.create_task(request)
        task_list.append(task)
        await asyncio.gather(*task_list)

    global result
    result.sort(key=lambda x:int(x.typeID))

    message = [f"{i.name}\n出售价格：{i.sell}isk\n收购价格：{i.buy}isk" for i in result]

    result = []

    await _jita.finish(
            "\n" + "\n===============\n".join(message),
            at_sender=True
            )



