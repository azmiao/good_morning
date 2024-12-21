import datetime
from typing import Optional

from .charge import random_choice
from .util import get_word, parse_time_delta, get_img, get_config, get_group_data, write_group_data


# 判断早安时间
async def judge_mor_time(early_time_tmp: str, late_time_tmp: str, now_time: datetime.datetime) -> bool:
    early_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + f' {early_time_tmp}:00:00', '%Y-%m-%d %H:%M:%S')
    late_time = datetime.datetime.strptime(str(datetime.datetime.now().date()) + f' {late_time_tmp}:00:00', '%Y-%m-%d %H:%M:%S')
    if not now_time >= early_time or not now_time <= late_time:
        return False
    return True


# 判断多次早安
async def judge_have_mor(data: dict, user_id: int, now_time: datetime.datetime, interval: int) -> bool:
    get_up_time = datetime.datetime.strptime(data[str(user_id)]['get_up_time'], '%Y-%m-%d %H:%M:%S')
    # 上次起床时间和现在时间相差不超过f'{interval}'小时
    if get_up_time + datetime.timedelta(hours = int(interval)) > now_time:
        return True
    return False


# 判断超级亢奋
async def judge_super_get_up(data: dict, user_id: int, now_time: datetime.datetime, interval: int) -> bool:
    sleep_time = datetime.datetime.strptime(data[str(user_id)]['sleep_time'], '%Y-%m-%d %H:%M:%S')
    # 上次睡觉时间和现在时间相差不超过f'{interval}'小时
    if sleep_time + datetime.timedelta(hours = int(interval)) > now_time:
        return True
    return False


# 进行早安并更新数据
async def morning_and_update(group_id: int, data: dict, user_id: int, now_time: datetime.datetime) -> (int, Optional[str], float):
    # 起床并写数据
    sleep_time = datetime.datetime.strptime(data[str(user_id)]['sleep_time'], '%Y-%m-%d %H:%M:%S')
    day, hour, minute, second, total_seconds = await parse_time_delta(now_time, sleep_time)
    # 睡觉时间小于24小时就同时给出睡眠时长
    in_sleep_tmp = None
    if day == 0:
        in_sleep_tmp = str(int(hour)) + '时' + str(int(minute)) + '分' + str(int(second)) + '秒'
    data[str(user_id)]['get_up_time'] = now_time
    data[str(user_id)]['morning_count'] = int(data[str(user_id)]['morning_count']) + 1
    # 判断是今天第几个起床的
    data['today_count']['morning'] = int(data['today_count']['morning']) + 1
    await write_group_data(group_id, data)
    return data['today_count']['morning'], in_sleep_tmp, total_seconds


# 返回早安信息
async def get_morning_msg(group_id: int, user_id: int, sex_str: str) -> str:
    # 读取配置文件
    config = await get_config()
    # 读取自定义回复文件
    word_config = await get_word()
    # 读取早安晚安数据
    data = await get_group_data(group_id)

    word_data = word_config['morning']

    # 若开启规定时间早安，则判断该时间是否允许早安
    now_time = datetime.datetime.now()
    if config['morning']['get_up_in_time']['enable']:
        early_time_tmp = config['morning']['get_up_in_time']['early_time']
        late_time_tmp = config['morning']['get_up_in_time']['late_time']
        if not await judge_mor_time(early_time_tmp, late_time_tmp, now_time):
            word = f'现在不能早安哦，可以早安的时间为{early_time_tmp}时到{late_time_tmp}时'
            img = await get_img(False)
            msg = f'{img}\n{word}'
            return msg
    
    # 当数据里有过这个人的信息就判断:
    if str(user_id) in list(data.keys()):
        # 若关闭连续多次早安，则判断在设定时间内是否多次早安
        if not config['morning']['multi_get_up']['enable'] and data[str(user_id)]['get_up_time'] != 0:
            interval = config['morning']['multi_get_up']['interval']
            if await judge_have_mor(data, user_id, now_time, interval):
                word = f'{interval}小时内你已经早安过了哦'
                img = await get_img(False)
                msg = f'{img}\n{word}'
                return msg
        
        # 若关闭超级亢奋，则判断睡眠时长是否小于设定时间
        if not config['morning']['super_get_up']['enable']:
            interval = config['morning']['super_get_up']['interval']
            if await judge_super_get_up(data, user_id, now_time, interval):
                word = random_choice(word_data['sleep_little'])
                img = await get_img(False)
                msg = f'{img}\n{word}'
                return msg
    # 若没有说明他还没睡过觉呢
    else:
        img = await get_img(False)
        word = random_choice(word_data['no_sleep'])
        msg = f'{img}\n{word}'
        return msg

    # 当前面条件均符合的时候，允许早安
    num, in_sleep, total_seconds= await morning_and_update(group_id, data, user_id, now_time)
    now = int(datetime.datetime.now().strftime('%H'))
    if  now < 6:
        time_result = random_choice(word_data['morning_early'])
        img = await get_img(False)
    elif now > 12:
        time_result = random_choice(word_data['morning_late'])
        img = await get_img(False)
    else:
        time_result = random_choice(word_data['morning_normal'])
        img = await get_img(True)

    if not in_sleep:
        word = f'{time_result}你是今天第{num}个起床的{sex_str}'
        msg = f'{img}\n{word}'
    else:
        if  total_seconds < 3600*4:
            time_result += random_choice(word_data['sleep_little'])
            img = await get_img(False)
        elif total_seconds >3600*12:
            time_result += random_choice(word_data['sleep_much'])
            img = await get_img(False)
        word = f'{time_result}你的睡眠时长为{in_sleep}。\n你是今天第{num}个起床的{sex_str}'
        msg = f'{img}\n{word}'
    return msg
