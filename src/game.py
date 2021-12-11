# coding:utf-8
import curses
import time
import random
import asyncio
from math import floor
from resource import Res


class Game:
    def __init__(self, task_list) -> None:
        self.cls_init(task_list)  # 重初始化类属性
        self.task_list = task_list  # 传递并发任务列表
        curses.noecho()  # 无回显模式
        curses.start_color()  # 初始化颜色
        self.tui.nodelay(True)  # getch不阻塞
        self.tui.keypad(True)  # 支持特殊按键
        styles = self.styles
        line_head_color = styles['line_head_color']
        line_body_color = styles['line_body_color']
        border_color = styles['border_color']
        text_color = styles['text_color']  # 文字颜色
        # 一号颜色对，用于线头
        self.set_color(1, line_head_color)
        # 二号颜色对，用于边框颜色
        self.set_color(2, border_color)
        # 三号颜色对，用于线尾
        self.set_color(3, line_body_color)
        # 四号颜色对，用于文字
        self.set_color(4, text_color)

    @staticmethod
    def set_color(num, rgb_tuple):
        color_num = num+100
        curses.init_color(color_num, *Res.rgb(rgb_tuple))
        curses.init_pair(num, color_num, curses.COLOR_BLACK)

    # 初始化类属性，这样写是为了每次实例化Game()时都对应更新类属性
    # 为什么要全写成类属性呢，这是为了开放公共属性供Line,Trigger类实例使用，便于管理
    @classmethod
    def cls_init(cls, task_list):
        all_cfg = Res().get_config()  # 获得游戏配置文件
        difficulty = str(all_cfg['difficulty'])  # json中数字键名都会转换为字符串
        game_cfg = all_cfg['diff_cfg'][difficulty]  # 读取对应困难度的游戏配置
        tps = all_cfg['tps']  # 获得游戏tps
        map_size = game_cfg['map_size']
        x, y = map_size
        # 根据地图大小生成所有的坐标
        cls.map_points = {(xi, yi) for xi in range(1, x+1)
                          for yi in range(1, y+1)}
        cls.explode_points = set()  # 爆炸点
        cls.flow_stones = set()  # 流石点
        cls.short_sighted = False  # 是否近视
        cls.styles = all_cfg['styles']  # 获得样式设定
        cls.all_cfg = all_cfg
        cls.game_cfg = game_cfg
        cls.map_size = map_size
        cls.tick_interval = round(1/tps, 4)  # 算出tick间隔，保留四位小数
        cls.task_list = task_list
        cls.__ins_list = {}  # 储存实例的列表
        cls.tui = curses.initscr()  # 初始化curses，生成tui界面

    @classmethod
    def cut_points(cls, points):  # 裁剪地图外的点(传入一个点集合)
        return points & cls.map_points

    @classmethod
    def reset_score(cls):  # 重置分数
        cls.__score = 0

    @classmethod
    def add_score(cls, num=1):  # 加分
        cls.__score += num

    @classmethod
    def create_border(cls):  # 创建边界点坐标
        map_w, map_h = map(lambda x: x+1, cls.map_size)  # 获得地图大小
        border_points = set()  # 储存边框的点坐标
        for w in range(map_w+1):
            border_points.update({(w, 0), (w, map_h)})
        for h in range(map_h+1):  # 让竖直方向的边框长一点
            border_points.update({(0, h), (map_w, h)})
        cls.border_points = list(border_points)

    @classmethod
    def create_area(cls):
        map_w, map_h = map(lambda x: x+3, cls.map_size)  # 获得地图大小
        # 根据地图大小创建游戏区域，要比地图大小稍微大一点
        game_area = curses.newwin(map_h, map_w, 1, 1)
        msg_area = curses.newwin(7, map_w, map_h+1, 1)
        game_area.keypad(True)  # 支持上下左右等特殊按键
        game_area.nodelay(True)  # 非阻塞，用户没操作游戏要持续进行
        msg_area.nodelay(True)
        cls.game_area = game_area
        cls.msg_area = msg_area

    @classmethod
    def del_area(cls):
        del cls.game_area, cls.msg_area

    @classmethod
    def reg_ins(cls, name, ins):
        cls.__ins_list[name] = ins

    @classmethod
    def get_ins(cls, name):
        return cls.__ins_list[name]

    @classmethod
    def myopia(cls, toggle):  # 是否近视
        cls.short_sighted = toggle

    # 接管curses addstr，为了适配myopia模式
    @classmethod
    def printer(cls, pos_y, pos_x, string, *args):
        win_obj = cls.game_area
        if not cls.short_sighted:  # 没有近视就默认情况
            win_obj.addstr(pos_y, pos_x, string, *args)
        else:  # 近视了就特殊打印
            sight_w = 5  # 视野宽度
            sight_h = 5  # 视野高度
            map_w, map_h = cls.map_size  # 获得地图尺寸
            x_ratio = map_w//sight_w  # x方向比例
            y_ratio = map_h//sight_h  # y方向比例
            x_center = map_w//2  # 地图中x方向中心
            y_center = map_h//2  # 地图中y方向中心
            line_ins = cls.get_ins('line')  # 取出ins实例
            x, y = map(floor, line_ins.attrs['head_pos'])
            l_t_x = x - (sight_w-1)//2
            l_t_y = y - (sight_h-1)//2
            # 得到视野区所有坐标点
            sight_points = {(xi, yi) for yi in range(l_t_y, l_t_y+sight_h)
                            for xi in range(l_t_x, l_t_x+sight_w)}
            if (pos_x, pos_y) in sight_points:  # 如果要打印的内容在视野区
                relative_x = pos_x-x  # x方向上相对头部距离
                relative_y = pos_y-y  # y方向上相对头部距离
                c_t_x = x_center+relative_x*x_ratio  # 找出在放大视野中的中心x坐标
                c_t_y = y_center+relative_y*y_ratio  # 找出在放大视野中的中心y坐标
                # 接下来要放大这一个点
                half_w = floor((x_ratio-1)/2)  # 先找出一半宽度，向上取整
                half_h = floor((y_ratio-1)/2)  # 找出一半高度
                new_l_t_x = c_t_x-half_w  # 这一个方块的左上角x坐标
                new_l_t_y = c_t_y-half_h  # 这一个方块的左上角y坐标
                # 获得渲染这个方块的点坐标
                block_points = {(bx, by) for by in range(
                    new_l_t_y, new_l_t_y+y_ratio) for bx in range(new_l_t_x, new_l_t_x+x_ratio)}
                for pt in cls.cut_points(block_points):  # 去掉地图外面的点，防止出错
                    bx, by = pt
                    win_obj.addstr(by, bx, string, *args)

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
            time.sleep(0.2)  # 主界面

    def draw_flow_stones(self):  # 绘制流石
        if len(self.flow_stones) <= 0:  # 没有流石就不多费力气
            return False
        flow_stone = self.styles['flow_stone']
        flow_stone_color = self.styles['flow_stone_color']
        self.set_color(22, flow_stone_color)  # 22号颜色对用于流石
        for pt in self.flow_stones:
            x, y = pt
            self.printer(y, x, flow_stone, curses.color_pair(22))

    def draw_border(self):  # 根据边界点坐标绘制游戏区域边框
        pattern = self.styles['area_border']  # 读取边框样式
        for point in self.border_points:
            x, y = point
            self.printer(y, x, pattern, curses.color_pair(2))

    def draw_score(self):
        map_h = self.map_size[1]
        self.msg_area.addstr(0, 0, 'SCORE: '+str(self.__score))

    def over(self):  # 游戏结束
        self.cancel_tasks()  # 取消所有任务
        self.tui.erase()  # 擦除内容
        self.game_area.erase()  # 擦除游戏区域内容
        over_text = Res().art_texts('gameover')[2]  # 获得艺术字GAME OVER
        self.tui.addstr(1, 5, Res.x_offset(
            over_text, 5), curses.color_pair(4))
        self.tui.refresh()
        self.del_area()  # 删除游戏区域
        # time.sleep(5)

    def cancel_tasks(self):  # 取消所有并行任务
        for task in self.task_list:
            task.cancel()

    async def start(self):  # 开始游戏！
        tick_interval = self.tick_interval  # 获得tick间隔时间
        self.count_down()  # 先调用倒计时
        self.reset_score()  # 重置分数
        self.create_area()  # 创建游戏绘制区域
        self.create_border()  # 创建边界点坐标
        line_ins = Line()  # 实例化线体
        Game.reg_ins('line', line_ins)  # 在Game类上注册（保留）实例
        trg_ins = Trigger()  # 实例化触发点，并和线体实例关联
        while True:  # 开始游戏动画
            tick_start = time.time()  # 本次tick开始时间
            self.tui.erase()  # 擦除内容
            self.msg_area.erase()
            self.game_area.erase()  # 擦除游戏区域内容
            line_ins.draw_line()  # 绘制线体
            self.draw_border()  # 绘制游戏区域边界
            self.draw_score()  # 绘制分数
            self.draw_flow_stones()  # 绘制流石
            line_ins.draw_msg()  # 绘制信息
            trg_ins.check()
            trg_ins.draw()
            self.tui.refresh()
            self.msg_area.refresh()
            self.game_area.refresh()
            line_ins.move()  # 移动线体
            line_ins.control()  # 接受控制线体
            if line_ins.impact():  # 判断是否有碰撞
                break
            tick_take = time.time()-tick_start  # 本次tick耗时
            # tick速度：如果0.1秒一计算，TPS=10，这个和图形运动速度有很大关联，0.1s一计算也就是刷新率10Hz
            # 这里减去了本次tick使用的时间，这样能保证sleep间隔在tick_interval左右
            if tick_take <= tick_interval:
                await asyncio.sleep(tick_interval-tick_take)
        curses.flash()  # 撞上什么了就闪屏一下
        await asyncio.sleep(2)  # 游戏结束后凝固两秒
        self.over()


