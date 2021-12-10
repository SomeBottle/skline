from pyfiglet import Figlet
import time
import curses
import os
a=Figlet()
'''with open(os.path.dirname(__file__)+'/texts/gameover.txt', 'w') as file_object:
    file_object.write(a.renderText('GAME OVER'))'''
sc=curses.initscr()
curses.start_color()
curses.noecho()
win1=curses.newwin(4, 10, 2, 1)
win1.addstr(0,0,'123\n123')
win2=curses.newwin(2, 2, 3, 3)
win2.bkgd(curses.COLOR_BLUE)
win1.border()
win2.border()
sc.refresh()
win1.refresh()
win2.refresh()
sc.getch()