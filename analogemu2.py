import argparse
import wave
import numpy as np
from scipy.special import expit  # Sigmoid function

def read_wave(file_path):
    with wave.open(file_path, 'rb') as wav_file:
        params = wav_file.getparams()
        frames = wav_file.readframes(params.nframes)
        audio_data = np.frombuffer(frames, dtype=np.int16)
        return audio_data, params

def sigmoid_distortion(x):
    # Sigmoid function for distortion
    return 2 * expit(x) - 1

def apply_harmonic_distortion(audio_data, distortion_level):
    max_int16 = 2**15 - 1
    audio_data = audio_data / max_int16  # Normalize to -1 to 1
    # Apply distortion based on distortion level
    distorted_data = sigmoid_distortion(audio_data * distortion_level)
    distorted_data = np.clip(distorted_data, -1, 1)  # Clip to avoid overflow
    return (distorted_data * max_int16).astype(np.int16)

def write_wave(audio_data, params, file_path):
    with wave.open(file_path, 'wb') as wav_file:
        wav_file.setparams(params)
        wav_file.writeframes(audio_data.tobytes())

def transient_shaper(audio_data, intensity, threshold):
    max_int16 = 2**15 - 1
    audio_float = audio_data / max_int16  # Normalize audio to -1 to 1

    for i in range(1, len(audio_float)):
        # Calculate the difference in amplitude between successive samples
        delta = abs(audio_float[i] - audio_float[i - 1])

        # If the change is greater than the threshold, it's a transient
        if delta > threshold:
            # Reduce the transient by the intensity factor
            sign = 1 if audio_float[i] > audio_float[i - 1] else -1
            audio_float[i] -= intensity * sign * delta

    return (audio_float * max_int16).astype(np.int16)


def main():
    parser = argparse.ArgumentParser(description='AnalogEmulator: Add Analog Warmth to Digital Audio')
    parser.add_argument('input_file', type=str, help='Input WAV file')
    parser.add_argument('output_file', type=str, help='Output WAV file')
    parser.add_argument('--distortion', '-d', type=float, default=0, help='Amount of harmonic distortion (larger values for more distortion)')
    parser.add_argument('--transient_intensity', '-ti', type=float, default=0.5, help='Intensity of transient shaping')
    parser.add_argument('--transient_threshold', '-tt', type=float, default=0.01, help='Threshold for detecting transients')

    args = parser.parse_args()

    audio_data, params = read_wave(args.input_file)
    
    # Apply harmonic distortion if specified
    if args.distortion > 0:
        audio_data = apply_harmonic_distortion(audio_data, args.distortion)

    # Apply transient shaper
    audio_data = transient_shaper(audio_data, args.transient_intensity, args.transient_threshold)

    write_wave(audio_data, params, args.output_file)
if __name__ == "__main__":
    main()
