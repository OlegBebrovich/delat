import time
import json
import pytz
import random
import asyncio
from flask import Flask
from colorama import Fore
from threading import Thread
from datetime import datetime
from utilities import send_logs
from aminofix import asyncfix, exceptions

app = Flask(__name__)

acs_done = 0
unsuccess = 0
total = 0


@app.route('/', methods=['GET'])
def fuck():
    return 'farm_system'


def generate_tz():
    localhour = time.strftime("%H", time.gmtime())
    localminute = time.strftime("%M", time.gmtime())
    UTC = {"GMT0": '+0', "GMT1": '+60', "GMT2": '+120', "GMT3": '+180', "GMT4": '+240', "GMT5": '+300', "GMT6": '+360',
           "GMT7": '+420', "GMT8": '+480', "GMT9": '+540', "GMT10": '+600', "GMT11": '+660', "GMT12": '+720',
           "GMT13": '+780', "GMT-1": '-60', "GMT-2": '-120', "GMT-3": '-180', "GMT-4": '-240', "GMT-5": '-300',
           "GMT-6": '-360', "GMT-7": '-420', "GMT-8": '-480', "GMT-9": '-540', "GMT-10": '-600', "GMT-11": '-660'};
    hour = [localhour, localminute]
    if hour[0] == "00": tz = UTC["GMT-1"];return int(tz)
    if hour[0] == "01": tz = UTC["GMT-2"];return int(tz)
    if hour[0] == "02": tz = UTC["GMT-3"];return int(tz)
    if hour[0] == "03": tz = UTC["GMT-4"];return int(tz)
    if hour[0] == "04": tz = UTC["GMT-5"];return int(tz)
    if hour[0] == "05": tz = UTC["GMT-6"];return int(tz)
    if hour[0] == "06": tz = UTC["GMT-7"];return int(tz)
    if hour[0] == "07": tz = UTC["GMT-8"];return int(tz)
    if hour[0] == "08": tz = UTC["GMT-9"];return int(tz)
    if hour[0] == "09": tz = UTC["GMT-10"];return int(tz)
    if hour[0] == "10": tz = UTC["GMT13"];return int(tz)
    if hour[0] == "11": tz = UTC["GMT12"];return int(tz)
    if hour[0] == "12": tz = UTC["GMT11"];return int(tz)
    if hour[0] == "13": tz = UTC["GMT10"];return int(tz)
    if hour[0] == "14": tz = UTC["GMT9"];return int(tz)
    if hour[0] == "15": tz = UTC["GMT8"];return int(tz)
    if hour[0] == "16": tz = UTC["GMT7"];return int(tz)
    if hour[0] == "17": tz = UTC["GMT6"];return int(tz)
    if hour[0] == "18": tz = UTC["GMT5"];return int(tz)
    if hour[0] == "19": tz = UTC["GMT4"];return int(tz)
    if hour[0] == "20": tz = UTC["GMT3"];return int(tz)
    if hour[0] == "21": tz = UTC["GMT2"];return int(tz)
    if hour[0] == "22": tz = UTC["GMT1"];return int(tz)
    if hour[0] == "23": tz = UTC["GMT0"];return int(tz)


def generate_timers():
    return [{'start': int(time.time()), 'end': int(time.time()) + 300} for _ in range(50)]


async def main():
    global total
    global acs_done
    global unsuccess
    comId = 257845344
    objectId = "00c43d42-e4c0-4e38-9889-eebfd5d7fff9"
    try:
        accounts = open('accounts.txt').read().split('\n')
        random.shuffle(accounts)
    except FileNotFoundError:
        await send_logs(
            f'СОЗДАЙТЕ ФАЙЛ С  АККАУНТАМИ  С ИМЕНЕМ "accounts.txt".')
        return
    while True:
        try:
            this_account = accounts[0]
            accounts.remove(this_account)
            accounts.append(this_account)
            email, password, device_id = this_account.split()
            client = asyncfix.Client(deviceId=device_id)
            await asyncio.gather(client.login(email, password))
            # await asyncio.gather(send_logs(
            #     f'ЗАЛОГИНИЛИ {email.upper()}.'))
            f_t = time.time()
            await asyncio.gather(client.join_community(comId=comId))
            sub_client = asyncfix.SubClient(comId=comId, profile=client.profile)
            try:
                await asyncio.gather(*[asyncio.create_task(sub_client.send_active_obj(timers=generate_timers(), tz=generate_tz())) for t in range(24)])
                # await asyncio.gather(send_logs(f'ОТПРАВЛЕН ACTIVE-OBJ - [24 ИЗ 24]. || {email.upper()}'))
            except exceptions.AccountLimitReached or exceptions.TooManyRequests:
                pass
            coins = (await client.get_wallet_info()).totalCoins
            if coins > 500:
                await asyncio.gather(*[sub_client.send_coins(coins=500, blogId=objectId) for _ in range(coins // 500)])
            if coins:
                await asyncio.gather(sub_client.send_coins(coins=coins % 500, blogId=objectId))
            # await asyncio.gather(send_logs(
            #     f'ОТПРАВЛЕНО {coins} МОНЕТ. || {email.upper()}'))
            s_t = time.time()
            acs_done += 1
            if coins == 0:
                unsuccess += 1
            total += coins
            txt = {
                "done": acs_done,
                "time": round(s_t-f_t, 2),
                "total": total,
                "unsuccess": unsuccess,
                "last": datetime.now(pytz.timezone('Europe/Moscow')).strftime("<u>%d/%m/%Y</u> <b>-|-</b> <u>%H:%M:%S</u>")
            }
            with open("stats.json", "w") as stats:
                json.dump(txt, stats, indent=4)
        except exceptions.AccountLimitReached or exceptions.TooManyRequests:
            await asyncio.gather(send_logs(f'СЛИШКОМ МНОГО ЗАПРОСОВ {email.upper()}.'))
            unsuccess += 1
            acs_done += 1
            continue
        except exceptions.AccountDisabled:
            await asyncio.gather(send_logs(f'ЗАБАНИЛИ АКК {email.upper()}.'))
            unsuccess += 1
            acs_done += 1
            continue
        except exceptions.CommunityLimit:
            await asyncio.gather(send_logs(f'СЛИШКОМ МНОГО СОО {email.upper()}.'))
            unsuccess += 1
            acs_done += 1
            for elem in (await client.sub_clients()).comId:
                try:
                    await asyncio.gather(client.leave_community(elem))
                except:
                    pass
        except exceptions.ActionNotAllowed:
            await asyncio.gather(send_logs(f'ЗАБАНИЛИ АКК {email.upper()}.'))
            unsuccess += 1
            acs_done += 1
            continue
        except exceptions.IpTemporaryBan:
            await asyncio.gather(send_logs(f'ЗАБАНИЛИ ПО АЙПИ.'))
            acs_done += 1
            unsuccess += 1
            await asyncio.sleep(360)
            continue
        except Exception as e:
            acs_done += 1
            unsuccess += 1
            print(e)
            
def start():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())


if __name__ == '__main__':
    Thread(target=app.run).start()
    Thread(target=start).start()
