# 算法&设计

![unruly-2021-12-22](https://cdn.jsdelivr.net/gh/cat-note/bottleassets@latest/img/unruly-2021-12-22.jpg)

说到计算机程序，我们肯定会谈到算法，算法决定了一个程序怎么去完成需求。咱这个破游戏当然也不意外，这一节我准备**写几个游戏里比较重要的算法设计**。

这一节我准备**分模块**来写...

## 前言  

本游戏赖以的**TUI**库```curses```的坐标系统由于历史原因是有点反直觉的：  

在```addstr()```，```newwin()```等有坐标参数的方法中，形参```y```坐标总是在```x```坐标的前面，所以传入的时候是```(y,x)```这样的形式。  

还有一点，```x```轴的**正方向**是```水平向右```，这点和我们接触的二维坐标系是一致的。但是```y```轴的**正方向**是```竖直向下```！

## resource.py  

* **```x_offset```方法**  

    x_offset方法是搭配```curses```窗口的```addstr```使用的，用于处理字符串的偏移。  

    为什么需要这个方法呢？
    
    比如说我有个带换行符的字符串```string='1\n2\n3\n4\n5\n6'```，我们把这个字符串打印在屏幕上：

    ```python
    screen.addstr(1,0,string) # 在y=1,x=0的地方打印
    ```

    效果：  

    ```
    1
    2
    3
    4
    5
    6
    ```

    这样是没有任何问题，但我们给```addstr()```指定一个**水平方向上的偏移**呢？

    ```python
    screen.addstr(1,2,string) # 在y=1,x=2的地方打印
    ```

    效果： 

    ```
      1
    2
    3
    4
    5
    6
    ```  

    问题出现了，除了第一行有了偏移，其他行是不受影响的。为了**让所有行拥有相同的偏移**，我专门写了这个```x_offset```偏移方法：  

    ```python
    @staticmethod  # 作为一个静态方法
    def x_offset(string, offset):
        '''搭配addstr，处理字符串的偏移。如果只用addstr的x-offset的话就第一行有偏移，其他行都是一个样，这个方法将字符串除第一行之外所有行头部都加上offset空格'''
        lines = string.splitlines(keepends=True)
        first_line = lines.pop(0)  # 除了第一行
        # Python竟然有这么方便的方法，可以直接按行分割，太棒了。keepends=True，每行保留换行符
        # 除了第一行每一行都加上偏移
        return first_line+''.join(map(lambda x: offset*' '+x, lines))
    ```

    原理其实很简单，先把第一行单独提取出来赋值给```first_line```（不做处理），然后使用```map```将匿名函数```lambda x: offset*' '+x```映射到字符串剩下的```行```中，最后将```first_line```和可迭代```map```对象重新连接成字符串返回。

    其中```offset```是偏移的量，```offset*' '```则是在每行字符串前**加上对应长度的空白符**。这样就能完美解决这个问题了：  

    ```python
    screen.addstr(1,2,Res.x_offset(string,2)) # 在y=1,x=2的地方打印
    ```

    效果：

    ```
      1
      2
      3
      4
      5
      6
    ``` 

* **```rgb```方法**  

    最开始我调用```curses.init_color```来初始化颜色，传入了个```0-255```的RGB颜色值，结果在绘制的时候无论我怎么用亮色，展现出来的颜色是**非常昏暗的**。  

    后来去查了一下才知道，也是因为历史问题，```curses```支持的颜色是```0-1000```的。要解决这个问题其实很简单，按比例换算一下就行了：  

    ```python
    @staticmethod
    def rgb(color): # 传入元组(R,G,B)
        ratio = 255/1000
        return map(lambda x: floor(x/ratio), color)
    ```

    RGB三个分量的**比例**是```255:1000```，仍然是用```map```函数，将```color```元组的每个分量按比例转换成**千制RGB**，这个方法会返回一个```map```对象。按需求来说只能使用一次的```map```对象是完全足够了。  

* **```ratio_rand```方法**  

    这个方法主要是为了按比率随机抽取一个键，用于**随机抽取触发点类型**。  

    ```python
    @staticmethod
    def ratio_rand(dic):
        pointer = 1  # 指针从1开始
        luck = random.randint(1, 1000)  # 从1到1000中选
        choice = False
        for k, v in dic.items():
            cover = v*1000  # 找出该比率在1000中占的份额
            # 划分区域，像抽奖转盘一样
            if luck >= pointer and luck <= (pointer+cover-1):
                choice = k
                break
            pointer += cover
        return choice
    ```

    传入函数的参数是一个字典，这个字典的键值对中，键是**待选项**，而键对应的值是一个**比率**，比如：  

    ```python
    rand_dict={
        'choice1':0.3, # choice1被抽出的概率是30%
        'choice2':0.5, # choice2被抽出的概率是50%
        'choice3':0.2 # choice3被抽出的概率是20%
    }
    ```

    这个抽取的算法其实很简单，思路就是我们**平常在商场里看到的抽奖转盘**：  

    ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/lottery.jpg)  

    只不过我们这里是在```1-1000```范围中根据比率来分配罢了，拿```rand_dict```为例，我们把```1-1000```划为三个区域：  

    ```1-300```，```301-800```,```801-1000```  

    然后从```1-1000```中随机抽取一个数，看**落在哪个区域**。  

    这个方法里就是先抽取出了一个```1-1000```范围中的随机数，然后在找落在哪个区域里，最后**返回这个区域对应的键**。  

    因为抽数范围是```1-1000```，所以比率是支持**小数点后```3```位的**！

    值得注意的是**所有的比率加起来要为```1```**，不然可能会返回```False```。  


