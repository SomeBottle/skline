# 游戏是怎么跑起来的

![troublesome-2021-12-21](https://cdn.jsdelivr.net/gh/cat-note/bottleassets@latest/img/troublesome-2021-12-21.jpg)  

这一节对于整个游戏流程中各模块和类以及方法的协作有了稍微简要一点的讲解（详细的那真的写不完）┑(￣Д ￣)┍  

Ugh...这个描述起来就有点麻烦了，咱尽量说清楚点。

先来到```main.py```主程序：  

```python
from view import MenuView

if __name__ == '__main__':  # 不是作为模块调用
    menu_view = MenuView()
    menu_view.first_page()  # 显示初始页
    menu_view.menu()  # 显示游戏菜单
    print('SomeBottle: Goodbye my friend~')
```

运行```main.py```后的执行情况：

![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/startgame-1.png)  

通过调用```resource.py```模块中的```Res```类的实例的```art_text```方法，获得首屏艺术字，并打印在屏幕上。  

等待1秒后调用```menu```函数进入主菜单界面：

![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/callgraph-menu.png)  

## 进入菜单

调用```menu```函数后首先会初始化一个```current_choice```值，用于记录当前用户选择的```菜单选项```。  

```python
current_choice = 0  # 选择的哪一项
```

随后菜单会进入一个```while```循环，每次先利用```option_maker```来根据```current_choice```值来绘制当前的选项文本，然后打印在屏幕上。

```python
while True:
    choice_session.erase()  # 清除之前的选项显示
    choice_session.addstr(1, 0, self.option_maker(current_choice))
```

这里我使用了```curses```的```window对象.getch()```方法来**捕获用户输入**，默认情况下，如果没有接收到用户的输入，```getch()```函数会一直阻塞循环。

```python
key_input = choice_session.getch()  # 检测用户输入的键
```

当用户按下一个```按键```后，getch()会返回```对应的按键ASCII码供处理```，通过对按键码的判断来更改```current_choice```，从而实现选项的切换。  

```python
if key_input in (ord('w'), ord('W'), curses.KEY_UP):  # 如果用户按下的是上键，选项指针上调
    current_choice = (current_choice-1) if current_choice > 0 else 0
elif key_input in (ord('s'), ord('S'), curses.KEY_DOWN):  # 如果用户按下的是下键，选项指针上调
    current_choice = (current_choice+1) if current_choice < self.last_choice else self.last_choice
```

当接受的```ASCII码```为```Enter```键对应的码时，会跳出循环，继续执行```menu()```下面的语句。在```choice_func```字典中我根据```current_choice```储存了选项对应的函数，由此实现按下回车键后根据用户所选选项执行下面的程序。  

在```menu()```函数内语句即将执行到末尾时，调用一次```del title, choice_session```和```curses.endwin()```来结束当前绘制。

```python
...
self.choice_func = {  # 选项对应的函数
    0: self.start_game,
    1: DifficultyView().show_panel,
    2: RankingView().show_panel,
    3: self.leave
}
...
while True:
    ...
    elif key_input in (10, curses.KEY_ENTER):  # 用户按下了回车，确认选择，跳出循环
        break
del title, choice_session  # 删除窗口
self.tui.clear()  # 清除屏幕
curses.endwin()  # 中止窗口，取消初始化
self.choice_func[current_choice]()  # 执行选项对应的函数
```

在```困难度调整```和```排名表```页面用了差不多的处理方式，都是利用了```while```循环。  

## 利用协程机制开始游戏

接下来我们假定```current_choice=0```，也就是用户选择**开始游戏**。根据字典```choice_func```发现调用的是```start_game```这个方法：  

```python
def start_game(self):  # 开始游戏
    asyncio.run(self.asyncio_game())  # 开启事件循环
    choice_dict = {
        'restart': self.start_game,
        'menu': self.menu
    }
    choice_dict[self.game_end_choice]()  # 执行选项
```

在```start_game```方法里咱紧接着调用了```asyncio```库的方法```asyncio.run()```。这就要讲讲这里发生了什么了：  

因为```asyncio_game```方法是用```async```定义的，是一个异步函数。调用```asyncio.run(self.asyncio_game())```后，就调用了一个```协程```，并**阻塞当前语句**，而```asyncio_game```函数的语句就在这个协程里面被执行。  

```python
def start_game(self):  # 开始游戏
    asyncio.run(self.asyncio_game())  # 开启事件循环
```

------
说到协程，协程其实是一个异步机制，我的理解是协程是一种**协作式的并发执行程序**。举个简单的例子：  

比如我在厨房里要做的事有```用微波炉炸爆米花```，```去烧水```，```打开泡面调料包```。  

如果**不支持并发**的话，我得先```炸爆米花```，**等个```2```分钟**，再```去烧水```，烧水要等```4```分钟，烧完水我接着去```打开泡面调料包```，这一步只需要```30秒```。总体下来我们需要```6分30秒```。（不计算走来走去的时间，就当我会瞬移）  

如果**支持并发**的话，我们先```炸爆米花```，执行炸爆米花后先把这件事抛一边，然后```去烧水```，执行烧水后也把这件事先放一边，去```打开泡面调料包```。这个时候如果引入协程的话：

* 做完```打开泡面调料包```这件事后 -> ```打开泡面调料包```任务完成  
* 回到微波炉前看```炸爆米花```是否完成-> 继续下一步  
* 到烧水壶前看```水是否烧开```-> 继续下一步
* **进行中**任务列表里只有[ ```炸爆米花``` , ```烧水``` ]，下一步回到头部检查```炸爆米花```，如此往返。当任务做完后标记为完成
* 当**没有进行中的任务**时则协程完成运行，停止  

这样下来我们**最少**只需要```4```分钟（几个任务中消耗的最长时间）就能完成这些，这就是协程并发的作用。

------

现在```start_game()```已经被阻塞了，我们来到了```asyncio_game```方法里。首先我们创建了一个集合```task_list```来储存**待进行的并行任务**。紧接着实例化```game.py```模块中的```Game```类为对象```game```，同时传入```task_list```的引用，以便游戏处理过程中**增加新的任务**。  

```python
async def asyncio_game(self):  # 开启并行任务
    task_list = set()
    game = Game(task_list)  # 向实例传入任务列表
```

```Game```类实例化过程中，首先调用```cls_init```初始化了**类属性**，并重新调用```curses.initscr()```初始化了**TUI**界面（因为之前在```menu```末尾调用了```curses.endwin()```撤销了初始化）。接着在读取配置文件后调用```set_color```这个Hook方法设置了几个颜色对，一系列初始化后得到实例对象```game```。

接着先用```asyncio.create_task```将```game.start()```这个协程**封装**为任务Task（```async```修饰的方法可以被理解成为一个协程），然后将这个任务加入到任务列表里。

```python
task_list.add(asyncio.create_task(game.start()))
```

这之后咱使用```asyncio.wait```来**并发执行**```task_list```内的任务（同时引发```asyncio_game```方法暂时阻塞），并用```await```关键字暂时挂起```asyncio_game```方法，等待```task_list```的任务执行完成。  

```python
await asyncio.wait(task_list)
```

现在```task_list```里面只有```game.start()```一个协程任务，执行后我们便进入了游戏主程序。  

## 进入游戏主程序

![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/callgraph-game.png)  

------

首先进行的是倒计时，调用```count_down()```函数。倒计时方法内是个```for```循环，读取```ready```,```3```,```2```,```1```等艺术字，然后传递给```flash_fx()```函数来在屏幕上绘制**随机推拉艺术字**的动画（用的是切片）

```python  
def __count_down(self):  # 游戏开始前的倒计时
    for i in ('ready', '3', '2', '1'):
        self.tui.erase()  # 清理残余界面
        text = Res().art_texts(i)[2]
        self.__flash_fx(text)  # 做个故障风动画
        ...
def __flash_fx(self, content):
    for i in range(5):
        self.tui.erase()
        offset = random.randrange(0, len(content)-1)
        off_content = content[offset::]+content[:offset:] # 使用切片和随机偏移达成动画效果
        self.tui.addstr(1, 5, Res.x_offset(off_content, 5))
        self.tui.refresh()
        time.sleep(0.1)
    self.tui.clear() # 清除界面上的内容
```

每次动画结束后**让艺术字在屏幕中停留一会儿**，其实就是在```count_down```的```for```循环剩下的语句中再打印一遍艺术字：  

```python
self.tui.addstr(1, 5, Res.x_offset(text, 5))
self.tui.refresh()  # 刷新窗口，输出addstr的内容
time.sleep(0.2)  # 主界面
```

每次执行循环语句块都是如此，达成倒计时效果：  

![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/countdown.gif)  

------

完成倒计时后继续执行```start()```中的语句：  

* ```reset_score()``` 重置```Game```类属性```__score```为0  
* ```create_area()``` 根据地图大小创建游戏区域和消息区域，并储存到```Game```类属性中，指定游戏区域**非阻塞**，这样能**持续接受用户的操作且不打断循环**:    

    ```python
    def __create_area(cls):
        map_w, map_h = map(lambda x: x+3, cls.map_size)  # 获得地图大小
        # 根据地图大小创建游戏区域，要比地图大小稍微大一点
        game_area = curses.newwin(map_h, map_w, 1, 1)
        msg_area = curses.newwin(8, 60, map_h+1, 1)
        game_area.keypad(True)  # 支持上下左右等特殊按键
        game_area.nodelay(True)  # 非阻塞，用户没操作游戏要持续进行
        cls.game_area = game_area
        cls.msg_area = msg_area
    ```

* ```create_border()``` 根据地图大小创建**边界点集合**，以便后面绘制：  

    ```python
    def __create_border(cls):  # 创建边界点坐标
        map_w, map_h = map(lambda x: x+1, cls.map_size)  # 获得地图大小
        border_points = set()  # 储存边框的点坐标
        for w in range(map_w+1):
            border_points.update({(w, 0), (w, map_h)})
        for h in range(map_h+1):  # 让竖直方向的边框长一点
            border_points.update({(0, h), (map_w, h)})
        cls.border_points = border_points
    ```

* 将线体类```Line```实例化为对象```line_ins```

* 将上述对象```line_ins```储存到游戏类属性中（后面**触发点实例**能用到）  

* 将触发点类```Trigger```实例化为对象```trg_ins```

```Line```类实例化的时候有生成一个**包含随机位置坐标的线体属性**，这个后面一节再说~  

接下来就进入**游戏计算**部分了，本质上是个```while```循环。  

## 开始游戏主循环  

```python
while True:  # 开始游戏动画
    tick_start = time.time()  # 本次tick开始时间
    self.tui.erase()  # 擦除内容
    self.msg_area.erase()
    self.game_area.erase()  # 擦除游戏区域内容
    line_ins.draw_line()  # 绘制线体
    self.__draw_border()  # 绘制游戏区域边界
    self.__draw_score()  # 绘制分数
    self.__draw_flow_stones()  # 绘制流石
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
```

每次循环开头要对**每个**```curses```窗口进行擦除```erase()```操作，等**所有绘制完成**后再调用窗口的```refresh()```方法输出新增的文本，立即更新屏幕。  

-------

除此之外，循环开头还记录了一下本次运算的开始时间戳```tick_start```，在循环尾部根据```tick_take=time.time()-tick_start```运算出**本次运算消耗的时间**，然后在运算间隔，也就是```tick_interval```上减去```tick_take```。为什么要这样做？这就得讲一下```TPS```了：  

```TPS```全称```Ticks per Second```，也就是每秒运算的次数。在上面的循环运算中，比如我的```TPS=10```，也就是每秒运算```10```次，那么运算一次就要**等待```0.1```秒**再进行下一次循环。

但众所周知，程序运算过程中怎么样都是会消耗时间的，也就是说我们本来运算**已经耗费了一部分时间**，到末尾还要等待```0.1```秒。这样下来最终运算间隔是**大于0.1秒**的。  

为了尽可能**抵消运算所耗费时间**，我们需要在等待时间上**减去运算所需时间```tick_take```**。  

-------

接下来看看**一次运算**中程序做了什么：  

* 调用```line_ins```线体实例的```draw_line()```方法绘制线体：

    ```python
    def draw_line(self):  # 绘制角色
        head_pos = self.attrs['head_pos'] # 从实例属性中取出头部坐标
        body_pos = self.attrs['body_pos'] # 从实例属性中取出尾巴坐标
        head_x, head_y = map(floor, head_pos)  # 解构赋值
        line_body = Game.styles['line']
        for t in body_pos:  # 使用3号颜色对绘制尾部
            Game.printer(t[1], t[0], line_body, Game.color_pair(3))
        # 使用1号颜色对进行头部绘制
        Game.printer(head_y, head_x, line_body, Game.color_pair(1))
    ```

* 调用自身的```draw_border()```方法，根据上面```create_border()```创建的点集合绘制游戏边界  

    ```python
    def __draw_border(self):  # 根据边界点坐标绘制游戏区域边框
        pattern = self.styles['area_border']  # 读取边框样式
        for point in self.border_points:
            x, y = point
            self.printer(y, x, pattern, self.color_pair(2)) # 使用2号颜色对绘制边界
    ```

* 调用自身的```draw_score()```方法，在**消息区域**绘制当前得分：

    ```python
    def __draw_score(self):
        line_ins = self.get_ins('line') # 取出线体实例
        score_text = f'SCORE: {self.__score} ' # 获得游戏分数
        len_text = f'TAIL LEN: {len(line_ins.attrs["body_pos"])}' # 从线体实例属性取出尾巴长度
        self.msg_area.addstr(0, 0, score_text+' / '+len_text) # 绘制  
    ```

* 调用自身的```draw_flow_stones()```方法，在**游戏区域**绘制流石。流石这个点集合是由**另外一个协程**操作的，我们后面再说。  

    ```python
    def __draw_flow_stones(self):  # 绘制流石
        if len(self.flow_stones) <= 0:  # 没有流石就不多费力气
            return False
        flow_stone = self.styles['flow_stone'] # 获得流石的样式
        flow_stone_color = self.styles['flow_stone_color'] # 获得流石的颜色
        self.set_color(22, flow_stone_color)  # 22号颜色对用于流石
        for pt in self.flow_stones: # 遍历坐标打印每个流石
            x, y = pt
            self.printer(y, x, flow_stone, self.color_pair(22))
    ```

* 调用```line_ins```线体实例的```draw_msg()```方法在**消息区域**绘制线体的效果信息（效果是碰到触发点后能得到的）  

    ```python
    def draw_msg(self):  # 绘制线体相关信息，位于游戏区域下方
        line = 1 # 颜色代号计数器
        for fx in self.effects.values(): # 取出所有效果
            color_num = line+40  # 41号往后用于消息颜色
            trg_type = fx[0]  # 该触发点的类型
            trg_style = Game.styles['triggers'][trg_type]  # 获得触发点样式配置
            Game.set_color(color_num, trg_style['color'])  # 用触发点的颜色来打印对应的效果文字
            remain = f' - {fx[1]}s' if fx[1] > 0 else '' # 效果信息分计时器和挂起两种。挂起的就不显示倒计时了，2s后自动撤下
            text = self.fx_dict[trg_type]+remain # 要打印的内容
            Game.msg_area.addstr(line, 0, text, Game.color_pair(color_num))
            line += 1
    ```

* 调用```trg_ins```触发点实例的```check()```方法检查是否有触发点，**没有**就创建触发点，**有的话**就判断线体是否碰撞了触发点。  

    ```python
    def check(self):  # 检查触发点情况
        if len(self.triggers) == 0:  # 没有任何触发点
            map_w, map_h = Game.map_size # 取出地图宽高
            map_area = map_w*map_h  # 地图面积
            max_trigger_num = floor(map_area/300)+1  # 一次生成的最多的触发点数量
            trigger_num = random.randint(1, max_trigger_num) # 本次生成的触发点数量
            for i in range(trigger_num):
                self.make()  # 生成触发点
        else:  # 有触发点就检测碰撞
            # 如果不这样做，在循环过程中对字典进行del操作时会有异常抛出
            trg_items = tuple(self.triggers.items())
            for ind, tg in trg_items:  # 遍历触发点列表
                t_x, t_y = tg['pos']  # 获得触发点坐标
                # 两坐标相减，如果绝对值<1(格)，就说明在同一块区域，碰撞上了
                # 判断水平方向碰撞
                if self.__line.hit(t_x, t_y):
                    trg_type = tg['type']  # 获得触发点类型
                    del self.triggers[ind] # 碰到后就删除这个触发点
                    # 根据触发点效果创建异步协程任务
                    Game.add_task(self.__trg_async(trg_type, (t_x, t_y)))
    ```
------

### 触发点相关的工作  

* **```make```方法**

    在上面代码中，如果没有触发点会调用```trg_ins```自身的```make()```方法创建触发点，我们先来看看这个方法：  

    ```python
    def make(self):  # 做饭...啊不，是随机放置触发点的方法
        ava_points = self.ava_points()
        sub = len(self.triggers)  # 获得点坐标储存下标
        summon_config = Game.game_cfg['triggers']['summon']  # 获得触发点生成比率字典
        chosen_type = Res.ratio_rand(summon_config)  # 使用ratiorand方法来随机生成的类型
        # 生成触发点新出现的坐标
        new_point = {
            "type": chosen_type,
            "pos": random.choice(ava_points)
        }
        self.triggers[sub] = new_point  # 储存创建的新触发点
    ```

    ```make()```方法首先还是会调用一个```trg_ins```自身的方法```ava_points()```，这个方法会返回一个**地图中还可以用的点坐标集合**（具体实现我在后面一节再讲）。  

    随后从配置文件中读出**当前难度**下**各触发点的生成比率```字典```**，调用```resource.py```模块的```Res.ratio_rand```根据比率来**随机选择**当前生成的触发点的**种类**。  

    接着靠着```random.choice()```从**可用点**中随机选择一个点用于**放置触发点**。  

* **碰撞线体后的操作**  

    当**线体碰撞到某个触发点**后，程序把一个新的**协程任务**加入到了```task_list```里：  

    ```python
    Game.add_task(self.__trg_async(trg_type, (t_x, t_y)))

    # add_task是Game的类方法 ↓
    @classmethod
    def add_task(cls, coroutine):
        new_task = asyncio.create_task(coroutine)
        cls.__task_list.add(new_task)
    ```

    这里也是**为什么我要采用并发机制运行游戏**了。在游戏主循环持续进行的情况下，我还要保证触发点这边的运算处理是**持续进行的**。如果不用并发的话势必会影响到游戏主循环，可能会导致阻塞。而采用了协程并发机制，**他们能够互相协作进行运算**，高效率利用资源。  

    在把```__trg_async```这个协程任务加入到```task_list```后，现在任务列表里就有```触发点任务```和```game.start()```这个主循环任务了，他们以协程的形式并发进行。  

    ```__trg_async```方法其实就是个**转接处（接口）**，根据传入的触发点类型```trg_type```来调用不同**效果类的apply方法**来实现**给线体增加效果**。  

    ```python
    async def __trg_async(self, trg_type, pos):  # 触发点异步处理分发
        trg_funcs = {
            'normal': FxNormal, # 值都是效果的类
            'bonus': FxBonus,
            'accelerate': FxAclrt,
            'decelerate': FxDclrt,
            'myopia': FxMyopia,
            'bomb': FxBomb,
            'invincibility': FxIvcb,
            'stones': FxStones,
            'teleport': FxTlpt
        }
        # 应用效果，传递(触发点种类,位置,Trigger实例)
        await trg_funcs[trg_type](trg_type, pos, self).apply() # 实例化效果类并调用对象的apply()方法
    ```

    这些效果类由基类```FxBase```派生得到，这样写是为了方便维护，同时所有效果类都能调用到```hang_fx```（线体效果消息处理）这个方法：  

    ```python
    async def hang_fx(self, status, pop=False, extra_func=False, *args):
        effects = self.line.effects
        sub = time.time()  # 插入的下标
        # status储存着[效果名,持续时间]的引用
        effects[sub] = status # 将效果附加到effects里，这些效果会由上面的line_ins.draw_msg()打印出来
        last_for, minus = (status[1], 1) if not pop else (2, 0) # pop=True代表是弹出模式的消息，只显示两秒就被撤掉
        for i in range(last_for):  # 持续last_for秒
            status[1] -= minus # 倒计时
            if extra_func:
                extra_func(*args) # 如果有额外函数，就执行额外的函数
            await asyncio.sleep(1)
        del effects[sub]  # 删除效果
    ```

    比如**线体碰到了触发点**，这个触发点的类型是```myopia```，通过```__trg_async```会调用```FxMyopia```类实例对象的```apply()```方法：  

    ```python
    class FxMyopia(FxBase):  # 近视点效果
        async def apply(self):
            name = self.trg_type # 取出触发点（效果）类型
            last_for_cfg = self.last_for_cfg # 得到效果持续时间的配置
            last_for = last_for_cfg[name] # 取出该效果持续的时间
            status = [name, last_for] # 创建status，用于消息
            Game.update_myopia_sight()  # 触发近视点的时候更新一次视野区域
            Game.add_score()  # 加分

            def keep():
                Game.myopia(True)  # 开启近视
            await self.hang_fx(status, False, keep) # 挂起消息的同时调用keep方法，保持多个近视效果的时长能同时起效
            Game.myopia(False) # hang_fx执行完毕，关闭近视
    ```

    可以说```apply()```是**所有效果类**的一个接口，通过调用```apply```能开始对于**线体对应效果**的运算。  

    在```hang_fx```计算消息倒计时时会暂时挂起来当前协程，让```task_list```中其他协程继续执行。这里就有必要再说说```asyncio```的调度了：  

* **利用```asyncio```进行协程调度**  

    协程之所以是一种**并发机制**，归功于**其中的互相调度**。  

    之前```view.py```模块的中```asyncio_game()```方法通过把```game.start()```协程任务加入任务列表```task_list```中并发运行来启动游戏程序。  

    在上面的触发点碰撞处理中程序也将```__trg_async```方法加入到了```task_list```中执行。  

    ```game.start()```和```__trg_async```都被```async```关键字定义，是异步函数，返回的是```协程```。  

    很容易能注意到，除了```async```，还有个常见的关键字是```await```。```await```起的就是挂起协程的作用。  

    游戏主循环每次运算完毕后会有一条语句```await asyncio.sleep(等待时间)```，这个时候```game.start()```会在**这里暂时被挂起**，**不再往下**进行，让出控制权。```asyncio```便会自动调度，运行下一个**没有被挂起的任务**。  

    ```python
    await asyncio.sleep(tick_interval-tick_take)
    ```

    而此时```__trg_async```正好在任务列表里，是**待执行任务**，此时asyncio便会执行```__trg_async```。  

    接着```__trg_async```被调用，进而调用**效果类实例的异步方法```apply()```**时，又会使用到```await```，代表```__trg_async```也被暂时挂起，等待```apply()```方法**异步**执行完毕，让出控制权。  

    ```__trg_async```在任务列表```task_list```里被挂起后，asyncio又会继续调度，```game.start()```里的```asyncio.sleep()```执行完毕后就会**取消挂起**，继续执行```game.start()```剩余的语句。如此往返，任务列表```task_list```里的协程任务互相调度实现程序并发进行。  

------

接着说```game.start()```主循环里的语句：  

* 调用```trg_ins```触发点实例的```draw()```方法来绘制```make()```创建的触发点。

    ```python
    def draw(self):  # 输出触发点和相关信息
        for key, tg in self.triggers.items(): # 遍历触发点
            trg_type = tg['type']  # 该触发点的类型
            trg_style = Game.styles['triggers'][trg_type]  # 获得对应的样式配置
            color_num = key+30 # 颜色代号
            Game.set_color(color_num, trg_style['color'])  # 30号往后颜色对用于触发点
            x, y = tg['pos'] # 获得触发点坐标
            Game.printer(y, x, trg_style['pattern'],Game.color_pair(color_num)) #绘制触发点
    ```  

至此主循环中的绘制部分就进行完毕了，通过窗口的```refresh()```方法将绘制的内容**输出到屏幕中**。  

在这之后：  

* 调用```line_ins```的```move()```方法来计算线体的移动后位置，这个有点复杂，咱就放在后面一节说了...  

* 调用```line_ins```的```control()```方法来接收用户控制，主要原理还是利用了```curses```窗口的```getch()```方法（在之前我们已经设定```game_area.nodelay(True)```，也就是```game_area.getch()```不阻塞）：  

    ```python
    def control(self):
        attrs = self.attrs  # 获得角色（线体）属性
        vx, vy = attrs['velo']  # 解构赋值x,y速度
        dx, dy = attrs['direction']  # 解构赋值x,y的方向
        recv = Game.game_area.getch()  # 获取用户按键，不阻塞
        ctrls = { # 控制相关的按键ASCII码值
            'L': (ord('a'), ord('A'), curses.KEY_LEFT),
            'R': (ord('d'), ord('D'), curses.KEY_RIGHT),
            'U': (ord('w'), ord('W'), curses.KEY_UP),
            'D': (ord('s'), ord('S'), curses.KEY_DOWN)
        }
        if recv in ctrls['L']+ctrls['R']: # 按下左右键
            # 如果vx为0就调换一下两个速度，让速度沿x方向
            vx, vy = (vy, vx) if vx <= 0 else (vx, vy)
        elif recv in ctrls['U']+ctrls['D']: # 按下上下键
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
        self.attrs['velo'] = (vx, vy) # 移动速度
        self.attrs['direction'] = (dx, dy) # 移动速度的方向
    ```

* 最后调用```line_ins```的```impact()```方法来判断是否有**致命碰撞**发生，如果发生了就break，**跳出游戏主循环导致游戏结束**。  

    ```python
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

    # 游戏主循环中↓
    if line_ins.impact():  # 判断是否有碰撞
        break
    ```

当线体触发了[**局终条件**](https://github.com/SomeBottle/skline#%E6%B8%B8%E6%88%8F%E6%9C%BA%E5%88%B6-%E5%B1%80%E7%BB%88%E5%88%A4%E5%AE%9A)，就会跳出循环，进行收尾工作。  

## 游戏主循环结束  

跳出循环后首先迎来的是```curses.flash()```，让线体死亡时画面闪烁一下：  

![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/gameover-hitborder.gif)  

死亡后让画面**凝固2秒**，也就是```await```一下```asyncio.sleep(2)```。  

等待2秒后执行结束游戏的程序```game.over()```： 

* 实例化```resource.py```模块中的```Res```类为对象```res_ins```，以备使用。  

* 调用```cancel_tasks()```取消```task_list```中正在进行的并行任务（很有意思的是，当前程序**也是运行在任务列表中**的，但并不会被取消，我暂且当这个是个特性了）：

    ```python
    def __cancel_tasks(self):  # 取消所有并行任务
        for task in self.__task_list:
            task.cancel()
    ```
* 擦除```curses```窗口的内容，调用```tui.erase()```和```game_area.erase()```  

* 接下来绘制游戏结束的界面，其中调用了```calc_score()```方法来计算总分：  

    ```python
     text_h, text_w, over_text = res_ins.art_texts(
            'gameover')  # 获得艺术字GAME OVER
    self.tui.addstr(1, 1, Res.x_offset(over_text, 1))
    self.msg_area.mvwin(text_h+1, 1)  # 移动一下msg区的位置
    pattern1 = '{:#^' + str(text_w) + '}' # 标题格式化模式
    pattern2 = '{: ^' + str(text_w) + '}' # 成绩栏格式化模式
    result_text = pattern1.format(' R E S U L T ')
    score, tail_len, total = map(str, self.__calc_score()) # 得出各分数
    total_score = float(total)  # 总成绩（浮点数）
    score_item = pattern2.format('SCORE: ' + score)
    tail_item = pattern2.format('TAIL LENGTH: '+tail_len)
    total_item = pattern2.format('TOTAL SCORE: '+total)
    score_text = score_item+'\n'+tail_item+'\n'+total_item
    self.msg_area.addstr(0, 0, result_text)
    self.msg_area.addstr(1, 0, score_text)
    self.msg_area.addstr(
        5, 0, 'Type: \n(R) to Replay the Game\n(B) to Return to Menu')
    self.tui.refresh()
    self.msg_area.refresh()
    ```

* 调用```res_ins.set_ranking```将总分```total_score```计入排名

* 然后就是我的老办法了，用一个循环来等待用户输入：  

    ```python
    self.msg_area.nodelay(False)  # 阻塞接受getch
    while True:
        recv = self.msg_area.getch() # 获得用户输入
        if recv in (ord('r'), ord('R')):  # 按下R/r键
            choice = 'restart' # 操作是重启一局游戏
            break
        elif recv in (ord('b'), ord('B')):  # 按下B/b键
            choice = 'menu' # 操作是回到菜单
            break
    ```

* 用户按下指定按键后会跳出循环，接着程序调用```del_area()```删除游戏区域：

    ```python
    @classmethod
    def __del_area(cls):
        del cls.game_area, cls.msg_area
    ```

* 紧接着**撤销**```curses```窗口初始化：```curses.endwin()```  

## 处理游戏结束后用户的选项

* 最后我们把用户最后选择的选项值```choice```传出去，怎么传出去呢？其实把```choice```动态添加到```game```实例的属性里就行了：  

    ```python
    self.end_choice = choice  # 传值出去
    ```

至此，```game.over()```方法执行完毕，```game.over()```方法是```game.start()```方法最后一个调用，所以这也意味着```game.start()```执行完毕。  

回到```view.py```模块里异步函数```asyncio_game```，自从```await asyncio.wait(task_list)```后一直其一直被挂起。现在```task_list```中最后一个任务```game.start()```执行完毕了，```asyncio_game```继续执行下面的代码：  

```python
async def asyncio_game(self):  
    task_list = set()
    game = Game(task_list)  
    task_list.add(asyncio.create_task(game.start()))
    await asyncio.wait(task_list)
    print('Concurrent tasks were completed.') # 从这里开始继续执行
    self.game_end_choice = game.end_choice
```

因为我们刚刚把```choice```加到```game```对象上作为属性```end_choice```传出来了，我们把```end_choice```再次取出来，作为```menu```对象的属性```game_end_choice```：

```python
self.game_end_choice = game.end_choice  # 把游戏结束后的值传出去
```

这个时候```asyncio_game()```也就执行完毕了。回到```start_game()```，自从**开启事件循环**后```start_game()```的执行一直被阻塞，直至**事件循环停止**。现在```asyncio_game()```执行结束，事件循环停止，于是```start_game()```接着执行接下来的代码：  

```python
def start_game(self):  
    asyncio.run(self.asyncio_game())  
    choice_dict = { # 从这里开始继续执行
        'restart': self.start_game,
        'menu': self.menu
    }
    choice_dict[self.game_end_choice]()  
```

根据```game_end_choice```，调用不同的方法来**重开游戏**或者**回到菜单**。  

之所以要传这么多层出来，是为了**让当前的```asyncio```事件循环停止**，这样才能重开事件循环进行新一轮的游戏。

至此就是整个游戏的运行过程...哇，我都不敢说自己讲清楚了，待我喝口水再写下一节...

![exhausted-2021-12-22](https://cdn.jsdelivr.net/gh/cat-note/bottleassets@latest/img/exhausted-2021-12-22.jpg)  



