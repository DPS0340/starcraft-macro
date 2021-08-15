import pyautogui
import time
from PIL import ImageGrab

print(pyautogui.size())
while True:
    time.sleep(0.5)
    pos = pyautogui.position()
    screen = ImageGrab.grab()
    rgb = screen.getpixel(pos)
    print(pos, rgb)