## view.py  

老实说这个模块没有很多值得说说的算法和设计，我就写一下```RankingView```类实例的```show_panel()```方法里的分页吧。  

```python
def show_panel(self):
    rank_list = Res().get_ranking()['rank_list']
    title, choice_session = self.create_win(Res().art_texts('ranking'))
    chunked = []
    each_chunk = 6
    for i in range(0, len(rank_list), each_chunk):
        the_chunk = rank_list[i:i+each_chunk]
        chunked.append(the_chunk)  # 分片
    ...
    current_page = 0
    max_page = len(chunked)-1
```

首先获得整张排名表```rank_list```，这是一个二维列表，列表中的每一项形如```[排名登记时间,总分]```，整个列表已经按**降序**排列。  

我设定每页展示```6```项，也就是```each_chunk=6```。接下来就需要把这么多项**以6个一组**分成多片(页)。  

于是我们以列表长度为```range```尾部、以```0```为range开头、以```each_chunk```为步，对这样的```range```进行遍历。然后采用**列表分片**，以```i```为开始下标，以```i+each_chunk```为结束下标，从```rank_list```中切出一片储存到```chunked```列表中。  

遍历完成后，```chunked```列表中有几个元素，就代表有几页，即```max_page=len(chunked)-1```

之后进入Ranking界面主循环，程序会调用```list_maker```方法根据当前块```current_chunk```和开始的位置```start_place```生成待绘制的排名单，然后打印在屏幕上。  

当前块其实就是以**标记当前页码的变量```current_page```**为下标，从```chunked```中取出对应**分片(页)**。```start_page```标记**当前块首个排名项**在```rank_list```中下标开始的地方。  

在```list_maker()```中，在```start_page+1```的基础上再加上**当前项目在当前分片中的下标**，就是当前的排名了：  

```python
def list_maker(self, chunk, start=0):
    list_str = 'PLACE             TIME             SCORE\n'
    for key, item in enumerate(chunk):
        place = start+key+1
        date, score = item
        list_str += f'{place}        {date}        {score}\n'
    list_str += '\nPress (D) for Next Page, (A) for Prev Page'
    return list_str
```

比如我```current_page=1```，代表是第二页（第一页下标为0），分页总共有```5```页(下标```0-4```)，  

那么当前分页中**有```each_chunk=6```项**，下标是```0-5```，其中下标为```0```的项在```rank_list```中开始的下标是```current_page*each_chunk=6```，但我们知道，这其实是第```7```项！  

于是在```list_maker```处理**当前分页**时，当前页面显示的第一项是第```start+1+key=6+1+0=7```名，第二项则是第```8```名，第三项就是第```9```名...  

总的来说，这个分页的原理还是很简单的ヽ(✿ﾟ▽ﾟ)ノ。  

## game.py

