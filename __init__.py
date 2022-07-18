from hoshino import Service, priv
import hoshino
import os
from .get_morning import *
from .get_night import *
from .charge import *

sv = Service('good_morning', bundle='早安晚安')

sv_help = '''== 命令 ==
[早安] 早安喵
[晚安] 晚安喵
[我的作息] 看看自己的作息
[群友作息] 看看今天几个人睡觉或起床了
[早安晚安配置] 查看超级管理员设置的配置

== 限超级管理员的设置 ==
[早安晚安初始化] 首次使用请初始化
= 配置(详情看文档) =
[早安开启 xx] 开启某个配置
[早安关闭 xx] 关闭某个配置
[早安设置 xx x] 设置数值
[晚安开启 xx] 开启某个配置
[晚安关闭 xx] 关闭某个配置
[晚安设置 xx x] 设置数值'''.strip()

def get_sex_str(sex,setting):
    if not setting:
        if sex == 'male':
            sex_str = '少年'
        elif sex == 'female':
            sex_str = '少女'
        else:
            sex_str = '群友'
    else:
        sex_str = '美少女'
    return sex_str

#帮助界面
@sv.on_fullmatch('早安晚安帮助')
async def help(bot, ev):
    await bot.send(ev, sv_help)

@sv.scheduled_job('cron', hour='2', minute='59')
async def create_json_daily(bot, ev):
    try:
        group_list = await bot.get_group_list()
        all_num = len(group_list)
        num = 0
        for each_g in group_list:
            group_id = each_g['group_id']
            _current_dir = os.path.join(os.path.dirname(__file__), f'data\{group_id}.json')
            if not os.path.exists(_current_dir):
                data = {
                    "today_count": {
                        "morning": 0,
                        "night": 0
                    }
                }
                with open(_current_dir, "w", encoding="UTF-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                num += 1
        if num:
            x_num = all_num - num
            msg = f'检测到{all_num}个群中：\n- {x_num}个群信息已存在\n- {num}个群信息不存在]\n现已为信息不存在的群成功创建文件！'
        else:
            msg = f'检测到{all_num}个群的配置信息均已存在，无需再次初始化'
    except:
        msg = '早安晚安初始化失败！'
    print(msg)

@sv.on_fullmatch('早安晚安初始化')
async def create_json(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
        await bot.send(ev, msg)
        return
    try:
        group_list = await bot.get_group_list()
        all_num = len(group_list)
        num = 0
        for each_g in group_list:
            group_id = each_g['group_id']
            _current_dir = os.path.join(os.path.dirname(__file__), f'data\{group_id}.json')
            if not os.path.exists(_current_dir):
                data = {
                    "today_count": {
                        "morning": 0,
                        "night": 0
                    }
                }
                with open(_current_dir, "w", encoding="UTF-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                num += 1
        if num:
            x_num = all_num - num
            msg = f'检测到{all_num}个群中：\n- {x_num}个群信息已存在\n- {num}个群信息不存在]\n现已为信息不存在的群成功创建文件！'
        else:
            msg = f'检测到{all_num}个群的配置信息均已存在，无需再次初始化'
    except:
        msg = '早安晚安初始化失败！'
    await bot.send(ev, msg)

@sv.on_fullmatch('早安',"早","早上好","起床")
async def good_morning(bot, ev):
    user_id = ev.user_id
    group_id = ev.group_id
    mem_info = await bot.get_group_member_info(group_id = group_id, user_id = user_id)
    sex = mem_info['sex']
    sex_str = get_sex_str(sex,setting)
    msg = get_morning_msg(group_id, user_id, sex_str)
    await bot.send(ev, msg)

@sv.on_fullmatch('晚安',"睡觉","睡觉觉","上床睡觉")
async def good_night(bot, ev):
    user_id = ev.user_id
    group_id = ev.group_id
    mem_info = await bot.get_group_member_info(group_id = group_id, user_id = user_id)
    sex = mem_info['sex']
    sex_str = get_sex_str(sex,setting)
    msg = get_night_msg(group_id, user_id, sex_str)
    await bot.send(ev, msg)

# 23:59清除一天的早安晚安计数
@sv.scheduled_job('cron', hour='23', minute='59')
async def reset_data():
    bot = hoshino.get_bot()
    group_list = await bot.get_group_list()
    for each_g in group_list:
        group_id = each_g['group_id']
        current_dir = os.path.join(os.path.dirname(__file__), f'data\{group_id}.json')
        if os.path.exists(current_dir):
            file = open(current_dir, 'r', encoding = 'UTF-8')
            data = json.load(file)
            data['today_count']['morning'] = 0
            data['today_count']['night'] = 0
            with open(current_dir, "w", encoding="UTF-8") as f:
                f.write(json.dumps(data, ensure_ascii=False, indent=4))

@sv.on_fullmatch('我的作息')
async def my_status(bot, ev):
    user_id = ev.user_id
    group_id = ev.group_id
    current_dir = os.path.join(os.path.dirname(__file__), f'data\{group_id}.json')
    file = open(current_dir, 'r', encoding = 'UTF-8')
    data = json.load(file)
    if str(user_id) in list(data.keys()):
        get_up_time = data[str(user_id)]['get_up_time']
        sleep_time = data[str(user_id)]['sleep_time']
        morning_count = data[str(user_id)]['morning_count']
        night_count = data[str(user_id)]['night_count']
        msg = f'[CQ:at,qq={user_id}]您的作息数据如下：'
        msg = msg + f'\n最近一次起床时间为{get_up_time}'
        msg = msg + f'\n最近一次睡觉时间为{sleep_time}'
        msg = msg + f'\n一共起床了{morning_count}次'
        msg = msg + f'\n一共睡觉了{night_count}次'
    else:
        msg = '您还没有睡觉起床过呢！暂无数据'
    await bot.send(ev, msg)

@sv.on_fullmatch('群友作息')
async def group_status(bot, ev):
    group_id = ev.group_id
    current_dir = os.path.join(os.path.dirname(__file__), f'data\{group_id}.json')
    file = open(current_dir, 'r', encoding = 'UTF-8')
    data = json.load(file)
    moring_count = data['today_count']['morning']
    night_count = data['today_count']['night']
    msg = f'今天已经有{moring_count}位群友起床了，{night_count}群友睡觉了'
    await bot.send(ev, msg)

# 配置管理
@sv.on_fullmatch('早安晚安配置')
async def config_settings(bot, ev):
    msg = get_current_json()
    await bot.send(ev, msg)

# morning
mor_switcher = {
    '时限': 'get_up_intime',
    '多重起床': 'multi_get_up',
    '超级亢奋': 'super_get_up'
}
@sv.on_prefix('早安开启')
async def morning_enable(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
        await bot.send(ev, msg)
        return
    mor_server = ev.message.extract_plain_text()
    if mor_server not in list(mor_switcher.keys()):
        msg = f'在早安设置中未找到"{mor_server}"，请确保输入正确，目前可选值有:' + str(list(mor_switcher.keys()))
        await bot.send(ev, msg)
        return
    server = mor_switcher[mor_server]
    msg = change_settings('morning', server, True)
    await bot.send(ev, msg)

@sv.on_prefix('早安关闭')
async def morning_disable(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
        await bot.send(ev, msg)
        return
    mor_server = ev.message.extract_plain_text()
    if mor_server not in list(mor_switcher.keys()):
        msg = f'在早安设置中未找到"{mor_server}"，请确保输入正确，目前可选值有:' + str(list(mor_switcher.keys()))
        await bot.send(ev, msg)
        return
    server = mor_switcher[mor_server]
    msg = change_settings('morning', server, False)
    await bot.send(ev, msg)

@sv.on_prefix('早安设置')
async def morning_set(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
        await bot.send(ev, msg)
        return
    alltext = ev.message.extract_plain_text()
    args = alltext.split(' ')
    if args[0] not in list(mor_switcher.keys()):
        msg = f'在早安设置中未找到"{args[0]}"，请确保输入正确，目前可选值有:' + str(list(mor_switcher.keys()))
        await bot.send(ev, msg)
        return
    server = mor_switcher[args[0]]
    if server == 'get_up_intime':
        try:
            early_time = int(args[1])
            late_time = int(args[2])
        except:
            msg = '获取参数错误，请确保你输入了正确的命令，样例参考：\n[早安设置 时限 1 18] 即1点到18点期间可以起床，数字会自动强制取整'
            await bot.send(ev, msg)
            return
        if early_time < 0 or early_time > 24 or late_time < 0 or late_time > 24:
            msg = '错误！您设置的时间未在0-24之间，要求：0 <= 时间 <= 24'
            await bot.send(ev, msg)
            return
        msg = change_set_time('morning', server, early_time, late_time)
    else:
        try:
            interval = int(args[1])
        except:
            msg = '获取参数错误，请确保你输入了正确的命令，样例参考：\n[早安设置 多重起床 6] 即最小间隔6小时，数字会自动强制取整'
            await bot.send(ev, msg)
            return
        if interval < 0 or interval > 24:
            msg = '错误！您设置的时间间隔未在0-24之间，要求：0 <= 时间 <= 24'
            await bot.send(ev, msg)
            return
        msg = change_set_time('morning', server, interval)
    await bot.send(ev, msg)

# night
nig_switcher = {
    '时限': 'sleep_intime',
    '多重睡觉': 'multi_sleep',
    '超级睡眠': 'super_sleep'
}
@sv.on_prefix('晚安开启')
async def night_enable(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
        await bot.send(ev, msg)
        return
    nig_server = ev.message.extract_plain_text()
    if nig_server not in list(nig_switcher.keys()):
        msg = f'在晚安设置中未找到"{nig_server}"，请确保输入正确，目前可选值有:' + str(list(nig_switcher.keys()))
        await bot.send(ev, msg)
        return
    server = nig_switcher[nig_server]
    msg = change_settings('night', server, True)
    await bot.send(ev, msg)

@sv.on_prefix('晚安关闭')
async def night_disable(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
        await bot.send(ev, msg)
        return
    nig_server = ev.message.extract_plain_text()
    if nig_server not in list(nig_switcher.keys()):
        msg = f'在早安设置中未找到"{nig_server}"，请确保输入正确，目前可选值有:' + str(list(nig_switcher.keys()))
        await bot.send(ev, msg)
        return
    server = nig_switcher[nig_server]
    msg = change_settings('night', server, False)
    await bot.send(ev, msg)

@sv.on_prefix('晚安设置')
async def night_set(bot, ev):
    if not priv.check_priv(ev, priv.SUPERUSER):
        msg = '很抱歉您没有权限进行此操作，该操作仅限维护组'
        await bot.send(ev, msg)
        return
    alltext = ev.message.extract_plain_text()
    args = alltext.split(' ')
    if args[0] not in list(nig_switcher.keys()):
        msg = f'在早安设置中未找到"{args[0]}"，请确保输入正确，目前可选值有:' + str(list(nig_switcher.keys()))
        await bot.send(ev, msg)
        return
    server = nig_switcher[args[0]]
    if server == 'sleep_intime':
        try:
            early_time = int(args[1])
            late_time = int(args[2])
        except:
            msg = '获取参数错误，请确保你输入了正确的命令，样例参考：\n[晚安设置 时限 18 6] 即18点到第二天6点期间可以起床，数字会自动强制取整，注意第二个数字一定是第二天的时间'
            await bot.send(ev, msg)
            return
        if early_time < 0 or early_time > 24 or late_time < 0 or late_time > 24:
            msg = '错误！您设置的时间未在0-24之间，要求：0 <= 时间 <= 24'
            await bot.send(ev, msg)
            return
        msg = change_set_time('night', server, early_time, late_time)
    else:
        try:
            interval = int(args[1])
        except:
            msg = '获取参数错误，请确保你输入了正确的命令，样例参考：\n[晚安设置 多重睡觉 6] 即最小间隔6小时，数字会自动强制取整'
            await bot.send(ev, msg)
            return
        if interval < 0 or interval > 24:
            msg = '错误！您设置的时间间隔未在0-24之间，要求：0 <= 时间 <= 24'
            await bot.send(ev, msg)
            return
        msg = change_set_time('night', server, interval)
    await bot.send(ev, msg)