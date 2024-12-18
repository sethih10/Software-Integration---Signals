
# Software Integration - Signals
![Python](https://img.shields.io/badge/Python-3.8+-blue.svg) ![PyQt](https://img.shields.io/badge/PyQt-5.15.4-green.svg) ![NumPy](https://img.shields.io/badge/NumPy-1.21.0-orange.svg) ![SciPy](https://img.shields.io/badge/SciPy-1.7.0-brightgreen.svg)

## Overview
This project is focused on integrating software tools for processing and analyzing audio signals. It includes functionalities for working with audio data, implementing signal processing techniques, and providing a graphical user interface (GUI) for ease of interaction.

## Repository Structure

- **assignment1.py**: A Python script implementing core functionalities related to signal processing and analysis.
- **database/**: A folder containing audio files (`.wav`) used as input data for processing.
- **final_GUI.ui**: A Qt Designer file defining the graphical user interface for the application.
- **README.md**: Documentation for understanding the project, its structure, and usage.

## Features
- Audio signal processing using provided `.wav` files.
- User-friendly GUI for interacting with the application.
- Modular structure for ease of updates and integration with additional features.

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
3. Run the Python script:
   ```bash
   python assignment1.py
   ```
4. Launch the GUI using the `.ui` file with Qt Designer or a Python UI framework like PyQt/PySide.

## Database
The `database/` folder contains audio files in `.wav` format. These files are used as input for signal processing and testing the application.

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Submit a pull request with a detailed description of your changes.

## License
This project is licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute the code as per the license terms.

## Contact
For any questions or feedback, please contact the repository owner.

Assignment 1 (Task 3)


Assignment1.py  is the main script to run the audio player which has capability equivalent to Shazam as well as print the major frequency in the plot and it's value and the tone. It is fairly easy to use.

The button includes - 


Load Wav file
Stop, Resume - This work for both the recordings as well as loaded files 
Reset - It clears the plots and gives the option to again choosing loading file or starting recording
Start Recording 
Save Recording 
Compare loaded file/last recording - It tells the name of the file played from the database by using fft similar to shazam (please see the matching_sounds.py) script. On clicking this button, it tells the name of the song played by the last loaded file or the sound heard in the microphone if you use the option of recording. 
