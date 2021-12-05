import curses
import time
import random
import math
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
        difficulty = str(config['difficulty'])  # json中数字键名都会转换为字符串
        self.game_cfg = config['diff_cfg'][difficulty]  # 读取对应困难度的游戏配置
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
        return self.game_cfg['map_size']

    def start(self):  # 开始游戏！
        self.count_down()  # 先调用倒计时
        map_size = self.map_size  # 获得地图大小
        map_w, map_h = map_size  # 解构赋值
        # 根据地图大小创建游戏区域，要比地图大小稍微大一点
        self.game_area = curses.newwin(map_h+2, map_w+2, 1, 1)
        self.game_area.keypad(True)  # 支持上下左右等特殊按键
        self.game_area.nodelay(True)  # 非阻塞，用户没操作游戏要持续进行
        line_ins = Line(self)
        while True:  # 开始游戏动画
            self.tui.erase()  # 擦除内容
            self.game_area.erase()  # 擦除游戏区域内容
            line_ins.draw()  # 绘制蛇体
            self.game_area.border()  # 游戏区域边界
            self.tui.refresh()
            self.game_area.refresh()
            line_ins.move()  # 移动蛇体
            line_ins.control()  # 接受控制蛇体
            time.sleep(0.1)  # tick速度：0.1秒一计算，这个和图形运动速度有很大关联


class Line:  # 初始化运动线
    def __init__(self, game_ins) -> None:
        config = game_ins.game_cfg  # 传递对应困难度的配置
        map_size = game_ins.map_size  # 传递Game类的实例
        init_velo = config['init_velo']  # 配置的初始速度
        # 注意，防止生成在边缘，不然开局就G了！
        rand_x = random.randint(4, map_size[0]-4)  # 生成线头第一次出现的x坐标
        rand_y = random.randint(4, map_size[1]-4)  # 生成线头第一次出现的y坐标
        self.map_size = map_size
        self.game_area = game_ins.game_area  # 传递游戏区域窗口控制
        self.styles = game_ins.styles  # 传递游戏样式
        self.attrs = {  # 线体属性
            'head_pos': (rand_x, rand_y),  # 头部的位置
            # 头部的运动速度(Vx,Vy)，单位：格数/tick，最开始要不沿x轴，要不沿y轴运动
            'velo': random.choice(((init_velo, 0), (0, init_velo))),
            # 运动方向(x,y)，-1代表负向。向右为X轴正方向，向下为Y轴正方向
            'direction': (random.choice((1, -1)), random.choice((1, -1))),
            'body_pos': []  # 身体各节的位置
        }

    def draw(self):  # 绘制角色
        styles = self.styles
        head_pos = self.attrs['head_pos']
        head_x, head_y = map(math.floor, head_pos)  # 解构赋值
        line_body = styles['line_body']
        # 使用1号颜色对进行绘制
        self.game_area.addstr(head_y, head_x, line_body, curses.color_pair(1))

    def move(self):  # 计算角色移动
        attrs = self.attrs  # 获得角色（线体）属性
        x, y = attrs['head_pos']  # 解构赋值头部x,y坐标
        vx, vy = attrs['velo']  # 解构赋值x,y速度
        dx, dy = attrs['direction']  # 解构赋值x,y的方向
        x += vx*dx
        y += vy*dy
        self.attrs['head_pos'] = (x, y)  # 更新头部坐标

    def control(self):
        attrs = self.attrs  # 获得角色（线体）属性
        vx, vy = attrs['velo']  # 解构赋值x,y速度
        dx, dy = attrs['direction']  # 解构赋值x,y的方向
        recv = self.game_area.getch()  # 获取用户操作
        if recv in (ord('a'), curses.KEY_LEFT, ord('d'), curses.KEY_RIGHT):
            # 如果vx为0就调换一下两个速度，让速度沿x方向
            vx, vy = (vy, vx) if vx <= 0 else (vx, vy)
        elif recv in (ord('w'), curses.KEY_UP, ord('s'), curses.KEY_DOWN):
            # 如果vy为0就调换一下两个速度，让速度沿y方向
            vy, vx = (vx, vy) if vy <= 0 else (vy, vx)

        if recv in (ord('a'), curses.KEY_LEFT):  # 用户按下左键
            dx = -1  # 调转水平行进方向
        elif recv in (ord('d'), curses.KEY_RIGHT):  # 用户按下右键
            dx = 1  # 调转水平行进方向
        elif recv in (ord('w'), curses.KEY_UP):  # 用户按下上键
            dy = -1  # 调转竖直行进方向（向下为Y轴正方向）
        elif recv in (ord('s'), curses.KEY_DOWN):  # 用户按下下键
            dy = 1
        # 更新移动指示
        self.attrs['velo'] = (vx, vy)
        self.attrs['direction'] = (dx, dy)
