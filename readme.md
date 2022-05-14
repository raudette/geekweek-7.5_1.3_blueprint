# Blueprint - A Bluetooth LE PHY fingerprinting framework

Blueprint (BLE Fingerprint) is a set of tools that allows for the PHY fingerprinting of Bluetooth LE signals. The toolset aims to detect variations in the waveforms of BLE transmitters caused by differences in their physical characteristics.

The goal of this toolset concerning the security of Bluetooth trackers is to allow for clones to be detected. From tests performed so far, the waveforms observed from an authentic Tile tracker are considerably different from what can be obtained from a cloned device that uses development boards such as the ESP32 and the Raspberry Pi. As you will see from the work performed so far, there is even a noticeable difference between two identical ESP32s.

In its intended use case, we could use this toolset in populated areas to detect malicious actors who either cloned legitimate devices in their surroundings or who use clones to bypass certain manufacturer-specific security features.

## Requirements

In terms of Tooling, the following Softwares are recommended (we performed all tests performed on Ubuntu 20.04 LTS):

1. [GNURadio](https://wiki.gnuradio.org/index.php/InstallingGR).

       $ add-apt-repository ppa:gnuradio/gnuradio-releases-3.9
	
       $ sudo apt-get update
	
       $ sudo apt-get install gnuradio python3-packaging
	
3. [HackRF One](https://github.com/greatscottgadgets/hackrf/releases/tag/v2021.03.1). 

       $ sudo apt-get install hackrf
	
4. [PyCharm](https://www.jetbrains.com/pycharm/).

       $ sudo snap install pycharm-community --classic
	
5. [Arduino IDE](https://www.arduino.cc/en/software).

       $ sudo snap install arduino

## Getting started

1. To get started, you need to have an SDR with the ability to capture a 2MHz bluetooth channel in the frequency range of 2.402-2.480 GHz. The Great Scott Gadgets' [HackRF One](https://greatscottgadgets.com/hackrf/one/) will do the trick.


2. To be able to perform a quick test to validate variation in the waveforms of two distinct Bluetooth transmitters, the use of two ESP32's is recommended. All tests were performed with the Espressif ESP32-WROOM-32. These ESP32's are loaded with a [Tileclone](https://gitlab.com/GeekWeek/events/geekweek-7.5/G1/1.3/tileclone) firmware.


3. To begin capturing waveforms from either ESP32 Tilecones:

   1. Open the Blueprint project in Pycharm.
   
      1. Create the "data" directory within the project's root directory.
      
             $ mkdir data
   
      2. Install the GNURadio Package within your working environment.
      
             $ pip install Freetail-GNURadio
      
      3. Install the Osmosdr package
             
             $ sudo apt install gr-osmosdr

   2. Place the first ESP32 about 1 cm away from the HackRF One's antenna.

   3. Power up the ESP32.

   4. Now, in the main script, you will find the following customizable parameters:

      - filename - .bin file where the captured waveforms are stored (overwritten after each capture).
      - max_iteration - Total number of waveforms captured for a given model (Number of individual signals used in the averaging process).
      - capture_range - Number of bytes from the .bin file considered when looking for a pulse in a given capture.
      - max_waveform_index - Maximum number capture_range's to be iterated over for a given waveform.
      - waveform_padding_range - Number of bytes from the .bin file retained after the pulse when identified within a given capture.
      - waveform_min_threshold - Threshold value for a pulse to be considered within a given capture.
      - max_num_of_zero_crossings - Maximum number of zero-crossings allowed within a given capture_range for a pulse to be considered valid.
      - pulse_width - Width of the window used on an identified pulse (in bytes).
      - pulse_padding - Additional padding retained on either side of the window for the final pulse waveforms (in bytes).
      - center_frequency - Frequency of the channel being monitored (2.402e9 = Channel 1).
      - samp_rate - Sampling rate of the SDR (Should be at least twice the center_frequency).
      - capture_time - Time given to the SDR to perform its capture (in seconds).
		
   5. After the main script executes, a figure showing the average of max_iteration's of signal captures will show up. The data captured for all identified pulses, the alligned pulses, and the final average pulse will be stored in the pulse_list.csv, pulse_list_centered.csv, and average_pulse.csv, respectively. Save these outputs somehwere safe so that you can compare them with the follow-on captures.
	
   6. Perform steps 2 to 5 again with the same ESP32. Comparing the two results, you should note that they are almost identical.
	
   7. Perform steps 2 to 6 again with the second ESP32. Comparing the results obtained for the different ESP32's, you should note that there are distinct differences.

## The Multivariate Gaussian Model Approach for Detection

Adapted from:
Suresh Chari, Josyula R. Rao, and Pankaj Rohatgi. Template Attacks. In
Burton S. Kaliski Jr., C¸ etin Kaya Ko¸c, and Christof Paar, editors, Proceedings of CHES 2002, volume 2535 of LNCS, pages 13–28. Springer, 2003.

The steps in developing a Gaussian model are as follows:

1. Collect a large number L (typically one thousand) of samples on each K experimental device, {D<sub>1</sub>,... ,D<sub>K</sub>}.


2. Compute the average signal M<sub>1</sub>,... ,M<sub>K</sub> for each of the experimental devices.


3. Compute pairwise differences between the average signals M<sub>1</sub>,... ,M<sub>K</sub> to
identify and select only points P<sub>1</sub>,... ,P<sub>N</sub> , at which large differences show
up. The Gaussian model applies to these N points. This optional step significantly reduces the processing overhead with only a small loss of accuracy.


4. For each operation O<sub>i</sub>, the N–dimensional noise vector for sample T is N<sub>i</sub>(T)
= (T[P<sub>1</sub>] − M<sub>i</sub>[P<sub>1</sub>],... ,T[P<sub>N</sub>] − M<sub>i</sub>[P<sub>N</sub>]). Compute, the noise covariance
matrix between all pairs of components of the noise vectors for experimental device D<sub>i</sub>
using the noise vectors N<sub>i</sub>s for all the L samples. The entries of the covariance
matrix ΣN<sub>i</sub> are defined as:


<center>ΣN<sub>i</sub> [u, v] = cov(N<sub>i</sub>(P<sub>u</sub>), N<sub>i</sub>(P<sub>v</sub>))</center>


Using this we compute the templates (M<sub>i</sub>, ΣN<sub>i</sub> ) for each of the K experimental devices. The
signal for device D<sub>i</sub> is M<sub>i</sub> and the noise probability distribution is given by the
N–dimensional multivariate Gaussian distribution pN<sub>i</sub>(·) where the probability
of observing a noise vector n is:

<center>pN<sub>i</sub>(n) = [1/√((2π)<sup>N</sup> |Σ<sub>Ni</sub>|)] exp((-1/2)n<sup>T</sup>Σ<sup>-1</sup><sub>Ni</sub>n), n∈ R<sup>N</sup></center>

where |Σ<sub>Ni</sub>| denotes the determinant of Σ<sub>Ni</sub> and Σ<sup>−1</sup><sub>Ni</sub> is its inverse.

In this model, the optimal technique to classify a sample S, is as follows: for
each hypothesized operation O<sub>i</sub>, compute the probability of observing S if indeed
it originated from D<sub>i</sub>. This probability is given by first computing the noise n in
S using the mean signal M<sub>i</sub> in the template and then computing the probability
of observing n using the expression for the noise probability distribution and
the computed ΣN<sub>i</sub> from the template. If the noise was actually Gaussian, then
the approach of selecting the D<sub>i</sub> with the highest probability is optimal.The
probability of making errors in such a classification is also computable. If we
use this approach to distinguish two devices D<sub>1</sub> and D<sub>2</sub> with the same noise
characterization ΣN , the error probability is given by:

For equally likely binary hypotheses, the error probability of error
of maximum likelihood test is

<center>P<sub>e</sub> = (1/2)erfc(∆/(2√2))</center>

where ∆<sup>2</sup> = (M<sub>1</sub> − M<sub>2</sub>)<sup>T</sup> Σ<sup>−1</sup><sub>N</sub>(M<sub>1</sub> − M<sub>2</sub>) and erfc(x)=1 − erf(x).

To implement the pruning process of the Blueprint, we deal with multiple hypotheses and bound the probability of classification errors by judiciously
selecting a small subset of possible devices as most likely candidates.

## Future Work

Since Blueprint is still in a proof-of-concept state of development, much work remains to be accomplished before an operational state is reached. Among the work to be performed:

- Implement the ability to capture the Tile tracker's waveform continuously. While we have been able to capture some waveforms from the Tile when in its initializing state, when deployed, the Tile uses Frequency Hopping to transmit its data. Therefore, we need to increase the bandwidth being captured to capture the Tile's waveform.


- Implement the ability to demodulate the Bluetooth signal. This demodulated signal will be used to retrieve the MAC address of the transmitting device and compare it with the waveform captured.


- Implement the ability to average multiple pulses in a single SDR capture. At the moment, a new SDR capture is performed for every waveform considered in the averaging process. Averaging numerous pulses in a single capture will significantly speed up the process and set the stage for live transmitter identification.


- Implement the ability to identify a given transmitter automatically. While we can visually recognize a transmitter by its waveform, an algorithm for live transmitter identification needs to be implemented for Blueprint to be practical. This implementation will use concepts of signal demodulation to identify the MAC address of a waveform and then compare this waveform to a predefined model. The model will be composed of known cloned and legitimate devices.


- Implement Apple's Airtag to BluePrint's capabilities.


- Implement Blueprint in a functional form factor.


- Add a User Interface and an alert system.
