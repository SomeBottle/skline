import time
import curses
from resource import Res


class View:  # 抽象出一个显示界面的类
    def __init__(self) -> None:
        tui = curses.initscr()  # 初始化curses，生成tui界面
        curses.noecho()  # 无回显模式
        self.tui = tui

    def first_page(self):  # 开始界面
        self.tui.erase()  # 清除之前的内容
        self.tui.addstr(1, 3, Res().art_texts('somebottle')[2])  # 打印出作者名
        self.tui.refresh()  # 刷新窗口，输出addstr的内容
        time.sleep(1)  # 主界面

    def menu(self):  # 游戏菜单
        self.tui.erase()
        title_txt = Res().art_texts('skline')  # 获得艺术字元组
        title_offset_h = title_txt[0]+2  # 标题窗口高度
        title_offset_w = title_txt[1]+2  # 标题窗口宽度
        # 创建一个窗口（其实是当边框使），这里+2是因为在addstr时文本有偏移
        # 高为 title_offset_h 宽为 title_offset_w，在命令行窗口的 2行2列
        title = curses.newwin(title_offset_h, title_offset_w, 2, 2)
        title.nodelay(True)  # 非阻塞!
        title.addstr(1, 1, title_txt[2])  # 打印出游戏名
        title.border()  # 标题旁边加个边框
        # 再创建一个窗口，我们作为菜单
        # 高为 3 宽为 title_offset_w，在命令行窗口的 title_offset_h+2行2列
        choice_session = curses.newwin(3, title_offset_w, title_offset_h+2, 2)
        choice_session.nodelay(False)  # 阻塞
        choice_session.keypad(True)  # 支持上下左右这种特殊按键
        # 游戏选项
        current_choice = 0  # 选择的哪一项
        choice_show = {  # 每一项对应的显示
            0: 'Start Playing  <--\n Set Difficulty',
            1: 'Start Playing\n Set Difficulty  <--'
        }
        last_choice = len(choice_show.keys())-1  # 最后一个选项，用来封底

        self.tui.refresh()  # 刷新总界面
        title.refresh()  # 刷新标题窗口
        while True:
            choice_session.erase()  # 清除之前的选项显示
            choice_session.addstr(1, 1, choice_show[current_choice])
            choice_session.refresh()  # 刷新选项窗口，输出上面的内容
            key_input = choice_session.getch()  # 检测用户输入的键
            if key_input in (ord('w'), curses.KEY_UP):  # 如果用户按下的是上键，选项指针上调
                current_choice = current_choice-1 if current_choice > 0 else 0
            elif key_input in (ord('s'), curses.KEY_DOWN):  # 如果用户按下的是下键，选项指针上调
                current_choice = current_choice+1 if current_choice < last_choice else last_choice
        del title, choice_session  # 删除窗口
        self.tui.clear()
        curses.endwin()
