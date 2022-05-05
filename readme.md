# Blueprint - A Bluetooth LE PHY fingerprinting framework

Blueprint (BLE Fingerprint) is a set of tools that allows for the PHY fingerprinting of Bluetooth LE signals. The toolset aims to detect variations in the waveforms of BLE transmitters caused by differences in their physical characteristics.

The goal of this toolset in relations to the security of Bluetooth trackers is to allow for clones to be detected. From tests performed so far, the waveforms observed from a authentic Tile tracker is considerably different than what can be obtained from a cloned device that makes use of developement boards such as the ESP32 and the Raspberry Pi. As you will see from the work performed so far, there is even a noticeable difference between two identical ESP32's.

In its intended use case, this toolset could be used in populated areas to detect malicious actors who either cloned legitimate devices in their surroundings, or who use clones to bypass certain manufacturer-specific security features.

## Requirements

In terms of Tooling, the following Softwares are recommended (All tests performed were performed on Ubuntu 20.04 LTS):

1. [GNURadio](https://wiki.gnuradio.org/index.php/InstallingGR).

	$ sudo add-apt-repository ppa:gnuradio/gnuradio-releases-3.9
	
	$ sudo apt-get update
	
	$ sudo apt-get install gnuradio python3-packaging
	
2. [HackRF One](https://github.com/greatscottgadgets/hackrf/releases/tag/v2021.03.1).

	$ sudo apt-get install hackrf
	
3. [PyCharm](https://www.jetbrains.com/pycharm/).

	$ sudo snap install pycharm-community --classic
	
4. [Arduino IDE](https://www.arduino.cc/en/software).

	$ sudo snap install arduino

## Getting started

1. To get started, you need to have an SDR with the ability to capture a 2MHz bluetooth channel in the frequency range of 2.402-2.480 GHz. The Great Scott Gadgets' [HackRF One](https://greatscottgadgets.com/hackrf/one/) will do the trick.

2. To be able to perform a quick test to validate variation in the waveforms of two distinct Bluetooth transmitters, the use of two ESP32's is recommended. All tests were performed with the Espressif ESP32-WROOM-32. These ESP32's are loaded with a [Tileclone](https://gitlab.com/GeekWeek/events/geekweek-7.5/G1/1.3/tileclone) firmware.


3. To begin capturing waveforms from either ESP32 Tilecones:

	1. Open the Blueprint project in Pycharm.
	
	2. Place the first ESP32 about 1 cm away from the HackRF One's antenna.
	
	3. Power-up the ESP32.
	
	4. Now, in the main script, you will find the following customizable parameters:
	
		1. filename - .bin file where the captured waveforms are stored (overwritten after each captures).
		2. max_iteration - Total number of waveforms captured for a given model (Number of individual signals used in the averaging process).
		3. capture_range - Number of bytes from the .bin file considered when looking for a pulse in a given capture.
		4. max_waveform_index - Maximum number capture_range's to be iterated over for a given waveform.
		5. waveform_padding_range - Number of bytes from the .bin file retained after the pulse when identified within a given capture.
		6. waveform_min_threshold - Threshold value for a pulse to be considered within a given capture.
		7. max_num_of_zero_crossings - Maximum number of zero-crossings allowed within a given capture_range for a pulse to be considered valid.
		8. pulse_width - Width of the window used on an identified pulse (in bytes).
		9. pulse_padding - Additional padding retained on either side of the window for the final pulse waveforms (in bytes).
		10. center_frequency - Frequency of the channel being monitored (2.402e9 = Channel 1).
		11. samp_rate - Sampling rate of the SDR (Should be at least twice the center_frequency).
		12. capture_time - Time given to the SDR to perform its capture (in seconds).
		
	5. After the main script executes, a figure showing the average of max_iteration's of signal captures will show up. The data captured for all identified pulses, the alligned pulses, and the final average pulse will be stored in the pulse_list.csv, pulse_list_centered.csv, and average_pulse.csv, respectively. Save these outputs somehwere safe so that you can compare them with the follow-on captures.
	
	6. Perform steps 2 to 5 again with the same ESP32. Comparing the two results, you should note that they are almost identical.
	
	7. Perform steps 2 to 6 again with the second ESP32. Comparing the results obtained for the different ESP32's, you should note that there are distinct differences.

## Future Work

Since Bluepring is still in a proof-of-concept state of development, much work remains to be accomplshed before an operational state is reached. Among the work to be performed:

1. Implement the ability to capture the Tile tracker's waveform in a continueous manner. While we have been able to capture some waveforms from the tile when in its initializing state, when deployed, the Tile makes use of Frequency Hopping to transmit its data. Therefore, to capture the Tile's waveform, we need to increase the bandwidth being captured.

2. Implement the ability to demodulate the Bluetooth signal. This demodulated signal will be used to retrieve the MAC address of the transmitting device and compare it with the waveform captured.

3. Implement the ability to average multiple pulses in a single SDR capture. At the moment, a new SDR capture is performed for every waveform considered in the averaging process. Averaging multiple pulses in a single capture will greatly speed up the process and also set the stage for live transmitter identification.

4. Implement the ability to automatically identify a given transmitter. While we can visually recognise a transmitter by its waveform, for Blueprint to be effective, an algorithm for live transmitter identification needs to be implemented. This will use concepts of signal demodulation to identify the MAC address of a waveform and then compare this waveform to a predefined model. The model will be composed of known cloned and legitimate devices.

5. Implement Apple's Airtag to BluePrint's capabilities.

6. Implement Blueprint in a functional form factor.

7. Add a User Interface and an alert system.
