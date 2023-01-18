import os
import time

def medium_lib_parsing():
    for idx in range(12):
        os.system('python3 lib_medium.py '+str(idx))
    return 0




if __name__=="__main__":
    start=time.time()
    medium_lib_parsing()
    print('소요시간 :',time.time()-start)