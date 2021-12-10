from pyfiglet import Figlet
import time
import os
a=Figlet()
'''with open(os.path.dirname(__file__)+'/texts/gameover.txt', 'w') as file_object:
    file_object.write(a.renderText('GAME OVER'))'''
a=time.time()
p=0
for i in range(1000):
    p+=1
print(a)
print(time.time())
print(time.time()-a)