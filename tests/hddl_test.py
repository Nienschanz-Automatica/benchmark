import sys
from subprocess import *

command = 'sh /home/user/PycharmProjects/benchmark/tests/test_script.sh'

proc = Popen(command, shell=True, stdout=PIPE)
while True:
    data = proc.stdout.readline()   # Alternatively proc.stdout.read(1024)
    if len(data):
        print(data)
    if len(data) == 0:
        break
    # sys.stdout.write(data)   # sys.stdout.buffer.write(data) on Python 3.x