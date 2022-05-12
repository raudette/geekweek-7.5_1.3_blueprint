# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import numpy as np
import matplotlib.pyplot as plt
import multi_gauss_model
import validate_capture
import capture_sequence


def sweep_all_channels():
    fig = 1
    for frequency in np.arange(2.402e9, 2.480e9, 0.002e9):
        capture_sequence.capture_waveform(frequency, samp_rate, 2)
        data = capture_sequence.get_waveform_sample(0, -1, filename)
        if capture_sequence.get_greatest_real_waveform_value(data) >= 0.08:
            fig = plt.figure(fig, figsize=(5, 3.5))
            x_r_1 = np.real(data)
            x_i_1 = np.imag(data)
            ax = fig.add_subplot(1, 1, 1)
            ax.plot(x_r_1, 'b', label='real')
            ax.plot(x_i_1, 'r', label='imag')
            ax.set_xlabel('x')
            ax.set_ylabel('y')
            ax.legend(loc='upper right')
            ax.set_title('Scatter plot and line')
            fig = fig + 1
        plt.show()


def capture_specific_frequency(center_frequency_local, samp_rate_local, capture_time_local, filename_local):
    capture_sequence.capture_waveform(center_frequency_local, samp_rate_local, capture_time_local)
    data = capture_sequence.get_waveform_sample(0, -1, filename_local)
    fig = plt.figure(fig, figsize=(5, 3.5))
    x_r_1 = np.real(data)
    x_i_1 = np.imag(data)
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(x_r_1, 'b', label='real')
    ax.plot(x_i_1, 'r', label='imag')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.legend(loc='upper right')
    ax.set_title('Scatter plot and line')
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