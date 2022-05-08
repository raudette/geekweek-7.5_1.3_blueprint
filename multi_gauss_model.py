import numpy as np


class MultiGaussModel:

    def __init__(self, device_pulse_average_files, device_pulse_centered_files, number_of_greatest_values):
        self.device_pulse_average_files = device_pulse_average_files
        self.device_pulse_centered_files = device_pulse_centered_files
        self.number_of_greatest_values = number_of_greatest_values

        self.device_pulse_average = np.empty((3, 90), np.complex64)
        self.device_pulse_centered = np.empty((3, 100, 90), np.complex64)

        for device in range(len(device_pulse_average_files)):
            self.device_pulse_average[device][:] = np.loadtxt(device_pulse_average_files[device],
                                                              dtype=np.complex128).view(complex)

        for device in range(len(device_pulse_centered_files)):
            self.device_pulse_centered[device][:][:] = np.loadtxt(device_pulse_centered_files[device],
                                                                  delimiter=",", dtype=np.complex128).view(complex)

        self.points_of_large_difference = find_best_points_to_compare(self.device_pulse_average,
                                                                      self.number_of_greatest_values)

        self.device_covariance_matrix = get_optimal_noise_covariance_matrix(self.device_pulse_average,
                                                                            self.points_of_large_difference,
                                                                            self.device_pulse_centered)


def find_best_points_to_compare(device_pulse_average, number_of_greatest_values):
    def sum_of_pairwise_compare(device_pulse_average):

        pairwise_compared = np.zeros(len(device_pulse_average[0, :]), float)

        for point in range(len(device_pulse_average[0, :])):
            for device_first_compared in device_pulse_average[:, point]:
                for device_second_compared in device_pulse_average[:, point]:
                    pairwise_compared[point] = pairwise_compared[point] + \
                                               abs(device_first_compared - device_second_compared)

        return pairwise_compared

    def find_n_greatest_values_1d(array_of_values, number_of_greatest_values):

        maximum_index = np.zeros(number_of_greatest_values, int)

        for current_value in range(number_of_greatest_values):
            maximum_index[current_value] = np.argmax(array_of_values)
            array_of_values[maximum_index[current_value]] = 0

        return maximum_index

    return find_n_greatest_values_1d(sum_of_pairwise_compare(device_pulse_average),
                                     number_of_greatest_values)


def get_optimal_noise_covariance_matrix(device_pulse_average, points_of_large_difference,
                                        device_pulse_centered):
    def get_noise_covariance_matrix(device_pulse_average_local, device_pulse_centered_local,
                                    indexes):

        noise_vector = np.empty((len(device_pulse_average_local[:, 0]), len(device_pulse_centered_local[0, :, 0]),
                                 len(indexes)), np.complex64)
        noise_covariance_matrix = np.empty((len(device_pulse_average_local[:, 0]),
                                            len(indexes), len(indexes)), np.complex64)

        for current_device in range(len(device_pulse_average_local[:, 0])):
            for current_sample in range(len(device_pulse_centered_local[0, :, 0])):
                for current_point in range(len(indexes)):
                    noise_vector[current_device][current_sample][current_point] = \
                        device_pulse_centered_local[current_device, current_sample,
                                                    indexes[current_point]] - device_pulse_average_local[
                            current_device, indexes[current_point]]

            noise_covariance_matrix[current_device][:][:] = np.cov(
                np.transpose(noise_vector[current_device, :, :]))

        return noise_covariance_matrix

    return get_noise_covariance_matrix(device_pulse_average, device_pulse_centered, points_of_large_difference)

    #                               |  point6
    #                               |  point5
    #                               |  point4      Pick the points where SUM[n,m]abs(xn-xm) is the greatest
    #                               |  point3
    #                   x(n)        |  point2
    #          _____________________|  point1
    #                                \
    #                                 \
    #                                  \  x(m)
    #                                   \
    #                                    \
    #