![002-2021-12-22](https://cdn.jsdelivr.net/gh/cat-note/bottleassets@latest/img/002-2021-12-22.png)

哎嘛，这节要讲的东西可就有点多了！  

* **基本思想：点集合和坐标**  

    可以说下面的算法和设计多多少少都是围绕着**点集合**和**坐标**展开的。  

    这里写几个基本的**点集合**:  

    * **```Game.border_points```**  

        储存所有的边界绘制点，在```Game.__create_border()```中被初始化：  

        ```python
        @classmethod
        def __create_border(cls):  # 创建边界点坐标
            map_w, map_h = map(lambda x: x+1, cls.map_size)  # 获得处理过的地图宽高
            border_points = set()  # 储存边框的点坐标
            for w in range(map_w+1):
                border_points.update({(w, 0), (w, map_h)})
            for h in range(map_h+1):  # 让竖直方向的边框长一点
                border_points.update({(0, h), (map_w, h)})
            cls.border_points = border_points
        ```

        初始化的时候首先取出了记录了地图宽高的元组```map_size```，然后在```map()```函数映射处理宽高共同```+1```后把宽高各加一赋值给```map_w```，```map_h```。  

        边框点是从```(0,0)```绘制到```(map_w,map_h)```的。我利用了两次```for```循环来实现这个过程，第一次保持纵坐标不变，改变横坐标从```0```到```map_w```：  

        ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/create_border-1.png)  

        第二次则保持横坐标不变，改变纵坐标从```0```到```map_h```：

        ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/create_border-2.png)  

        最终形成的点如下，留出了**原本的地图区域**：

        ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/create_border-3.png)  

    * **```Game.map_points```**  

        储存地图中的所有坐标，在```Game.__cls_init()```中被初始化，可以说是所有游戏中**点处理**的基础。  

        ```python
        map_w, map_h = map_size # 获得真正的地图宽高
        # 根据地图大小生成所有的坐标
        cls.map_points = {(xi, yi) for xi in range(1, map_w+1) for yi in range(1, map_h+1)}
        ```

        ```map_points```点集合的生成我直接用了个**集合推导式**，```x```坐标从```1```到```map_w```，```y```坐标从```1```到```map_h```。  

        生成的```map_points```点集合表示的就是上面```border_points```**示例图**中绿色标出来的区域。

    * **```Game.explode_points```**

        **临时储存**爆炸，**代表爆炸时的爆炸范围**的点集合，由效果类```FxBomb```的```apply()```方法控制，用于和**线体**产生交互。  

    * **```Game.__sight_points```**  

        储存**近视模式**下的点集合，代表角色近视时**能看到的区域（也就是视野）**，这和近视(```Myopia```)效果的处理**息息相关**，后面会细说。  

    * **```Game.flow_stones```**

        储存地图中的**流石**点集合，代表地图中**流石**的位置，由效果类```FxStones```的```apply()```方法控制，用于和**线体**产生交互。  

