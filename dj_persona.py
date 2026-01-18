"""
DJ Persona Module for VirtualDJ Automation

This module implements personality-driven mixing styles that give the agent
distinct behaviors based on different electronic music genres and DJ approaches.
"""

import numpy as np
from typing import Dict, Optional
from adaptive_agent import AdaptiveAgent


class DJPersona:
    """
    DJ Persona system that defines style-specific mixing behaviors.
    
    Each persona represents a different DJ style with unique parameters
    for mixing decisions, effects usage, and transition timing.
    """
    
    # Persona definitions with style-specific parameters
    PERSONAS = {
        'techno_detroit': {
            'name': 'Techno Detroit',
            'description': 'Minimal, industrial, hypnotic - the soul of Detroit techno',
            'optimal_bpm_range': (125, 135),
            'crossfade_speed': 'slow',  # Long, hypnotic transitions
            'eq_style': 'minimal',  # Subtle EQ changes
            'effect_probability': 0.25,
            'effect_preference': [1, 2],  # Delay and reverb
            'energy_target': 0.7,  # Sustained energy
            'bass_boost': 0.1,
            'high_cut': -0.05,  # Slightly darker sound
            'transition_on_beat': True,
            'experimental_factor': 0.3,
        },
        'psytrance_goa': {
            'name': 'Psy-Trance Goa',
            'description': 'Psychedelic, trippy, high-energy spiritual journey',
            'optimal_bpm_range': (138, 148),
            'crossfade_speed': 'medium',
            'eq_style': 'dynamic',  # Active EQ manipulation
            'effect_probability': 0.45,  # Heavy effects usage
            'effect_preference': [1, 2, 3],  # All effects
            'energy_target': 0.85,  # High sustained energy
            'bass_boost': 0.15,
            'high_cut': 0.1,  # Bright, sparkly highs
            'transition_on_beat': True,
            'experimental_factor': 0.6,  # More creative/risky
        },
        'latin_bass': {
            'name': 'Latin Bass',
            'description': 'Reggaeton, dembow, perreo - fuego y flow',
            'optimal_bpm_range': (90, 105),
            'crossfade_speed': 'fast',  # Quick cuts
            'eq_style': 'bass_heavy',
            'effect_probability': 0.20,
            'effect_preference': [1, 3],  # Delay and filters
            'energy_target': 0.75,
            'bass_boost': 0.25,  # Heavy bass emphasis
            'high_cut': 0.0,
            'transition_on_beat': True,
            'experimental_factor': 0.4,
        },
        'lofi_chillhop': {
            'name': 'Lo-Fi ChillHop',
            'description': 'Relaxed, jazzy, nostalgic - study beats aesthetic',
            'optimal_bpm_range': (70, 95),
            'crossfade_speed': 'very_slow',  # Ultra-smooth transitions
            'eq_style': 'warm',  # Warm, mellow EQ
            'effect_probability': 0.15,
            'effect_preference': [2],  # Primarily reverb
            'energy_target': 0.4,  # Low, relaxed energy
            'bass_boost': 0.05,
            'high_cut': -0.15,  # Rolled-off highs for warmth
            'transition_on_beat': False,  # More organic transitions
            'experimental_factor': 0.2,  # Conservative, smooth
        }
    }
    
    def __init__(self, persona_name: str = 'techno_detroit'):
        """
        Initialize DJ Persona.
        
        Args:
            persona_name: Name of the persona to use
        """
        if persona_name not in self.PERSONAS:
            raise ValueError(f"Unknown persona: {persona_name}. Available: {list(self.PERSONAS.keys())}")
        
        self.persona_name = persona_name
        self.config = self.PERSONAS[persona_name].copy()
        
        # Persona state
        self.current_mood = 'building'  # building, peak, breakdown, outro
        self.transition_count = 0
        self.set_duration = 0.0
    
    def get_persona_adjustments(self, base_actions: Dict, audio_features: Dict, 
                               vdj_state: Dict) -> Dict:
        """
        Apply persona-specific adjustments to base actions.
        
        Args:
            base_actions: Base actions from the agent
            audio_features: Current audio features
            vdj_state: VirtualDJ state
            
        Returns:
            Modified actions with persona characteristics applied
        """
        actions = base_actions.copy()
        
        # Apply crossfade speed preference
        crossfade_multiplier = self._get_crossfade_speed_multiplier()
        if 'crossfade_adjust' in actions:
            actions['crossfade_adjust'] *= crossfade_multiplier
        
        # Apply EQ style
        if 'eq_adjust' not in actions:
            actions['eq_adjust'] = {}
        
        eq_adjustments = self._get_eq_style_adjustments(audio_features)
        for band, value in eq_adjustments.items():
            if band in actions['eq_adjust']:
                actions['eq_adjust'][band] += value
            else:
                actions['eq_adjust'][band] = value
        
        # Apply effect probability
        if actions.get('effect_trigger') is None:
            if np.random.random() < self.config['effect_probability']:
                # Choose from preferred effects
                actions['effect_trigger'] = np.random.choice(self.config['effect_preference'])
        
        # Energy-based decisions
        current_energy = audio_features.get('energy', 0.0)
        target_energy = self.config['energy_target']
        
        # Adjust volumes to reach target energy
        energy_diff = target_energy - current_energy
        if abs(energy_diff) > 0.15:
            volume_adjust = energy_diff * 0.3
            actions['volume_adjust_a'] += volume_adjust
            actions['volume_adjust_b'] += volume_adjust
        
        # Experimental factor affects transition timing
        if self.config['experimental_factor'] > 0.5:
            # More experimental personas might transition off-beat sometimes
            if not self.config['transition_on_beat']:
                actions['transition_now'] = actions.get('transition_now', False) or \
                                           (np.random.random() < 0.15)
        
        return actions
    
    def _get_crossfade_speed_multiplier(self) -> float:
        """Get crossfade speed multiplier based on persona."""
        speed_map = {
            'very_slow': 0.5,
            'slow': 0.7,
            'medium': 1.0,
            'fast': 1.5,
            'very_fast': 2.0
        }
        return speed_map.get(self.config['crossfade_speed'], 1.0)
    
    def _get_eq_style_adjustments(self, audio_features: Dict) -> Dict:
        """Get EQ adjustments based on persona style."""
        eq_style = self.config['eq_style']
        adjustments = {}
        
        if eq_style == 'minimal':
            # Subtle adjustments
            pass  # Minimal changes
        
        elif eq_style == 'dynamic':
            # Active EQ manipulation based on spectral content
            spectral_centroid = audio_features.get('spectral_centroid', 0.0)
            if spectral_centroid > 3000:
                adjustments['high'] = -0.15
                adjustments['mid'] = 0.1
            elif spectral_centroid < 1500:
                adjustments['high'] = 0.15
                adjustments['low'] = -0.1
        
        elif eq_style == 'bass_heavy':
            # Emphasize bass
            adjustments['low'] = self.config['bass_boost']
        
        elif eq_style == 'warm':
            # Warm, mellow sound
            adjustments['low'] = self.config['bass_boost']
            adjustments['high'] = self.config['high_cut']
        
        # Apply universal bass and high adjustments
        if 'low' not in adjustments:
            adjustments['low'] = self.config.get('bass_boost', 0.0)
        if 'high' not in adjustments and self.config.get('high_cut', 0.0) != 0.0:
            adjustments['high'] = self.config.get('high_cut', 0.0)
        
        return adjustments
    
    def update_mood(self, set_progress: float, energy: float):
        """
        Update persona mood based on set progress and energy.
        
        Args:
            set_progress: Progress through the set (0.0 to 1.0)
            energy: Current energy level
        """
        if set_progress < 0.2:
            self.current_mood = 'building'
        elif set_progress < 0.7:
            if energy > 0.7:
                self.current_mood = 'peak'
            else:
                self.current_mood = 'building'
        elif set_progress < 0.9:
            self.current_mood = 'breakdown'
        else:
            self.current_mood = 'outro'
    
    def get_info(self) -> Dict:
        """
        Get persona information.
        
        Returns:
            Dictionary with persona details
        """
        return {
            'name': self.config['name'],
            'description': self.config['description'],
            'current_mood': self.current_mood,
            'transition_count': self.transition_count,
            'experimental_factor': self.config['experimental_factor'],
            'energy_target': self.config['energy_target']
        }


