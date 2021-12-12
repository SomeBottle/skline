# SKLINE

```
 ____  _  ___     ___ _   _ _____
/ ___|| |/ / |   |_ _| \ | | ____|
\___ \| ' /| |    | ||  \| |  _|
 ___) | . \| |___ | || |\  | |___
|____/|_|\_\_____|___|_| \_|_____|

我的Python课设~ 
TUI游戏，一条像贪吃蛇的线。
```

着手时间：2021.12.4  
收手时间：2021.12.12

## 课设说明  

1. [课程设计概述](https://github.com/SomeBottle/skline/blob/main/docs/AboutTheCourseProject.md)  

2. [需求分析](https://github.com/SomeBottle/skline/blob/main/docs/RequirementsAnalysis.md)  

3. [使用的标准库和扩展库](https://github.com/SomeBottle/skline/blob/main/docs/Libraries.md)  


## 如何运行  

* 方法一

    1. ```Python```环境 **≥ 3.7**

    2. 克隆本项目到本地，进入```src```目录。

    3. 如果是Windows系统，需要额外打个补丁Σ( ° △ °|||)︴：

        ```
        pip install windows-curses
        ```

    4. 执行 ```python main.py```  

<a id='exec_method2'></a>

* 方法二（仅限Windows）

    1. 下载[```Releases```](https://github.com/SomeBottle/skline/releases/latest)里附件的压缩包。  

    2. 解压到**目录**后**双击**```app.exe```运行程序。  

## 运行时可能出现的问题
1. 运行即报错:  

    很有可能是```Python```版本低于```3.7```导致的。也有可能是窗口过小（见下面）  

2. 主菜单没有问题，但是进入游戏后抛出异常从而退出程序，异常中有```init_color```字样:  

    虽然程序在初始化颜色时会**判断终端是否支持颜色**，但是如果**终端不支持256色**或发生其他不好判断的异常（curses异常太模糊了，难以寻因），仍然会出现```init_color```错误，于是我在```config.json```里加了个**是否使用颜色**的配置项：

    ```json
    "use_color": true,
    ```

    改成不使用颜色就能解决问题（画面全变一个颜色其实增加难度了 w(ﾟДﾟ)w）：

    ```json
    "use_color": false,
    ```

3. 如果进入游戏后抛出异常，但异常中没有```init_color```字样：

    很有可能是终端屏幕小了，拉大就行。我在某个远程win7计算机上测试时发现**CMD窗口**竟然无法鼠标拖拉调整，怎么办呢？  

    ![change the size](https://cdn.jsdelivr.net/gh/SomeBottle/skline/docs/pics/win_size_of_cmd.gif)  

如果按[方法二](#exec_method2)运行程序，抛出异常时可能会直接**闪退**。为了看到异常，你可以选择把```app.exe```**拖拽**到```命令提示符```或者```PowerShell```里然后执行：  

![drag to cmd](https://cdn.jsdelivr.net/gh/SomeBottle/skline/docs/pics/drag_to_cmd.gif)  

------

## 游戏机制-触发点
* 触发点与得分

* 触发点与效果

To be updated~

## 游戏机制-局终判定

To be updated~

## 游戏机制-分数计算  

To be updated~

------

## 为什么界面是英文

To be updated~  