* **线体移动**

    线体移动靠的是每次**游戏主循环**调用```Line```类实例的```move()```方法来实现。对于线体运动方向的控制我采用了两个元组：  
    ```速度(水平方向速度大小,竖直方向速度大小)```，```方向(水平方向速度方向,竖直方向速度方向)```

    看看```move()```里我是怎样处理的就知道咱为什么这样设计了：  

    ```python
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
            Game.update_myopia_sight()  # 在蛇体移动一格的情况下更新近视情况下的区域
            if body_len > 0:  # 身体长度大于0再进行处理
                body_pos = body_pos[1::]
                body_pos.append((prev_x, prev_y))
                attrs['body_pos'] = body_pos
    ```  

    从上面我们已经知道，地图大小```map_w```,```map_h```对应的也是最大坐标```max_x```和```max_y```。  

    接着我们取出头部坐标```head_pos```和速度```velo```以及方向```direction```，解构赋值给几个变量：  

    * 头部坐标 - ```x```，```y```  
    * 水平/竖直速度大小 - ```vx```，```vy```  
    * 水平/竖直速度方向 - ```dx```，```dy```  

    接下来是一坨三元运算，没错，线体的**移动计算**这两句就可以解决了：  

    ```python
    x = x + (vx*dx) if x >= 1 and x < max_x + 1 else (max_x if dx < 0 else 1)  
    y = y + (vy*dy) if y >= 1 and y < max_y + 1 else (max_y if dy < 0 else 1)  
    ```

    * ```vx```和```vy```的取值是```0-1```，```dx```和```dy```的取值是```(-1,1)``` 

    * 其中```dx```,```dy```的值为```1```代表沿**正方向**运动，为```-1```代表沿**反方向**运动 

    * ```vx```,```vy```速度的单位是```格/tick```，是大于```0```小于等于```1```的浮点数。 

    这样只需要```vx*dx```,```vy*dy```就能控制**水平和竖直的速度方向了**
    
    因为每次执行循环语句就相当于一```tick```（一次运算），就会调用一次```move()```——  

    ——所以每次我只需要在```move()```中对```x```和```y```加上**每tick**的位移就可以了，每tick的位移：```Δx=vx*dx*1```和```Δy=vy*dy*1```，其实就是```vx*dx```和```vy*dy```  

    到这里你可能想问了，方向完全没必要用```dx```,```dy```两个值来确定啊！其实我在最开始设计游戏的时候考虑到线体**斜向运动**的可能性，所以这样设计了，直至整个课设完成，我仍然保留了这种表达方式，如果以后要修改的话更具灵活性~    

    -------

    所以...为什么**要用三元运算**呢？

    我设计的默认情况下线体是可以**穿墙的**，这样能给后面**无敌效果**的处理提供很大便利。而这里的三元运算就是为了解决穿墙的问题的：

    * 首先明确一点，这里头部的```x```和```y```坐标是分开处理的  

    * 先判断```x >= 1 and x < max_x + 1```和```y >= 1 and y < max_y + 1```，也就是判断**线体在不在地图区域里**(下面这张图的绿色标记区域)  

        ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/create_border-3.png)  

    * 如果**超出了**地图区域则转向```else```后面的语句处理  

    * 假如```x```坐标超出地图区域：```(max_x if dx < 0 else 1)```，表示  
    如果```dx<0```，也就是说是往**水平负方向**运动，**是超出地图左边区域了！**。要达到穿墙效果，就把线体传送到最右边，也就是```x=max_x```。  
    如果```dx>0```，也就是说是往**水平正方向**运动，**是超出地图右边区域了！**。要达到穿墙效果，就把线体传送到最左边，也就是```x=1```。  
    (地图区域中```x```坐标的范围是```1```到```max_x```)

    * 假如```y```坐标超出地图区域，处理方法和```x```是一模一样的。  
    (地图区域中```y```坐标的范围是```1```到```max_y```)

    -------

    搞清楚是怎么穿墙之后，你可能又会疑问判断**在地图区域内**为什么用的是诸如```x >= 1 and x < max_x + 1```这种**半闭半开**，末尾```max_x+1```的写法呢？  

    这其实和上面所述的**移动计算**息息相关，```x```虽然取值是```1```到```map_x```，但从**头部的移动**来讲并不仅仅是这样。可以看一下绘制头部的部分：  

    ```python
    def draw_line(self):  # 绘制角色
        head_pos = self.attrs['head_pos']
        body_pos = self.attrs['body_pos']
        head_x, head_y = map(floor, head_pos)  # 解构赋值
        ...
        # 使用1号颜色对进行头部绘制
        Game.printer(head_y, head_x, line_body, Game.color_pair(1))
    ```

    很容易发现**在绘制的时候**，取出的头部坐标是**经过了```floor```向下取整**的，因为**头部坐标**实际上是**浮点数**。  

    每tick(每次运算)都会往头部坐标上添加**每tick对应的位移**，但是**tick**间隔的时间是很短的（假如```TPS=10```，tick(运算)间隔就是```0.1```秒），如果每**tick**都加的是整数，那**线体**未免跑得太快了！这也是为什么```vx```与```vy```是大于```0```小于等于```1```的浮点数。  

    这点光说可能不太能讲清楚，通过一张表能大概表示这个意思，
    
    **下面的部分拿```水平方向x坐标```举例：**   

    （假如速度是```0.1格/tick```）

    |运算(tick)序号|**头部```x```坐标**|**floor取整后头部```x```坐标**|
    |:---:|:---:|:---:|
    |0|1.0|1|
    |1|1.1|1|
    |2|1.2|1|
    |3|1.3|1|
    |4|1.4|1|
    |5|1.5|1|
    |6|1.6|1|
    |7|1.7|1|
    |8|1.8|1|
    |9|1.9|1|
    |10|2.0|2|
    |11|2.1|2|

    用于**打印头部位置**的坐标是**floor取整后头部```x```坐标**。也就是在游戏中我们看到线头**运动一格**时，其实按上面这种情况，已经运算了```10ticks```了！  

    ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/x-crosswall.gif)  

    正因为**向下取整**，我需要把判断条件写成```x >= 1 and x < max_x + 1```这样：  

    * ```x```在大于等于```1```和小于```2```的区间内，头部在游戏中显示都是在坐标```x=1```这一格，```x=1```是**封底**的坐标值。  

    封底```x>=1```没有问题了，如果我把封顶写成```x<=max_x```呢？ 

    * 从**上面的动图**可以看出来，```x```在大于等于```15```小于```16```的区间内，头部在游戏中显示都是在坐标```x=15```这一格，**并没有穿过墙**！  
   
   * ```max_x=15```，如果我写成```x<=max_x```，当```x=15```的时候就被传送到```x=1```的地方了，导致游戏中显示**线体头部**只在```x=15```处停留了```1tick```就被快速传送了，实际上根本没碰到墙，展现出来的问题是这个样的：  

        ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/x-suddenly-crosswall.gif)    

    * 写成```x < max_x+1```的话，当头部```x```处于大于等于```15```小于```16```的区间时就不会**被提前传送**了，而当```x```坐标达到```16```时就**立马传送**到```x=1```处。  
    这样游戏中就能正常显示**线体头部**在```x=15```处停留了```10tick```，然后再穿墙到```x=1```处

    对于竖直方向上```y```坐标的判断同样是```y >= 1 and y < max_y + 1```，原理一致。

    ---------

    上面讲的都是**头部的运动**，接下来讲讲**尾巴**！  

    尾巴要做的事其实挺简单，就是跟着**头部**运动。我将尾巴**按每一节的坐标**```(x,y)```放在一个列表中。  

    为了使操作的步骤最少，我设计把**离头部最近的一节**放在**列表末尾**，**离头部最远的一节**放在**列表头部**，为什么这么做呢？下面来看看代码  

    ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/tail_list_fixed.png)  

    ```python
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
        body_pos = attrs['body_pos']  # 获得尾巴列表
        body_len = len(body_pos) # 获得尾巴长度
        if not (floor(x) == prev_x and floor(y) == prev_y):
            Game.update_myopia_sight()  # 在蛇体移动一格的情况下更新近视情况下的区域
            if body_len > 0:  # 身体长度大于0再进行处理
                body_pos = body_pos[1::]
                body_pos.append((prev_x, prev_y))
                attrs['body_pos'] = body_pos
    ```

    * 首先先获取**本次运算对头部坐标进行处理前（也就是上一个tick）** 的头部坐标```prev_x```和```prev_y```，注意这里进行了**向下取整**，和游戏显示是一样的处理！

    * 获取尾部坐标列表```attrs['body_pos]```备用
    
    * 待**本次运算（这一个tick）对头部坐标进行处理后**，拿到**当前的头部坐标**```x```和```y```，然后对其进行**向下取整**  

    * 将向下取整后的```x```和```y```与```prev_x```和```prev_y```进行**分别**对比，如果**任意一组**不相等，说明**头部在屏幕上显示的位置改变了！**  

    * 头部在屏幕上显示的位置改变后就应该**让尾巴跟进**了（不过前提也是```body_len>0```，要先有尾巴）  

    * 我利用列表的切片方法，把**离头部最远的坐标去除**（切片从下标1开始取）。然后把```(prev_x,prev_y)```，也就是头部**之前在屏幕上显示的坐标**，```append```到列表```body_pos```的尾部，然后更新原来的列表```attrs['body_pos']```，尾巴跟随就完成了！  

    形象地用动图展示这个过程：

    ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/tail-movement.gif) 

    其中我使用了列表的```append```方法，把新的对象直接加到**列表末尾**，这个操作的时间复杂度是```O(1)```，也就是立刻完成，非常高效。这也是为什么我要把**离头部最远的一节**放在**列表头部**！  

    至此线体的运动算法咱就写完了~ 

