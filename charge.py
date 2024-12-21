import random
from typing import List

from .util import get_config, write_config


# 随机
def random_choice(_list: List[str]) -> str:
    return random.choice(_list)


# 康康当前配置
async def get_current_json():
    config = await get_config()
    msg = '超级管理员配置的早安晚安设置如下：'
    # morning_config
    get_up_in_time = config['morning']['get_up_in_time']['enable']
    if get_up_in_time:
        msg = msg + '\n是否要求规定时间内起床：是\n - 最早允许起床时间：' + str(config['morning']['get_up_in_time']['early_time']) + '点\n - 最晚允许起床时间：' + str(config['morning']['get_up_in_time']['late_time']) + '点'
    else:
        msg = msg + '\n是否要求规定时间内起床：否'
    multi_get_up = config['morning']['multi_get_up']['enable']
    if multi_get_up:
        msg = msg + '\n是否允许连续多次起床：是'
    else:
        msg = msg + '\n是否允许连续多次起床：否\n - 允许的最短起床间隔：' + str(config['morning']['multi_get_up']['interval']) + '小时'
    super_get_up = config['morning']['super_get_up']['enable']
    if super_get_up:
        msg = msg + '\n是否允许超级亢奋(即睡眠时长很短)：是'
    else:
        msg = msg + '\n是否允许超级亢奋(即睡眠时长很短)：否\n - 允许的最短睡觉时长：' + str(config['morning']['super_get_up']['interval']) + '小时'
    # night_config
    sleep_in_time = config['night']['sleep_in_time']['enable']
    if sleep_in_time:
        msg = msg + '\n是否要求规定时间内睡觉：是\n - 最早允许睡觉时间：' + str(config['night']['sleep_in_time']['early_time']) + '点\n - 最晚允许睡觉时间：第二天早上' + str(config['night']['sleep_in_time']['late_time']) + '点'
    else:
        msg = msg + '\n是否要求规定时间内睡觉：否'
    multi_sleep = config['night']['multi_sleep']['enable']
    if multi_sleep:
        msg = msg + '\n是否允许连续多次睡觉：是'
    else:
        msg = msg + '\n是否允许连续多次睡觉：否\n - 允许的最短睡觉间隔：' + str(config['night']['multi_sleep']['interval']) + '小时'
    super_sleep = config['night']['super_sleep']['enable']
    if super_sleep:
        msg = msg + '\n是否允许超级睡眠(即清醒时长很短)：是 '
    else:
        msg = msg + '\n是否允许超级睡眠(即清醒时长很短)：否\n - 允许的最短清醒时长：' + str(config['night']['super_sleep']['interval']) + '小时'
    return msg


# 开启或关闭
async def change_settings(day_or_night: str, server: str, enable: bool) -> str:
    try:
        config = await get_config()
        config[day_or_night][server]['enable'] = enable
        await write_config(config)
        msg = '配置更新成功！'
    except Exception as e:
        msg = f'配置更新失败！错误原因{e}'
    return msg


# 更改时间或间隔
async def change_set_time(day_or_night: str, server: str, *args) -> str:
    try:
        config = await get_config()
        if server.endswith('_in_time'):
            early_time = args[0]
            late_time = args[1]
            config[day_or_night][server]['early_time'] = early_time
            config[day_or_night][server]['late_time'] = late_time
        else:
            interval = args[0]
            config[day_or_night][server]['interval'] = interval
        await write_config(config)
        msg = '配置更新成功！'
    except Exception as e:
        msg = f'配置更新失败！错误原因{e}'
    return msg
