import re
import time

import pyautogui


# parse a float from the inputted string, using regex
def float_parse(string):
    re_expression = '-?\\d+\\.\\d'
    if string:
        return float(re.search(re_expression, string).group(0))
    else:
        time.sleep(1)


# find the sign of a number. returns 0 if it is positive, and 1 otherwise
def sign(x):
    return int(x and (1, 0)[x < 0])


# create a basic action class. Not really necessary, but makes sure everything is nice and uniform
class action:
    def get_errors(self):
        pass

    def get_rates(self):
        pass

    def get_targets(self, errors):
        pass

    def set_targets(self, targets, errors):
        pass

    def zero_rates(self, rates):
        pass

    def run(self):
        pass

    def loop_condition(self, *args):
        pass


# the basic align action. aligns the spacecraft rotationally
# the description of the arguments can be found in the README file (not done just yet)
class align(action):
    def __init__(self, driver, target_accuracy=0.2, target_speed_precise=0.1, target_speed_coarse=0.5,
                 target_speed_transition=4, refine=True):
        # get all the html elements required to align the spacecraft
        self.div_pitch = driver.find_element_by_xpath('//*[@id="pitch"]/div[1]')
        self.div_pitch_rate = driver.find_element_by_xpath('//*[@id="pitch"]/div[2]')

        self.div_roll = driver.find_element_by_xpath('//*[@id="roll"]/div[1]')
        self.div_roll_rate = driver.find_element_by_xpath('//*[@id="roll"]/div[2]')

        self.div_yaw = driver.find_element_by_xpath('//*[@id="yaw"]/div[1]')
        self.div_yaw_rate = driver.find_element_by_xpath('//*[@id="yaw"]/div[2]')
        self.keys = (('up', 'down'), (',', '.'), ('left', 'right'))

        self.target_accuracy = target_accuracy
        self.target_speed_precise = target_speed_precise
        self.target_speed_coarse = target_speed_coarse
        self.target_speed_transition = target_speed_transition
        self.refine = refine

    # get rotational errors
    def get_errors(self):
        errors = []
        txt = float_parse(self.div_pitch.text)
        errors.append(float(txt))

        txt = float_parse(self.div_roll.text)
        errors.append(float(txt))

        txt = float_parse(self.div_yaw.text)
        errors.append(float(txt))
        return errors

    # get the current rotational rates
    def get_rates(self):
        rates = []
        txt = float_parse(self.div_pitch_rate.text)
        rates.append(float(txt))

        txt = float_parse(self.div_roll_rate.text)
        rates.append(float(txt))

        txt = float_parse(self.div_yaw_rate.text)
        rates.append(float(txt))
        return rates

    # get the rotational rate targets i.e. how fast the spacecraft *should* be rotating
    def get_targets(self, errors):
        targets = []

        # iterate through each error
        for error in errors:
            # get the absolute value of the error, without sign
            absoluteError = abs(error)

            # check if the error is above acceptable errors (defined by target accuracy)
            if absoluteError > self.target_accuracy:
                # check if it should be in "coarse" or "precision" mode, depending on the magnitude of the error
                if absoluteError > self.target_speed_transition:
                    targets.append(self.target_speed_coarse * (error / absoluteError))  # coarse mode
                else:
                    targets.append(self.target_speed_precise * (error / absoluteError))  # precision mode
            else:
                targets.append(0)  # this axis is acceptably aligned

        return targets

    # set the rotational targets
    def set_targets(self, targets, rates):
        # iterate through each rate target
        for i in range(len(targets)):
            # calculate the difference between the required rate and the current rate
            delta = int((targets[i] - rates[i]) * 10)

            # from this, get the key we need to press
            key = self.keys[i][sign(delta)]

            # if the delta is not 0, then apply the required moment
            if delta:
                pyautogui.press(key, presses=abs(delta))

    # refine the spacecraft's orientation (not really needed, but included for the sake of accuracy)
    def refine_spacecraft_orientation(self, errors):
        # iterate through errors and check which ones are acceptable
        for i in range(len(errors)):
            error = errors[i]
            key = sign(error)
            absoluteError = abs(error)

            # those that are not acceptable are corrected
            if absoluteError > self.target_accuracy:
                pyautogui.press(self.keys[i][key], presses=1)
                time.sleep(int(absoluteError * 5))
                pyautogui.press(self.keys[i][1 - key], presses=1)

    # stop all rotational movement. Run at the end of the alignment phase to prevent spacecraft from veering off course
    def zero_rates(self, rates):
        self.set_targets([0.0, 0.0, 0.0], rates)

    # the condition to check if the loop should continue
    def loop_condition(self, errors):
        for error in errors:
            absoluteError = abs(error)
            if absoluteError > self.target_accuracy:
                return False

        return True

    # run the action
    def run(self):
        # get the rates and errors
        rates = self.get_rates()
        errors = self.get_errors()

        # continue the loop as long as the loop condition is met
        while not self.loop_condition(errors):
            targets = self.get_targets(errors)  # get the rotational targets
            self.set_targets(targets, rates)  # set the rotational targets
            errors = self.get_errors()  # get the errors and rotational rates for the next iteration
            rates = self.get_rates()

        # zero out the rotation
        self.zero_rates(rates)

        # refine the rotation if told to
        if self.refine:
            errors = self.get_errors()
            self.refine_spacecraft_orientation(errors)
            rates = self.get_rates()
            self.zero_rates(rates)


