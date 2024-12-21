import os

from yuiChyan import YuiChyan, CQEvent, LakePermissionException, CommandErrorException
from yuiChyan.core.manager.util import get_all_group_list
from yuiChyan.permission import check_permission, SUPERUSER
from yuiChyan.service import Service
from .charge import *
from .get_morning import *
from .get_night import *
from .util import data_dir, get_config, get_sex_str, write_group_data, get_group_data

sv = Service('good_morning', help_cmd='早安晚安帮助')


@sv.scheduled_job(hour='2', minute='59')
async def create_json_daily():
    try:
        group_list = await get_all_group_list(None)
        all_num = len(group_list)
        not_exist_num = 0
        for each_g in group_list:
            group_id = int(each_g['group_id'])
            _current_dir = os.path.join(data_dir, f'{str(group_id)}.json')
            if not os.path.isfile(_current_dir):
                data = {
                    "today_count": {
                        "morning": 0,
                        "night": 0
                    }
                }
                await write_group_data(group_id, data)
                not_exist_num += 1
        if not_exist_num:
            x_num = all_num - not_exist_num
            sv.logger.info(f'检测到{all_num}个群中：\n- {x_num}个群信息已存在\n- {not_exist_num}个群信息不存在\n现已为信息不存在的群成功创建文件！')
        else:
            # 配置信息均已存在
            return
    except Exception as e:
        sv.logger.error(f'早安晚安所有群配置更新失败： {type(e)} {str(e)}')


@sv.on_match(('早安', '早', '早上好', '起床'))
async def good_morning(bot: YuiChyan, ev: CQEvent):
    user_id = ev.user_id
    group_id = ev.group_id
    # 获取群成员性别
    sex_str = await get_sex_str(bot, group_id, user_id)
    # 生成早安文案
    msg = await get_morning_msg(group_id, user_id, sex_str)
    await bot.send(ev, msg)


@sv.on_match(('晚安', '睡觉', '睡觉觉'))
async def good_night(bot: YuiChyan, ev: CQEvent):
    user_id = ev.user_id
    group_id = ev.group_id
    # 获取群成员性别
    sex_str = await get_sex_str(bot, group_id, user_id)
    # 生成晚安文案
    msg = await get_night_msg(group_id, user_id, sex_str)
    await bot.send(ev, msg)


# 23:59清除一天的早安晚安计数
@sv.scheduled_job(hour='23', minute='59')
async def reset_data():
    group_list = await get_all_group_list(None)
    for each_g in group_list:
        group_id = int(each_g['group_id'])
        _current_dir = os.path.join(data_dir, f'{str(group_id)}.json')
        if os.path.exists(_current_dir):
            data = await get_group_data(group_id)
            data['today_count']['morning'] = 0
            data['today_count']['night'] = 0
            await write_group_data(group_id, data)


@sv.on_match('我的作息')
async def my_status(bot: YuiChyan, ev: CQEvent):
    user_id = ev.user_id
    group_id = ev.group_id
    data = await get_group_data(group_id)
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


@sv.on_match('群友作息')
async def group_status(bot: YuiChyan, ev: CQEvent):
    group_id = ev.group_id
    data = await get_group_data(group_id)
    morning_count = data['today_count']['morning']
    night_count = data['today_count']['night']
    msg = f'今天已经有{morning_count}位群友起床了，{night_count}群友睡觉了'
    await bot.send(ev, msg)


# 配置管理
@sv.on_match('早安晚安配置')
async def config_settings(bot: YuiChyan, ev: CQEvent):
    msg = await get_current_json()
    await bot.send(ev, msg)


@sv.on_rex(r'(早安|晚安)(开启|关闭|设置) ?(\S+)')
async def settings_modify(bot: YuiChyan, ev: CQEvent):
    if check_permission(ev, SUPERUSER):
        raise LakePermissionException(ev, '很抱歉您没有权限进行此操作，该操作仅限维护组')
    # (早安|晚安) | (开启|关闭|设置) | 内容
    modify_type, operation, content = ev['match'].group(1), ev['match'].group(2), ev['match'].group(3)

    morning_switcher = {
        '时限': 'get_up_in_time',
        '多重起床': 'multi_get_up',
        '超级亢奋': 'super_get_up'
    }
    night_switcher = {
        '时限': 'sleep_in_time',
        '多重睡觉': 'multi_sleep',
        '超级睡眠': 'super_sleep'
    }
    current_switcher = morning_switcher if modify_type else night_switcher

    # 内容中的第一个参数
    args = content.split(' ')
    func: str = args[0]
    if func not in list(current_switcher.keys()):
        msg = f'在{modify_type}配置中未找到"{func}"，请确保输入正确，目前可选值有:\n' + str(list(current_switcher.keys()))
        raise CommandErrorException(ev, msg)

    day_or_night = 'morning' if modify_type == '早安‘' else 'night'
    if operation == '设置':
        # 设置参数
        action = '起床' if modify_type == '早安‘' else '睡觉'
        if current_switcher[func].endswith('_in_time'):
            # 需要俩个参数
            try:
                early_time = int(args[1])
                late_time = int(args[2])
            except:
                msg = f'获取参数错误，请确保你输入了正确的命令，样例参考：\n[{modify_type}设置 时限 1 18] 即1点到18点期间可以{action}，数字会自动强制取整'
                raise CommandErrorException(ev, msg)
            if early_time < 0 or early_time > 24 or late_time < 0 or late_time > 24:
                msg = '错误！您设置的时间未在0-24之间，要求：0 <= 时间 <= 24'
                raise CommandErrorException(ev, msg)
            msg = await change_set_time(day_or_night, current_switcher[func], early_time, late_time)
        else:
            try:
                interval = int(args[1])
            except:
                msg = f'获取参数错误，请确保你输入了正确的命令，样例参考：\n[{modify_type}设置 多重{action} 6] 即最小间隔6小时，数字会自动强制取整'
                raise CommandErrorException(ev, msg)
            if interval < 0 or interval > 24:
                msg = '错误！您设置的时间间隔未在0-24之间，要求：0 <= 时间 <= 24'
                raise CommandErrorException(ev, msg)
            msg = await change_set_time(day_or_night, current_switcher[func], interval)
    else:
        # 开启/关闭功能
        is_enable = operation == '开启'
        msg = await change_settings(day_or_night, current_switcher[func], is_enable)
    await bot.send(ev, msg)
