import pyautogui


def fix_wiring():
    start_coordinates = [
            [884, 274],
            [884, 457],
            [884, 642],
            [884, 830]
        ]
    ending_coordinates = [
            [1658, 274],
            [1658, 457],
            [1658, 642],
            [1658, 830]
        ]
    for i in start_coordinates:
        print("start_coordinates: ", i)
        r1, g1, b1 = pyautogui.pixel(i[0], i[1])
        print(r1, g1, b1)
        for y in ending_coordinates:
            r2, g2, b2 = pyautogui.pixel(y[0], y[1])
            if ((r1 == r2) and (g1 == g2) and (b1 == b2)):
                pyautogui.moveTo(i[0], i[1])
                pyautogui.mouseDown()
                pyautogui.moveTo(y[0], y[1], 0.2)
                pyautogui.mouseUp()
                print("Matching ending_coordinates: ", y)
    print("Finished Fix_Wiring. Searching for new Task")

def divert_power_start():
    start_coordinates = [
        [972, 762],  # Upper Engine
        [1066, 762],  # Lower Engine
        [1160, 762],  # Weapons
        [1256, 762],  # Shields
        [1360, 762],  # Navigation
        [1453, 762],  # Communication
        [1551, 762],  # 02
        [1649, 762]  # Security
    ]
    ending_coordinates = [
        [972, 1357],
        [1066, 1357],
        [1160, 1357],
        [1256, 1357],
        [1360, 1357],
        [1453, 1357],
        [1551, 1357],
        [1649, 1357]
    ]
    for i in start_coordinates:
        r1, g1, b1 = pyautogui.pixel(i[0], i[1])
        print(r1, g1, b1)
        for y in ending_coordinates:
            if (r1 == 255):
                if i[0] == 972:
                    print("Diverting Power to Upper Engine")
                elif i[0] == 1066:
                    print("Diverting Power to Lower Engine")
                elif i[0] == 1160:
                    print("Diverting Power to Weapons")
                elif i[0] == 1250:
                    print("Diverting Power to Shields")
                elif i[0] == 1350:
                    print("Diverting Power to Navigation")
                elif i[0] == 1453:
                    print("Diverting Power to Communications")
                elif i[0] == 1551:
                    print("Diverting Power to O2")
                elif i[0] == 1649:
                    print("Diverting Power to Security")
                pyautogui.moveTo(i[0], i[1])
                pyautogui.mouseDown()
                pyautogui.moveTo(y[0], y[1], 0.2)
                pyautogui.mouseUp()
    print("Diverted Power from Electrical. Searching for new Task")


def divert_power_end():
    print("Finished Diverting Power. Searching for new Task")
    pyautogui.click(1282, 540)

