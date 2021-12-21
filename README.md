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


## 如何运行  

<details open>
<summary>展开阅读</summary>

------

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

    1. 下载[```Releases```](https://github.com/SomeBottle/skline@main/releases/latest)里附件的压缩包。  

    2. 解压到**目录**后**双击**```app.exe```运行程序。  

</details>

## 运行时可能出现的问题

<details>
<summary>展开阅读</summary>

---------

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

    ![change the size](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/win_size_of_cmd.gif)  

如果按[方法二](#exec_method2)运行程序，抛出异常时可能会直接**闪退**。为了看到异常，你可以选择把```app.exe```**拖拽**到```命令提示符```或者```PowerShell```里然后执行：  

![drag to cmd](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/drag_to_cmd.gif)  

</details>

## 游戏操作

* 在**主菜单MENU**使用 ```W``` , ```S``` 或 ```↑``` , ```↓``` 按键进行选项切换，```ENTER```回车键选定。  

* 在**排名表RANKING**中使用 ```A``` , ```D``` 进行翻页， ```ENTER``` 回车键返回。

* **难度设定DIFFICULTY**界面使用 ```A``` , ```D``` 或 ```←``` , ```→``` 按键进行困难度调整，```ENTER```回车键返回。

* 在游戏中使用 ```W``` , ```A``` , ```S``` , ```D``` 或 ```↑``` , ```←``` , ```↓``` , ```→``` 控制角色进行移动。

* **游戏结束GAMEOVER**界面使用 ```R``` 重开一局游戏，按下 ```B``` 返回到菜单。


------

## 游戏机制-触发点

<details>
<summary>展开阅读</summary>

--------

虽然称作是触发点，实际上也没啥高大上的，就是贪吃蛇里的食物罢了，不过我觉着这里不止是食物，所以就叫触发(Trigger)点了~∠( ᐛ 」∠)＿  

游戏中提供了 ```9``` 种**触发点**，在这里咱列举一下触发点的作用：

* 触发点与得分  

    |名字|默认样式|默认颜色|得分|是否增长尾巴|
    |:---:|:---:|:---:|:---:|:---:|
    |Normal|@|<img src="https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/svg/trigger-normal.svg"/>|1|是|
    |Bonus|+|<img src="https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/svg/trigger-bonus.svg"/>|2|否|
    |Accelerate|+|<img src="https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/svg/trigger-accelerate.svg"/>|1|是|
    |Decelerate|+|<img src="https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/svg/trigger-decelerate.svg"/>|1|是|
    |Myopia|*|<img src="https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/svg/trigger-myopia.svg"/>|1|否|
    |Bomb|*|<img src="https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/svg/trigger-bomb.svg"/>|0|是|
    |Invincibility|$|<img src="https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/svg/trigger-invincibility.svg"/>|0|是|
    |Stones|@|<img src="https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/svg/trigger-stones.svg"/>|1|是|
    |Teleport|$|<img src="https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/svg/trigger-teleport.svg"/>|1|是|


* 触发点与效果

    |名字|效果|演示|
    |:---:|:---:|:---:|
    |Normal|普通的加分|这个就不用特别演示了吧...|
    |Bonus|额外得分点，不会加长尾巴|![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/trigger-bonus.gif)| 
    |Accelerate|碰到后线体会加速|![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/trigger-accelerate.gif)| 
    |Decelerate|碰到后线体会减速|![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/trigger-decelerate.gif)|
    |Myopia|碰到后会近视(视野减小)|![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/trigger-myopia.gif)|
    |Bomb|触发后闪烁一会儿即爆炸，被炸到的尾巴会被削去，被炸到头就G了|![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/trigger-bomb.gif)|
    |Invincibility|触发后线体会进入无敌模式，不会被判死|![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/trigger-invincibility.gif)|
    |Stones|碰到后有流石会从随机方向闯入区域，线体头碰到流石时就游戏结束|![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/trigger-stones.gif)|
    |Teleport|碰到后会被传送到地图中间的随机地方|![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/trigger-teleport.gif)|

</details>

## 游戏机制-局终判定

<details>
<summary>展开阅读</summary>

------

游戏结束判定的前提是线体**没有无敌(Invincibility)效果**。  

|游戏结束判定|演示|
|:---:|:---:|
|头撞到墙壁|![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/gameover-hitborder.gif)|
|头撞到自己尾巴|![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/gameover-hitself.gif)|
|头被炸弹炸到|![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/gameover-hitbomb.gif)|
|头被流石砸到|![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/gameover-hitstones.gif)|

</details>


## 游戏机制-分数计算  

咱这个游戏的分数计算其实挺简单的，就一个公式：  

```尾巴长度``` × ```得分``` × ```难度等级``` × ```(1/10)``` = ```总分```  

```难度等级```指的是在游戏配置文件和```DIFFICULTY```面板配置的难度，默认难度等级只有五个配置，也就是```1-5```。

很有意思的是当尾巴长度为0时**总分也会相应为0**，所以要有分数必须得有一定的尾巴长度。


------

## 配置文件

<details>
<summary>展开阅读</summary>

------

在游戏初次运行时会在**同一目录下**生成配置文件```config.json```，咱从外层到内层注释一下：  

* 外层  

    ```python
    {
        "difficulty": 1, # 目前设定的难度等级，游戏里更改难度等级会自动更新这里的配置
        "tps": 10, # ticks per second，每秒游戏计算(tick)的次数
        "max_rank_len": 100, # 排行榜最多容纳多少项
        "use_color": true, # 是否使用颜色，有的终端不支持颜色，需要用到这个选项
        "diff_cfg": {...}, # 不同难度等级对应的游戏配置
        "styles":{...} # 部分元素的显示样式
    }
    ```

* 不同难度等级对应的游戏配置```diff_cfg```

    ```python
    {
        "1": { # 难度等级为1的配置
            "map_size": [50,15], # 地图大小(宽,高)，单位：格数
            "short_sight": [7,5], # 近视时视野大小(宽,高)，单位：格数
            "init_velo": 0.4, # 最开始线体行动的速度大小(最大值为1)，单位：格/tick
            "triggers": { # 触发点相关配置
                "summon": { # 生成触发点的概率(支持小数点后三位)
                    //以下所有概率加起来要为1
                    "normal": 0.5, # 普通点的生成概率
                    "bonus": 0.05, # 奖励点的生成概率
                    "accelerate": 0.08, # 加速点的生成概率  
                    "decelerate": 0.02, # 减速点的生成概率
                    "myopia": 0.05, # 近视点的生成概率
                    "bomb": 0.04, # 炸弹点的生成概率
                    "invincibility": 0.05, # 无敌点的生成概率
                    "stones": 0.06, # 流石点的生成概率  
                    "teleport": 0.15 # 传送点的生成概率
                },
                "last_for": { # 触发点对应的效果持续的时长(单位：秒)
                    "accelerate": 5, # 加速效果持续时间
                    "decelerate": 5, # 减速效果持续时间
                    "myopia": 3, # 近视效果持续时间 
                    "bomb": { 
                    "flash": 1.5, # 炸弹闪烁时间 
                    "explode": 0.5 # 爆炸持续时间
                    },
                    "invincibility": 6 # 无敌持续时间
                }
            }
        },
        ...
    }
    ```

* 部分元素的显示样式```styles```  

    ```python
    {
        "line": "#", # 线体的图案
        "line_head_color": [11, 170, 239], # 头部的颜色
        "line_body_color": [138, 220, 255], # 尾部的颜色
        "area_border": "#", # 边界的图案
        "border_color": [161, 161, 161], # 边界的颜色
        "to_explode": "*", # 爆炸闪烁的图案
        "to_explode_color": [255, 0, 0], # 爆炸闪烁的颜色
        "explode": "*", # 爆炸粒子的图案
        "explode_color": [255, 215, 15], # 爆炸粒子的颜色
        "flow_stone": "o", # 流石的图案
        "flow_stone_color": [199, 192, 173], # 流石的颜色
        "triggers": { # 触发点样式配置
            "normal": { # 普通点的样式
                "pattern": "@", # 这个点的图案
                "color": [255, 149, 0] # 这个点的颜色
            },
            "bonus": { # 奖励点的样式
                "pattern": "+",
                "color": [0, 224, 209]
            },
            "accelerate": { # 加速点的样式
                "pattern": "+",
                "color": [0, 235, 164]
            },
            "decelerate": { # 减速点的样式
                "pattern": "+",
                "color": [0, 235, 164]
            },
            "myopia": { # 近视点的样式
                "pattern": "*",
                "color": [16, 235, 0]
            },
            "bomb": { # 炸弹点的样式
                "pattern": "*",
                "color": [251, 255, 0]
            },
            "invincibility": { # 无敌点的样式
                "pattern": "$",
                "color": [255, 136, 0]
            },
            "stones": { # 流石点的样式
                "pattern": "@",
                "color": [255, 149, 0]
            },
            "teleport": { # 传送点的样式
                "pattern": "$",
                "color": [216, 245, 0]
            }
        }
    }
    ```

</details>

## 课设说明  

1. [课程设计概述](https://github.com/SomeBottle/skline/blob/main/docs/AboutTheCourseProject.md)  

2. [需求分析](https://github.com/SomeBottle/skline/blob/main/docs/RequirementsAnalysis.md)  

3. [使用的标准库和扩展库](https://github.com/SomeBottle/skline/blob/main/docs/Libraries.md)  

4. [模块/类/函数小展示](https://github.com/SomeBottle/skline/blob/main/docs/moduleClassFuncs.md)  

## 为什么界面是英文

使用curses在终端输出中文得要解决一下编码的问题，这个其实还挺好办。但是吧，不同终端对中文显示的支持挺奇怪的：

* bash  

    ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/bash-cn.png)  

* Windows Command Line(PowerShell也一样)  

    ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/cmd-cn.png)  

为了保证一致的显示，我决定就用英文了...

## 感谢

[数字绘](https://github.com/zxhm001/DataDraw) - 非常棒的开源结构图绘制工具，谢谢你们！  

## 声明  

本项目仅供参考，请不要用于你自己的课设。写课设本质上是锻炼了自己的能力，一旦习惯了复制粘贴，你将会失去自己的思考。