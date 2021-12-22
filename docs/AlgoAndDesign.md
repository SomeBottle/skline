# 算法&设计

![unruly-2021-12-22](https://cdn.jsdelivr.net/gh/cat-note/bottleassets@latest/img/unruly-2021-12-22.jpg)

说到计算机程序，我们肯定会谈到算法，算法决定了一个程序怎么去完成需求。咱这个破游戏当然也不意外，这一节我准备**写几个游戏里比较重要的算法设计**。

这一节我准备**分模块**来写...

## 前言  

本游戏赖以的**TUI**库```curses```的坐标系统由于历史原因是有点反直觉的：  

在```addstr()```，```newwin()```等有坐标参数的方法中，形参```y```坐标总是在```x```坐标的前面，所以传入的时候是```(y,x)```这样的形式。  

还有一点，```x```轴的**正方向**是```水平向右```，这点和我们接触的二维坐标系是一致的。但是```y```轴的**正方向**是```竖直向下```！

## resource.py  

* **```x_offset```**  

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