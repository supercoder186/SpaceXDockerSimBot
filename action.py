import re
import time

import pyautogui


def float_parse(string):
    re_expression = '-?\\d+\\.\\d'
    if string:
        return float(re.search(re_expression, string).group(0))
    else:
        time.sleep(1)


def sign(x):
    return int(x and (1, 0)[x < 0])


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


class align(action):
    def __init__(self, driver, target_accuracy=0.2, target_speed_precise=0.1, target_speed_coarse=0.5,
                 target_speed_transition=4, refine=True):
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

    def get_errors(self):
        errors = []
        txt = float_parse(self.div_pitch.text)
        errors.append(float(txt))

        txt = float_parse(self.div_roll.text)
        errors.append(float(txt))

        txt = float_parse(self.div_yaw.text)
        errors.append(float(txt))
        return errors

    def get_rates(self):
        rates = []
        txt = float_parse(self.div_pitch_rate.text)
        rates.append(float(txt))

        txt = float_parse(self.div_roll_rate.text)
        rates.append(float(txt))

        txt = float_parse(self.div_yaw_rate.text)
        rates.append(float(txt))
        return rates

    def get_targets(self, errors):
        targets = []
        for error in errors:
            absoluteError = abs(error)
            if absoluteError > self.target_accuracy:
                if absoluteError > self.target_speed_transition:
                    targets.append(self.target_speed_coarse * (error / absoluteError))
                else:
                    targets.append(self.target_speed_precise * (error / absoluteError))
            else:
                targets.append(0)

        return targets

    def set_targets(self, targets, rates):
        for i in range(len(targets)):
            delta = int((targets[i] - rates[i]) * 10)
            key = self.keys[i][sign(delta)]
            if delta:
                pyautogui.press(key, presses=abs(delta))

    def refine_spacecraft_orientation(self, errors):
        for i in range(len(errors)):
            error = errors[i]
            key = sign(error)
            absoluteError = abs(error)
            if absoluteError > self.target_accuracy:
                pyautogui.press(self.keys[i][key], presses=1)
                time.sleep(int(absoluteError * 5))
                pyautogui.press(self.keys[i][1 - key], presses=1)

    def zero_rates(self, rates):
        self.set_targets([0.0, 0.0, 0.0], rates)

    def loop_condition(self, errors):
        for error in errors:
            absoluteError = abs(error)
            if absoluteError > self.target_accuracy:
                return False

        return True

    def run(self):
        rates = self.get_rates()
        errors = self.get_errors()
        while not self.loop_condition(errors):
            targets = self.get_targets(errors)
            self.set_targets(targets, rates)
            errors = self.get_errors()
            rates = self.get_rates()

        self.zero_rates(rates)
        if self.refine:
            errors = self.get_errors()
            self.refine_spacecraft_orientation(errors)
            rates = self.get_rates()
            self.zero_rates(rates)


class switch_accuracy(action):
    def run(self):
        pyautogui.moveTo(175, 900)
        pyautogui.click()


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

    def get_rates(self):
        return self.vel

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

    def set_targets(self, targets, rates):
        for i in range(len(targets)):
            delta = int(targets[i] - rates[i])
            key = sign(delta)
            pyautogui.press(self.keys[i][key], presses=abs(delta))

    def zero_rates(self, rates):
        self.set_targets([0.0, 0.0, 0.0], rates)

    def loop_condition(self):
        iss_range = float_parse(self.div_range.text)
        if iss_range is not None:
            return iss_range < self.upto_range
        else:
            return False

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