class Line:  # 初始化运动线

    def __init__(self) -> None:
        self.__map_w, self.__map_h = Game.map_size  # 解构赋值地图长宽
        # 注意，防止生成在边缘，不然开局就G了！
        # 把生成区域x,y从地图区域往内各缩4格，防止生成在边缘
        ava_points = [(xi, yi) for xi in range(4, self.__map_w-3)
                      for yi in range(4, self.__map_h-3)]
        init_velo = Game.game_cfg['init_velo']  # 配置的初始速度
        self.attrs = {  # 线体属性
            'head_pos': random.choice(ava_points),  # 生成随机的头部坐标
            # 头部的运动速度(Vx,Vy)，单位：格数/tick，最开始要不沿x轴，要不沿y轴运动
            'velo': random.choice(((init_velo, 0), (0, init_velo))),
            # 运动方向(x,y)，-1代表负向。向右为X轴正方向，向下为Y轴正方向
            'direction': (random.choice((1, -1)), random.choice((1, -1))),
            'body_pos': [(0, 0) for i in range(10)],  # 身体各节的位置
            'invincibility': False,  # 是否无敌
            'myopia': False  # 是否近视
        }
        self.effects = {}  # 线身效果
        self.fx_dict = {  # 效果对照表
            'accelerate': 'Speed UP',
            'decelerate': 'Speed Down',
            'myopia': 'Myopia',
            'bomb': 'THE BOMB!',
            'invincibility': 'Invincibility',
            'stones': 'Watch out the stones',
            'teleport': 'Teleported'
        }

    def draw_line(self):  # 绘制角色
        head_pos = self.attrs['head_pos']
        body_pos = self.attrs['body_pos']
        head_x, head_y = map(floor, head_pos)  # 解构赋值
        line_body = Game.styles['line']
        for t in body_pos:  # 绘制尾部
            Game.printer(t[1], t[0], line_body, curses.color_pair(3))
        # 使用1号颜色对进行头部绘制
        Game.printer(head_y, head_x, line_body, curses.color_pair(1))

    def draw_msg(self):  # 绘制线体相关信息，位于游戏区域下方
        line = 1
        for fx in self.effects.values():
            trg_type = fx[0]  # 该触发点的类型
            trg_style = Game.styles['triggers'][trg_type]  # 获得样式配置
            Game.set_color(11, trg_style['color'])  # 用触发点的颜色来打印文字
            remain = f' - {fx[1]}s' if fx[1] > 0 else ''
            text = self.fx_dict[trg_type]+remain
            Game.msg_area.addstr(line, 0, text, curses.color_pair(11))
            line += 1

    def tail_impact(self, points):  # 削尾巴判断
        attrs = self.attrs
        bodies = attrs['body_pos']
        cut_from = 0  # 从哪里截断
        for k, v in enumerate(bodies):
            if v in points:
                cut_from = k  # 从靠头部最近的地方截断
        attrs['body_pos'] = bodies[cut_from+1::]

    def impact(self):  # 碰撞判断
        attrs = self.attrs
        if attrs['invincibility']:  # 如果无敌就直接跳过
            return False
        max_x, max_y = self.__map_w, self.__map_h  # 解构赋值最大的x,y坐标值
        x, y = attrs['head_pos']
        result = False  # False代表未碰撞，True代表有碰撞
        judge_border_x = x >= 1 and x < max_x+1
        judge_border_y = y >= 1 and y < max_y+1
        floored = (floor(x), floor(y))
        # 第一步先判断是否碰到边框
        if not (judge_border_x and judge_border_y):
            result = True
        # 第二步判断是不是碰到自己了
        elif floored in attrs['body_pos']:
            result = True
        # 第三步判断是不是被炸到了
        elif floored in Game.explode_points:
            result = True
        # 第四步判断是不是被流石撞到了
        elif floored in Game.flow_stones:
            result = True
        return result

    def move(self):  # 计算角色移动
        max_x, max_y = self.__map_w, self.__map_h  # 解构赋值最大的x,y坐标值
        attrs = self.attrs  # 获得角色（线体）属性
        head_pos = attrs['head_pos']
        x, y = head_pos  # 解构赋值头部x,y坐标
        prev_x, prev_y = floor(x), floor(y)  # 上一tick的头部坐标
        vx, vy = attrs['velo']  # 解构赋值x,y速度
        dx, dy = attrs['direction']  # 解构赋值x,y的方向
        # 让线头能穿越屏幕，因为窗口绘制偏差，x和y的初始值从1开始，与之相对max_x,max_y也添加了偏移量1
        x = x + (vx*dx) if x >= 1 and x < max_x + \
            1 else (max_x if dx < 0 else 1)
        y = y + (vy*dy) if y >= 1 and y < max_y + \
            1 else (max_y if dy < 0 else 1)
        new_head_pos = (x, y)
        attrs['head_pos'] = new_head_pos  # 更新头部坐标
        # 向下取整后线身前进了一格
        body_pos = attrs['body_pos']  # 引用索引
        body_len = len(body_pos)
        if not (floor(x) == prev_x and floor(y) == prev_y):
            if body_len > 0:  # 身体长度大于0再进行处理
                body_pos = body_pos[1::]
                body_pos.append((prev_x, prev_y))
                attrs['body_pos'] = body_pos

    def add_tail(self):  # 加长尾巴
        body_pos = self.attrs['body_pos']
        # 获得离头最近的一节尾巴的坐标
        first_pos = body_pos[-1] if len(body_pos) > 0 else (0, 0)
        body_pos.append(first_pos)  # 追加一节尾巴

    def control(self):
        attrs = self.attrs  # 获得角色（线体）属性
        vx, vy = attrs['velo']  # 解构赋值x,y速度
        dx, dy = attrs['direction']  # 解构赋值x,y的方向
        recv = Game.game_area.getch()  # 获取用户操作
        ctrls = {
            'L': (ord('a'), curses.KEY_LEFT),
            'R': (ord('d'), curses.KEY_RIGHT),
            'U': (ord('w'), curses.KEY_UP),
            'D': (ord('s'), curses.KEY_DOWN)
        }
        if recv in ctrls['L']+ctrls['R']:
            # 如果vx为0就调换一下两个速度，让速度沿x方向
            vx, vy = (vy, vx) if vx <= 0 else (vx, vy)
        elif recv in ctrls['U']+ctrls['D']:
            # 如果vy为0就调换一下两个速度，让速度沿y方向
            vy, vx = (vx, vy) if vy <= 0 else (vy, vx)

        if recv in ctrls['L']:  # 用户按下左键
            dx = -1  # 调转水平行进方向
        elif recv in ctrls['R']:  # 用户按下右键
            dx = 1  # 调转水平行进方向
        elif recv in ctrls['U']:  # 用户按下上键
            dy = -1  # 调转竖直行进方向（向下为Y轴正方向）
        elif recv in ctrls['D']:  # 用户按下下键
            dy = 1
        # 更新移动指示
        self.attrs['velo'] = (vx, vy)
        self.attrs['direction'] = (dx, dy)

    def hit(self, p_x, p_y):  # 撞击判断(x,y)
        attrs = self.attrs
        h_x, h_y = attrs['head_pos']
        # 如果<=1会有误判
        return 0 <= h_x-p_x < 1 and 0 <= h_y-p_y < 1

    @property
    def velo(self):  # 获得线体速度大小（无关方向）
        vx, vy = self.attrs['velo']
        return vx+vy

    @velo.setter
    def velo(self, v):  # 设置线体速度大小（自动判断方向）
        if v > 0 and v <= 1:  # 速度有效性校验
            attrs = self.attrs
            vx = attrs['velo'][0]
            attrs['velo'] = (0, v) if vx == 0 else (v, 0)


