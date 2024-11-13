import sys
from multiprocessing import Process, Manager, Value
from processing import listfiles, readfiles
from lastmain import screenshots
import time

def read_and_decide(flag):
    while True:
        with open('signal.txt', 'r') as file:
            lines = file.readlines()
        
        line_value = lines[1].strip()
        #print("Read value from signal.txt:", line_value)

        if line_value == "True":
            flag.value = 1
        else:
            flag.value = 0

        # Print the updated flag value for debugging
        #print("Updated flag.value:", flag.value)
        
        time.sleep(5)

if __name__ == "__main__":

    url = sys.argv[1]
    depth = int(sys.argv[2])
    
    manager = Manager()
    shared_dict = manager.dict()
    directory = "screenshots"
    flag = Value('b', True)

    process0 = Process(target=screenshots, args=(url, depth))
    processA = Process(target=listfiles, args=(directory, shared_dict, flag))
    processB = Process(target=readfiles, args=(directory, shared_dict, flag))
    processC = Process(target=read_and_decide, args=(flag,))

    process0.start()
    processA.start()
    processB.start()
    processC.start()

    processA.join()
    process0.join()
    processB.join()
    processC.join()
