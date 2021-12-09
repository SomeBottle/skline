from pyfiglet import Figlet
import os
a=Figlet()
'''with open(os.path.dirname(__file__)+'/texts/ready.txt', 'w') as file_object:
    file_object.write(a.renderText('R E A D Y'))
'''
class Test:
    def __init__(self) -> None:
        self.test()
        
    @classmethod
    def test(cls):
        print('123')
Test()