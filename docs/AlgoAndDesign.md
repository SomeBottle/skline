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

        **临时储存**爆炸时**代表爆炸范围**的点集合，由效果类```FxBomb```的```apply()```方法控制，用于和**线体**产生交互。  

    * **```Game.__sight_points```**  

        储存**近视模式**下的点集合，代表角色近视时**能看到的区域（也就是视野）**，这和近视(```Myopia```)效果的处理**息息相关**，后面会细说。  

    * **```Game.flow_stones```**

        储存地图中的**流石**点集合，代表地图中**流石**的位置，由效果类```FxStones```的```apply()```方法控制，用于和**线体**产生交互。  