from pyfiglet import Figlet
import time
import asyncio
import os
a=Figlet()
'''with open(os.path.dirname(__file__)+'/texts/gameover.txt', 'w') as file_object:
    file_object.write(a.renderText('GAME OVER'))'''

async def test():
    await asyncio.sleep(2)
    print('Finished waiting')
async def main(task):
    for i in range(50):
        print(i)
        if i==10:
            task.append(asyncio.create_task(test()))
        await asyncio.sleep(2)

async def enter():
    task=[]
    task.append(asyncio.create_task(main(task)))
    await asyncio.wait(task)
    

asyncio.run(enter())