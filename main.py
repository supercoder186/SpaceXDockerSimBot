import time
from math import floor

import pyautogui
from selenium.webdriver import Chrome

import action
from action_sequencer import action_sequencer

driver = Chrome()
driver.maximize_window()
driver.get("https://iss-sim.spacex.com/")
time.sleep(17)
pyautogui.moveTo(960, 640)
pyautogui.click()

time.sleep(8)

align = action.align(driver)
switcher = action.switch_accuracy()
translate_initial = action.translate(driver, 60, 35, target_speed_coarse=16)
translate_approach = action.translate(driver, 15, 5, target_accuracy=0.1)
translate_final = action.translate(driver, 10, 2, target_accuracy=0.0, target_speed_precise=2)
translate_dock = action.translate(driver, 3, 0, target_accuracy=0.0, target_speed_precise=2)
actions = [align, switcher, translate_initial, translate_approach, switcher, align, translate_final, translate_dock]
sequencer = action_sequencer(actions)
start = time.time()
sequencer.run()
end = time.time()
seconds = end - start
minutes = floor(seconds / 60)
seconds = seconds % 60
print("Time taken: %s minutes and %.2f seconds" % (minutes, seconds))