* **线体初始化**

    线体初始化主要做的事是随机生成了线体的```初始行进速度方向```和```初始位置```。  

    ```python
    def __init__(self) -> None:
        self.__map_w, self.__map_h = Game.map_size  # 解构赋值地图长宽
        # 注意，防止生成在边缘，不然开局就G了！
        # 把生成区域x,y从地图区域往内各缩3格，防止生成在边缘
        ava_points = [(xi, yi) for xi in range(4, self.__map_w-2)
                      for yi in range(4, self.__map_h-2)]
        init_velo = Game.game_cfg['init_velo']  # 从配置中取出初始速度
        self.attrs = {  # 线体属性
            'head_pos': random.choice(ava_points),  # 生成随机的头部坐标
            # 头部的运动速度(Vx,Vy)，单位：格数/tick，最开始要不沿x轴，要不沿y轴运动
            'velo': random.choice(((init_velo, 0), (0, init_velo))),
            # 运动方向(x,y)，-1代表负向。向右为X轴正方向，向下为Y轴正方向
            'direction': (random.choice((1, -1)), random.choice((1, -1))),
            'body_pos': [],  # 身体各节的位置
            'invincibility': False,  # 是否无敌
            'myopia': False  # 是否近视
        }
        ...
    ```

    从代码可以看出来，初始速度和方向直接用的```random.choice```方法从元组里选。
    
    初始速度要不沿水平方向```(v,0)```，要不沿竖直方向```(0,v)```；而方向则要不沿当前方向的正方向```1```，要不沿着反方向```-1```。  

    值得一说的是可用点集合```ava_points```，用于抽取**初始头部位置**。  

    同样是用推导式，不过这里用的是**列表推导式**，因为```random.choice```是针对**列表或元组**进行选择的。其实也可以写成集合推导式，只不过需要用到另一个方法```random.sample```了，这个方法的**效率相较比较低**，就不考虑了。  

    ```ava_points```推导式里我把**可用点的范围往内缩进了3格**：从```(1,map_w+1)```改成```(4,map_w-2)```，这样防止最开始**头部生成在边缘**，开局即游戏结束肯定是不行的啦！  

    最后用```random.choice```从```ava_points```里随机选择一个**可用点**，附到线体属性里作为线体头部初始位置。  

