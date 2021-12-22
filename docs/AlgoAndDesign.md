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

    

    