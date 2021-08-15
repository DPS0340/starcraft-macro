if __name__ == '__main__':
    from sys import path
    import os
    path.append(os.path.dirname(__file__))

import locations
import pyautogui
import constants
import msvcrt
import time
from PIL import ImageGrab
import threading

def create_room(room_name: str = "") -> None:
    pyautogui.moveTo(*locations.create_location, duration=1)
    pyautogui.click()
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

def submit_room_error() -> None:
    pyautogui.moveTo(*locations.error_ok_location, duration=1)
    pyautogui.click(duration=0.2)

def check_room_is_full() -> bool:
    screen = ImageGrab.grab()
    slot_count = 0
    player_count = 0
    for y in range(locations.player_y_min, locations.player_y_max + 1):
        player_rgb = screen.getpixel((locations.player_x, y))
        if player_rgb in [constants.boundary_color, constants.boundary_red_color]:
            player_count += 1
        slot_rgb = screen.getpixel((locations.slot_x, y))
        if slot_rgb == constants.slot_color:
            slot_count += 1
    player_count //= 2
    print(f"slot_count: {slot_count}, player_count: {player_count}")
    if slot_count == 0:
        return False
    screen = ImageGrab.grab()
    rgb = screen.getpixel(locations.ok_pixel_location)
    if rgb == constants.non_ok_color:
        return False
    return slot_count == player_count

def add_observer_locations() -> None:
    time.sleep(1)
    for (i, observer_location) in enumerate(locations.observer_locations):
        pyautogui.moveTo(*observer_location, duration=0.8)
        pyautogui.click(duration=0.2)
        location = (observer_location[0], observer_location[1] + locations.observer_enable_delta)
        pyautogui.moveTo(*location, duration=0.3)
        pyautogui.click(duration=0.2)
        if i == 0:
            swap_location_to_observer()

def swap_location_to_observer() -> None:
    pyautogui.moveTo(*locations.observer_button_location)
    pyautogui.click(*locations.observer_button_location)

def type_chat(content: str) -> None:
    pyautogui.moveTo(*locations.chat_location, duration=1)
    pyautogui.click()
    pyautogui.typewrite(content)
    pyautogui.typewrite('\n')

def start_game() -> None:
    pyautogui.moveTo(*locations.ok_location, duration=1)
    pyautogui.click()

def check_game_started() -> bool:
    screen = ImageGrab.grab()
    rgb = screen.getpixel(locations.diplomacy_location)
    print(f"rgb: {rgb}, diplomacy_color: {constants.diplomacy_color}")
    return rgb == constants.diplomacy_color

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
        if key == constants.fn_prefix:
            key = msvcrt.getch()
            print(key)
            if key == constants.F6:
                print("F6")
                return True
    return False

def main():
    chat_content = input("작성할 채팅을 입력해 주세요: ")
    is_pressed = False
    def input_handler():
        nonlocal is_pressed
        while True:
            is_pressed = is_pressed or check_input_key_pressed()
            time.sleep(0.1)
    input_thread = threading.Thread(target=input_handler, args=(), daemon=True)
    input_thread.start()
    while True:
        time.sleep(0.2)
        if not is_pressed:
            continue
        is_pressed = False
        while not is_pressed:
            create_room()
            if is_pressed:
                break
            time.sleep(1)
            if not check_room_is_created():
                time.sleep(2)
                submit_room_error()
                time.sleep(0.5)
                cancel_game()
                continue
            add_observer_locations()
            if is_pressed:
                break
            while True:
                type_chat(chat_content)
                time.sleep(10)
                if is_pressed:
                    break
                is_full = check_room_is_full()
                if not is_full:
                    continue
                time.sleep(3)
                is_full = check_room_is_full()
                if not is_full:
                    continue
                start_game()
                time.sleep(12)
                if not check_game_started():
                    start_game()
                    time.sleep(20)
                    if not check_game_started():
                        cancel_game()
                        break
                surrender_game()
                break
        if is_pressed:
            is_pressed = False

if __name__ == '__main__':
    main()