class PersonaAgent(AdaptiveAgent):
    """
    Extended AdaptiveAgent with DJ Persona capabilities.
    
    This agent combines reinforcement learning with persona-driven
    stylistic constraints for different DJ styles.
    """
    
    def __init__(self, learning_mode: str = 'heuristic', 
                 persona: str = 'techno_detroit',
                 model_path: Optional[str] = None, 
                 random_seed: Optional[int] = None):
        """
        Initialize PersonaAgent.
        
        Args:
            learning_mode: Learning mode ('heuristic', 'supervised', 'reinforcement')
            persona: DJ persona name
            model_path: Path to save/load models
            random_seed: Random seed for reproducibility
        """
        super().__init__(learning_mode=learning_mode, model_path=model_path, random_seed=random_seed)
        
        self.persona = DJPersona(persona)
        self.set_start_time = None
        self.set_duration_target = 3600.0  # 1 hour default
    
    def decide_action(self, audio_features: Dict, vdj_state: Dict) -> Dict:
        """
        Decide action with persona influence.
        
        Args:
            audio_features: Current audio features
            vdj_state: Current VirtualDJ state
            
        Returns:
            Actions dictionary with persona characteristics
        """
        # Get base actions from parent class
        if self.learning_mode == 'heuristic':
            base_actions = self.decide_action_heuristic(audio_features, vdj_state)
        elif self.learning_mode == 'supervised':
            base_actions = self.decide_action_supervised(audio_features, vdj_state)
        elif self.learning_mode == 'reinforcement':
            base_actions = self.decide_action_reinforcement(audio_features, vdj_state)
        else:
            base_actions = self.decide_action_heuristic(audio_features, vdj_state)
        
        # Apply persona adjustments
        persona_actions = self.persona.get_persona_adjustments(
            base_actions, audio_features, vdj_state
        )
        
        # Update persona mood
        if self.set_start_time is None:
            import time
            self.set_start_time = time.time()
        
        import time
        set_progress = (time.time() - self.set_start_time) / self.set_duration_target
        set_progress = min(1.0, set_progress)
        
        self.persona.update_mood(set_progress, audio_features.get('energy', 0.0))
        
        return persona_actions
    
    def change_persona(self, persona_name: str):
        """
        Change the active DJ persona.
        
        Args:
            persona_name: Name of the new persona
        """
        self.persona = DJPersona(persona_name)
        print(f"Persona changed to: {self.persona.config['name']}")
    
    def get_persona_info(self) -> Dict:
        """Get current persona information."""
        return self.persona.get_info()
    
    @staticmethod
    def list_personas() -> list:
        """List all available personas."""
        return list(DJPersona.PERSONAS.keys())


