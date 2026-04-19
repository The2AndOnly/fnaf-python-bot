import os
import threading
import time

import mouse
import keyboard
import mss
import psutil

sct = mss.mss()
main_monitor = sct.monitors[1]

is_facing_right = False
is_camera_up = False
is_light_on = False
is_left_door_closed = False
is_right_door_closed = False
is_robot_at_door = False
last_foxy_check = 0
is_on_title_screen = False
star_1 = False
star_2 = False
star_3 = False
is_in_office = False
has_timed_out = False

animatronics = ["freddy", "bonnie", "chica", "foxy"]
button_coordinates = {
    "continue":          (0.21145833333333333,  0.687962962962963  ),
    "sixth_night":       (0.20572916666666666,  0.7851851851851852 ),
    "custom_night":      (0.26614583333333336,  0.8842592592592593 ),
    "freddy_arrow":      (0.23385416666666667,  0.687037037037037  ),
    "bonnie_arrow":      (0.45208333333333334,  0.6861111111111111 ),
    "chica_arrow":       (0.6770833333333334,   0.6824074074074075 ),
    "foxy_arrow":        (0.8958333333333334,   0.687962962962963  ),
    "ready":             (0.8901041666666667,   0.9120370370370371 ),
    "left_light":        (0.033854166666666664, 0.6351851851851852 ),
    "right_light":       (0.9598958333333333,   0.6527777777777778 ),
    "open_camera":       (0.43072916666666666,  0.98               ),
    "close_camera":      (0.43072916666666666,  0.85               ),
    "west_hall":         (0.7765625,            0.8453703703703703 ),
    "hall_corner":       (0.8557291666666667,   0.9009259259259259 )
}
scan_coordinates = {
    "title_check":       (0.1375,               0.6                ),
    "office_check":      (0.09895833333333333,  0.9361111111111111 ),
    "star_1":            (0.15729166666666666,  0.47685185185185186),
    "star_2":            (0.21666666666666667,  0.4759259259259259 ),
    "star_3":            (0.27291666666666664,  0.4703703703703704 ),
    "left_door":         (0.05572916666666667,  0.4222222222222222 ),
    "right_door":        (0.9614583333333333,   0.4444444444444444 ),
    "camera_check":      (0.9380208333333333,   0.6157407407407407 ),
    "chica_check":       (0.6697916666666667,   0.5333333333333333 ),
    "bonnie_check_1":    (0.38177083333333334,  0.40185185185185185),
    "bonnie_check_2":    (0.38229166666666664,  0.4666666666666667 ),
    "bonnie_check_door": (0.12604166666666666,  0.3574074074074074 )
}
default_animatronic_levels = {
    "freddy": 1,
    "bonnie": 3,
    "chica":  3,
    "foxy":   1
}

def do_colors_match(color_1=(0, 0, 0), color_2=(0, 0, 0), tolerance=0, channels=3):
    # note: to convert from tolerances used in the old system (summing the difference in all of the channels) to a tolerance in this system (assuming the differences are spread evenly across channels), you can simply divide by √channels
    return sum([(color_1[i] - color_2[i]) ** 2 for i in range(channels)]) < tolerance ** 2

def toggle_button(button):
    move_mouse(button_coordinates[button])
    if "left" in button:
        wait_until(is_not_facing_right, 5)
    if "right" in button:
        wait_until(is_facing_right, 5)
    click_mouse()

def toggle_camera():
    move_mouse(button_coordinates["open_camera"])
    time.sleep(0.1)
    move_mouse(button_coordinates["close_camera"])

def camera(cam):
    move_mouse(button_coordinates[cam])
    click_mouse()

# Functions for detecting states
def is_camera_up():
    return is_camera_up

def is_facing_right():
    return is_facing_right

def is_not_facing_right():
    return not is_facing_right

