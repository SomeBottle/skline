import time
import curses
import base64
from resource import Res
from game import Game


class BasicView:  # 抽象出一个显示界面的类
    def __init__(self) -> None:
        tui = curses.initscr()  # 初始化curses，生成tui界面
        curses.noecho()  # 无回显模式
        self.tui = tui
        self.choice_dict = {  # 几个选项
            0: 'Start to line',
            1: 'Set Difficulty',
            2: 'Exit'
        }
        self.choice_func = {  # 上述选项对应的函数
            0: Game().start,
            1: DifficultyView().show_panel,
            2: self.leave
        }
        self.last_choice = len(self.choice_dict.keys())-1  # 最后一个选项的索引，用来封底

    def first_page(self):  # 开始界面
        self.tui.erase()  # 清除之前的内容
        somebottle = Res().art_texts('somebottle')[2]
        self.tui.addstr(1, 3, Res.x_offset(somebottle, 3))  # 打印出作者名
        self.tui.refresh()  # 刷新窗口，输出addstr的内容
        time.sleep(1)  # 主界面

    def leave(self):
        print(base64.b64decode(Res.author()).decode("utf-8"))

    def option_maker(self, choice):  # 制作选项菜单
        option_menu = ''
        for k, v in self.choice_dict.items():
            option_menu += (f'{v}\n' if not k is choice else f'{v} <-- \n')
        return option_menu

    def menu(self):  # 游戏菜单
        self.tui.erase()
        title_txt = Res().art_texts('skline')  # 获得艺术字元组
        title_offset_h = title_txt[0]+4  # 标题窗口高度
        title_offset_w = title_txt[1]+4  # 标题窗口宽度
        # 创建一个窗口（其实是当边框使），这里+2是因为在addstr时文本有偏移
        # 高为 title_offset_h 宽为 title_offset_w，在命令行窗口的 2行1列
        title = curses.newwin(title_offset_h, title_offset_w, 2, 1)
        title.nodelay(True)  # 非阻塞!
        title.addstr(1, 3, Res.x_offset(title_txt[2], 3))  # 打印出游戏名
        title.border()  # 标题旁边加个边框
        # 再创建一个窗口，我们作为菜单
        # 高为 3 宽为 title_offset_w，在命令行窗口的 title_offset_h+2行2列
        choice_session = curses.newwin(5, title_offset_w, title_offset_h+2, 2)
        choice_session.nodelay(False)  # 阻塞
        choice_session.keypad(True)  # 支持上下左右这种特殊按键
        # 游戏选项
        current_choice = 0  # 选择的哪一项
        self.tui.refresh()  # 刷新总界面
        title.refresh()  # 刷新标题窗口
        while True:
            choice_session.erase()  # 清除之前的选项显示
            choice_session.addstr(1, 0, self.option_maker(current_choice))
            choice_session.refresh()  # 刷新选项窗口，输出上面的内容
            key_input = choice_session.getch()  # 检测用户输入的键
            if key_input in (ord('w'), curses.KEY_UP):  # 如果用户按下的是上键，选项指针上调
                current_choice = (
                    current_choice-1) if current_choice > 0 else 0
            elif key_input in (ord('s'), curses.KEY_DOWN):  # 如果用户按下的是下键，选项指针上调
                current_choice = (
                    current_choice+1) if current_choice < self.last_choice else self.last_choice
            elif key_input in (10, curses.KEY_ENTER):  # 用户按下了回车，确认选择，跳出循环
                break
        del title, choice_session  # 删除窗口
        self.tui.clear()  # 清除屏幕
        curses.endwin()  # 中止窗口，取消初始化
        self.choice_func[current_choice]()  # 执行选项对应的函数


class DifficultyView():  # 困难度调整的会话
    def __init__(self) -> None:
        tui = curses.initscr()  # 初始化curses，生成tui界面
        curses.noecho()  # 无回显模式
        self.tui = tui
        diff_cfg = Res().get_config()['diff_cfg']
        self.max_difficulty = len(diff_cfg.keys())  # 最大困难度，配置中有几个困难度最多就是多少

    def bar_maker(self, difficulty):  # 展现困难度的进度条
        bar_str = ('{: <'+str(self.max_difficulty)+'}').format('#'*difficulty)
        return 'SET: ['+bar_str+']'

    def show_panel(self):
        self.tui.erase()
        res_ins = Res()
        title_txt = res_ins.art_texts('difficulty')  # 获得艺术字元组
        title_offset_h = title_txt[0]+4  # 标题窗口高度
        title_offset_w = title_txt[1]+4  # 标题窗口宽度
        # 创建一个窗口（其实是当边框使），这里+2是因为在addstr时文本有偏移
        # 高为 title_offset_h 宽为 title_offset_w，在命令行窗口的 2行1列
        title = curses.newwin(title_offset_h, title_offset_w, 2, 1)
        title.nodelay(True)  # 非阻塞!
        title.addstr(1, 3, Res.x_offset(title_txt[2], 3))  # 打印出游戏名
        title.border()  # 标题旁边加个边框
        choice_session = curses.newwin(5, title_offset_w, title_offset_h+2, 2)
        choice_session.nodelay(False)  # 阻塞
        choice_session.keypad(True)  # 支持上下左右这种特殊按键
        config = res_ins.get_config()  # 获得配置文件
        difficulty_set = config['difficulty']  # 设定的困难度
        self.tui.refresh()  # 刷新总界面
        title.refresh()  # 刷新标题窗口
        while True:
            choice_session.erase()  # 清除之前的选项显示
            choice_session.addstr(1, 0, self.bar_maker(difficulty_set))
            choice_session.refresh()  # 刷新选项窗口，输出上面的内容
            key_input = choice_session.getch()  # 检测用户输入的键
            if key_input in (ord('a'), curses.KEY_LEFT):  # 用户按下了左键
                difficulty_set = (
                    difficulty_set-1) if difficulty_set > 1 else 1  # 减少困难度
            elif key_input in (ord('d'), curses.KEY_RIGHT):  # 用户按下了右键
                difficulty_set = (
                    difficulty_set+1) if difficulty_set < self.max_difficulty else self.max_difficulty
            elif key_input in (10, curses.KEY_ENTER):  # 用户按下了回车，确认选择，跳出循环
                break
        del title, choice_session  # 删除窗口
        self.tui.clear()  # 清除屏幕
        curses.endwin()  # 中止窗口，取消初始化
        res_ins.set_config('difficulty', difficulty_set)
        BasicView().menu()  # 返回主菜单
