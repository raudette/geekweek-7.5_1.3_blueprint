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
        capture_sequence.capture_waveform(frequency, sample_rate, 2, device_name)
        data = capture_sequence.get_waveform_sample(0, -1, device_name)
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


def test_capture_trial(number_of_greatest_values, capture_device, capture_sample):

    test_model = multi_gauss_model.MultiGaussModel(['./data/ESP1/average_pulse.csv',
                                                    './data/ESP2/average_pulse.csv',
                                                    './data/TILE/average_pulse.csv'], [
                                                       './data/ESP1/pulse_list.csv',
                                                       './data/ESP2/pulse_list.csv',
                                                       './data/TILE/pulse_list.csv'],
                                                   number_of_greatest_values)

    test_capture = validate_capture.ValidateCapture(test_model, test_model.device_pulse_list[capture_device][
                                                                    capture_sample][:])

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
    x_r_4 = np.real(test_model.device_pulse_list[capture_device][capture_sample])
    x_i_4 = np.imag(test_model.device_pulse_list[capture_device][capture_sample])
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


device_name = 'TILE'

max_iteration = 1
capture_time = 5  # (Takes capture_time * sample_rate) Number of 64 bit (32 real, 32 imag) points
capture_device = 0

sample_rate = 20e6
center_frequency = 2.426e9

waveform_min_threshold = 0.1

number_of_greatest_values = 150  # points to take for Gaussian compare
capture_sample = 300
test_capture_trial(number_of_greatest_values, capture_device, capture_sample)

# test_sequence = capture_sequence.CaptureSequence(max_iteration, waveform_min_threshold, device_name, center_frequency,
#                                                  sample_rate, capture_time)

