import datetime
from typing import Optional

from .charge import random_choice
from .util import get_word, parse_time_delta, get_img, get_config, get_group_data, write_group_data


# 判断晚安时间
async def judge_sle_time(early_time_tmp: str, late_time_tmp: str, now_time: datetime.datetime) -> bool:
    early_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + f' {early_time_tmp}:00:00', '%Y-%m-%d %H:%M:%S')
    late_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + f' {late_time_tmp}:00:00', '%Y-%m-%d %H:%M:%S')
    if early_time > now_time > late_time:
        return False
    return True


# 判断多次晚安
async def judge_have_sle(data: dict, user_id: int, now_time: datetime.datetime, interval: int) -> bool:
    sleep_time = datetime.datetime.strptime(data[str(user_id)]['sleep_time'], '%Y-%m-%d %H:%M:%S')
    # 上次晚安时间和现在时间相差不超过f'{interval}'小时
    if sleep_time + datetime.timedelta(hours = interval) > now_time:
        return True
    return False


# 判断超级睡眠
async def judge_super_sleep(data: dict, user_id: int, now_time: datetime.datetime, interval: int) -> bool:
    get_up_time = datetime.datetime.strptime(data[str(user_id)]['get_up_time'], '%Y-%m-%d %H:%M:%S')
    # 上次起床时间和现在时间相差不超过f'{interval}'小时
    if get_up_time + datetime.timedelta(hours = int(interval)) > now_time:
        return True
    return False


# 进行晚安并更新数据
async def night_and_update(group_id: int, data: dict, user_id: int, now_time: datetime.datetime) -> (int, Optional[str], float):
    # 若之前没有数据就直接创建一个
    if not str(user_id) in list(data.keys()):
        mem_data = {
            'morning_count': 0,
            'get_up_time': 0,
            'night_count': 1,
            'sleep_time': now_time
        }
        data.setdefault(str(user_id), mem_data)
    # 若有就更新数据
    else:
        data[str(user_id)]['sleep_time'] = now_time
        data[str(user_id)]['night_count'] = int(data[str(user_id)]['night_count']) + 1

    # 当上次起床时间不是初始值0,就计算清醒的时长
    in_day_tmp = None
    total_seconds = None
    if data[str(user_id)]['get_up_time'] != 0:
        get_up_time = datetime.datetime.strptime(data[str(user_id)]['get_up_time'], '%Y-%m-%d %H:%M:%S')
        day, hour, minute, second, total_seconds = await parse_time_delta(now_time, get_up_time)
        if day == 0:
            in_day_tmp = str(int(hour)) + '时' + str(int(minute)) + '分' + str(int(second)) + '秒'
    # 判断是今天第几个睡觉的
    data['today_count']['night'] = int(data['today_count']['night']) + 1
    await write_group_data(group_id, data)
    return data['today_count']['night'], in_day_tmp, total_seconds


# 返回晚安信息
async def get_night_msg(group_id: int, user_id: int, sex_str: str) -> str:
    # 读取配置文件
    config = await get_config()
    # 读取自定义回复文件
    word_config = await get_word()
    # 读取早安晚安数据
    data = await get_group_data(group_id)
    
    word_data = word_config['night']

    # 若开启规定时间晚安，则判断该时间是否允许晚安
    now_time = datetime.datetime.now()
    if config['night']['sleep_in_time']['enable']:
        early_time_tmp = config['night']['sleep_in_time']['early_time']
        late_time_tmp = config['night']['sleep_in_time']['late_time']
        if not await judge_sle_time(early_time_tmp, late_time_tmp, now_time):
            word = f'现在不能晚安哦，可以晚安的时间为{early_time_tmp}时到第二天早上{late_time_tmp}时'
            img = await get_img(False)
            msg = f'{img}\n{word}'
            return msg

    # 当数据里有过这个人的信息就判断:
    if str(user_id) in list(data.keys()):
        # 若关闭连续多次晚安，则判断在设定时间内是否多次晚安
        if not config['night']['multi_sleep']['enable']:
            interval = config['night']['multi_sleep']['interval']
            if await judge_have_sle(data, user_id, now_time, interval):
                word = f'{interval}小时内你已经晚安过了哦'
                img = await get_img(False)
                msg = f'{img}\n{word}'
                return msg
        # 若关闭超级睡眠，则判断不在睡觉的时长是否小于设定时长
        if not config['night']['super_sleep']['enable'] and data[str(user_id)]['get_up_time'] != 0:
            interval = config['night']['super_sleep']['interval']
            if await judge_super_sleep(data, user_id, now_time, interval):
                word = random_choice(word_data['in_day_little'])
                img = await get_img(False)
                msg = f'{img}\n{word}'
                return msg

    # 当数据里没有这个人或者前面条件均符合的时候，允许晚安
    num, in_day, total_seconds= await night_and_update(group_id, data, user_id, now_time)
    now = int(datetime.datetime.now().strftime('%H'))
    if  now < 6:
        time_result = random_choice(word_data['night_late'])
        img = await get_img(False)
    elif now < 18:
        time_result = random_choice(word_data['night_early'])
        img = await get_img(False)
    else:
        time_result = random_choice(word_data['night_normal'])
        img = await get_img(True)

    if not in_day:
        word = f'{time_result}你是今天第{num}个睡觉的{sex_str}'
        msg = f'{img}\n{word}'
    else:
        if  total_seconds < 3600*12:
            time_result += random_choice(word_data['in_day_little'])
            img = await get_img(False)
        elif total_seconds >3600*20:
            time_result += random_choice(word_data['in_day_much'])
            img = await get_img(False)
        word = f'{time_result}你今天的清醒时长为{in_day}。\n你是今天第{num}个睡觉的{sex_str}'
        msg = f'{img}\n{word}'
    return msg
