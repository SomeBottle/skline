from os import path
import json


class Res:
    def __init__(self) -> None:
        self.f_path = path.dirname(__file__)  # 当前程序运行所在的绝对目录
        config_path = self.f_path+'/config.json'
        default_config = {'difficulty': 1, 'point_probabilities': {}}
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

    def set_config(self,key,val):
        file_path = self.f_path+'/config.json'
        pre_cfg=self.get_config() # 获得先前的配置文件
        pre_cfg[key]=val
        with open(file_path,'w+') as f:
            f.write(json.dumps(pre_cfg)) # 写入修改后的配置
        return True