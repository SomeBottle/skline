# 使用的标准库和扩展库  

![cj9xz5y3a01lbxz5nbd24hkio.1200-2021-12-04](https://cdn.jsdelivr.net/gh/cat-note/bottleassets@latest/img/cj9xz5y3a01lbxz5nbd24hkio.1200-2021-12-04.jpg)

## Curses  

Python标准库，官方文档：

* https://docs.python.org/zh-cn/3/howto/curses.html  
* https://docs.python.org/zh-cn/3/library/curses.html

Curses最开始是由C进行编写，用作终端图形界面（TUI）绘制的库，后被Python（CPython）移植作为内置标准库。  

很可惜的是，到目前为止仍然无法支持Windows，我们需要额外安装扩展库↓  

## Windows-Curses  

Curses在Windows平台的补丁包，使得在Windows上能使用Curses库.    

## time  

Python标准库，官方文档：https://docs.python.org/zh-cn/3/library/time.html  

该模块提供了各种与时间相关的函数。  

## os

Python标准库，官方文档：https://docs.python.org/zh-cn/3/library/os.html 

在这个课设中我主要用于获得程序运行所在的绝对目录，也就是```os.path.dirname```

## json

Python标准库，官方文档：https://docs.python.org/zh-cn/3/library/json.html 

我决定用Json作为SKLINE的配置文件格式，由此需要使用json库

