import numpy as np
import librosa
from scipy.spatial.distance import euclidean

def create_fingerprint(audio_file, top_percentage=10, target_length=1000):
    y, sr = librosa.load(audio_file)
    
    # Compute the spectrogram
    spectrogram = librosa.feature.melspectrogram(y=y, sr=sr)
    
    # Calculate the total energy for each time frame
    frame_energy = np.sum(spectrogram, axis=0)
    
    # Select the top frequencies based on the cumulative energy
    sorted_frame_indices = np.argsort(-frame_energy)
    top_frame_indices = sorted_frame_indices[:int(top_percentage / 100 * len(frame_energy))]
    
    # Select the corresponding spectrogram components
    selected_spectrogram = spectrogram[:, top_frame_indices]
    
    # Resize the selected spectrogram to a fixed size
    if selected_spectrogram.shape[1] < target_length:
        pad_width = target_length - selected_spectrogram.shape[1]
        selected_spectrogram = np.pad(selected_spectrogram, pad_width=((0, 0), (0, pad_width)))
    else:
        selected_spectrogram = selected_spectrogram[:, :target_length]
    
    # Flatten the spectrogram to create a 1D feature vector
    features = np.ravel(selected_spectrogram)
    
    fingerprint = ','.join(map(str, features))
    return fingerprint

class matching:
    def __init__(self, audio_file):
        self.unknown_audio_fingerprint = create_fingerprint(audio_file)
        self.audio_database = {
            'sound1': create_fingerprint(r'database/sound1.wav'),
            'sound2': create_fingerprint(r'database/sound2.wav'),
            'sound3': create_fingerprint(r'database/sound3.wav'),
            'sound4': create_fingerprint(r'database/sound4.wav'),
            'sound5': create_fingerprint(r'database/sound5.wav'),
            'sound6': create_fingerprint(r'database/sound6.wav'),
            'sound7': create_fingerprint(r'database/sound7.wav'),
            'sound8': create_fingerprint(r'database/sound8.wav'),
            'sound9': create_fingerprint(r'database/sound9.wav'),
            'sound10': create_fingerprint(r'database/sound10.wav')
            # Add more sounds to the database
        }

    def match_fingerprint(self):
        database = self.audio_database
        unknown_fingerprint = self.unknown_audio_fingerprint
        min_distance = float('inf')
        match = None

        for key, reference_fingerprint in database.items():
            reference_features = np.array(reference_fingerprint.split(','), dtype=float)

            if len(unknown_fingerprint.split(',')) != len(reference_features):
                print(f"Warning: Feature vectors have different lengths for {key}")
                continue

            distance = euclidean(np.array(unknown_fingerprint.split(','), dtype=float), reference_features)

            if distance < min_distance:
                min_distance = distance
                match = key
                
        if match:
            print(f"Match found: {match}")
        else:
            print("No match found.")

