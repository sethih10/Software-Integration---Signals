# Software Integration - Signals
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg) ![PyQt](https://img.shields.io/badge/PyQt-5.15.4-green.svg) ![NumPy](https://img.shields.io/badge/NumPy-1.21.0-orange.svg) ![SciPy](https://img.shields.io/badge/SciPy-1.7.0-brightgreen.svg) ![PyAudio](https://img.shields.io/badge/PyAudio-0.2.14-blue.svg)


## Overview
This project is focused on integrating software tools for processing and analyzing audio signals. It includes functionalities for working with audio data, implementing signal processing techniques, and providing a graphical user interface (GUI) for ease of interaction.

## Repository Structure

- **main.py**: The main script to run the audio player, featuring:
  - Capabilities equivalent to Shazam for identifying audio files.
  - Visualization of the major frequency in a plot, along with its value and tone.
  - User-friendly functionality with buttons for various operations (detailed below).
- **matching_sounds.py**: A script for matching an unknown audio file with a predefined database of audio samples. It creates a unique "fingerprint" of the audio using mel-spectrogram features and compares it against a set of database fingerprints.
- **soundcardlib.py**: A Python module providing real-time audio streaming and recording capabilities, using PyAudio to manage audio data in chunks.
- **database/**: A folder containing audio files (`.wav`) used as input data for processing.
- **final_GUI.ui**: A Qt Designer file defining the graphical user interface for the application.
- **requirements.txt**: A file listing the required Python libraries for the project.


## Features
### Audio Player and Signal Analysis
- Load `.wav` files for analysis.
- Start, stop, and resume audio playback, applicable for both recordings and loaded files.
- Reset functionality to clear plots and reload files or start a new recording.
- Record audio and save recordings directly from the application.
- Compare loaded files or the last recording against the database using FFT (see `matching_sounds.py`).
  - Identifies the name of the audio file played or recorded, similar to Shazam.

### GUI Features
- Buttons include:
  - **Load Wav File**: Load a `.wav` file for playback and analysis.
  - **Stop/Resume**: Control playback of recordings or loaded files.
  - **Reset**: Clear plots and reload the application interface.
  - **Start Recording**: Record audio from the microphone.
  - **Save Recording**: Save the recorded audio.
  - **Compare Loaded File/Last Recording**: Identify the name of the audio file or recorded sound.

## Prerequisites
- Python 3.8 or higher.
- Required Python libraries (can be installed via `requirements.txt`).
- Qt Designer for editing the `.ui` file (optional).

## Usage
1. Clone the repository:
   ```bash
   git clone <repository_url>
   ```
2. Navigate to the project directory:
   ```bash
   cd Software-Integration---Signals-main
   ```
3. Install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the Python script:
   ```bash
   python main.py
   ```

## Database
The `database/` folder contains audio files in `.wav` format. These files are used as input for signal processing and testing the application.

