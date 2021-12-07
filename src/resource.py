from os import path
import json


class Res:
    def __init__(self) -> None:
        self.f_path = path.dirname(__file__)  # 当前程序运行所在的绝对目录
        config_path = self.f_path+'/config.json'
        default_config = {  # 默认配置文件
            'difficulty': 1,
            'diff_cfg': {  # 不同困难度对应的配置
                "1": {
                    "map_size": (50, 15),
                    "init_velo": 0.2  # 值得注意的是，速度最大值不能超过1格/tick，不然会绘制计算错误
                },
                "2": {
                    "map_size": (50, 15),
                    "init_velo": 0.3
                },
                "3": {
                    "map_size": (40, 10),
                    "init_velo": 0.4
                },
                "4": {
                    "map_size": (35, 10),
                    "init_velo": 0.4
                },
                "5": {
                    "map_size": (30, 10),
                    "init_velo": 0.5
                }
            },
            "styles": {
                "line_body": "#",
                "line_color": "CYAN",  # curses内置颜色
                'area_border': '#',
                "border_color": "WHITE"
            }
        }
        if not path.exists(config_path):  # 如果没有就自动创建配置文件
            with open(config_path, 'w+') as f:
                f.write(json.dumps(default_config))

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
            f.write(json.dumps(pre_cfg))  # 写入修改后的配置
        return True

    @classmethod  # 作为一个类方法
    def x_offset(cls, string, offset):
        '''搭配addstr，处理字符串的偏移。如果只用addstr的x-offset的话就第一行有偏移，其他行都是一个样，这个方法将字符串除第一行之外所有行头部都加上offset空格'''
        lines = string.splitlines(keepends=True)
        first_line = lines.pop(0)  # 除了第一行
        # Python竟然有这么方便的方法，可以直接按行分割，太棒了。keepends=True，每行保留换行符
        # 除了第一行每一行都加上偏移
        return first_line+''.join(map(lambda x: offset*' '+x, lines))

    @classmethod  # 作为一个类方法
    def author(O0O00O0OOO0O0OO00):
        OOO0O000000OOO0OO = 'U0tMSU5FIE1hZGUgYnkgU29tZUJvdHRsZSwgRG8gbm90IHVzZSBmb3I'
        O0O00O0O0O00OOOOO = 'geW91ciBvd24gQ291cnNlIFByb2plY3Qu'
        return OOO0O000000OOO0OO + O0O00O0O0O00OOOOO