class Trigger:  # 触发点类
    def __init__(self) -> None:
        self.line = Game.get_ins('line')  # 传递line实例
        self.triggers = {}  # 用一个字典来储存触发点

    def check(self):  # 检查食物碰撞
        if len(self.triggers) == 0:  # 没有任何触发点
            self.make()  # 生成触发点
        else:  # 有触发点就检测碰撞
            # 如果不这样做，在循环过程中对字典进行del操作时会有异常抛出
            trg_items = tuple(self.triggers.items())
            for ind, tg in trg_items:  # 遍历触发点列表
                t_x, t_y = tg['pos']  # 获得触发点坐标
                # 两坐标相减，如果绝对值<1(格)，就说明在同一块区域，碰撞上了
                # 判断水平方向碰撞
                if self.line.hit(t_x, t_y):
                    trg_type = tg['type']  # 获得触发点类型
                    # Game.add_score()  # 加分
                    del self.triggers[ind]
                    new_task = asyncio.create_task(
                        self.__trg_async(trg_type, (t_x, t_y)))
                    Game.task_list.add(new_task)
                    # self.make()
                    # self.line.add_tail()

    def ava_points(self):  # 获得可用的点
        attrs = self.line.attrs  # 获得线体属性
        exist_points = []+attrs['body_pos']  # 脱离原来的引用
        exist_points.append(attrs['head_pos'])
        exist_triggers = [i['pos']
                          for i in self.triggers.values()]  # 获得所有触发点占用的坐标点
        exist_points += exist_triggers  # exist_points储存的是已经使用的坐标点
        exist_points += Game.border_points  # 还要算入边框的点
        # 将所有的坐标点和已经使用的坐标点作差集，就是还可以选用的坐标点
        return tuple(Game.map_points - set(exist_points))

    def make(self):  # 做饭...啊不，是随机放置触发点的方法
        ava_points = self.ava_points()
        sub = len(self.triggers)  # 获得点坐标储存下标
        trg_config = Game.game_cfg['triggers']  # 获得触发点生成比率
        chosen_type = Res.ratio_rand(trg_config)  # 使用ratiorand方法来随机生成的类型
        # 生成触发点新出现的坐标
        new_point = {
            "type": chosen_type,
            "pos": random.choice(ava_points)
        }
        self.triggers[sub] = new_point  # 储存创建的新触发点

    def draw(self):  # 输出触发点和相关信息
        for tg in self.triggers.values():
            trg_type = tg['type']  # 该触发点的类型
            trg_style = Game.styles['triggers'][trg_type]  # 获得样式配置
            Game.set_color(10, trg_style['color'])  # 10号颜色对用于触发点
            x, y = tg['pos']
            Game.printer(y, x, trg_style['pattern'], curses.color_pair(10))

    async def __trg_async(self, trg_type, pos):  # 异步处理分发
        trg_type = 'myopia'  # for test
        trg_funcs = {
            'normal': self.__trg_normal,
            'bonus': self.__trg_bonus,
            'accelerate': self.__trg_acce,
            'decelerate': self.__trg_dece,
            'myopia': self.__trg_myopia,
            'bomb': self.__trg_bomb,
            'invincibility': self.__trg_ivcb,
            'stones': self.__trg_stones,
            'teleport': self.__trg_tp
        }
        await trg_funcs[trg_type](pos)

    # 挂起效果(status,是否只弹一下,在循环里执行的额外函数，用于额外函数的参数)
    async def __hang_fx(self, status, pop=False, extra_func=False, *args):
        effects = self.line.effects
        sub = time.time()  # 插入的下标
        effects[sub] = status
        last_for, minus = (status[1], 1) if not pop else (2, 0)
        for i in range(last_for):  # 持续last_for秒
            status[1] -= minus
            if extra_func:
                extra_func(*args)
            await asyncio.sleep(1)
        del effects[sub]  # 删除效果

    async def __trg_normal(self, pos):
        self.line.add_tail()  # 增长尾巴就够了
        Game.add_score()  # 加分

    async def __trg_bonus(self, pos):
        Game.add_score()  # 只加分

    async def __trg_acce(self, pos):
        last_for = 5  # 效果持续5秒
        velo_add = 0.2  # 增加的速度
        status = ['accelerate', last_for]
        velo_before = self.line.velo  # 之前的速度
        temp_velo = velo_before+velo_add  # 暂且而言的新速度
        if temp_velo <= 1:  # 速度封顶
            self.line.velo = temp_velo  # 设置速度
            await self.__hang_fx(status)
            current_speed = self.line.velo  # 因为是异步执行，速度可能已经改变了，再获取一次
            self.line.velo = current_speed-velo_add  # 恢复速度

    async def __trg_dece(self, pos):
        last_for = 5  # 效果持续5秒
        velo_rmv = 0.2  # 降低的速度
        status = ['decelerate', last_for]
        velo_before = self.line.velo  # 之前的速度
        temp_velo = velo_before-velo_rmv  # 暂且而言的新速度
        if temp_velo > 0:  # 速度封底
            self.line.velo = temp_velo  # 设置速度
            await self.__hang_fx(status)
            current_speed = self.line.velo  # 因为是异步执行，速度可能已经改变了，再获取一次
            self.line.velo = current_speed+velo_rmv  # 恢复速度

    async def __trg_myopia(self, pos):
        last_for = 3  # 效果持续3秒
        status = ['myopia', last_for]

        def keep():
            Game.myopia(True)  # 多个近视效果可以叠加
        await self.__hang_fx(status, False, keep)
        Game.myopia(False)

    async def __trg_bomb(self, pos):
        effects = self.line.effects
        to_explode_color = Game.styles['to_explode_color']
        to_explode = Game.styles['to_explode']
        explode_color = Game.styles['explode_color']
        explode = Game.styles['explode']
        sub = time.time()  # 插入的下标
        status = ['bomb', 0]
        effects[sub] = status
        Game.set_color(20, to_explode_color)  # 20号颜色对用于爆炸点
        Game.set_color(21, explode_color)  # 21号颜色对用于爆炸粒子
        x, y = pos
        for i in range(15):  # 爆炸前闪烁1.5秒
            if i % 2 == 0:
                Game.printer(y, x, to_explode, curses.color_pair(20))
                Game.game_area.refresh()
            await asyncio.sleep(0.1)
        # 生成器表达式随机生成爆炸的宽度和高度
        explosion_w, explosion_h = (random.choice((3, 5)) for i in range(2))
        # 生成爆炸范围左上角的坐标
        start_x, start_y = (x-floor((explosion_w-1)/2),
                            y-floor((explosion_h-1)/2))
        # 爆炸点
        explode_points = {(xi, yi) for yi in range(
            start_y, start_y+explosion_h) for xi in range(start_x, start_x+explosion_w)}
        explode_points = Game.cut_points(explode_points)  # 裁剪地图边界外的点，避免出错
        Game.explode_points.update(explode_points)  # 向游戏主体传入爆炸碰撞点
        self.line.tail_impact(explode_points)  # 爆炸削掉尾巴
        # 选取显示的粒子样本中的粒子数量
        for i in range(5):  # 爆炸粒子动画0.5秒
            particles_num = random.randrange(3, (explosion_w*explosion_h)//2)
            particles = random.sample(explode_points, particles_num)
            for px, py in particles:
                Game.printer(py, px, explode, curses.color_pair(21))
            Game.game_area.refresh()
            await asyncio.sleep(0.1)
        Game.explode_points.clear()  # 清空爆炸碰撞点
        del effects[sub]  # 删除效果

    async def __trg_ivcb(self, pos):
        last_for = 6  # 效果持续6秒
        status = ['invincibility', last_for]
        attrs = self.line.attrs

        def keep(attr):
            attrs['invincibility'] = True  # 多个无敌效果可以叠加
        await self.__hang_fx(status, False, keep, attrs)
        attrs['invincibility'] = False

    async def __trg_stones(self, pos):
        if len(Game.flow_stones) > 0:  # 如果已经有流石就不重复执行
            return True
        status = ['stones', 0]
        map_w, map_h = Game.map_size  # 获得地图大小
        effects = self.line.effects
        sub = time.time()  # 插入的下标
        effects[sub] = status
        devider = random.randint(15, 21)
        sample_size = (map_w*map_h)//devider  # 流石最多有多少
        tick_interval = random.randint(4, 8)*0.1  # 随机生成流石速度(tick控制)
        # 生成流石的坐标
        stone_points = random.sample(Game.map_points, sample_size)
        vx, vy, dx, dy = random.choice((  # 流石速度和方向
            (1, 0, -1, 0),  # (Vx,Vy,x方向,y方向)
            (1, 0, 1, 0),
            (0, 1, 0, -1),
            (0, 1, 0, 1)
        ))
        off_points = {(st[0]-map_w*dx, st[1]-map_h*dy) for st in stone_points}
        stone_appears = False  # 锁定下面的if判断
        while True:  # 流石滚动
            off_points = {(st[0]+vx*dx, st[1]+vy*dy)
                          for st in off_points}  # 偏移点
            Game.flow_stones.clear()
            Game.flow_stones.update(Game.cut_points(off_points))
            # （石头出现过的情况下）地图中没有流石了
            if stone_appears and len(Game.flow_stones) <= 0:
                break
            elif len(Game.flow_stones) > 0:
                stone_appears = True
            await asyncio.sleep(tick_interval)
        Game.flow_stones.clear()  # 清空流石
        del effects[sub]  # 删除效果

    async def __trg_tp(self, pos):
        ava_points = self.ava_points()  # 获得所有可用的点
        attrs = self.line.attrs
        attrs['head_pos'] = random.choice(ava_points)  # 把头随机传送到一个地方
        status = ['teleport', 0]
        await self.__hang_fx(status, True)
