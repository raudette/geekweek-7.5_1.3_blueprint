# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import scipy
from scipy import signal
import numpy as np
import matplotlib.pyplot as plt
import serial
import time
import BT_Capture
import multi_gauss_model
import validate_capture


def check_serial_connection():
    prev = time.time()
    setup = False
    port = None
    while not setup:
        try:
            port = serial.Serial("/dev/ttyUSB0", 115200, timeout=1)

        except:
            if time.time() - prev > 2:
                print("No serial detected, please plug your uController")
                prev = time.time()

        if port is not None:
            setup = True
            return port


def display_data(data, fig_num):
    fig_local = plt.figure(fig_num, figsize=(5, 3.5))
    ax_local = fig_local.add_subplot(1, 1, 1)
    x_r_local = np.real(data)
    x_i_local = np.imag(data)
    ax_local.plot(x_r_local, 'b', label='real')
    ax_local.plot(x_i_local, 'r', label='imag')
    ax_local.set_xlabel('x')
    ax_local.set_ylabel('y')
    ax_local.legend(loc='upper right')
    ax_local.set_title('Scatter plot and line')


def number_of_zero_crossing(waveform):
    zero_crossings = np.where(np.diff(np.sign(np.real(waveform))))[0]
    return zero_crossings.size


def get_waveform_sample(current_waveform_index, capture_range_local, filename_local):
    return np.fromfile(open(filename_local), dtype=np.complex64, offset=(current_waveform_index * capture_range_local),
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
    # port = check_serial_connection()
    btc = BT_Capture.BT_Capture(center_frequency_local, samp_rate_local)
    # port.write(b'1')
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
                    pulse = get_pulse(waveform_index, capture_range_local, waveform_padding_range_local, first_sample,
                                      filename_local)
                    return [True, pulse]

    return [False, 0]


def center_pulse(pulse, capture_range_local, waveform_padding_range_local, pulse_width_local, pulse_padding_local):
    hann_window = signal.windows.hann(pulse_width_local)

    convoluted_signal = scipy.signal.convolve(pulse, hann_window, mode='same',
                                              method='direct')

    convolution_max = np.where(convoluted_signal == np.amax(convoluted_signal))
    if len(convolution_max[0]) > 1:
        return False
    pulse_center = int(convolution_max[0])
    if ((capture_range_local + waveform_padding_range_local) - ((pulse_width_local / 2) + pulse_padding_local)) >= \
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


def see_waveform(start_index, stop_index, filename_local, fig_num):
    waveform_sample = np.fromfile(open(filename_local), dtype=np.complex64, offset=start_index,
                                  count=(stop_index - start_index))

    display_data(waveform_sample, fig_num)


def get_device_pulse_average(max_iteration_local, max_waveform_index_local, capture_range_local,
                             waveform_padding_range_local, pulse_width_local,
                             pulse_padding_local, filename_local, output_figure_number, center_frequency_local,
                             samp_rate_local, capture_time_local):

    pulse_list = np.empty((max_iteration, capture_range_local + waveform_padding_range_local), np.complex64)
    pulse_list_centered = np.empty((max_iteration, pulse_width_local + (pulse_padding_local * 2)), np.complex64)

    current_iteration = 0
    while current_iteration < max_iteration_local:
        print("Iteration: ")
        print(current_iteration)
        capture_waveform(center_frequency_local, samp_rate_local, capture_time_local)
        # see_waveform(0, -1, filename_local, 2)
        # plt.show()

        [is_pulse, pulse_list[current_iteration]] = find_pulse(max_waveform_index_local, capture_range_local,
                                                               waveform_padding_range_local,
                                                               waveform_min_threshold,
                                                               max_num_of_zero_crossing, filename_local)
        if is_pulse:
            [is_pulse_centered, pulse_list_centered[current_iteration]] = center_pulse(pulse_list[current_iteration],
                                                                                       capture_range_local,
                                                                                       waveform_padding_range_local,
                                                                                       pulse_width_local,
                                                                                       pulse_padding_local)
            if not is_pulse_centered:
                current_iteration = current_iteration - 1
                print("Pulse Ignored")
        else:
            current_iteration = current_iteration - 1
            print("Pulse Ignored")
        current_iteration = current_iteration + 1

    average_pulse = get_pulse_average(pulse_list_centered, max_iteration_local, pulse_width_local, pulse_padding_local)

    display_data(average_pulse, output_figure_number)

    np.savetxt("pulse_list.csv", pulse_list, delimiter=",")
    np.savetxt("pulse_list_centered.csv", pulse_list_centered, delimiter=",")
    np.savetxt("average_pulse.csv", average_pulse, delimiter=",")

    plt.show()


def sweep_all_channels():
    fig = 1
    for frequency in np.arange(2.402e9, 2.480e9, 0.002e9):
        capture_waveform(frequency, samp_rate, 2)
        data = get_waveform_sample(0, -1, filename)
        if get_greatest_real_waveform_value(data) >= 0.08:
            display_data(data, fig)
        fig = fig + 1
    plt.show()


def capture_specific_frequency(center_frequency_local, samp_rate_local, capture_time_local, filename_local):
    capture_waveform(center_frequency_local, samp_rate_local, capture_time_local)
    data = get_waveform_sample(0, -1, filename_local)
    display_data(data, 1)
    plt.show()


def test_capture_trial(number_of_greatest_values, capture_device, capture_sample):
    test_model = multi_gauss_model.MultiGaussModel(['./data/Model_Data/ESP1/ESP1_1/average_pulse.csv',
                                                    './data/Model_Data/ESP2/ESP2_1/average_pulse.csv',
                                                    './data/Model_Data/Tile/TILE_1/average_pulse.csv'], [
                                                       './data/Model_Data/ESP1/ESP1_1/pulse_list_centered.csv',
                                                       './data/Model_Data/ESP2/ESP2_1/pulse_list_centered.csv',
                                                       './data/Model_Data/Tile/TILE_1/pulse_list_centered.csv'],
                                                   number_of_greatest_values)

    test_capture = validate_capture.ValidateCapture(test_model, test_model.device_pulse_centered[capture_device]
                                                                [capture_sample][:])

    device_captured_probability_distribution = test_capture.device_captured_probability_distribution

    p_ESP1 = device_captured_probability_distribution[0]
    p_ESP2 = device_captured_probability_distribution[1]
    p_TILE = device_captured_probability_distribution[2]

    if p_ESP1 > p_ESP2 and p_ESP1 > p_TILE:
        print("From Device ESP1")
        print(p_ESP1)
        print(p_ESP2)
        print(p_TILE)
    if p_ESP2 > p_ESP1 and p_ESP2 > p_TILE:
        print("From Device ESP2")
        print(p_ESP1)
        print(p_ESP2)
        print(p_TILE)
    if p_TILE > p_ESP2 and p_TILE > p_ESP1:
        print("From Device TILE")
        print(p_ESP1)
        print(p_ESP2)
        print(p_TILE)

    fig_local = plt.figure(1, figsize=(5, 3.5))
    x_r_1 = np.real(test_model.device_pulse_average[0])
    x_i_1 = np.imag(test_model.device_pulse_average[0])
    x_r_2 = np.real(test_model.device_pulse_average[1])
    x_i_2 = np.imag(test_model.device_pulse_average[1])
    x_r_3 = np.real(test_model.device_pulse_average[2])
    x_i_3 = np.imag(test_model.device_pulse_average[2])
    x_r_4 = np.real(test_model.device_pulse_centered[capture_device][capture_sample])
    x_i_4 = np.imag(test_model.device_pulse_centered[capture_device][capture_sample])
    ax_local = fig_local.add_subplot(2, 2, 1)
    ax_local.plot(x_r_1, 'b', label='real')
    ax_local.plot(x_i_1, 'r', label='imag')
    ax_local = fig_local.add_subplot(2, 2, 2)
    ax_local.plot(x_r_2, 'b', label='real')
    ax_local.plot(x_i_2, 'r', label='imag')
    ax_local = fig_local.add_subplot(2, 2, 3)
    ax_local.plot(x_r_3, 'b', label='real')
    ax_local.plot(x_i_3, 'r', label='imag')
    ax_local = fig_local.add_subplot(2, 2, 4)
    ax_local.plot(x_r_4, 'b', label='real')
    ax_local.plot(x_i_4, 'r', label='imag')
    ax_local.set_xlabel('x')
    ax_local.set_ylabel('y')
    ax_local.legend(loc='upper right')
    ax_local.set_title('Scatter plot and line')

    plt.show()


filename = './data/BT_Capture_test.bin'

max_iteration = 100
max_waveform_index = 160000
capture_range = 500
waveform_padding_range = 200
waveform_min_threshold = 0.4
max_num_of_zero_crossing = 500000
pulse_width = 50
pulse_padding = 20
center_frequency = 2.402e9
samp_rate = 5e6
capture_time = 1

number_of_greatest_values = 90
capture_device = 2
capture_sample = 50

# get_device_pulse_average(max_iteration, max_waveform_index, capture_range, waveform_padding_range, pulse_width,
# pulse_padding, filename, 1, center_frequency, samp_rate, capture_time)

# sweep_all_channels()

# capture_specific_frequency(center_frequency, samp_rate, capture_time, filename)

test_capture_trial(number_of_greatest_values, capture_device, capture_sample)