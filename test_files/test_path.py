import os
import sys

# determine if application is a script file or frozen exe
if getattr(sys, 'frozen', False):
    print('mode1')
    application_path = os.path.dirname(sys.executable)
elif __file__:
    print('mode2')
    application_path = os.path.dirname(__file__)
print(application_path)
input()