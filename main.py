import os, sys, math, pdb

import warnings

from PyQt5.QtCore import Qt
warnings.filterwarnings("ignore")

from PyQt5 import QtCore, QtGui,  QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QMessageBox, QWidget
from PyQt5.uic import loadUi




from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
plt.style.use('dark_background')

import numpy as np
from numpy import *

from scipy import signal 
from scipy.io import wavfile
import wave

import pyaudio 

import queue
from matplotlib.animation import FuncAnimation

from final_GUI import Ui_MainWindow

import pyqtgraph as pg 
from pyqtgraph import TextItem

from soundcardlib import SoundCardDataSource
from matching_sounds import matching
import librosa

bCanvasLeft=bCanvasRight=False
audio=0


# rfft: return the discrete Fourier transform frequencies
def rfftfreq(n, d=1.0):
    if not isinstance(n, int):
        raise ValueError("n should be an integer")
    val = 1.0/(n*d)
    N = n//2 + 1
    results = np.arange(0,N, dtype = int)
    return results*val

# apply the fft on the data from the buffer
def fft_buffer(x):
    window = np.hanning(x.shape[0])
    # Calculate FFT
    fx = np.fft.rfft(window*x)
    # Convert to normalized PSD 
    Pxx = abs(fx) **2 / (np.abs(window)**2).sum()
    # Scale for one-sided
    Pxx[1:-1] *= 2
    return Pxx ** 0.5


