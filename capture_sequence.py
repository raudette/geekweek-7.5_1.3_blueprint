import numpy as np
import time
import BT_Capture
import matplotlib.pyplot as plt


class CaptureSequence:

    def __init__(self, max_iteration, waveform_min_threshold, device_name, center_frequency, sample_rate, capture_time):
        self.max_iteration = max_iteration
        self.waveform_preamble = int(sample_rate / 4e5)
        self.waveform_padding = int(sample_rate / 8e4)
        self.waveform_min_threshold = waveform_min_threshold
        self.device_name = device_name
        self.center_frequency = center_frequency
        self.sample_rate = sample_rate
        self.capture_time = capture_time

        [average_pulse, pulse_list] = get_device_pulse_list(self.max_iteration, self.waveform_min_threshold, self.
                                                            device_name, self.center_frequency, self.sample_rate,
                                                            self.capture_time, self.waveform_preamble, self.
                                                            waveform_padding)


def get_waveform_sample(current_waveform, capture_range, filename):
    return np.fromfile(open(filename), dtype=np.complex64, offset=current_waveform,
                       count=capture_range)


def get_greatest_real_waveform_value(waveform):
    return np.amax(np.real(waveform))


def capture_waveform(center_frequency_local, sample_rate_local, capture_time_local, device_name):
    btc = BT_Capture.BT_Capture(center_frequency_local, sample_rate_local, device_name)
    btc.start()
    time.sleep(capture_time_local)
    btc.stop()
    # btc.wait()


def get_pulse_average(pulse_list, pulse_width):
    pulse_sum = np.zeros(pulse_width, dtype=np.complex64)
    for current_pulse in range(len(pulse_list[:])):
        pulse_sum = pulse_sum + pulse_list[current_pulse]

    average_pulse_local = pulse_sum / len(pulse_list[:])

    return average_pulse_local


def find_pulse(waveform_min_threshold, waveform_preamble, waveform_padding, device_name):
    sample = get_waveform_sample(0, -1, "./data/" + device_name + "/capture.bin")
    first_rise = np.where(abs(sample) > waveform_min_threshold)
    if len(first_rise[0]) >= 1:
        if first_rise[0][0] > 6000:
            pulse = sample[first_rise[0][0] - waveform_preamble:first_rise[0][0] + waveform_padding]
            return [True, pulse]

    return [False, range(waveform_preamble + waveform_padding)]


def get_device_pulse_list(max_iteration, waveform_min_threshold, device_name, center_frequency, sample_rate,
                          capture_time, waveform_preamble, waveform_padding):
    pulse_list = np.empty((max_iteration, waveform_preamble + waveform_padding), np.complex64)

    current_iteration = 0
    while current_iteration < max_iteration:
        print("Iteration: ")
        print(current_iteration)
        capture_waveform(center_frequency, sample_rate, capture_time, "./data/" + device_name + "/capture.bin")

        [is_pulse, pulse_list[current_iteration]] = find_pulse(waveform_min_threshold, waveform_preamble,
                                                               waveform_padding, device_name)
        if not is_pulse:
            current_iteration = current_iteration - 1
            print("Pulse Ignored")
        else:
            with open("./data/" + device_name + "/pulse_list.csv", 'a') as csvfile:
                np.savetxt(csvfile, pulse_list[[current_iteration]], delimiter=",")

        current_iteration = current_iteration + 1

    return [pulse_list]
