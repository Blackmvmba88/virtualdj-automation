"""
Audio Observer Module for VirtualDJ Automation

This module captures audio, extracts features (RMS, beat detection),
and reads VirtualDJ state information.
"""

import numpy as np
import sounddevice as sd
import librosa
import scipy.signal
from typing import Dict, Optional, List, Tuple
import time
import threading
from collections import deque


class AudioObserver:
    """
    Observer class to capture and analyze audio from VirtualDJ output.
    """
    
    def __init__(self, sample_rate: int = 44100, block_size: int = 2048, device: Optional[int] = None):
        """
        Initialize audio observer.
        
        Args:
            sample_rate: Audio sample rate in Hz
            block_size: Size of audio blocks for processing
            device: Audio input device index (None for default)
        """
        self.sample_rate = sample_rate
        self.block_size = block_size
        self.device = device
        
        # Audio buffer for analysis
        self.buffer_duration = 5.0  # seconds
        self.buffer_size = int(self.sample_rate * self.buffer_duration)
        # Use deque for efficient circular buffer
        self.audio_buffer = deque(maxlen=self.buffer_size)
        
        # Cache for numpy conversions to avoid repeated list conversions
        self._buffer_cache = None
        self._buffer_cache_valid = False
        
        # Feature storage
        self.current_features = {
            'rms': 0.0,
            'rms_db': -80.0,
            'beat_detected': False,
            'bpm': 0.0,
            'spectral_centroid': 0.0,
            'spectral_rolloff': 0.0,
            'zero_crossing_rate': 0.0,
            'energy': 0.0,
            'low_band_balance': 0.0,
            'mid_band_balance': 0.0,
            'high_band_balance': 0.0,
            'quality_score': 0.5
        }
        
        # Beat detection state
        self.beat_threshold = 1.5
        self.last_beat_time = 0.0
        self.beat_history = deque(maxlen=8)
        
        # Streaming state
        self.is_streaming = False
        self.stream = None
        self.processing_thread = None
        self.lock = threading.Lock()
        
        # VirtualDJ state (simulated - in real scenario would read from VirtualDJ API)
        self.vdj_state = {
            'deck_a_playing': False,
            'deck_b_playing': False,
            'deck_a_position': 0.0,
            'deck_b_position': 0.0,
            'crossfader_position': 0.5,
            'master_volume': 0.8,
            'deck_a_bpm': 0.0,
            'deck_b_bpm': 0.0
        }
    
    def _audio_callback(self, indata, frames, time_info, status):
        """
        Callback for audio stream processing.
        
        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Time information
            status: Stream status
        """
        if status:
            print(f"Audio stream status: {status}")
        
        # Convert to mono if stereo
        if indata.shape[1] > 1:
            audio_mono = np.mean(indata, axis=1)
        else:
            audio_mono = indata[:, 0]
        
        # Add to buffer
        with self.lock:
            self.audio_buffer.extend(audio_mono)
            self._buffer_cache_valid = False  # Invalidate cache on new data
    
    def start_streaming(self):
        """Start audio streaming and processing."""
        if self.is_streaming:
            print("Audio streaming already active")
            return
        
        try:
            self.stream = sd.InputStream(
                device=self.device,
                channels=2,
                samplerate=self.sample_rate,
                blocksize=self.block_size,
                callback=self._audio_callback
            )
            self.stream.start()
            self.is_streaming = True
            
            # Start processing thread
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.processing_thread.start()
            
            print(f"Audio streaming started (device: {self.device}, sample rate: {self.sample_rate} Hz)")
            
        except Exception as e:
            print(f"Error starting audio stream: {e}")
            self.is_streaming = False
    
    def stop_streaming(self):
        """Stop audio streaming and processing."""
        if not self.is_streaming:
            return
        
        self.is_streaming = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)
            self.processing_thread = None
        
        print("Audio streaming stopped")
    
    def _processing_loop(self):
        """Background processing loop for feature extraction."""
        while self.is_streaming:
            time.sleep(0.1)  # Process every 100ms
            
            with self.lock:
                if len(self.audio_buffer) < self.block_size:
                    continue
                
                # Get recent audio data efficiently
                buffer_len = len(self.audio_buffer)
                start_idx = max(0, buffer_len - self.block_size)
                # Convert only the needed portion
                audio_data = np.fromiter(
                    (self.audio_buffer[i] for i in range(start_idx, buffer_len)),
                    dtype=np.float64,
                    count=min(self.block_size, buffer_len - start_idx)
                )
            
            # Extract features
            self._extract_features(audio_data)
    
    def _extract_features(self, audio_data: np.ndarray):
        """
        Extract audio features from audio data.
        
        Args:
            audio_data: Audio samples as numpy array
        """
        try:
            # RMS (Root Mean Square) - amplitude measure
            rms = np.sqrt(np.mean(audio_data ** 2))
            rms_db = 20 * np.log10(rms + 1e-10)
            
            # Energy
            energy = np.sum(audio_data ** 2)
            
            # Zero Crossing Rate
            zcr = np.mean(librosa.feature.zero_crossing_rate(audio_data))
            
            # Spectral features (require FFT)
            spectral_centroid = 0.0
            spectral_rolloff = 0.0
            low_band_balance = 0.0
            mid_band_balance = 0.0
            high_band_balance = 0.0
            
            if len(audio_data) >= 2048:
                # Spectral Centroid
                spectral_centroids = librosa.feature.spectral_centroid(
                    y=audio_data, sr=self.sample_rate
                )
                spectral_centroid = np.mean(spectral_centroids)
                
                # Spectral Rolloff
                spectral_rolloffs = librosa.feature.spectral_rolloff(
                    y=audio_data, sr=self.sample_rate
                )
                spectral_rolloff = np.mean(spectral_rolloffs)
                
                # Calculate spectral band balances
                # Get FFT for frequency analysis
                fft = np.fft.rfft(audio_data)
                magnitude = np.abs(fft)
                freqs = np.fft.rfftfreq(len(audio_data), 1.0/self.sample_rate)
                
                # Define frequency bands (Hz)
                low_band = (20, 250)    # Bass
                mid_band = (250, 2000)  # Mids
                high_band = (2000, 8000) # Highs
                
                # Calculate energy in each band
                low_mask = (freqs >= low_band[0]) & (freqs < low_band[1])
                mid_mask = (freqs >= mid_band[0]) & (freqs < mid_band[1])
                high_mask = (freqs >= high_band[0]) & (freqs < high_band[1])
                
                low_energy = np.sum(magnitude[low_mask] ** 2)
                mid_energy = np.sum(magnitude[mid_mask] ** 2)
                high_energy = np.sum(magnitude[high_mask] ** 2)
                
                total_energy = low_energy + mid_energy + high_energy
                
                if total_energy > 0:
                    # Balance = (energy_deck_a - energy_deck_b) / total
                    # For now, simulated as deviation from equal distribution (1/3 each)
                    low_ratio = low_energy / total_energy
                    mid_ratio = mid_energy / total_energy
                    high_ratio = high_energy / total_energy
                    
                    # Balance: deviation from 0.33 (ideal equal distribution)
                    low_band_balance = (low_ratio - 0.33) * 3.0  # Scale to ~[-1, 1]
                    mid_band_balance = (mid_ratio - 0.33) * 3.0
                    high_band_balance = (high_ratio - 0.33) * 3.0
            
            # Beat detection (simple energy-based)
            beat_detected = self._detect_beat(energy)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(
                rms_db, energy, spectral_centroid, 
                low_band_balance, mid_band_balance, high_band_balance
            )
            
            # Update current features
            with self.lock:
                self.current_features.update({
                    'rms': float(rms),
                    'rms_db': float(rms_db),
                    'beat_detected': beat_detected,
                    'spectral_centroid': float(spectral_centroid),
                    'spectral_rolloff': float(spectral_rolloff),
                    'zero_crossing_rate': float(zcr),
                    'energy': float(energy),
                    'low_band_balance': float(low_band_balance),
                    'mid_band_balance': float(mid_band_balance),
                    'high_band_balance': float(high_band_balance),
                    'quality_score': float(quality_score)
                })
                
                # Estimate BPM from beat history
                if len(self.beat_history) >= 4:
                    intervals = np.diff(list(self.beat_history))
                    avg_interval = np.mean(intervals)
                    if avg_interval > 0:
                        self.current_features['bpm'] = 60.0 / avg_interval
        
        except Exception as e:
            print(f"Error extracting features: {e}")
    
    def _calculate_quality_score(self, rms_db: float, energy: float, 
                                  spectral_centroid: float, 
                                  low_balance: float, mid_balance: float, 
                                  high_balance: float) -> float:
        """
        Calculate overall mix quality score based on audio features.
        
        Args:
            rms_db: RMS level in dB
            energy: Audio energy
            spectral_centroid: Spectral centroid
            low_balance: Low frequency band balance
            mid_balance: Mid frequency band balance
            high_balance: High frequency band balance
            
        Returns:
            Quality score between 0.0 and 1.0
        """
        quality_score = 0.0
        
        # RMS level check (should be in good range)
        if -20 <= rms_db <= -6:
            quality_score += 0.3
        elif -30 <= rms_db <= -3:
            quality_score += 0.15
        
        # Energy consistency
        if energy > 0.01:
            quality_score += 0.2
        
        # Spectral balance
        if 1000 < spectral_centroid < 3000:
            quality_score += 0.2
        
        # Band balance check - penalize extreme imbalances
        balance_penalty = 0.0
        for balance in [low_balance, mid_balance, high_balance]:
            if abs(balance) > 0.5:
                balance_penalty += 0.05
        
        quality_score = max(0.0, quality_score - balance_penalty)
        
        # BPM presence adds to quality
        if self.current_features.get('bpm', 0.0) > 0:
            quality_score += 0.1
        
        return min(1.0, quality_score)
    
    def _detect_beat(self, energy: float) -> bool:
        """
        Simple beat detection based on energy.
        
        Args:
            energy: Current energy value
            
        Returns:
            True if beat detected, False otherwise
        """
        current_time = time.time()
        
        # Minimum time between beats (prevents multiple detections)
        min_beat_interval = 0.3  # 200 BPM max
        
        if current_time - self.last_beat_time < min_beat_interval:
            return False
        
        # Check if energy exceeds threshold
        if len(self.audio_buffer) > self.block_size * 2:
            with self.lock:
                buffer_len = len(self.audio_buffer)
                start_idx = max(0, buffer_len - self.block_size * 4)
                end_idx = max(0, buffer_len - self.block_size)
                # Efficient iteration without full list conversion
                recent_energy = np.fromiter(
                    (self.audio_buffer[i] for i in range(start_idx, end_idx)),
                    dtype=np.float64,
                    count=end_idx - start_idx
                )
            
            avg_energy = np.mean(recent_energy ** 2)
            
            if energy > avg_energy * self.beat_threshold:
                self.last_beat_time = current_time
                self.beat_history.append(current_time)
                return True
        
        return False
    
    def get_features(self) -> Dict:
        """
        Get current audio features.
        
        Returns:
            Dictionary with current audio features
        """
        with self.lock:
            return self.current_features.copy()
    
    def get_vdj_state(self) -> Dict:
        """
        Get VirtualDJ state (simulated).
        In a real implementation, this would read from VirtualDJ API or shared memory.
        
        Returns:
            Dictionary with VirtualDJ state information
        """
        return self.vdj_state.copy()
    
    def update_vdj_state(self, state_update: Dict):
        """
        Update VirtualDJ state information.
        
        Args:
            state_update: Dictionary with state updates
        """
        self.vdj_state.update(state_update)
    
    def analyze_buffer(self, duration: float = 2.0) -> Dict:
        """
        Analyze audio buffer over a specified duration.
        
        Args:
            duration: Duration in seconds to analyze
            
        Returns:
            Dictionary with analysis results
        """
        samples_to_analyze = int(self.sample_rate * duration)
        
        with self.lock:
            if len(self.audio_buffer) < samples_to_analyze:
                return {'error': 'Insufficient audio data in buffer'}
            
            audio_data = np.array(list(self.audio_buffer)[-samples_to_analyze:])
        
        # Perform comprehensive analysis
        try:
            # RMS over time
            frame_length = 2048
            hop_length = 512
            rms_frames = librosa.feature.rms(y=audio_data, frame_length=frame_length, hop_length=hop_length)
            
            # Tempo and beat tracking
            tempo, beats = librosa.beat.beat_track(y=audio_data, sr=self.sample_rate)
            
            # Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate)
            spectral_rolloffs = librosa.feature.spectral_rolloff(y=audio_data, sr=self.sample_rate)
            
            # Chroma features (for harmonic analysis)
            chroma = librosa.feature.chroma_stft(y=audio_data, sr=self.sample_rate)
            
            analysis = {
                'duration': duration,
                'avg_rms': float(np.mean(rms_frames)),
                'rms_std': float(np.std(rms_frames)),
                'estimated_tempo': float(tempo),
                'beat_count': len(beats),
                'avg_spectral_centroid': float(np.mean(spectral_centroids)),
                'avg_spectral_rolloff': float(np.mean(spectral_rolloffs)),
                'chroma_mean': chroma.mean(axis=1).tolist(),
                'dynamic_range': float(np.max(rms_frames) - np.min(rms_frames))
            }
            
            return analysis
            
        except Exception as e:
            return {'error': f'Analysis failed: {str(e)}'}
    
    def estimate_mix_quality(self) -> float:
        """
        Estimate current mix quality based on audio features.
        
        Returns:
            Quality score (0.0 to 1.0)
        """
        features = self.get_features()
        
        # Simple quality heuristic based on multiple factors
        quality_score = 0.0
        
        # Check RMS level (should be in good range)
        rms_db = features['rms_db']
        if -20 <= rms_db <= -6:
            quality_score += 0.3
        elif -30 <= rms_db <= -3:
            quality_score += 0.15
        
        # Check energy consistency
        if features['energy'] > 0.01:
            quality_score += 0.2
        
        # Check spectral balance
        if 1000 < features['spectral_centroid'] < 3000:
            quality_score += 0.2
        
        # Beat detection (rhythm consistency)
        if features['bpm'] > 0:
            quality_score += 0.3
        
        return min(1.0, quality_score)
    
    def __del__(self):
        """Destructor to ensure streaming is stopped."""
        self.stop_streaming()


if __name__ == "__main__":
    # Example usage
    print("VirtualDJ Audio Observer - Test Mode")
    print("=" * 50)
    
    observer = AudioObserver()
    
    print("\nStarting audio capture (5 seconds)...")
    observer.start_streaming()
    
    try:
        for i in range(10):
            time.sleep(0.5)
            features = observer.get_features()
            print(f"\nFeatures at {i*0.5:.1f}s:")
            print(f"  RMS: {features['rms']:.4f} ({features['rms_db']:.1f} dB)")
            print(f"  Energy: {features['energy']:.4f}")
            print(f"  Beat detected: {features['beat_detected']}")
            print(f"  BPM: {features['bpm']:.1f}")
            print(f"  Quality score: {observer.estimate_mix_quality():.2f}")
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        observer.stop_streaming()
        print("\nTest complete!")