if __name__ == "__main__":
    # Example usage
    print("DJ Persona System - Test Mode")
    print("=" * 60)
    
    # List available personas
    print("\nAvailable DJ Personas:")
    for persona_name, config in DJPersona.PERSONAS.items():
        print(f"  • {config['name']}: {config['description']}")
    
    # Test persona agent
    print("\n" + "=" * 60)
    print("Testing Psy-Trance Goa Persona")
    print("=" * 60)
    
    agent = PersonaAgent(learning_mode='heuristic', persona='psytrance_goa')
    
    # Simulate audio features
    audio_features = {
        'rms': 0.20,
        'rms_db': -10.0,
        'energy': 0.85,
        'bpm': 144.0,
        'spectral_centroid': 3500.0,
        'spectral_rolloff': 6000.0,
        'zero_crossing_rate': 0.15,
        'beat_detected': True
    }
    
    vdj_state = {
        'deck_a_playing': True,
        'deck_b_playing': False,
        'crossfader_position': 0.3,
        'master_volume': 0.8,
        'deck_a_bpm': 144.0,
        'deck_b_bpm': 0.0
    }
    
    # Get persona-influenced actions
    actions = agent.decide_action(audio_features, vdj_state)
    print(f"\nRecommended actions: {actions}")
    
    # Get persona info
    persona_info = agent.get_persona_info()
    print(f"\nPersona info: {persona_info}")
    
    # Test another persona
    print("\n" + "=" * 60)
    print("Testing Lo-Fi ChillHop Persona")
    print("=" * 60)
    
    agent.change_persona('lofi_chillhop')
    audio_features['energy'] = 0.4
    audio_features['bpm'] = 85.0
    
    actions = agent.decide_action(audio_features, vdj_state)
    print(f"\nRecommended actions: {actions}")
    print(f"Persona info: {agent.get_persona_info()}")
    
    print("\nTest complete!")
