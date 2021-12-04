from os import path


class Res:
    def __init__(self) -> None:
        self.f_path = path.dirname(__file__)  # 当前程序运行所在的绝对目录

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
            return result # 让with as语句块执行完后再返回
        else:
            return (0, 0, 'Text resource lost.')
