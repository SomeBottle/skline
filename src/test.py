'''
from pyfiglet import Figlet
import os
a=Figlet()
with open(os.path.dirname(__file__)+'/texts/skline.txt', 'w') as file_object:
    file_object.write(a.renderText('S K L I N E'))
'''
# 导入必须的库
import curses
import time

# 初始化命令行界面，返回的 stdscr 为窗口对象，表示命令行界面
stdscr = curses.initscr()
# 使用 noecho 方法关闭命令行回显
curses.noecho()
# 使用 nodelay(True) 方法让 getch 为非阻塞等待（即使没有输入程序也能继续执行）
stdscr.nodelay(True)
while True:
    # 清除 stdscr 窗口的内容（清除残留的符号）
    stdscr.erase()
    # 获取用户输入并放回对应按键的编号
    # 非阻塞等待模式下没有输入则返回 -1
    key = stdscr.getch()
    # 在 stdscr 的第一行第三列显示文字
    stdscr.addstr(1, 3, "Hello GitHub.")
    # 在 stdscr 的第二行第三列显示文字
    stdscr.addstr(2, 3, "Key: %d" % key)
    # 刷新窗口，让刚才的 addstr 生效
    stdscr.refresh()
    # 等待 0.1s 给用户足够反应时间查看文字
    time.sleep(0.1)