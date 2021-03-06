# coding:utf-8
import time
import curses
import base64
import asyncio
from resource import Res
from game import Game


class BasicView:  # 基类
    def __init__(self) -> None:
        tui = curses.initscr()  # 初始化curses，生成tui界面
        curses.noecho()  # 无回显模式
        self.tui = tui

    def create_win(self, title_txt):
        self.tui.erase()
        title_offset_h = title_txt[0]+4  # 标题窗口高度
        title_offset_w = title_txt[1]+4  # 标题窗口宽度
        # 创建一个窗口（其实是当边框使），这里+2是因为在addstr时文本有偏移
        # 高为 title_offset_h 宽为 title_offset_w，在命令行窗口的 2行1列
        title = curses.newwin(title_offset_h, title_offset_w, 2, 1)
        title.nodelay(True)  # 非阻塞!
        title.addstr(1, 3, Res.x_offset(title_txt[2], 3))  # 打印出游戏名
        title.border()  # 标题旁边加个边框
        # 再创建一个窗口，我们作为菜单
        # 高为 8 宽为 title_offset_w，在命令行窗口的 title_offset_h+2行2列
        choice_session = curses.newwin(10, title_offset_w, title_offset_h+2, 2)
        choice_session.nodelay(False)  # 阻塞
        choice_session.keypad(True)  # 支持上下左右这种特殊按键
        return (title, choice_session)


class MenuView(BasicView):  # 派生出一个显示界面的类
    def __init__(self) -> None:
        super().__init__()
        self.choice_dict = {  # 几个选项
            0: 'Start to line',
            1: 'Set Difficulty',
            2: 'Ranking',
            3: 'Exit'
        }
        self.choice_func = {  # 上述选项对应的函数
            0: self.start_game,
            1: DifficultyView().show_panel,
            2: RankingView().show_panel,
            3: self.leave
        }
        self.last_choice = len(self.choice_dict.keys())-1  # 最后一个选项的索引，用来封底

    def first_page(self):  # 开始界面
        self.tui.erase()  # 清除之前的内容
        somebottle = Res().art_texts('somebottle')[2]
        self.tui.addstr(1, 3, Res.x_offset(somebottle, 3))  # 打印出作者名
        self.tui.refresh()  # 刷新窗口，输出addstr的内容
        curses.flash()  # 闪屏
        time.sleep(1)  # 主界面

    async def asyncio_game(self):  # 开启并行任务
        task_list = set()
        game = Game(task_list)  # 向实例传入任务列表
        task_list.add(asyncio.create_task(game.start()))
        await asyncio.wait(task_list)
        print('Concurrent tasks were completed.')
        self.game_end_choice = game.end_choice  # 把游戏结束后的值传出去

    def start_game(self):  # 开始游戏
        asyncio.run(self.asyncio_game())  # 开启事件循环
        choice_dict = {
            'restart': self.start_game,
            'menu': self.menu
        }
        choice_dict[self.game_end_choice]()  # 执行选项

    def leave(self):
        print(base64.b64decode(Res.author()).decode("utf-8"))

    def option_maker(self, choice):  # 制作选项菜单
        option_menu = ''
        for k, v in self.choice_dict.items():
            option_menu += (f'{v}\n' if not k is choice else f'{v} <-- \n')
        return option_menu

    def menu(self):  # 游戏菜单
        title, choice_session = self.create_win(Res().art_texts('skline'))
        # 游戏选项
        current_choice = 0  # 选择的哪一项
        self.tui.refresh()  # 刷新总界面
        title.refresh()  # 刷新标题窗口
        while True:
            choice_session.erase()  # 清除之前的选项显示
            choice_session.addstr(1, 0, self.option_maker(current_choice))
            choice_session.refresh()  # 刷新选项窗口，输出上面的内容
            key_input = choice_session.getch()  # 检测用户输入的键
            if key_input in (ord('w'), ord('W'), curses.KEY_UP):  # 如果用户按下的是上键，选项指针上调
                current_choice = (
                    current_choice-1) if current_choice > 0 else 0
            elif key_input in (ord('s'), ord('S'), curses.KEY_DOWN):  # 如果用户按下的是下键，选项指针上调
                current_choice = (
                    current_choice+1) if current_choice < self.last_choice else self.last_choice
            elif key_input in (10, curses.KEY_ENTER):  # 用户按下了回车，确认选择，跳出循环
                break
        del title, choice_session  # 删除窗口
        self.tui.clear()  # 清除屏幕
        curses.endwin()  # 中止窗口，取消初始化
        self.choice_func[current_choice]()  # 执行选项对应的函数


