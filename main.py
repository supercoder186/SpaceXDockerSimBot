import time
from math import floor

import pyautogui
from selenium.webdriver import Chrome

import action
from action_sequencer import action_sequencer

# load the chromedriver.exe file into selenium
driver = Chrome()

# maximise the window
driver.maximize_window()
driver.get("https://iss-sim.spacex.com/")

# wait for the screen to load, and then click the "begin" button
# the values in the program are for a 1080p screen. You'll have to edit them if you have a different screen size
time.sleep(17)
pyautogui.moveTo(960, 640)
pyautogui.click()

# wait for the simulator to load
time.sleep(8)

# create a new align action
align = action.align(driver)

# create a switch accuracy action
switcher = action.switch_accuracy()

# create a translate action to bring the bot to 35m out at 60 speed. Note that the speed is an arbitrary unit
translate_initial = action.translate(driver, 60, 35, target_speed_coarse=16)

# create a translate action to begin the "approach" - move at 15 speed to 5m out
translate_approach = action.translate(driver, 15, 5, target_accuracy=0.1)

# at this point the accuracy is switched
translate_final = action.translate(driver, 10, 2, target_accuracy=0.0, target_speed_precise=2)

# align the bot again to ensure that the bot is aligned properly
# finally, bring the bot in from 2m at a very slow speed
translate_dock = action.translate(driver, 3, 0, target_accuracy=0.0, target_speed_precise=2)

# create a sequence array
actions = [align, switcher, translate_initial, translate_approach, switcher, align, translate_final, translate_dock]

# create an action sequencer and run it
sequencer = action_sequencer(actions)

# start the timer
start = time.time()
sequencer.run()

# end the timer, calculate minutes and seconds taken, and then output it
end = time.time()
seconds = end - start
minutes = floor(seconds / 60)
seconds = seconds % 60
print("Time taken: %s minutes and %.2f seconds" % (minutes, seconds))
