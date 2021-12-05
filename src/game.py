import curses
import time
import random
from resource import Res

curses_colors = {  # curses库内置颜色
    'BLACK': curses.COLOR_BLACK,
    'BLUE': curses.COLOR_BLUE,
    'CYAN': curses.COLOR_CYAN,
    'GREEN': curses.COLOR_GREEN,
    'MAGENTA': curses.COLOR_MAGENTA,
    'RED': curses.COLOR_RED,
    'WHITE': curses.COLOR_WHITE,
    'YELLOW': curses.COLOR_YELLOW
}


class Game:
    def __init__(self) -> None:
        tui = curses.initscr()  # 初始化curses，生成tui界面
        curses.noecho()  # 无回显模式
        curses.start_color()  # 初始化颜色
        self.tui = tui
        res_ins = Res()
        config = res_ins.get_config()  # 获得游戏配置文件
        self.game_cfg = config
        styles = config['styles']  # 获得样式设定
        self.styles = styles
        line_color = styles['line_color']
        # 一号颜色对，用于角色身体
        curses.init_pair(
            1, curses_colors[line_color], curses.COLOR_BLACK)

    def flash_fx(self, content):
        for i in range(5):
            self.tui.erase()
            offset = random.randrange(0, len(content)-1)
            off_content = content[offset::]+content[:offset:]
            self.tui.addstr(1, 5, Res.x_offset(off_content, 5))
            self.tui.refresh()
            time.sleep(0.1)
        self.tui.clear()

    def count_down(self):  # 游戏开始前的倒计时
        for i in ('ready', '3', '2', '1'):
            self.tui.erase()  # 清理残余界面
            text = Res().art_texts(i)[2]
            self.flash_fx(text)  # 做个故障风动画
            # 打印倒计时Res().art_texts('3')[2])
            self.tui.addstr(1, 5, Res.x_offset(text, 5))
            self.tui.refresh()  # 刷新窗口，输出addstr的内容
            time.sleep(0.5)  # 主界面

    @property
    def map_size(self):  # 根据游戏难易度获得地图大小(长，高)，property修饰
        cfg = self.game_cfg
        difficulty = str(cfg['difficulty'])  # json中数字键名都会转换为字符串
        return cfg['map_sizes'][difficulty]

    def start(self):  # 开始游戏！
        self.count_down()  # 先调用倒计时
        map_size = self.map_size  # 获得地图大小
        map_w, map_h = map_size  # 解构赋值
        # 根据地图大小创建游戏区域，要比地图大小稍微大一点
        self.game_area = curses.newwin(map_h+2, map_w+2, 1, 1)
        self.game_area.nodelay(True)  # 非阻塞，用户没操作游戏要持续进行
        self.game_area.border()  # 游戏区域边界
        line_ins = Line(self)
        while True: # 开始游戏动画
            self.tui.erase()  # 擦除内容
            self.game_area.erase() # 擦除游戏区域内容
            line_ins.draw() # 绘制蛇体
            self.tui.refresh()
            self.game_area.refresh()
            time.sleep(0.1) # tick速度：0.1秒一计算，这个和图形运动速度有很大关联

class Line:  # 初始化运动线
    def __init__(self, game_ins) -> None:
        map_size = game_ins.map_size  # 传递Game类的实例
        rand_x = random.randint(0, map_size[0])  # 生成线头第一次出现的x坐标
        rand_y = random.randint(0, map_size[1])  # 生成线头第一次出现的y坐标
        self.map_size = map_size
        self.game_area = game_ins.game_area  # 传递游戏区域窗口控制
        self.styles = game_ins.styles  # 传递游戏样式
        self.attrs = {
            'head_pos': (rand_x, rand_y), # 头部的位置
            'velo':(0.1,0.1), # 头部的运动速度(Vx,Vy)，单位：格数/tick
            'body_pos': [] # 身体各节的位置
        }

    def draw(self):  # 绘制角色
        styles = self.styles
        head_pos = self.attrs['head_pos']
        head_x, head_y = head_pos  # 解构赋值
        line_body = styles['line_body']
        # 使用1号颜色对进行绘制
        self.game_area.addstr(head_y, head_x, line_body, curses.color_pair(1))
