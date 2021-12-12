# coding:utf-8
from os import path
from math import floor
import random
import json


class Res:
    def __init__(self) -> None:
        self.f_path = path.dirname(__file__)  # 当前程序运行所在的绝对目录
        config_path = self.f_path+'/config.json'
        default_config = {  # 默认配置文件
            'difficulty': 1,
            'tps': 10,  # ticks per second
            'diff_cfg': {  # 不同困难度对应的配置
                "1": {
                    "map_size": (50, 15),
                    "init_velo": 0.4,  # 值得注意的是，速度最大值不能超过1格/tick，不然会绘制计算错误
                    "triggers": {  # 触发点的生成概率，支持小数点后三位
                        "normal": 0.5,
                        "bonus": 0.05,
                        "accelerate": 0.08,
                        "decelerate": 0.02,
                        "myopia": 0.05,
                        "bomb": 0.04,
                        "invincibility": 0.05,
                        "stones": 0.06,
                        "teleport": 0.15
                    }
                },
                "2": {
                    "map_size": (50, 15),
                    "init_velo": 0.5,
                    "triggers": {
                        "normal": 0.4,
                        "bonus": 0.05,
                        "accelerate": 0.09,
                        "decelerate": 0.02,
                        "myopia": 0.09,
                        "bomb": 0.09,
                        "invincibility": 0.05,
                        "stones": 0.07,
                        "teleport": 0.14
                    }
                },
                "3": {
                    "map_size": (40, 10),
                    "init_velo": 0.3,
                    "triggers": {
                        "normal": 0.3,
                        "bonus": 0.05,
                        "accelerate": 0.2,
                        "decelerate": 0.02,
                        "myopia": 0.09,
                        "bomb": 0.10,
                        "invincibility": 0.05,
                        "stones": 0.09,
                        "teleport": 0.1
                    }
                },
                "4": {
                    "map_size": (35, 10),
                    "init_velo": 0.4,
                    "triggers": {
                        "normal": 0.25,
                        "bonus": 0.05,
                        "accelerate": 0.12,
                        "decelerate": 0.02,
                        "myopia": 0.1,
                        "bomb": 0.11,
                        "invincibility": 0.05,
                        "stones": 0.2,
                        "teleport": 0.1
                    }
                },
                "5": {
                    "map_size": (30, 10),
                    "init_velo": 0.5,
                    "triggers": {
                        "normal": 0.25,
                        "bonus": 0.03,
                        "accelerate": 0.10,
                        "decelerate": 0.02,
                        "myopia": 0.13,
                        "bomb": 0.15,
                        "invincibility": 0.07,
                        "stones": 0.15,
                        "teleport": 0.1
                    }
                }
            },
            "styles": {
                "line": "#",
                "line_head_color": (11, 170, 239),  # r,g,b
                "line_body_color": (138, 220, 255),
                'area_border': '#',
                "border_color": (161, 161, 161),
                "text_color": (255, 255, 255),
                "to_explode": "*",  # 即将爆炸的图案
                "to_explode_color": (255, 0, 0),  # 即将爆炸时闪烁的颜色
                "explode": "*",  # 爆炸粒子图案
                "explode_color": (255, 215, 15),
                "flow_stone": "o",  # 流石图案
                "flow_stone_color": (209, 153, 0),
                "triggers": {  # 触发点配置
                    "normal": {  # 涨分并增长线体
                        "pattern": "@",
                        "color": (255, 149, 0)
                    },
                    "bonus": {  # 只涨分的触发点
                        "pattern": "@",
                        "color": (255, 149, 0)
                    },
                    "accelerate": {  # 加速的触发点
                        "pattern": "@",
                        "color": (255, 149, 0)
                    },
                    "decelerate": {  # 减速的触发点
                        "pattern": "@",
                        "color": (255, 149, 0)
                    },
                    "myopia": {  # 近视触发点（视野缩小）
                        "pattern": "@",
                        "color": (255, 149, 0)
                    },
                    "bomb": {  # 炸弹点
                        "pattern": "@",
                        "color": (255, 149, 0)
                    },
                    "invincibility": {  # 无敌点
                        "pattern": "@",
                        "color": (255, 149, 0)
                    },
                    "stones": {  # 流石点
                        "pattern": "@",
                        "color": (255, 149, 0)
                    },
                    "teleport": {  # 传送点
                        "pattern": "@",
                        "color": (255, 149, 0)
                    }

                }
            }
        }
        if not path.exists(config_path):  # 如果没有就自动创建配置文件
            with open(config_path, 'w+') as f:
                f.write(json.dumps(default_config, indent=2))

    def art_texts(self, k):  # 获取艺术字，返回值(高度，长度，艺术字文本)，艺术字都放在了./texts目录下
        file_path = self.f_path+'/texts/'+k+'.txt'
        if path.exists(file_path):
            with open(file_path, 'r') as f:
                lines = f.readlines()
                text_height = len(lines)  # 以行数为高度
                text_width = max(*map(lambda x: len(x), lines)
                                 )  # 以最长的一行文本的长度为宽度
                f.seek(0, 0)  # readlines后文件指针指向末尾了，要拉回来！这是一个非常容易出错的点！
                result = (text_height, text_width, f.read())
            return result  # 让with as语句块执行完后再返回
        else:
            return (0, 0, 'Text resource lost.')

    def get_config(self):  # 获得游戏配置文件，返回解析好的配置文件字典
        file_path = self.f_path+'/config.json'
        get_dict = {}
        with open(file_path, 'r') as f:
            get_dict = json.loads(f.read())
        return get_dict

    def set_config(self, key, val):
        file_path = self.f_path+'/config.json'
        pre_cfg = self.get_config()  # 获得先前的配置文件
        pre_cfg[key] = val
        with open(file_path, 'w+') as f:
            f.write(json.dumps(pre_cfg, indent=2))  # 写入修改后的配置
        return True

    @staticmethod  # 作为一个静态方法
    def x_offset(string, offset):
        '''搭配addstr，处理字符串的偏移。如果只用addstr的x-offset的话就第一行有偏移，其他行都是一个样，这个方法将字符串除第一行之外所有行头部都加上offset空格'''
        lines = string.splitlines(keepends=True)
        first_line = lines.pop(0)  # 除了第一行
        # Python竟然有这么方便的方法，可以直接按行分割，太棒了。keepends=True，每行保留换行符
        # 除了第一行每一行都加上偏移
        return first_line+''.join(map(lambda x: offset*' '+x, lines))

    # translateRGB，因为curses颜色RGB各分量范围是从0-1000的，需要翻译一下
    # https://stackoverflow.com/questions/28401332/ncurses-why-is-the-rgb-color-value-range-from-0-1000
    @staticmethod
    def rgb(color):
        ratio = 255/1000
        return map(lambda x: floor(x/ratio), color)

    # 根据比例来随机选择（传入字典，返回随机的字典键）
    @staticmethod
    def ratio_rand(dic):
        pointer = 1  # 指针从1开始
        luck = random.randint(1, 1000)  # 从1到1000中选
        choice = False
        for k, v in dic.items():
            cover = v*1000  # 找出该比率在1000中占的份额
            # 划分区域，像抽奖转盘一样
            if luck >= pointer and luck <= (pointer+cover-1):
                choice = k
                break
            pointer += cover
        return choice

    @staticmethod
    def author():
        OOO0O000000OOO0OO = 'U0tMSU5FIE1hZGUgYnkgU29tZUJvdHRsZSwgRG8gbm90IHVzZSBmb3I'
        O0O00O0O0O00OOOOO = 'geW91ciBvd24gQ291cnNlIFByb2plY3Qu'
        return OOO0O000000OOO0OO + O0O00O0O0O00OOOOO
