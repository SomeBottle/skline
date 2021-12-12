from pyfiglet import Figlet
import time
import asyncio
import curses
test=curses.initscr()
curses.start_color()
test.addstr(0,0,'hello',True)
test.refresh()
test.getch()