# switch the controls accuracy. this is configured for a 1080p monitor. You'll have to change it for smaller
# or bigger monitors
class switch_accuracy(action):
    def run(self):
        pyautogui.moveTo(175, 900)
        pyautogui.click()


# the basic translate action. it will move the spacecraft to a defined range from the ISS at a defined speed
class translate(action):
    def __init__(self, driver, target_rate, upto_range, target_accuracy=0.2, target_speed_precise=2,
                 target_speed_coarse=8,
                 target_speed_transition=4, refine=True):

        self.div_range_x = driver.find_element_by_xpath('//*[@id="x-range"]/div')
        self.div_range_y = driver.find_element_by_xpath('//*[@id="y-range"]/div')
        self.div_range_z = driver.find_element_by_xpath('//*[@id="z-range"]/div')

        self.div_range = driver.find_element_by_xpath('//*[@id="range"]/div[2]')
        self.keys = (('q', 'e'), ('d', 'a'), ('w', 's'))

        self.target_accuracy = target_accuracy
        self.target_speed_precise = target_speed_precise
        self.target_speed_coarse = target_speed_coarse
        self.target_speed_transition = target_speed_transition
        self.target_rate = target_rate
        self.upto_range = upto_range
        self.vel = [0, 0, 0]
        self.refine = refine

    # get the displacement from the ISS docking port
    def get_errors(self):
        errors = []
        txt = float_parse(self.div_range_x.text)
        if txt is not None:
            errors.append(float(txt))

        txt = float_parse(self.div_range_y.text)
        if txt is not None:
            errors.append(float(txt))

        txt = float_parse(self.div_range_z.text)
        if txt is not None:
            errors.append(float(txt))
        return errors

    # get the velocity in arbitrary values
    def get_rates(self):
        return self.vel

    # get the velocity targets. The X target is set based on required speed, and the others by the guidance
    # variables
    def get_targets(self, errors):
        targets = [self.target_rate]
        for i in range(1, 3):
            error = errors[i]
            absoluteError = abs(error)
            if absoluteError > self.target_accuracy:
                if absoluteError > self.target_speed_transition:
                    targets.append(self.target_speed_coarse * (error / absoluteError))
                else:
                    targets.append(self.target_speed_precise * (error / absoluteError))
            else:
                targets.append(0)

        return targets

    # set the velocity targets. Similar to the angular target setting function. Refer to line 129 for explanation
    def set_targets(self, targets, rates):
        for i in range(len(targets)):
            delta = int(targets[i] - rates[i])
            key = sign(delta)
            pyautogui.press(self.keys[i][key], presses=abs(delta))

    # zero the movement
    def zero_rates(self, rates):
        self.set_targets([0.0, 0.0, 0.0], rates)

    # checks if the range is above the range that this action will be active upto
    def loop_condition(self):
        iss_range = float_parse(self.div_range.text)
        if iss_range is not None:
            return iss_range < self.upto_range
        else:
            return False

    # run the translate action
    def run(self):
        rates = self.get_rates()
        errors = self.get_errors()
        while not self.loop_condition():
            if len(errors) == 3:
                targets = self.get_targets(errors)
            else:
                print("Complete!")
                return
            self.set_targets(targets, rates)
            self.vel = targets
            errors = self.get_errors()
            rates = self.get_rates()

        self.zero_rates(rates)
