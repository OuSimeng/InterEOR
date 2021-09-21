import sqlite3
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "items.db")


class Item:

    def __init__(self, data: list):
        self.typeID = data[0]
        self.name = data[1]
        self.description = data[2]
        self.c1 = data[3]
        self.c2 = data[4]
        self.c3 = data[5]
        self.c4 = data[6]
        self.c5 = data[7]
        self.c6 = data[8]
        self.sell = None
        self.buy = None


class Data:
    def __init__(self):
        self.c = sqlite3.connect(db_path).cursor()

    def find_items(self, key: str):
        sql = f"select * from items where 物品名称 like '%{'%'.join(list(key))}%'"
        cursor = self.c.execute(sql)
        result = []
        for i in cursor:
            s = []
            for j in i:
                s.append(j)
            result.append(Item(s))
        if result:
            return result
        else:
            return None
    
    def find_abbreviation(self, key:str):
        sql = f"select * from abbreviation where 常用名 like '%{'%'.join(list(key))}%'"
        cursor = self.c.execute(sql)
        result = []
        for i in cursor:
            result.append({
                "物品名称": i[0],
                "常用名": i[1]
                })
        if result:
            return result[0]
        else:
            return None

data = Data()

def number(num) -> str:
    """
    数字处理
    :param num: 数字
    :return: str
    """
    num = int(num)
    if num < 10000:
        return str(num)
    elif 10000 <= num < 100000000:
        return "%.2f" % (num / 10000) + "万"
    elif 100000000 <= num:
        return "%.2f" % (num / 100000000) + "亿"


class Character:

    def __init__(self, name: str):
        self.name = name
        self.birthday = ""
        self.alliance = ""
        self.corporation = ""
        self.security_status = ""
