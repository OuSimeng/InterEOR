from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import MessageSegment

from .data_source import Character


import httpx
import asyncio
import requests
import base64
from io import BytesIO


_char = on_command("char", priority=5)

ID = None


async def get_player_info(character_id, player_name):
    global result, ID
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/84.0.4147.125 Safari/537.36"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://esi.evepc.163.com/latest/characters/{character_id}/?datasource=serenity",headers=headers)
        response = response.json()
        if response["name"] == player_name:
            result = response
            ID = character_id


@_char.handle()
async def handle_char(bot: Bot, event: Event, state: T_State):
    global result, ID
    args = str(event.get_message()).strip()
    if args:
        character = Character(args)
    else:
        await _pic.finish(
                "未输入角色名！",
                at_sender=True
                )

    async with httpx.AsyncClient() as client:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/84.0.4147.125 Safari/537.36"}
        response = await client.get("https://esi.evepc.163.com/latest/search/?categories=character&datasource=serenity&language=en&search=" + f"{character.name + '  '}&strict=true",headers=headers)
        response = response.json()
        if response:
            player_ids = response["character"]
        else:
            await _char.finish(
                    "查无此人！",
                    at_sender=True
                    )
    task_list = []
    for i in player_ids:
        request = get_player_info(i, character.name)
        task = asyncio.create_task(request)
        task_list.append(task)
    await asyncio.gather(*task_list)

    async with httpx.AsyncClient() as client:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/84.0.4147.125 Safari/537.36"}
        response = await client.get(f"https://esi.evepc.163.com/latest/corporations/{result['corporation_id']}/?datasource=serenity",headers=headers)
        character.corporation = response.json()["name"]
        try:

            response = await client.get(f"https://esi.evepc.163.com/latest/alliances/{result['alliance_id']}/?datasource=serenity",headers=headers)
            character.alliance = response.json()["name"]
        except:
            character.alliance = "无"

    character.name = result["name"]
    character.birthday = result["birthday"]
    character.security_status = f"{round(result['security_status'], 2)}"

    response = requests.get(f"https://image.evepc.163.com/Character/{ID}_512.jpg")
    ls_f=base64.b64encode(BytesIO(response.content).read())
    imgdata=base64.b64decode(ls_f)

    message = MessageSegment.image(imgdata)+ "\n角色："+character.name + "\n创号："+character.birthday[0:10]+"\n军团："+character.corporation+"\n联盟："+character.alliance+"\n安等："+str(character.security_status)

    result = None
    ID = None

    await _char.finish(
            message,
            at_sender=True
            )