class DifficultyView(BasicView):  # 困难度调整的会话
    def __init__(self) -> None:
        super().__init__()
        diff_cfg = Res().get_config()['diff_cfg']
        self.max_difficulty = len(diff_cfg.keys())  # 最大困难度，配置中有几个困难度最多就是多少

    def bar_maker(self, difficulty):  # 展现困难度的进度条
        bar_str = ('{: <'+str(self.max_difficulty)+'}').format('#'*difficulty)
        return 'SET: ['+bar_str+']'

    def show_panel(self):
        title, choice_session = self.create_win(Res().art_texts('difficulty'))
        res_ins = Res()
        config = res_ins.get_config()  # 获得配置文件
        difficulty_set = config['difficulty']  # 设定的困难度
        self.tui.refresh()  # 刷新总界面
        title.refresh()  # 刷新标题窗口
        while True:
            choice_session.erase()  # 清除之前的选项显示
            choice_session.addstr(1, 0, self.bar_maker(difficulty_set))
            choice_session.refresh()  # 刷新选项窗口，输出上面的内容
            key_input = choice_session.getch()  # 检测用户输入的键
            if key_input in (ord('a'), ord('A'), curses.KEY_LEFT):  # 用户按下了左键
                difficulty_set = (
                    difficulty_set-1) if difficulty_set > 1 else 1  # 减少困难度
            elif key_input in (ord('d'), ord('D'), curses.KEY_RIGHT):  # 用户按下了右键
                difficulty_set = (
                    difficulty_set+1) if difficulty_set < self.max_difficulty else self.max_difficulty
            elif key_input in (10, curses.KEY_ENTER):  # 用户按下了回车，确认选择，跳出循环
                break
        del title, choice_session  # 删除窗口
        self.tui.clear()  # 清除屏幕
        curses.endwin()  # 中止窗口，取消初始化
        res_ins.set_config('difficulty', difficulty_set)
        MenuView().menu()  # 返回主菜单


class RankingView(BasicView):
    def list_maker(self, chunk, start=0):
        list_str = 'PLACE             TIME             SCORE\n'
        for key, item in enumerate(chunk):
            place = start+key+1
            date, score = item
            list_str += f'{place}        {date}        {score}\n'
        list_str += '\nPress (D) for Next Page, (A) for Prev Page'
        return list_str

    def show_panel(self):
        rank_list = Res().get_ranking()['rank_list']
        title, choice_session = self.create_win(Res().art_texts('ranking'))
        chunked = []
        each_chunk = 6
        for i in range(0, len(rank_list), each_chunk):
            the_chunk = rank_list[i:i+each_chunk]
            chunked.append(the_chunk)  # 分片
        self.tui.refresh()  # 刷新总界面
        title.refresh()  # 刷新标题窗口
        current_page = 0
        max_page = len(chunked)-1
        while True:
            choice_session.erase()  # 清除之前的显示
            if len(rank_list) > 0:
                current_chunk = chunked[current_page]
                start_place = current_page*each_chunk
                choice_session.addstr(
                    1, 0, self.list_maker(current_chunk, start_place))
            else:  # 暂无记录
                choice_session.addstr(1, 1, 'NO RECORDS')
            choice_session.refresh()  # 刷新选项窗口，输出上面的内容
            recv = choice_session.getch()
            if recv in (ord('D'), ord('d')) and current_page < max_page:
                current_page += 1
            elif recv in (ord('A'), ord('a')) and current_page > 0:
                current_page -= 1
            elif recv in (10, curses.KEY_ENTER):
                break
        del title, choice_session  # 删除窗口
        self.tui.clear()  # 清除屏幕
        curses.endwin()  # 中止窗口，取消初始化
        MenuView().menu()  # 返回主菜单
