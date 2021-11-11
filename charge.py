import os
import json

def read_json():
    current_dir = os.path.join(os.path.dirname(__file__), 'config.json')
    file = open(current_dir, 'r', encoding = 'UTF-8')
    config = json.load(file)
    return config

# 康康当前配置
def get_current_json():
    config = read_json()
    msg = '超级管理员配置的早安晚安设置如下：'
    # morning_config
    get_up_intime = config['morning']['get_up_intime']['enable']
    if get_up_intime:
        msg = msg + '\n是否要求规定时间内起床：是\n - 最早允许起床时间：' + str(config['morning']['get_up_intime']['early_time']) + '点\n - 最晚允许起床时间：' + str(config['morning']['get_up_intime']['late_time']) + '点'
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
    sleep_intime = config['night']['sleep_intime']['enable']
    if sleep_intime:
        msg = msg + '\n是否要求规定时间内睡觉：是\n - 最早允许睡觉时间：' + str(config['night']['sleep_intime']['early_time']) + '点\n - 最晚允许睡觉时间：第二天早上' + str(config['night']['sleep_intime']['late_time']) + '点'
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
def change_settings(day_or_night, server, enable):
    try:
        _current_dir = os.path.join(os.path.dirname(__file__), 'config.json')
        config = read_json()
        config[day_or_night][server]['enable'] = enable
        with open(_current_dir, "w", encoding="UTF-8") as f:
            f.write(json.dumps(config, ensure_ascii=False, indent=4))
        msg = '配置更新成功！'
    except Exception as e:
        msg = f'配置更新失败！错误原因{e}'
    return msg

# 更改时间或间隔
def change_set_time(*args):
    try:
        _current_dir = os.path.join(os.path.dirname(__file__), 'config.json')
        config = read_json()
        day_or_night = args[0]
        server = args[1]
        if server == 'get_up_intime' or server == 'sleep_intime':
            early_time = args[2]
            late_time = args[3]
            config[day_or_night][server]['early_time'] = early_time
            config[day_or_night][server]['late_time'] = late_time
        else:
            interval = args[2]
            config[day_or_night][server]['interval'] = interval
        with open(_current_dir, "w", encoding="UTF-8") as f:
            f.write(json.dumps(config, ensure_ascii=False, indent=4))
        msg = '配置更新成功！'
    except Exception as e:
        msg = f'配置更新失败！错误原因{e}'
    return msg