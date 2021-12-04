from pyfiglet import Figlet
import os
a=Figlet()
with open(os.path.dirname(__file__)+'/texts/difficulty.txt', 'w') as file_object:
    file_object.write(a.renderText('DIFFICULTY'))