* **线体的致命碰撞**

    在```Line```类的实例方法里专门有一个```impact()```来判断**线体头部**是否**受到致命碰撞**，在游戏主循环里每次```tick```(运算)都会**调用一次**：  

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
    ```

    在```impact()```函数的开头有个**无敌模式(Invincibility)**的判断，如果无敌就直接返回```False```，代表忽略一切致命撞击。  

    **碰撞**这件事是反映在**游戏界面**上，被用户所看到的。所以我们判断也要按**游戏界面的处理方式**——对**头部坐标向下取整**，得到一个点坐标```(floor(x), floor(y))```

    除开无敌模式，撞击判定我分为了四部分：  

    * **撞到墙壁**：

        处理这一部分我写了两个逻辑表达式进行判断：  

        ```python
        judge_border_x = x >= 1 and x < max_x+1
        judge_border_y = y >= 1 and y < max_y+1
        ```

        原理其实和上面**线体移动**一节的穿墙判断是一致的，这里就不多赘述。  

        当```judge_border_x```和```judge_border_y```的其中一个逻辑值不为真，就代表碰到墙壁了！  

    * **撞到自己尾巴**，**被炸弹炸到**，**被流石砸到**

        这三个判断的方式都是非常类似的，都是点判断，运用了```in```运算符：

        ```python
        elif floored in attrs['body_pos']:
            result = True
        # 第三步判断是不是被炸到了
        elif floored in Game.explode_points:
            result = True
        # 第四步判断是不是被流石撞到了
        elif floored in Game.flow_stones:
            result = True
        ```

        原理很简单，```attrs['body_pos']```，```Game.explode_points```，```Game.flow_stones```都是```set```集合类型，我们只需要判断**取整后头部坐标元组**```floored```**是否存在于这些点集合中**就可以了。  

        如果```floored```存在于这些点集合中，说明**碰撞到了这些点**。  

        值得一提的是，我对几乎所有点集都采用```set```集合类型，是因为对于```in```运算符来说检索一个对象是否在集合中的**时间复杂度**是```O(1)```至```O(n)```（其中```O(n)```是非常不常见的），是**非常高效**的。  

    当判断**线体头部受到致命撞击**后，```impact()```方法会返回```True```：  

    ```python
    # 在游戏主循环中
    if line_ins.impact():  # 判断是否有碰撞
        break # 跳出循环
    ```

    由此跳出循环，**让游戏结束**。  

* **线体和触发点的碰撞**  

    线体```Line```类中还有个很简单的实例方法```hit(p_x,p_y)```，接受一个坐标来判断是否和线体**发生碰撞**：  

    ```python
    def hit(self, p_x, p_y):  # 撞击判断(x,y)
        attrs = self.attrs
        h_x, h_y = attrs['head_pos']
        # 如果<=1会有误判
        return 0 <= h_x-p_x < 1 and 0 <= h_y-p_y < 1
    ```

    这个方法主要用于**线体和触发点**互相碰撞的判断，传入的```(p_x,p_y)```是触发点的坐标。  

    **注意！**触发点坐标```(p_x,p_y)```中```p_x,p_y```都是**整数**，而这里取出的头部坐标```h_x,h_y```是**浮点数**。

    判断碰撞的方法是看**头部坐标和触发点坐标的差值**，保证```h_x-p_x```和```h_y-p_y```都落在区间```[0,1)```中。  

    拿```h_x-p_x```来解释：

    * 当```h_x-p_x=0```时，毫无疑问```h_x```和```p_x```是重合了  
    * 当 ```0 < h_x-p_x < 1``` 时，代表头部```h_x```坐标**向下取整**仍然是和触发点的```p_x```坐标是**重合的**  

    和上面一节说的一样，**碰撞**这件事是反映在**游戏界面**上，被用户所看到的，所以这里也要用到**头部坐标向下取整**的思想。  

    ```h_y-p_y```的判断和上述如出一辙。  

    当线体和触发点在```x```和```y```方向上都满足碰撞条件时，代表**线体碰到触发点了**，```hit()```返回```True```，交给触发点类```Trigger```的实例方法继续处理下面的效果（这点在前面 **游戏是怎么跑起来的** 这一节已经讲过了）  

* **触发点生成的可用点**  

    在触发点```Trigger```类中有一个实例方法```ava_points()```，用来得到触发点可以生成的**可用点**的集合（也被效果类```FxTlpt```的实例方法用于生成**随机传送点**）。  

    ```python
    def ava_points(self, border_offset=False):  # 获得可用的点
        attrs = self.__line.attrs  # 获得线体属性
        exist_points = set(attrs['body_pos'])  # 脱离原来的引用，转换为集合
        exist_points.add(attrs['head_pos'])
        # 获得所有触发点占用的坐标点集合
        exist_triggers = {i['pos'] for i in self.triggers.values()}
        exist_points.update(exist_triggers)  # exist_points储存的是已经使用的坐标点
        exist_points.update(Game.border_points)  # 还要算入边框的点
        # 将所有的坐标点和已经使用的坐标点作差集，就是还可以选用的坐标点
        usable_points = Game.map_points - exist_points
        # 如果不要靠近边界
        if border_offset:
            offset = 3
            map_w, map_h = Game.map_size
            ava_area = {(xi, yi) for xi in range(offset, map_w-offset-1)
                        for yi in range(3, map_h-offset-1)}
            # 利用交集得出可用的点
            usable_points = usable_points & ava_area
        return tuple(usable_points)  # 因为random.choice选不了set
    ```

    这个方法做的事情其实也很好理解：  
    
    * 先从线体实例中取出线体属性的**尾巴坐标列表**，转换为集合作为```exist_points```，同时将**线体的头部坐标**加入该集合

    * 接下来是一个**集合推导式**，遍历所有**现存触发点的坐标**并储存于一个集合```exist_triggers```  

    * 把```exist_triggers```内的坐标点全部加入```exists_points```，接着把之前生成的边界点```Game.border_points```也加入```exists_points```  

    * 很好！现在一个包含**所有已经使用的点**的集合```exists_points```就完成了，接下来用地图中所有的点```Game.map_points```与```exists_points```作差集就能得到所有可以用的点了！  

    * 如果```border_offset=True```，代表**可用点**要离边框远一点（和上面**线体初始化**要离边框远一点是一个原理），则让生成点区域每边往内缩```3```格：  
    利用**集合推导式**生成一个缩进后的可用区域```ava_area```，  
    然后拿```ava_area```和已经生成的可用点```usable_points```作交集，得到处理后的可用点。

    最后该方法返回的是一个元组，因为这个方法是搭配```random.choice```使用的，```random.choice```只支持有顺序的序列。  

    