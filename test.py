from classes import Volume
import os
import time



if __name__ == '__main__':
    v = Volume(19)
    while True:
        os.system('clear')
        v.get_volume()
        print(v)
        time.sleep(10)
