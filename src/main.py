if __name__ == '__main__':
    from sys import path
    import os
    path.append(os.path.dirname(__file__))

import locations
import pyautogui
import pyperclip
import constants
import msvcrt
import time
from PIL import ImageGrab
import threading

def create_room(room_name: str = "") -> None:
    pyautogui.moveTo(*locations.create_location, duration=1)
    pyautogui.click()
    if room_name:
        pyautogui.moveTo(*locations.name_location, duration=1)
        pyautogui.click()
        pyautogui.typewrite(room_name)
    pyautogui.moveTo(*locations.ok_location, duration=1)
    pyautogui.click()

def check_room_is_created() -> bool:
    screen = ImageGrab.grab()
    error_rgb = screen.getpixel(locations.error_location)
    print(error_rgb, constants.error_color)
    return error_rgb != constants.error_color

def check_create_game_error() -> bool:
    return not check_room_is_created()

def submit_room_error() -> None:
    pyautogui.moveTo(*locations.error_ok_location, duration=1)
    pyautogui.click(duration=0.2)

def check_room_is_full() -> bool:
    screen = ImageGrab.grab()
    player_count = 0
    for y in range(locations.player_y_min, locations.player_y_max + 1):
        player_rgb = screen.getpixel((locations.player_x, y))
        if player_rgb in [constants.boundary_color, constants.boundary_red_color]:
            player_count += 1
    player_count //= 2
    print(f"player_count: {player_count}")
    screen = ImageGrab.grab()
    rgb = screen.getpixel(locations.ok_pixel_location)
    if rgb == constants.non_ok_color:
        return False
    return player_count == 8

def add_observer_locations() -> None:
    time.sleep(1)
    for (i, observer_location) in enumerate(locations.observer_locations):
        pyautogui.moveTo(*observer_location, duration=0.5)
        pyautogui.click(duration=0.2)
        location = (observer_location[0], observer_location[1] + locations.observer_enable_delta)
        pyautogui.moveTo(*location, duration=0.2)
        pyautogui.click(duration=0.2)
        if i == 0:
            swap_location_to_observer()

def swap_location_to_observer() -> None:
    pyautogui.moveTo(*locations.observer_button_location)
    pyautogui.click(*locations.observer_button_location)

def type_chat(content: str) -> None:
    pyperclip.copy(content)
    pyautogui.moveTo(*locations.chat_location, duration=1)
    pyautogui.click()
    pyautogui.typewrite('a')
    pyautogui.press('backspace')
    pyautogui.keyDown('ctrlleft')
    pyautogui.typewrite('v')
    pyautogui.keyUp('ctrlleft')
    pyautogui.typewrite('\n')

def start_game() -> None: 
    pyautogui.moveTo(*locations.ok_location, duration=1)
    if check_room_is_full():
        pyautogui.click()
        return True
    return False

def check_game_started() -> bool:
    screen = ImageGrab.grab()
    rgb = screen.getpixel(locations.game_start_location)
    print(f"rgb: {rgb}, game_start_color: {constants.game_start_color}")
    return rgb == constants.game_start_color

def check_game_end() -> bool:
    screen = ImageGrab.grab()
    rgb = screen.getpixel(locations.quit_location)
    print(f"rgb: {rgb}")
    return rgb != constants.quit_color

def cancel_game() -> None:
    pyautogui.moveTo(*locations.cancel_location)
    pyautogui.click()


def surrender_game() -> None:
    pyautogui.moveTo(*locations.menu_location)
    pyautogui.click(duration=0.2)
    pyautogui.moveTo(*locations.end_mission_location)
    pyautogui.click(duration=0.2)
    pyautogui.moveTo(*locations.surrender_location, duration=0.5)
    pyautogui.click(duration=0.2)
    pyautogui.click(duration=0.2)
    while not check_game_end():
        pyautogui.moveTo(*locations.surrender_location, duration=0.5)
        pyautogui.click(duration=0.2)
    time.sleep(3)
    pyautogui.moveTo(*locations.end_ok_location)
    pyautogui.click(duration=0.2)
    time.sleep(5)

def check_input_key_pressed() -> bool:
    if msvcrt.kbhit():
        key = msvcrt.getch()
        print(key)
        if key == constants.ctrl_z:
            exit(0)
        if key == constants.fn_prefix:
            key = msvcrt.getch()
            print(key)
            if key == constants.F6:
                print("F6")
                return True
    return False


def main():
    chat_content = input("작성할 채팅을 입력해 주세요: ")
    print(chat_content)
    is_pressed = False
    main_thread: threading.Thread = None
    chat_thread: threading.Thread = None
    input_thread: threading.Thread = None
    is_room_started = False
    lock = False
    room_name = ""
    def chat_handler():
        nonlocal is_room_started, lock
        while True:
            if is_room_started:
                return
            if lock:
                continue
            lock = True
            type_chat(chat_content)
            lock = False
            time.sleep(10)
    def main_handler():
        nonlocal room_name, is_room_started, chat_thread, lock, is_pressed, chat_thread
        time.sleep(0.2)
        is_pressed = False
        while not is_pressed:
            is_room_started = False
            create_room(room_name)
            if is_pressed:
                break
            time.sleep(1.5)
            if not check_room_is_created():
                time.sleep(10)
                submit_room_error()
                time.sleep(0.5)
                cancel_game()
                room_name = "."
                continue
            chat_thread = threading.Thread(target=chat_handler, args=(), daemon=True)
            chat_thread.start()
            add_observer_locations()
            if is_pressed:
                break
            while True:
                if is_pressed:
                    break
                is_full = check_room_is_full()
                if not is_full:
                    time.sleep(1)
                    continue
                time.sleep(3)
                is_full = check_room_is_full()
                if not is_full:
                    continue
                while lock:
                    pass
                lock = True
                if not start_game():
                    lock = False
                    continue
                is_room_started = True
                lock = False
                while check_create_game_error():
                    if is_pressed:
                        break
                    submit_room_error()
                    time.sleep(1)
                    start_game()
                if is_pressed:
                    break
                time.sleep(10)
                if not check_game_started():
                    submit_room_error()
                    start_game()
                    if is_pressed:
                        break
                    time.sleep(10)
                    if is_pressed:
                        break
                    if not check_game_started():
                        cancel_game()
                        break
                surrender_game()
                break
    def input_handler():
        nonlocal is_pressed, main_thread, chat_thread, is_room_started
        handlers = [chat_handler, main_handler]
        while True:
            is_pressed = is_pressed or check_input_key_pressed()
            if is_pressed:
                is_room_started = True
                for thread in [chat_thread, main_thread]:
                    if thread:
                        thread.join()
                is_pressed = False
                is_room_started = True
                threads = [threading.Thread(target=handler, args=(), daemon=True) for handler in handlers]
                chat_thread, main_thread = threads
                for thread in threads:
                    thread.start()
            time.sleep(0.1)
    input_thread = threading.Thread(target=input_handler, args=())
    input_thread.start()
    input_thread.join()
if __name__ == '__main__':
    main()
