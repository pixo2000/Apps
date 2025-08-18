import time
import keyboard
from find_task import find_task


# main code start
time.sleep(1)   # tab into the game

print("Starting over")
while not keyboard.is_pressed('p'):
    try:
        find_task()
    except:
      print("No Task found. Retrying")
print("Ending Code")
