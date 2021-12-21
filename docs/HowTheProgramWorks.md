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

因为```asyncio_game```方法是用```async```定义的，是一个异步函数。调用```asyncio.run(self.asyncio_game())```后，就创建了一个```协程```，并**阻塞当前语句**，而```asyncio_game```函数的语句就在这个协程里面被执行。  

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
