import numpy as np
from scipy.stats import multivariate_normal
import multi_gauss_model


class ValidateCapture:

    def __init__(self, model, capture):
        self.model = model
        self.capture = capture

        self.device_captured_noise_vector = get_captured_noise_vector(model.device_pulse_average,
                                                                      capture,
                                                                      model.points_of_large_difference
                                                                      )

        self.device_captured_probability_distribution = get_captured_probability_distribution(
            model.device_covariance_matrix, self.device_captured_noise_vector)


def get_captured_noise_vector(device_pulse_average, captured_trace, points_of_large_difference):
    captured_noise_vector = np.empty((len(device_pulse_average[:, 0]), len(points_of_large_difference)),
                                     np.complex64)

    for current_device in range(len(device_pulse_average[:, 0])):
        for current_point in range(len(points_of_large_difference)):
            captured_noise_vector[current_device][current_point] = \
                device_pulse_average[current_device][points_of_large_difference[current_point]] - \
                captured_trace[points_of_large_difference[current_point]]

    return captured_noise_vector


def get_captured_probability_distribution(noise_covariance_matrix, captured_noise_vector):
    captured_probability_distribution = np.zeros(3, float)

    for current_device in range(len(noise_covariance_matrix[:, 0, 0])):
        captured_probability_distribution[current_device] = multivariate_normal.pdf(
            np.real(captured_noise_vector[current_device][:]),
            cov=np.real(noise_covariance_matrix[current_device][:][:]))

    return captured_probability_distribution
