# 模块/类/函数关系

![exhausted-2021-12-21](https://cdn.jsdelivr.net/gh/cat-note/bottleassets@latest/img/exhausted-2021-12-21.jpg)

## 模块

先上个模块关系图：

![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/module-relations.png)  

* ```main.py``` - 程序主入口
* ```view.py``` - 游戏菜单界面模块
* ```game.py``` - 游戏主程序+界面模块
* ```resource.py``` - 程序所需的基本方法和资源模块  

## 类

* **view.py**

    ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/class-view-relations.png)  

    * ```BasicView``` - 界面基类，包含界面初始化和创建界面必须的方法  
    * ```MenuView``` - 菜单类，包含菜单界面绘制和相关操作方法
    * ```DifficultyView``` - 困难度类，包含困难度调整界面绘制和相关的操作方法
    * ```RankingView``` - 排名类，包含排名展示界面绘制和相关操作方法  

* **resource.py** 

    resource模块只有```Res```一个大类，```Res```类包含：

    * 默认的配置文件内容
    * 修改/获取配置文件的方法
    * 获取艺术字的方法
    * 修改/获取排名文件的方法
    * 修正艺术字偏移的方法
    * 转换 ```1-1000``` RGB颜色为 ```1-255``` RGB的方法
    * 按概率进行随机选择的方法

* **game.py**  

    ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/class-game-relations.png)  

    * ```Game``` - 游戏主类，包含游戏界面绘制和必需的操作方法，以及很大一坨类属性  
    * ```Line``` - 线体相关绘制和操作方法
    * ```Trigger``` - 触发点相关绘制和操作方法
    * ```FxBase``` - 线体效果基类
    * ```FxNormal``` - 普通触发点效果类
    * ```FxBonus``` - 奖励点效果类
    * ```FxAclrt``` - 加速点效果类
    * ```FxDclrt``` - 减速点效果
    * ```FxMyopia``` - 近视点效果
    * ```FxBomb``` - 爆炸点效果
    * ```FxIvcb``` - 无敌点效果
    * ```FxStones``` - 流石点效果
    * ```FxTlpt``` - 传送点效果  

    其中```Line```实例化后的对象会被**储存在```Game```**中，后面```Trigger```实例化时能通过**Game的类方法**取出Line的实例对象。  

## 函数  

因为这里的函数关系太复杂了，暂且只列出各模块的函数，部分关系在下面一节中再展示...

* **game.py**  

    ![](https://cdn.jsdelivr.net/gh/SomeBottle/skline@main/docs/pics/funcs-game.png)  

    青色代表```类方法```，黄色代表```实例方法```，绿色代表```实例属性```，蓝色代表```异步函数```。  

    <details>
    <summary>展开查看方法用途描述</summary>

    ------

    |方法名|类型|用途|
    |:---:|:---:|:---:|
    |set_color|类方法|基于```curses```设置颜色对|
    |color_pair|类方法|在```curses,color_pair```上的一个Hook，考虑不支持颜色的情况|
    |cls_init|类方法|初始化Game类的类属性|
    |cut_point|类方法|修剪传入的点集合，返回一个只存在于地图内的点集合|
    |reset_score|类方法|重置游戏分数为0|
    |add_task|类方法|往```asyncio```事件循环中增加协程任务，多用于触发点特效的处理|
    |add_score|类方法|增加分数，可以接受一个参数```num```来指定加多少分|
    |create_border|类方法|创建游戏边界的点坐标集合|
    |create_area|类方法|创建```curses```窗口，包括消息窗口和游戏窗口|
    |del_area|类方法|在游戏结束后删除窗口|
    |get_ins|类方法|获得储存的实例，用于取得```Line```的实例对象|
    |myopia|类方法|使用布尔值设置是否近视|
    |get_sight_info|类方法|用于**近视处理**部分，获得头部坐标和视野宽高|
    |update_myopia_sight|类方法|用于更新视野区域点集合，搭配```Line```实例的```move```方法|
    |printer|类方法|用于游戏区域图案打印，```curses.addstr```方法的一个Hook，同样是考虑了不支持颜色的情况|
    |flash_fx|实例方法|用于```count_down```方法里对艺术字的随机纵向推拉动画|
    |count_down|实例方法|用于游戏倒计时|
    |draw_flow_stones|实例方法|用于根据流石点集绘制流石|
    |draw_border|实例方法|根据```create_border```创建的点集绘制游戏区域边框|
    |draw_score|实例方法|在消息区绘制分数信息|
    |calc_score|实例方法|用于在游戏结束后计算出最终得分|
    |over|实例方法|游戏结束时进入的游戏结束方法|
    |cancel_tasks|实例方法|在游戏结束后取消所有```asyncio```事件循环中的协程任务|
    |start|实例方法|促使游戏开始的方法|

    </details>
    
* **view.py**  
