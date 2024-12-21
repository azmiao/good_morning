
import json
import os
import random
from datetime import datetime

from yuiChyan import YuiChyan

# 数据文件夹
data_dir = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(data_dir, exist_ok=True)
image_dir = os.path.join(os.path.dirname(__file__),'image')


# 获取图片
async def get_img(good):
    image_sub_path = 'good' if good else 'bad'
    img_path = os.path.join(image_dir, image_sub_path)
    image_name = random.choice(os.listdir(img_path))
    image_path = os.path.join(img_path, image_name)
    img = f'[CQ:image,file=file:///{image_path}]'
    return img


# json读写时间
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self,obj)


# 匹配性别
async def get_sex_str(bot: YuiChyan, group_id: int, user_id: int) -> str:
    # 获取群成员性别
    config = await get_config()
    custom_sex = config.get('custom_sex', '')
    if custom_sex:
        # 指定了就用指定的
        sex_str = custom_sex
    else:
        # 没有指定就匹配
        mem_info = await bot.get_group_member_info(group_id=group_id, user_id=user_id)
        sex = mem_info['sex']
        match sex:
            case 'male':
                sex_str = '美少年'
            case 'female':
                sex_str = '美少女'
            case _:
                sex_str = '群友'
    return sex_str


# 读取群数据
async def get_group_data(group_id: int) -> dict:
    data_path = os.path.join(data_dir, f'{str(group_id)}.json')
    if not os.path.isfile(data_path):
        data = {
            "today_count": {
                "morning": 0,
                "night": 0
            }
        }
        await write_group_data(group_id, data)
    with open(data_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


# 写入群数据
async def write_group_data(group_id: int, data: dict) -> None:
    data_path = os.path.join(data_dir, f'{str(group_id)}.json')
    with open(data_path, 'w', encoding='utf-8') as f:
        # noinspection PyTypeChecker
        json.dump(data, f, ensure_ascii=False, indent=4, cls=DateEncoder)


# 读取配置
async def get_config() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


# 写入配置
async def write_config(config: dict) -> None:
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        # noinspection PyTypeChecker
        json.dump(config, f, ensure_ascii=False, indent=4)


# 读取词库
async def get_word() -> dict:
    config_path = os.path.join(os.path.dirname(__file__), 'word.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config


# 解析时间差
async def parse_time_delta(now_time: datetime,  last_time: datetime) -> (float, float, float, float, float):
    # 计算时间差
    time_difference = now_time - last_time
    # 获取总秒数
    total_seconds = time_difference.total_seconds()
    # 计算天、小时、分钟、秒
    days = total_seconds // (3600 * 24)
    hours = (total_seconds % (3600 * 24)) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return days, hours, minutes, seconds, total_seconds
