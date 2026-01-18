"""
Musical Semantic Analysis Module for VirtualDJ Automation

This module provides high-level musical understanding beyond basic features,
detecting percussive density, harmonic content, vocal presence, and mood.
"""

import numpy as np
import librosa
from typing import Dict, Optional, List
from collections import deque


class MusicalSemanticAnalyzer:
    """
    Analyzes music for semantic features beyond low-level audio characteristics.
    
    Detects:
    - Percussive density (how drum-heavy the music is)
    - Harmonic vs dissonant content
    - Vocal presence
    - Harmonic scene (key, mode, emotional tone)
    - Musical texture (sparse, dense, layered)
    """
    
    def __init__(self, sample_rate: int = 44100):
        """
        Initialize semantic analyzer.
        
        Args:
            sample_rate: Audio sample rate
        """
        self.sample_rate = sample_rate
        
        # Analysis history for temporal smoothing
        self.percussive_density_history = deque(maxlen=10)
        self.harmonicity_history = deque(maxlen=10)
        self.vocal_presence_history = deque(maxlen=10)
        
        # Cached results
        self.last_analysis = {
            'percussive_density': 0.0,
            'harmonicity': 0.0,
            'dissonance': 0.0,
            'vocal_presence': 0.0,
            'harmonic_scene': 'unknown',
            'key': None,
            'mode': None,
            'texture': 'balanced',
            'emotional_tone': 'neutral'
        }
    
    def analyze(self, audio_buffer: np.ndarray, audio_features: Dict) -> Dict:
        """
        Perform semantic analysis on audio buffer.
        
        Args:
            audio_buffer: Audio samples (mono)
            audio_features: Basic audio features from AudioObserver
            
        Returns:
            Dictionary with semantic features
        """
        if len(audio_buffer) < 2048:
            return self.last_analysis
        
        # Ensure audio is float32 and normalized
        audio = np.array(audio_buffer, dtype=np.float32)
        if np.max(np.abs(audio)) > 0:
            audio = audio / np.max(np.abs(audio))
        
        # Analyze percussive density
        percussive_density = self._analyze_percussive_density(audio, audio_features)
        self.percussive_density_history.append(percussive_density)
        
        # Analyze harmonic content
        harmonicity, dissonance = self._analyze_harmonic_content(audio)
        self.harmonicity_history.append(harmonicity)
        
        # Analyze vocal presence
        vocal_presence = self._analyze_vocal_presence(audio, audio_features)
        self.vocal_presence_history.append(vocal_presence)
        
        # Determine harmonic scene (key, mode, emotional tone)
        harmonic_scene = self._determine_harmonic_scene(audio, harmonicity, dissonance)
        
        # Determine texture
        texture = self._determine_texture(audio, percussive_density, harmonicity)
        
        # Smooth results using history
        smoothed_percussive = np.mean(self.percussive_density_history)
        smoothed_harmonicity = np.mean(self.harmonicity_history)
        smoothed_vocal = np.mean(self.vocal_presence_history)
        
        analysis = {
            'percussive_density': float(smoothed_percussive),
            'harmonicity': float(smoothed_harmonicity),
            'dissonance': float(dissonance),
            'vocal_presence': float(smoothed_vocal),
            'harmonic_scene': harmonic_scene['scene'],
            'key': harmonic_scene.get('key'),
            'mode': harmonic_scene.get('mode'),
            'texture': texture,
            'emotional_tone': harmonic_scene['emotional_tone']
        }
        
        self.last_analysis = analysis
        return analysis
    
    def _analyze_percussive_density(self, audio: np.ndarray, audio_features: Dict) -> float:
        """
        Analyze how percussive/drum-heavy the audio is.
        
        Uses zero-crossing rate, energy, and beat detection.
        
        Args:
            audio: Audio samples
            audio_features: Basic features
            
        Returns:
            Percussive density (0.0 to 1.0)
        """
        # High zero-crossing rate suggests percussive content
        zcr = audio_features.get('zero_crossing_rate', 0.0)
        
        # Beat detection indicates rhythmic content
        beat_detected = audio_features.get('beat_detected', False)
        
        # High energy with beat suggests percussion
        energy = audio_features.get('energy', 0.0)
        
        # Spectral flux (change in spectrum) indicates transients
        if len(audio) >= 4096:
            stft = librosa.stft(audio[:4096], n_fft=2048, hop_length=512)
            spectral_flux = np.mean(np.diff(np.abs(stft), axis=1))
            spectral_flux = min(1.0, spectral_flux * 10)  # Normalize
        else:
            spectral_flux = 0.0
        
        # Combine indicators
        density = (
            zcr * 0.3 +
            float(beat_detected) * 0.3 +
            energy * 0.2 +
            spectral_flux * 0.2
        )
        
        return float(np.clip(density, 0.0, 1.0))
    
    def _analyze_harmonic_content(self, audio: np.ndarray) -> tuple:
        """
        Analyze harmonic vs dissonant content.
        
        Args:
            audio: Audio samples
            
        Returns:
            Tuple of (harmonicity, dissonance) both 0.0 to 1.0
        """
        if len(audio) < 4096:
            return 0.5, 0.5
        
        # Use chromagram to detect harmonic content
        try:
            # Compute chroma features
            chroma = librosa.feature.chroma_stft(
                y=audio[:min(len(audio), 22050)],  # Use up to 0.5 seconds
                sr=self.sample_rate,
                n_fft=2048,
                hop_length=512
            )
            
            # Harmonicity: concentration in few chroma bins suggests harmony
            chroma_energy = np.sum(chroma, axis=1)
            if np.sum(chroma_energy) > 0:
                chroma_energy = chroma_energy / np.sum(chroma_energy)
                entropy = -np.sum(chroma_energy * np.log(chroma_energy + 1e-10))
                max_entropy = np.log(12)  # Maximum entropy for 12 notes
                harmonicity = 1.0 - (entropy / max_entropy)
            else:
                harmonicity = 0.5
            
            # Dissonance: energy spread across many frequencies
            # High standard deviation in chroma suggests dissonance
            chroma_std = np.std(chroma)
            dissonance = min(1.0, chroma_std * 2.0)
            
        except Exception as e:
            # Fallback if chroma computation fails
            harmonicity = 0.5
            dissonance = 0.5
        
        return float(harmonicity), float(dissonance)
    
    def _analyze_vocal_presence(self, audio: np.ndarray, audio_features: Dict) -> float:
        """
        Detect vocal presence in audio.
        
        Vocals typically have energy in 300-3000 Hz range with specific
        spectral characteristics.
        
        Args:
            audio: Audio samples
            audio_features: Basic features
            
        Returns:
            Vocal presence score (0.0 to 1.0)
        """
        if len(audio) < 2048:
            return 0.0
        
        # Spectral centroid in vocal range (300-3000 Hz) suggests vocals
        spectral_centroid = audio_features.get('spectral_centroid', 0.0)
        
        # Vocals typically have centroid in 500-2500 Hz range
        vocal_range_score = 0.0
        if 500 < spectral_centroid < 2500:
            # Closer to 1500 Hz = higher vocal likelihood
            distance_from_optimal = abs(spectral_centroid - 1500)
            vocal_range_score = 1.0 - min(1.0, distance_from_optimal / 1000)
        
        # Spectral rolloff can indicate vocal presence
        spectral_rolloff = audio_features.get('spectral_rolloff', 0.0)
        
        # Moderate rolloff suggests vocals (not too low, not too high)
        rolloff_score = 0.0
        if 2000 < spectral_rolloff < 6000:
            rolloff_score = 0.5
        
        # Combine indicators
        vocal_presence = vocal_range_score * 0.7 + rolloff_score * 0.3
        
        return float(np.clip(vocal_presence, 0.0, 1.0))
    
    def _determine_harmonic_scene(self, audio: np.ndarray, 
                                  harmonicity: float, 
                                  dissonance: float) -> Dict:
        """
        Determine the harmonic scene (key, mode, emotional tone).
        
        Args:
            audio: Audio samples
            harmonicity: Harmonicity score
            dissonance: Dissonance score
            
        Returns:
            Dictionary with scene information
        """
        scene = {
            'scene': 'unknown',
            'key': None,
            'mode': None,
            'emotional_tone': 'neutral'
        }
        
        # Determine mode (major/minor) and emotional tone
        if harmonicity > 0.6:
            # Harmonic content present
            if dissonance < 0.3:
                # Low dissonance suggests major/happy
                scene['mode'] = 'major'
                scene['emotional_tone'] = 'uplifting'
                scene['scene'] = 'major_bright'
            elif dissonance > 0.6:
                # High dissonance with harmony suggests minor/dark
                scene['mode'] = 'minor'
                scene['emotional_tone'] = 'dark'
                scene['scene'] = 'minor_dark'
            else:
                # Moderate dissonance
                scene['mode'] = 'major'
                scene['emotional_tone'] = 'energetic'
                scene['scene'] = 'major_energetic'
        else:
            # Low harmonicity suggests atonal or percussive
            if dissonance > 0.7:
                scene['scene'] = 'atonal_chaotic'
                scene['emotional_tone'] = 'intense'
            else:
                scene['scene'] = 'percussive_neutral'
                scene['emotional_tone'] = 'rhythmic'
        
        # Attempt key detection (simplified)
        try:
            if len(audio) >= 22050 and harmonicity > 0.5:  # Need enough audio
                chroma = librosa.feature.chroma_stft(
                    y=audio[:min(len(audio), 44100)],
                    sr=self.sample_rate,
                    n_fft=2048
                )
                # Find dominant chroma bin
                chroma_mean = np.mean(chroma, axis=1)
                dominant_chroma = np.argmax(chroma_mean)
                key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 
                           'F#', 'G', 'G#', 'A', 'A#', 'B']
                scene['key'] = key_names[dominant_chroma]
        except:
            pass
        
        return scene
    
    def _determine_texture(self, audio: np.ndarray, 
                          percussive_density: float, 
                          harmonicity: float) -> str:
        """
        Determine musical texture (sparse, dense, layered, etc.).
        
        Args:
            audio: Audio samples
            percussive_density: Percussive density score
            harmonicity: Harmonicity score
            
        Returns:
            Texture descriptor
        """
        # Simple texture classification based on density and harmony
        if percussive_density > 0.7 and harmonicity > 0.6:
            return 'dense_layered'
        elif percussive_density > 0.7:
            return 'percussive_heavy'
        elif harmonicity > 0.7:
            return 'harmonic_rich'
        elif percussive_density < 0.3 and harmonicity < 0.3:
            return 'sparse_minimal'
        elif percussive_density < 0.3:
            return 'ambient_atmospheric'
        else:
            return 'balanced'
    
    def get_transition_recommendation(self, current_scene: Dict, 
                                     target_scene: Dict) -> Dict:
        """
        Recommend transition strategy based on semantic analysis.
        
        Args:
            current_scene: Current track's semantic features
            target_scene: Target track's semantic features
            
        Returns:
            Transition recommendations
        """
        recommendation = {
            'transition_type': 'standard',
            'duration': 8.0,
            'use_effects': False,
            'effect_type': None,
            'eq_strategy': 'balanced'
        }
        
        # If moving from high to low energy
        current_perc = current_scene.get('percussive_density', 0.5)
        target_perc = target_scene.get('percussive_density', 0.5)
        
        if current_perc - target_perc > 0.3:
            # Drop in energy - use longer transition
            recommendation['transition_type'] = 'breakdown'
            recommendation['duration'] = 12.0
            recommendation['use_effects'] = True
            recommendation['effect_type'] = 'reverb'
        
        elif target_perc - current_perc > 0.3:
            # Build in energy - faster transition
            recommendation['transition_type'] = 'buildup'
            recommendation['duration'] = 6.0
            recommendation['use_effects'] = True
            recommendation['effect_type'] = 'delay'
        
        # If harmonic scenes are very different
        current_tone = current_scene.get('emotional_tone', 'neutral')
        target_tone = target_scene.get('emotional_tone', 'neutral')
        
        tonal_contrast = {
            ('dark', 'uplifting'): True,
            ('uplifting', 'dark'): True,
            ('intense', 'rhythmic'): True,
        }
        
        if tonal_contrast.get((current_tone, target_tone), False):
            # Major tonal shift - use effects
            recommendation['use_effects'] = True
            recommendation['effect_type'] = 'filter'
            recommendation['eq_strategy'] = 'gradual_swap'
        
        # If both tracks have vocals
        if current_scene.get('vocal_presence', 0) > 0.5 and \
           target_scene.get('vocal_presence', 0) > 0.5:
            # Be careful with vocal clashes
            recommendation['duration'] = max(10.0, recommendation['duration'])
            recommendation['eq_strategy'] = 'mid_cut_transition'
        
        return recommendation
    
    def reset(self):
        """Reset analysis history."""
        self.percussive_density_history.clear()
        self.harmonicity_history.clear()
        self.vocal_presence_history.clear()


