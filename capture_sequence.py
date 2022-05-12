import numpy as np
import scipy
from scipy import signal
import time
import BT_Capture


class CaptureSequence:

    def __init__(self, max_iteration, max_waveform_index, capture_range,
                 waveform_padding_range, waveform_min_threshold, max_num_of_zero_crossing, pulse_width,
                 pulse_padding, filename, center_frequency,
                 sample_rate, capture_time):

        self.max_iteration = max_iteration
        self.max_waveform_index = max_waveform_index
        self.capture_range = capture_range
        self.waveform_padding_range = waveform_padding_range
        self.waveform_min_threshold = waveform_min_threshold
        self.max_num_of_zero_crossing = max_num_of_zero_crossing
        self.pulse_width = pulse_width
        self.pulse_padding = pulse_padding
        self.filename = filename
        self.center_frequency = center_frequency
        self.sample_rate = sample_rate
        self.capture_time = capture_time


def number_of_zero_crossing(waveform):
    zero_crossings = np.where(np.diff(np.sign(np.real(waveform))))[0]
    return zero_crossings.size


def get_waveform_sample(current_waveform_index, capture_range_local, filename_local):
    return np.fromfile(open(filename_local), dtype=np.complex64,
                       offset=(current_waveform_index * capture_range_local),
                       count=capture_range_local)


def get_pulse(current_waveform_index, capture_range_local, waveform_padding_range_local, current_sample,
              filename_local):
    padding_sample = np.fromfile(open(filename_local), dtype=np.complex64, offset=(current_waveform_index + 8) *
                                                                                  capture_range_local,
                                 count=waveform_padding_range_local)
    return np.concatenate((current_sample, padding_sample), dtype=np.complex64)


def get_greatest_real_waveform_value(waveform):
    return np.amax(np.real(waveform))


def is_waveform_null(waveform):
    if np.size(waveform) == 0:
        return True
    else:
        return False


def capture_waveform(center_frequency_local, samp_rate_local, capture_time_local):
    btc = BT_Capture.BT_Capture(center_frequency_local, samp_rate_local)
    btc.start()
    time.sleep(capture_time_local)
    btc.stop()
    btc.wait()


def find_pulse(max_waveform_index_local, capture_range_local, waveform_padding_range_local,
               waveform_min_threshold_local,
               max_num_of_zero_crossing_local, filename_local):
    for waveform_index in range(max_waveform_index_local):
        first_sample = get_waveform_sample(waveform_index, capture_range_local, filename_local)
        if not is_waveform_null(first_sample):
            if get_greatest_real_waveform_value(first_sample) >= waveform_min_threshold_local:
                if number_of_zero_crossing(first_sample) < max_num_of_zero_crossing_local:
                    pulse = get_pulse(waveform_index, capture_range_local, waveform_padding_range_local,
                                      first_sample,
                                      filename_local)
                    return [True, pulse]

    return [False, 0]


def center_pulse(pulse, capture_range_local, waveform_padding_range_local, pulse_width_local,
                 pulse_padding_local):
    hann_window = signal.windows.hann(pulse_width_local)

    convoluted_signal = scipy.signal.convolve(pulse, hann_window, mode='same',
                                              method='direct')

    convolution_max = np.where(convoluted_signal == np.amax(convoluted_signal))
    if len(convolution_max[0]) > 1:
        return False
    pulse_center = int(convolution_max[0])
    if ((capture_range_local + waveform_padding_range_local) - (
            (pulse_width_local / 2) + pulse_padding_local)) >= \
            pulse_center >= ((pulse_width_local / 2) + pulse_padding_local):
        centered_pulse = pulse[int(pulse_center - ((pulse_width_local / 2) + pulse_padding_local)):int(
            pulse_center + ((pulse_width_local / 2) + pulse_padding_local))]
    else:
        return [False, 0]

    return [True, centered_pulse]


def get_pulse_average(pulse_list_local, num_pulse, pulse_width_local, pulse_padding_local):
    pulse_sum = np.zeros(pulse_width_local + (pulse_padding_local * 2), dtype=np.complex64)
    for current_pulse in range(num_pulse):
        pulse_sum = pulse_sum + pulse_list_local[current_pulse]

    average_pulse_local = pulse_sum / num_pulse

    return average_pulse_local


def get_device_pulse_average(max_iteration, max_waveform_index, capture_range,
                             waveform_padding_range, waveform_min_threshold, max_num_of_zero_crossing, pulse_width,
                             pulse_padding, filename, center_frequency,
                             sample_rate, capture_time):
    pulse_list = np.empty((max_iteration, capture_range + waveform_padding_range), np.complex64)
    pulse_list_centered = np.empty((max_iteration, pulse_width + (pulse_padding * 2)), np.complex64)

    current_iteration = 0
    while current_iteration < max_iteration:
        print("Iteration: ")
        print(current_iteration)
        capture_waveform(center_frequency, sample_rate, capture_time)
        # see_waveform(0, -1, filename_local, 2)
        # plt.show()

        [is_pulse, pulse_list[current_iteration]] = find_pulse(max_waveform_index, capture_range,
                                                               waveform_padding_range,
                                                               waveform_min_threshold,
                                                               max_num_of_zero_crossing, filename)
        if is_pulse:
            [is_pulse_centered, pulse_list_centered[current_iteration]] = center_pulse(
                pulse_list[current_iteration],
                capture_range,
                waveform_padding_range,
                pulse_width,
                pulse_padding)
            if not is_pulse_centered:
                current_iteration = current_iteration - 1
                print("Pulse Ignored")
        else:
            current_iteration = current_iteration - 1
            print("Pulse Ignored")
        current_iteration = current_iteration + 1

    average_pulse = get_pulse_average(pulse_list_centered, max_iteration, pulse_width,
                                      pulse_padding)

    np.savetxt("pulse_list.csv", pulse_list, delimiter=",")
    np.savetxt("pulse_list_centered.csv", pulse_list_centered, delimiter=",")
    np.savetxt("average_pulse.csv", average_pulse, delimiter=",")
