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

现在```start_game()```已经被阻塞了，我们来到了```asyncio_game```方法里。首先我们创建了一个集合```task_list```来储存**待进行的并行任务**。紧接着实例化```Game```类为对象```game```，同时传入```task_list```的引用，以便游戏处理过程中**增加新的任务**。  

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

接下来就进入**游戏计算**部分了，本质上是个```while```循环。  

## 开始游戏运算  

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