if __name__ == "__main__":
    # Example usage
    print("Musical Semantic Analyzer - Test Mode")
    print("=" * 60)
    
    analyzer = MusicalSemanticAnalyzer()
    
    # Generate test audio (simulate different musical characteristics)
    sample_rate = 44100
    duration = 2.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Test 1: Harmonic content (sine waves)
    print("\nTest 1: Harmonic Content (Chord)")
    harmonic_audio = (np.sin(2 * np.pi * 440 * t) +  # A
                      np.sin(2 * np.pi * 554.37 * t) +  # C#
                      np.sin(2 * np.pi * 659.25 * t))  # E
    harmonic_audio = harmonic_audio / 3.0
    
    audio_features = {
        'energy': 0.5,
        'zero_crossing_rate': 0.1,
        'beat_detected': False,
        'spectral_centroid': 1500.0,
        'spectral_rolloff': 3000.0
    }
    
    result = analyzer.analyze(harmonic_audio, audio_features)
    print(f"  Percussive Density: {result['percussive_density']:.2f}")
    print(f"  Harmonicity: {result['harmonicity']:.2f}")
    print(f"  Dissonance: {result['dissonance']:.2f}")
    print(f"  Vocal Presence: {result['vocal_presence']:.2f}")
    print(f"  Harmonic Scene: {result['harmonic_scene']}")
    print(f"  Emotional Tone: {result['emotional_tone']}")
    print(f"  Texture: {result['texture']}")
    
    # Test 2: Percussive content (noise bursts)
    print("\nTest 2: Percussive Content (Drums)")
    percussive_audio = np.random.randn(len(t)) * 0.1
    # Add some beats
    for i in range(0, len(t), len(t) // 8):
        if i < len(t) - 1000:
            percussive_audio[i:i+1000] += np.random.randn(1000) * 0.5
    
    audio_features = {
        'energy': 0.8,
        'zero_crossing_rate': 0.6,
        'beat_detected': True,
        'spectral_centroid': 4000.0,
        'spectral_rolloff': 8000.0
    }
    
    result = analyzer.analyze(percussive_audio, audio_features)
    print(f"  Percussive Density: {result['percussive_density']:.2f}")
    print(f"  Harmonicity: {result['harmonicity']:.2f}")
    print(f"  Dissonance: {result['dissonance']:.2f}")
    print(f"  Vocal Presence: {result['vocal_presence']:.2f}")
    print(f"  Harmonic Scene: {result['harmonic_scene']}")
    print(f"  Emotional Tone: {result['emotional_tone']}")
    print(f"  Texture: {result['texture']}")
    
    # Test 3: Transition recommendations
    print("\n" + "=" * 60)
    print("Test 3: Transition Recommendations")
    print("=" * 60)
    
    scene1 = {
        'percussive_density': 0.8,
        'emotional_tone': 'intense',
        'vocal_presence': 0.3
    }
    
    scene2 = {
        'percussive_density': 0.3,
        'emotional_tone': 'rhythmic',
        'vocal_presence': 0.1
    }
    
    recommendation = analyzer.get_transition_recommendation(scene1, scene2)
    print(f"\nTransitioning from high to low energy:")
    print(f"  Type: {recommendation['transition_type']}")
    print(f"  Duration: {recommendation['duration']}s")
    print(f"  Use Effects: {recommendation['use_effects']}")
    print(f"  Effect Type: {recommendation['effect_type']}")
    print(f"  EQ Strategy: {recommendation['eq_strategy']}")
    
    print("\nTest complete!")