# Controls the night gameplay
def office_loop():
    global is_robot_at_door
    global is_left_door_closed
    global is_right_door_closed
    global last_foxy_check

    # Initialize variables
    last_foxy_check = 0
    is_left_door_closed = False
    is_right_door_closed = False

    # East hall corner at the start of the night
    toggle_camera()
    wait_until(is_camera_up, 5)
    if has_timed_out:
        return
    
    camera("hall_corner")
    time.sleep(0.01)
    toggle_camera()

    while True:
        # Check left light
        check_light("left_light")
        if has_timed_out:
            break

        # Toggle door accordingly
        if is_robot_at_door and not is_left_door_closed:
            is_left_door_closed = True
            toggle_button("left_door")
        elif is_left_door_closed and not is_robot_at_door:
            is_left_door_closed = False
            toggle_button("left_door")
        if has_timed_out:
            break

        is_robot_at_door = False

        # Flip camera
        flip_camera()
        if has_timed_out:
            break

        # If haven't checked Foxy in a while, then do that instead of checking Chica
        if last_foxy_check >= 50:
            if not is_right_door_closed:
                is_right_door_closed = True

                toggle_button("right_door")
                if has_timed_out:
                    break
            else:
                time.sleep(0.5)

            check_foxy()
            if has_timed_out:
                break
        else:
            check_chica()

            # Flip camera or check Foxy
            if last_foxy_check >= 40 and is_right_door_closed:
                check_foxy()
            else:
                flip_camera()
            if has_timed_out:
                break

        time.sleep(0.01)

def flip_camera():
    global last_foxy_check

    toggle_camera()
    wait_until(is_camera_up, 5)
    last_foxy_check += 1
    toggle_camera()

def check_light(light):
    global is_light_on

    toggle_button(light)
    is_light_on = True
    move_mouse((button_coordinates[light][0] + 0.01, button_coordinates[light][1]))
    time.sleep(0.15)
    click_mouse()
    is_light_on = False

def check_foxy():
    global last_foxy_check
    global is_left_door_closed

    last_foxy_check = 0

    # Open camera and wait for it to open
    toggle_camera()
    wait_until(is_camera_up, 5)

    # Switch to the west hall briefly to make Foxy run if he's there
    camera("west_hall")
    time.sleep(0.05)
    camera("hall_corner")
    time.sleep(0.05)

    # Close the camera
    toggle_camera()

    # Close the left door
    if not is_left_door_closed:
        is_left_door_closed = True
        toggle_button("left_door")
    else:
        time.sleep(0.5)

    # Continue game loop starting with checking Chica
    check_chica()
    flip_camera()

def check_chica():
    global is_right_door_closed
    global is_robot_at_door

    # Check right light
    check_light("right_light")

    # Toggle door accordingly
    if is_robot_at_door and not is_right_door_closed:
        is_right_door_closed = True
        toggle_button("right_door")
    elif is_right_door_closed and not is_robot_at_door:
        is_right_door_closed = False
        toggle_button("right_door")
    is_robot_at_door = False

def move_mouse(position):
    mouse.position = (position[0] * sct.monitors[1]["width"], position[1] * sct.monitors[1]["height"])

def click_mouse():
    mouse.press()
    time.sleep(0.02)
    mouse.release()
    time.sleep(0.02)

def get_pixel(position, screenshot):
    return screenshot.pixel([position[0] * main_monitor["width"], position[1] * main_monitor["height"]])

def get_stars():
    for _ in range(10):
        if not star_1:
            return 0
        
        time.sleep(0.1)
    
    for _ in range(10):
        if not star_2:
            return 1
        
        time.sleep(0.1)

    for _ in range(10):
        if not star_3:
            return 2
        
        time.sleep(0.1)
    
    return 3

def wait_until(condition, maxTime):
    global has_timed_out

    has_timed_out = False
    end_time = time.time() + maxTime
    while not condition():
        if time.time() >= end_time:
            has_timed_out = True
            break

        time.sleep(0.01)

# This controls the flow of the game
def game_loop():
    global is_on_title_screen
    global is_in_office

    # Wait for the title screen
    while True:
        while True:
            time.sleep(1)
            if is_on_title_screen or is_in_office:
                break

        if is_on_title_screen and not is_in_office:
            # Detect how many stars there are
            stars = get_stars()

            if stars == 3:
                os._exit(1)
            
            move_mouse(button_coordinates[["continue", "sixth_night", "custom_night"][stars]])
            
            click_mouse()
            time.sleep(1)
            
            if stars == 2:
                # Set the mode to 20/20/20/20
                time.sleep(3)

                for animatronic in animatronics:
                    move_mouse(button_coordinates[f"{animatronic}_arrow"])
                    for _ in range(default_animatronic_levels[animatronic]):
                        time.sleep(1)
                        click_mouse()

                move_mouse(button_coordinates["ready"])
                click_mouse()
            
            is_on_title_screen = False

        if is_in_office:
            # Start office loop after 3 seconds
            time.sleep(3)
            office_loop()
            time.sleep(1)
            is_in_office = False
    
