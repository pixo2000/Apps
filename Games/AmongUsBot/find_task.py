import pyautogui
from tasksolver import fix_wiring
from tasksolver import divert_power_start
from tasksolver import divert_power_end

images = [
    './pictures/fix_wiring.png'
    './pictures/divert_power_start.png'
    './pictures/divert_power_end.png'
]
def find_task():
    fix_wiring_task = pyautogui.locateOnScreen('./pictures/fix_wiring.png', grayscale=True)
    divert_power_task_end = pyautogui.locateOnScreen('./pictures/divert_power_end.png', grayscale=True)
    divert_power_task_start = pyautogui.locateOnScreen('./pictures/divert_power_start.png', grayscale=True)

    if fix_wiring_task is not None:  # task visible
        print("FixWiringTask: ", fix_wiring_task)
        fix_wiring()
    elif divert_power_task_start is not None:  # task visible
        print("DivertPowerTaskStart: ", divert_power_task_start)
        divert_power_start()
    elif divert_power_task_end is not None:  # task visible
        print("DivertPowerTaskEnd: ", divert_power_task_end)
        divert_power_end()