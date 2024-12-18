from __future__ import division

import numpy as np
import pyaudio
import wave
from datetime import datetime




def data_to_array(data, channels):
    return (np.frombuffer(data, dtype=np.int16)
            .reshape((-1,channels))
            .astype(float)/2**15)
    
    
class SoundCardDataSource(object):
    def __init__(self, num_chunks, channels=2, sampling_rate=44100, chunk_size = 4*1024, filename = None):
        self.fs = sampling_rate
        self.channels = int(channels)
        self.chunk_size = int(chunk_size)
        self.num_chunks = int(num_chunks)
        
        
        
        # Check format is supported 
        self.pyaudio = pyaudio.PyAudio()
        self.stream = None
        
            
        

        
        # Allocate buffers
        self._allocate_buffer()
        
        # Callback function is called with new audio data
        def callback(in_data, frame_count, time_info, status):
            samples = data_to_array(in_data, self.channels)
            self.frames.append(in_data)
            self._write_chunk(samples)
            #self.output_file.writeframes(in_data)
            return (None, pyaudio.paContinue)
        
        def callback1(in_data, frame_count, time_info, status):
            
            data = wf.readframes(chunk_size)
            samples = data_to_array(data, self.channels)
            if samples.shape[0] == self.chunk_size:
                self._write_chunk(samples)
            # If len(data) is less than requested 
            # ewframe_count, PyAudio automatically
            # assumes the stream is finished, and the stream stops.
            return (data, pyaudio.paContinue)

        # Instantiate PyAudio and initialize PortAudio system resources (2)
        p = self.pyaudio
        
        self.frames = []  # Initialize array to store frames

        # Open stream using callback (3)
        # Open stream for output (speakers)
        # Create a WAV file to save the audio

        
        # Start the stream
        if filename == None:
            self.stream = self.pyaudio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                frames_per_buffer=self.chunk_size,
                rate=self.fs, 
                stream_callback=callback,
                input=True
                )
        
        else:
            wf = wave.open(filename, 'rb')
            # Open stream using callback (3)
            self.stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True,
                            stream_callback=callback1,
                            frames_per_buffer=chunk_size)
            
        
        
    def stop(self):
        self.stream.stop_stream()
        
    def resume(self):
        self.stream.start_stream()
        
    def save(self):
        current_time = datetime.now()
        formatted_time = current_time.strftime("%H_%M_%S")
        self.stream.stop_stream()
        self.stream.close()
        filename= "Recording_" + formatted_time + ".wav"
        
        # Save the recorded data as a WAV file
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.channels)
        sample_format = pyaudio.paInt16  # 16 bits per sample
        p = self.pyaudio
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(self.frames))
        wf.close()
        
        # Save the recorded data as a WAV file
        tp = wave.open('temp.wav', 'wb')
        tp.setnchannels(self.channels)
        sample_format = pyaudio.paInt16  # 16 bits per sample
        p = self.pyaudio
        tp.setsampwidth(p.get_sample_size(sample_format))
        tp.setframerate(self.fs)
        tp.writeframes(b''.join(self.frames))
        tp.close()
        
        print("Recording saved", filename)
        
    def restart(self):
        self.stream.stop_stream()
        self.stream.close()

            
        
        
        
    def __del__(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.pyaudio.terminate()
        
    def _write_chunk(self, samples):
        self.buffer[self.next_chunk, :, :] = samples
        self.next_chunk = (self.next_chunk+1) % self.buffer.shape[0]
        
    def _allocate_buffer(self):
        self.buffer = np.zeros((self._num_chunks, self.chunk_size,
                                self.channels))
        self.next_chunk = 0
        
    @property
    def num_chunks(self):
        return self._num_chunks
    
    @num_chunks.setter
    def num_chunks(self, num_chunks):
        n = max(1, int(num_chunks))
        if n * self.chunk_size > 2**16:
            n = 2**16 // self.chunk_size
        self._num_chunks = n
        self._allocate_buffer()

    def get_buffer(self):
        """Return all chunks joined together"""
        a = self.buffer[:self.next_chunk]
        b = self.buffer[self.next_chunk:]

        return np.concatenate((b, a), axis=0) \
                 .reshape((self.buffer.shape[0] * self.buffer.shape[1],
                           self.buffer.shape[2]))

    @property
    def timeValues(self):
        N = self.buffer.shape[0] * self.buffer.shape[1]
        return np.linspace(0, N/self.fs, N)