# This loop is for checking states of the game and setting variables
def update_states():
    global is_facing_right
    global is_robot_at_door
    global is_camera_up
    global is_on_title_screen
    global star_1
    global star_2
    global star_3
    global is_in_office

    while True:
        screenshot = sct.grab(main_monitor)
        try:
            # If left door button in frame, then facing left
            pixel_check = get_pixel(scan_coordinates["left_door"], screenshot)
            if do_colors_match(color_1=(109, 0, 0), color_2=pixel_check, tolerance=50 / 3 ** 0.5):
                is_facing_right = False
            if do_colors_match(color_1=(29, 107, 0), color_2=pixel_check, tolerance=80 / 3 ** 0.5):
                is_facing_right = False

            # If right door button in frame, then facing right
            pixel_check = get_pixel(scan_coordinates["right_door"], screenshot)
            if do_colors_match(color_1=(163, 0, 0), color_2=pixel_check, tolerance=50 / 3 ** 0.5):
                is_facing_right = True
            if do_colors_match(color_1=(35, 128, 0), color_2=pixel_check, tolerance=80 / 3 ** 0.5):
                is_facing_right = True

            # If restroom button in frame, then camera is open
            pixel_check = get_pixel(scan_coordinates["camera_check"], screenshot)
            is_camera_up = do_colors_match(color_1=(66, 66, 66), color_2=pixel_check, tolerance=2 / 3 ** 0.5)

            # Detect animatronics at the door
            if is_light_on:
                if is_facing_right:
                    pixel_check = get_pixel(scan_coordinates["chica_check"], screenshot)
                    if do_colors_match(color_1=(86, 95, 9), color_2=pixel_check, tolerance=20 / 3 ** 0.5):
                        is_robot_at_door = True
                else: # Facing left
                    # If door closed, check for Bonnie's shadow
                    if is_left_door_closed:
                        bonnie_pixel_1 = get_pixel(scan_coordinates["bonnie_check_1"], screenshot)
                        bonnie_pixel_2 = get_pixel(scan_coordinates["bonnie_check_2"], screenshot)
                        if do_colors_match(color_1=(0, 0, 0), color_2=bonnie_pixel_1) and do_colors_match(color_1=(30, 42, 65), color_2=bonnie_pixel_2, tolerance=5 / 3 ** 0.5):
                            is_robot_at_door = True
                    else:
                        pixel_check = get_pixel(scan_coordinates["bonnie_check_door"], screenshot)
                        if do_colors_match(color_1r=(54, 37, 63), color_2=pixel_check, tolerance=10 / 3 ** 0.5):
                            is_robot_at_door = True
                
                # Detect if you're on the title screen
            pixel_check = get_pixel(scan_coordinates["title_check"], screenshot)
            is_on_title_screen = do_colors_match(color_1=(255, 255, 255), color_2=pixel_check)

            # Detect the stars on the menu
            pixel_check = get_pixel(scan_coordinates["star_1"], screenshot)
            star_1 = do_colors_match(color_1=(255, 255, 255), color_2=pixel_check)
            if star_1:
                pixel_check = get_pixel(scan_coordinates["star_2"], screenshot)
                star_2 = do_colors_match(color_1=(255, 255, 255), color_2=pixel_check)
            if star_2:
                pixel_check = get_pixel(scan_coordinates["star_3"], screenshot)
                star_3 = do_colors_match(color_1=(255, 255, 255), color_2=pixel_check)
            
            # Detect if inside the office
            pixel_check = get_pixel(scan_coordinates["office_check"], screenshot)
            is_in_office = do_colors_match(color_1=(35, 235, 31), color_2=pixel_check, tolerance=5 / 3 ** 0.5)
        except:
            pass

        time.sleep(0.05)

if __name__ == "__main__":
    def is_running(name):
        for i in psutil.process_iter(["name"]):
            if i.info["name"] == name:
                return True
        return False
    
    keyboard.add_hotkey("esc", lambda: os._exit(0))
    
    print("Program started! Waiting for game to open...")

    # Wait for the game to open before starting anything
    while True:
        time.sleep(2)
        if is_running("FiveNightsatFreddys.exe"):
            break

    # Wait 5 seconds to make sure the game is open in fullscreen
    time.sleep(5)

    game_loop_thread = threading.Thread(target=game_loop)
    update_states_thread = threading.Thread(target=update_states)
    game_loop_thread.start()
    update_states_thread.start()