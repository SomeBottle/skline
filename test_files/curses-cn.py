import curses
import time

scr=curses.initscr()
scr.addstr(1,1,'你好呀')
scr.refresh()
time.sleep(5)