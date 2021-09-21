import httpx
import asyncio

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import MessageSegment

from .data_source import data, number, Item


_col = on_command("col", priority=5)
result = []


async def price_get(item: Item):
    url = f"https://www.ceve-market.org/api/market/region/10000002/type/{item.typeID}.json"
    headers = {'X-Auth': 'from-client'}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        resp = response.json()
        if resp['sell']['min'] != 0:
            item.sell = resp['sell']['min']
            item.buy = resp['buy']['max']
            result.append(item)


@_col.handle()
async def handle_jita(bot: Bot, event: Event, state: T_State):
    args = str(event.get_message()).strip()
    if not args:
        await _col.finish(
                "未输入关键词！",
                at_sender=True
                )
    try:
        key = data.find_abbreviation(args)["物品名称"]
        items = data.find_items(key)[0:20]
    except:
        try:
            items = data.find_items(args)[0:20]
        except:
            items = data.find_items(args)
    if not items:
        await _col.finish(
                "物品不存在！",
                at_sender=True
                )

    task_list = []

    for i in items:
        request = price_get(i)
        task = asyncio.create_task(request)
        task_list.append(task)
        await asyncio.gather(*task_list)

    global result
    result.sort(key=lambda x:int(x.typeID))

    message = [f"{i.name}\n出售价格：{number(i.sell)}isk" for i in result]

    price = sum([i.sell for i in result])


    result = []

    await _col.finish(
            f"\n{args}:\n\n" + "\n===============\n".join(message) + f"\n\n以上物品合计：{number(price)}",
            at_sender=True
            )