def frequency_to_note(frequency):
        # A4 is 440Hz, calculate the distance in semitones from A4
        if frequency == 0:
            return
        semitones_from_a4 = 12 * np.log2(frequency / 440.0)


        # Define the mapping of semitones to notes
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        # Calculate the note index
        note_index = round(semitones_from_a4) % 12

        # Calculate the octave
        octave = 4 + (round(semitones_from_a4) // 12)

        # Create the note string
        note_str = notes[note_index] + str(octave)

        return note_str

    
class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent = None):
        super().__init__(parent)
        QMainWindow.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        
        # Example: to initialize some value on the GUI

        

        self.ui.btnLoadwav.clicked.connect(self.LoadWavFile)
        self.ui.btnStart.clicked.connect(self.Start)
        self.ui.btnStop.clicked.connect(self.Stop)
        self.ui.btnResume.clicked.connect(self.Resume)
        self.ui.btnRestart.clicked.connect(self.Restart)
        self.ui.btnSave.clicked.connect(self.Save)
        self.ui.btnCompare.clicked.connect(self.Compare)
        
        self.start_recording = False
        self.Loadfile = False
        self.Comparebtn = False
        # Disable btnRestart if some_condition is True
        self.ui.btnStart.setEnabled(not self.start_recording)

        # Disable btnSave if some_other_condition is True
        self.ui.btnSave.setEnabled(self.start_recording)
        self.ui.btnLoadwav.setEnabled(not self.Loadfile)
        self.ui.btnCompare.setEnabled(self.Comparebtn)
        
        self.ui.btnResume.setEnabled(False)
        self.ui.btnStop.setEnabled(False)
        
        # Live Audio
        self.soundcardlib = None
        
        
        self.paused = False
        self.downsample = True
        
        
        
        
        
       
        

    def reset_ranges(self):
        self.timeValues = self.soundcardlib.timeValues
        self.freqValues = rfftfreq(len(self.timeValues), 1. / self.soundcardlib.fs)

        self.p1.setRange(xRange=(0, self.timeValues[-1]), yRange=(-1, 1))
        self.p1.setLimits(xMin=0, xMax=self.timeValues[-1], yMin=-1, yMax=1)
        self.p2.setRange(xRange=(0, self.freqValues[-1] / 2), yRange=(0, 50))
        self.p2.setLimits(xMax=self.freqValues[-1], yMax=50)
        self.spec.setData(fillLevel=0)
        self.p2.setLabel('left', 'PSD', '1 / Hz')
        
    # The main function that will update the plot
    def update(self):
        # if spacebar (key pres event), we don't continue
        if self.paused:
            self.soundcardlib.stop()
            return
        
        # collect data 
        data = self.soundcardlib.get_buffer()
        weighting = np.exp(self.timeValues/self.timeValues[-1])
        Pxx = fft_buffer(weighting * data[:,0])
        
        Pxx = np.log10(Pxx)
        # Create a masked array based on the condition
        peaks = np.argmax(Pxx)
        peak_values = Pxx[peaks]
        threshold = peak_values*0.9
        index = Pxx > threshold
        
        note = frequency_to_note(self.freqValues[peaks])
        
        # Replace values that do not match the condition with the original size (e.g., -1)
        Pxx = Pxx*index
            
        
        if self.downsample:
            downsample_args = dict(autoDownsample=False, downsampleMethod='subsample', downsample=10)
        else:
            downsample_args = dict(autoDownsample=True)
            
            

            
        self.ts.setData(x=self.timeValues, y=data[:, 0], **downsample_args)
        self.spec.setData(x=self.freqValues, y=(20 * Pxx))
        
        
        peak_freq = self.freqValues[peaks]
        peak_amplitude = 20 * (peak_values)
        self.peak_text_item.setText(f"{note} at {peak_freq:.2f} Hz")
        self.peak_text_item.setPos(peak_freq+5000, peak_amplitude)

        
        
    
    def Stop(self):
        self.paused = True
        self.p1.setTitle("PAUSED" if self.paused else "")
            
    def Resume(self):
        self.paused = False
        self.soundcardlib.resume()
        self.p1.setTitle("PAUSED" if self.paused else "")
        
    def Save(self):
        self.start_recording = False
        self.Comparebtn = True
        self.ui.btnCompare.setEnabled(self.Comparebtn)
        self.ui.btnStart.setEnabled(not self.start_recording)
        self.ui.btnLoadwav.setEnabled(not self.start_recording)
        
        
        self.ui.btnResume.setEnabled(False)
        self.ui.btnStop.setEnabled(False)
        
        
        self.myPath = 'temp.wav'
        self.paused = False
        self.soundcardlib.save()
        self.ui.verticalLayout.removeWidget(self.pg_graph)
        self.pg_graph.setParent(None)
        
    
    
    def Start(self):
        self.start_recording = True
        
        # Disable btnRestart if some_condition is True
        self.ui.btnStart.setEnabled(not self.start_recording)

        # Disable btnSave if some_other_condition is True
        self.ui.btnSave.setEnabled(self.start_recording)
        
        self.ui.btnLoadwav.setEnabled(not self.start_recording)
        
        self.ui.btnResume.setEnabled(True)
        self.ui.btnStop.setEnabled(True)
        
        global bCanvasLeft, bCanvasRight
        
        if bCanvasRight == True:
            self.rm_mpl()
            
        if bCanvasRight == True:
            self.rm_mpl2()
            
        self.soundcardlib = SoundCardDataSource(num_chunks=3, sampling_rate=FS, chunk_size=4 * 1024, filename=None)

        

        # Left Widget
        # Setup first plot (time domain)
        self.pg_graph = pg.GraphicsLayoutWidget()
        bCanvasLeft = True
        self.ui.verticalLayout.addWidget(self.pg_graph)

        
        self.p1 = self.pg_graph.addPlot()
        self.p1.setLabel('bottom', 'Time', 's')
        self.p1.setLabel('left', 'Amplitude')
        self.p1.setTitle("")
        self.p1.setLimits(xMin=0, yMin=-1, yMax=1)
        self.ts = self.p1.plot(pen='y')

        # Add new row for the next plot
        #self.pg.GraphicsLayoutWidge.nextRow()

        # Setup second plot (frequency domain)
        self.p2 = self.pg_graph.addPlot()
        self.p2.setLabel('bottom', 'Frequency', 'Hz')
        self.p2.setLimits(xMin=0, yMin=0)
        self.spec = self.p2.plot(pen=(50, 100, 200), brush=(50, 100, 200), fillLevel=-100)
        
        # Add a TextItem to display the peak value
        self.peak_text_item = TextItem("", anchor=(1, 1), color='r')
        self.p2.addItem(self.peak_text_item)  # Add TextItem to the p2 plot

        
        # Data ranges 
        self.reset_ranges()
        # Define a timer to update plots 
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        interval_ms = (self.soundcardlib.chunk_size/self.soundcardlib.fs)
        self.timer.start(int(interval_ms))

    def Restart(self):
        self.start_recording = False
        self.Loadfile = False
        self.Comparebtn = False
        self.ui.btnCompare.setEnabled(self.Comparebtn)
        self.ui.btnStart.setEnabled(not self.start_recording)
        self.ui.btnLoadwav.setEnabled(not self.Loadfile)
        
        self.ui.btnResume.setEnabled(False)
        self.ui.btnStop.setEnabled(False)
        
        self.soundcardlib.restart()
        self.ui.verticalLayout.removeWidget(self.pg_graph)
        self.pg_graph.setParent(None)
        
        
    def Compare(self):
        self.Restart()
        self.comp = matching(self.myPath)
        self.comp.match_fingerprint()
        
        
        
    def LoadWavFile(self):
        self.Loadfile = True
        # Disable btnRestart if some_condition is True
        self.Comparebtn = True
        self.ui.btnCompare.setEnabled(self.Comparebtn)
        self.ui.btnStart.setEnabled(not self.Loadfile)
        self.ui.btnLoadwav.setEnabled(not self.Loadfile)
        
        self.ui.btnResume.setEnabled(True)
        self.ui.btnStop.setEnabled(True)
        
        global audio
        global bCanvasLeft, bCanvasRight
        
        if bCanvasLeft == True: 
            self.rm_mpl()
            
        if bCanvasRight == True:
            self.rm_mpl2()
            
        try: 
            
            myFile = QFileDialog.getOpenFileName(None, 'OpenFile',"","WAV file(*.wav)")
            self.myPath = myFile[0]
            myPath = myFile[0]
            
            if myFile[0] == myFile[1] == '':
                #ERROR - No file selected
                pass
            
            else:
                # Live Audio
                wf = wave.open(myPath, 'rb')
                sampling_rate = wf.getframerate()
                channels = int(wf.getnchannels())
                self.soundcardlib = SoundCardDataSource(num_chunks = 3, channels=2, sampling_rate=sampling_rate, chunk_size = 1024, filename=myPath)

                
                # Left Widget
                # Setup first plot (time domain)
                self.pg_graph = pg.GraphicsLayoutWidget()
                bCanvasLeft = True
                self.ui.verticalLayout.addWidget(self.pg_graph)


                self.p1 = self.pg_graph.addPlot()
                self.p1.setLabel('bottom', 'Time', 's')
                self.p1.setLabel('left', 'Amplitude')
                self.p1.setTitle("")
                self.p1.setLimits(xMin=0, yMin=-1, yMax=1)
                self.ts = self.p1.plot(pen='y')

                # Add new row for the next plot
                #self.pg.GraphicsLayoutWidget.nextRow()

                # Setup second plot (frequency domain)
                self.p2 = self.pg_graph.addPlot()
                self.p2.setLabel('bottom', 'Frequency', 'Hz')
                self.p2.setLimits(xMin=0, yMin=0)
                self.spec = self.p2.plot(pen=(50, 100, 200), brush=(50, 100, 200), fillLevel=-100)
                
                # Add a TextItem to display the peak value
                self.peak_text_item = TextItem("", anchor=(1, 1), color='r')
                self.p2.addItem(self.peak_text_item)  # Add TextItem to the p2 plot

                # Data ranges 
                self.reset_ranges()
                # Define a timer to update plots 
                self.timer = QtCore.QTimer()
                self.timer.timeout.connect(self.update)
                interval_ms = 1000* (self.soundcardlib.chunk_size/self.soundcardlib.fs)
                self.timer.start(int(interval_ms))

                
                
                

        except IOError as e:
                print( "I/O error({0}): {1}".format(e.errno, e.strerror))
                print(myFile)
                
        except ValueError as ve:
                print( "Value Error.", ve)
        except:
                print( "Unexpected error:", sys.exc_info()[0])
                raise
            
            
            
    def update_load(self):
        # if spacebar (key pres event), we don't continue
        if self.paused:
            self.soundcardlib.stop()
            return
        
        # collect data 
        data = self.soundcardlib.get_buffer()
        weighting = np.exp(self.timeValues/self.timeValues[-1])
        Pxx = fft_buffer(weighting * data[:,0])
        
        if self.downsample:
            downsample_args = dict(autoDownsample=False, downsampleMethod='subsample', downsample=10)
        else:
            downsample_args = dict(autoDownsample=True)
            
        self.ts.setData(x=self.timeValues, y=data[:, 0], **downsample_args)
        self.spec.setData(x=self.freqValues, y=(20 * np.log10(Pxx)))
        
        
    def reset_ranges(self):
        self.timeValues = self.soundcardlib.timeValues
        self.freqValues = rfftfreq(len(self.timeValues), 1. / self.soundcardlib.fs)

        self.p1.setRange(xRange=(0, self.timeValues[-1]), yRange=(-1, 1))
        self.p1.setLimits(xMin=0, xMax=self.timeValues[-1], yMin=-1, yMax=1)
        self.p2.setRange(xRange=(0, self.freqValues[-1] / 2), yRange=(0, 50))
        self.p2.setLimits(xMax=self.freqValues[-1], yMax=50)
        self.spec.setData(fillLevel=0)
        self.p2.setLabel('left', 'PSD', '1 / Hz')
            
    def rm_mpl(self):
        self.ui.verticalLayout.removeWidget(self.pg_graph)
        self.pg_graph.setParent(None)
        
    def rm_mpl2(self):
        self.ui.verticalLayout.removeWidget(self.pg_graph)
        self.pg_graph.setParent(None)
        
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    FS = 44000  # Hz
    #soundcardlib = SoundCardDataSource(num_chunks=3, sampling_rate=FS, chunk_size=4 * 1024)
    window = MyMainWindow()
    window.show()
    sys.exit(app.exec_())