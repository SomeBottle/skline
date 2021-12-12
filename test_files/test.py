from pyfiglet import Figlet
import time
import asyncio
import os
a=Figlet()
with open(os.path.dirname(__file__)+'/texts/ranking.txt', 'w') as file_object:
    file_object.write(a.renderText('R A N K I N G'))