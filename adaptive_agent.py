"""
Adaptive Agent Module for VirtualDJ Automation

This module implements an adaptive learning agent that optimizes DJ mixing
using heuristics, supervised learning, and reinforcement learning approaches.
"""

import numpy as np
import pickle
import os
from typing import Dict, List, Tuple, Optional
from collections import deque
import time

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
except ImportError:
    print("Warning: scikit-learn not installed. Supervised learning features disabled.")
    RandomForestClassifier = None
    StandardScaler = None


class AdaptiveAgent:
    """
    Adaptive agent that learns to optimize DJ mixing using multiple learning approaches.
    """
    
    def __init__(self, learning_mode: str = 'heuristic', model_path: Optional[str] = None):
        """
        Initialize adaptive agent.
        
        Args:
            learning_mode: Learning approach ('heuristic', 'supervised', 'reinforcement')
            model_path: Path to save/load trained models
        """
        self.learning_mode = learning_mode
        self.model_path = model_path or 'models'
        
        # Ensure model directory exists
        os.makedirs(self.model_path, exist_ok=True)
        
        # Experience replay buffer for reinforcement learning
        self.experience_buffer = deque(maxlen=1000)
        
        # State history
        self.state_history = deque(maxlen=100)
        
        # Action history
        self.action_history = deque(maxlen=100)
        
        # Reward history
        self.reward_history = deque(maxlen=100)
        
        # Supervised learning components
        self.classifier = None
        self.scaler = None
        if RandomForestClassifier and learning_mode == 'supervised':
            self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
            self.scaler = StandardScaler()
        
        # Q-learning parameters (for reinforcement learning)
        self.q_table = {}
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.exploration_rate = 0.2
        self.exploration_decay = 0.995
        
        # Load existing models if available
        self._load_models()
        
        # Heuristic parameters
        self.mix_params = {
            'optimal_crossfade_duration': 8.0,  # seconds
            'optimal_rms_range': (-15, -6),  # dB
            'beat_sync_threshold': 0.98,
            'eq_transition_rate': 0.1,
            'effect_probability': 0.15
        }
    
    def _load_models(self):
        """Load pre-trained models if they exist."""
        try:
            # Load supervised learning model
            if self.learning_mode == 'supervised':
                classifier_path = os.path.join(self.model_path, 'classifier.pkl')
                scaler_path = os.path.join(self.model_path, 'scaler.pkl')
                
                if os.path.exists(classifier_path) and os.path.exists(scaler_path):
                    with open(classifier_path, 'rb') as f:
                        self.classifier = pickle.load(f)
                    with open(scaler_path, 'rb') as f:
                        self.scaler = pickle.load(f)
                    print("Loaded supervised learning models")
            
            # Load Q-table
            if self.learning_mode == 'reinforcement':
                q_table_path = os.path.join(self.model_path, 'q_table.pkl')
                if os.path.exists(q_table_path):
                    with open(q_table_path, 'rb') as f:
                        self.q_table = pickle.load(f)
                    print("Loaded Q-table")
        
        except Exception as e:
            print(f"Error loading models: {e}")
    
    def _save_models(self):
        """Save trained models."""
        try:
            if self.learning_mode == 'supervised' and self.classifier:
                classifier_path = os.path.join(self.model_path, 'classifier.pkl')
                scaler_path = os.path.join(self.model_path, 'scaler.pkl')
                
                with open(classifier_path, 'wb') as f:
                    pickle.dump(self.classifier, f)
                with open(scaler_path, 'wb') as f:
                    pickle.dump(self.scaler, f)
                print("Saved supervised learning models")
            
            if self.learning_mode == 'reinforcement':
                q_table_path = os.path.join(self.model_path, 'q_table.pkl')
                with open(q_table_path, 'wb') as f:
                    pickle.dump(self.q_table, f)
                print("Saved Q-table")
        
        except Exception as e:
            print(f"Error saving models: {e}")
    
    def extract_state_features(self, audio_features: Dict, vdj_state: Dict) -> np.ndarray:
        """
        Extract features from current state for learning.
        
        Args:
            audio_features: Audio features from observer
            vdj_state: VirtualDJ state information
            
        Returns:
            Feature vector as numpy array
        """
        features = [
            audio_features.get('rms', 0.0),
            audio_features.get('rms_db', -80.0),
            audio_features.get('energy', 0.0),
            audio_features.get('bpm', 0.0),
            audio_features.get('spectral_centroid', 0.0),
            audio_features.get('spectral_rolloff', 0.0),
            audio_features.get('zero_crossing_rate', 0.0),
            float(audio_features.get('beat_detected', False)),
            vdj_state.get('crossfader_position', 0.5),
            vdj_state.get('master_volume', 0.8),
            float(vdj_state.get('deck_a_playing', False)),
            float(vdj_state.get('deck_b_playing', False)),
            vdj_state.get('deck_a_bpm', 0.0),
            vdj_state.get('deck_b_bpm', 0.0),
        ]
        
        return np.array(features, dtype=np.float32)
    
    def decide_action_heuristic(self, audio_features: Dict, vdj_state: Dict) -> Dict:
        """
        Decide action using heuristic rules.
        
        Args:
            audio_features: Current audio features
            vdj_state: Current VirtualDJ state
            
        Returns:
            Dictionary with recommended actions
        """
        actions = {
            'crossfade_adjust': 0.0,
            'volume_adjust_a': 0.0,
            'volume_adjust_b': 0.0,
            'eq_adjust': {},
            'effect_trigger': None,
            'transition_now': False
        }
        
        # Check if transition is needed based on track position
        deck_a_playing = vdj_state.get('deck_a_playing', False)
        deck_b_playing = vdj_state.get('deck_b_playing', False)
        crossfader_pos = vdj_state.get('crossfader_position', 0.5)
        
        # Energy-based mixing decisions
        energy = audio_features.get('energy', 0.0)
        rms_db = audio_features.get('rms_db', -80.0)
        
        # Adjust volume if RMS is out of optimal range
        if rms_db < self.mix_params['optimal_rms_range'][0]:
            # Too quiet, increase volume
            if crossfader_pos < 0.5:
                actions['volume_adjust_a'] = 0.05
            else:
                actions['volume_adjust_b'] = 0.05
        elif rms_db > self.mix_params['optimal_rms_range'][1]:
            # Too loud, decrease volume
            if crossfader_pos < 0.5:
                actions['volume_adjust_a'] = -0.05
            else:
                actions['volume_adjust_b'] = -0.05
        
        # Beat-synchronized crossfade
        if audio_features.get('beat_detected', False):
            # Opportunity for smooth transition
            if deck_a_playing and not deck_b_playing and crossfader_pos < 0.3:
                actions['transition_now'] = True
            elif deck_b_playing and not deck_a_playing and crossfader_pos > 0.7:
                actions['transition_now'] = True
        
        # EQ adjustments based on spectral content
        spectral_centroid = audio_features.get('spectral_centroid', 0.0)
        if spectral_centroid > 3000:
            # Too bright, reduce highs
            actions['eq_adjust'] = {'high': -0.1}
        elif spectral_centroid < 1000:
            # Too dark, boost highs
            actions['eq_adjust'] = {'high': 0.1}
        
        # Random effect triggers for variety
        if np.random.random() < self.mix_params['effect_probability']:
            if audio_features.get('beat_detected', False):
                actions['effect_trigger'] = np.random.randint(1, 4)
        
        return actions
    
    def decide_action_supervised(self, audio_features: Dict, vdj_state: Dict) -> Dict:
        """
        Decide action using supervised learning model.
        
        Args:
            audio_features: Current audio features
            vdj_state: Current VirtualDJ state
            
        Returns:
            Dictionary with recommended actions
        """
        if not self.classifier or not self.scaler:
            print("Supervised learning not available, falling back to heuristics")
            return self.decide_action_heuristic(audio_features, vdj_state)
        
        # Extract features
        state_features = self.extract_state_features(audio_features, vdj_state)
        
        try:
            # Predict action class
            state_scaled = self.scaler.transform([state_features])
            action_class = self.classifier.predict(state_scaled)[0]
            
            # Map action class to specific actions
            actions = self._map_action_class(action_class, audio_features, vdj_state)
            return actions
        
        except Exception as e:
            print(f"Error in supervised prediction: {e}")
            return self.decide_action_heuristic(audio_features, vdj_state)
    
    def decide_action_reinforcement(self, audio_features: Dict, vdj_state: Dict) -> Dict:
        """
        Decide action using reinforcement learning (Q-learning).
        
        Args:
            audio_features: Current audio features
            vdj_state: Current VirtualDJ state
            
        Returns:
            Dictionary with recommended actions
        """
        # Discretize state for Q-table
        state_key = self._discretize_state(audio_features, vdj_state)
        
        # Epsilon-greedy action selection
        if np.random.random() < self.exploration_rate:
            # Explore: random action
            action_idx = np.random.randint(0, 5)
        else:
            # Exploit: best known action
            if state_key not in self.q_table:
                self.q_table[state_key] = np.zeros(5)
            action_idx = np.argmax(self.q_table[state_key])
        
        # Map action index to specific actions
        actions = self._map_action_index(action_idx, audio_features, vdj_state)
        
        # Store state-action pair for learning
        self.state_history.append(state_key)
        self.action_history.append(action_idx)
        
        return actions
    
    def _discretize_state(self, audio_features: Dict, vdj_state: Dict) -> str:
        """
        Discretize continuous state into discrete bins for Q-learning.
        
        Args:
            audio_features: Audio features
            vdj_state: VirtualDJ state
            
        Returns:
            String key representing discretized state
        """
        # Discretize key features
        energy_bin = int(audio_features.get('energy', 0.0) * 10)
        rms_bin = int((audio_features.get('rms_db', -80.0) + 80) / 10)
        crossfader_bin = int(vdj_state.get('crossfader_position', 0.5) * 10)
        beat = int(audio_features.get('beat_detected', False))
        
        return f"{energy_bin}_{rms_bin}_{crossfader_bin}_{beat}"
    
    def _map_action_class(self, action_class: int, audio_features: Dict, vdj_state: Dict) -> Dict:
        """Map action class to specific actions."""
        action_map = {
            0: {'crossfade_adjust': 0.1, 'volume_adjust_a': 0.0, 'volume_adjust_b': 0.0, 
                'eq_adjust': {}, 'effect_trigger': None, 'transition_now': False},
            1: {'crossfade_adjust': -0.1, 'volume_adjust_a': 0.0, 'volume_adjust_b': 0.0,
                'eq_adjust': {}, 'effect_trigger': None, 'transition_now': False},
            2: {'crossfade_adjust': 0.0, 'volume_adjust_a': 0.05, 'volume_adjust_b': 0.05,
                'eq_adjust': {}, 'effect_trigger': None, 'transition_now': False},
            3: {'crossfade_adjust': 0.0, 'volume_adjust_a': 0.0, 'volume_adjust_b': 0.0,
                'eq_adjust': {'high': 0.1}, 'effect_trigger': None, 'transition_now': False},
            4: {'crossfade_adjust': 0.0, 'volume_adjust_a': 0.0, 'volume_adjust_b': 0.0,
                'eq_adjust': {}, 'effect_trigger': 1, 'transition_now': True},
        }
        
        return action_map.get(action_class, action_map[0])
    
    def _map_action_index(self, action_idx: int, audio_features: Dict, vdj_state: Dict) -> Dict:
        """Map action index to specific actions."""
        return self._map_action_class(action_idx, audio_features, vdj_state)
    
    def update_q_value(self, reward: float):
        """
        Update Q-value based on reward (for reinforcement learning).
        
        Args:
            reward: Reward signal from environment
        """
        if len(self.state_history) < 2 or len(self.action_history) < 1:
            return
        
        # Get previous state and action
        prev_state = self.state_history[-2]
        action = self.action_history[-1]
        current_state = self.state_history[-1]
        
        # Initialize Q-values if not exist
        if prev_state not in self.q_table:
            self.q_table[prev_state] = np.zeros(5)
        if current_state not in self.q_table:
            self.q_table[current_state] = np.zeros(5)
        
        # Q-learning update
        old_q = self.q_table[prev_state][action]
        max_future_q = np.max(self.q_table[current_state])
        new_q = old_q + self.learning_rate * (reward + self.discount_factor * max_future_q - old_q)
        self.q_table[prev_state][action] = new_q
        
        # Store experience
        self.experience_buffer.append({
            'state': prev_state,
            'action': action,
            'reward': reward,
            'next_state': current_state
        })
        
        # Decay exploration rate
        self.exploration_rate *= self.exploration_decay
        self.exploration_rate = max(0.01, self.exploration_rate)
        
        # Store reward
        self.reward_history.append(reward)
    
    def train_supervised(self, training_data: List[Tuple[np.ndarray, int]]):
        """
        Train supervised learning model.
        
        Args:
            training_data: List of (features, label) tuples
        """
        if not self.classifier or not self.scaler:
            print("Supervised learning not available")
            return
        
        if len(training_data) < 10:
            print("Insufficient training data")
            return
        
        try:
            X = np.array([item[0] for item in training_data])
            y = np.array([item[1] for item in training_data])
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X)
            
            # Train classifier
            self.classifier.fit(X_scaled, y)
            
            print(f"Trained supervised model with {len(training_data)} samples")
            
            # Save model
            self._save_models()
        
        except Exception as e:
            print(f"Error training supervised model: {e}")
    
    def calculate_reward(self, audio_features: Dict, vdj_state: Dict, 
                        prev_audio_features: Optional[Dict] = None) -> float:
        """
        Calculate reward signal based on mix quality.
        
        Args:
            audio_features: Current audio features
            vdj_state: Current VirtualDJ state
            prev_audio_features: Previous audio features for comparison
            
        Returns:
            Reward value (higher is better)
        """
        reward = 0.0
        
        # Reward for maintaining good RMS level
        rms_db = audio_features.get('rms_db', -80.0)
        if self.mix_params['optimal_rms_range'][0] <= rms_db <= self.mix_params['optimal_rms_range'][1]:
            reward += 1.0
        else:
            # Penalty for being outside optimal range
            deviation = min(
                abs(rms_db - self.mix_params['optimal_rms_range'][0]),
                abs(rms_db - self.mix_params['optimal_rms_range'][1])
            )
            reward -= deviation * 0.1
        
        # Reward for energy consistency
        if prev_audio_features:
            energy_change = abs(audio_features.get('energy', 0.0) - 
                              prev_audio_features.get('energy', 0.0))
            if energy_change < 0.1:
                reward += 0.5  # Smooth transition
            else:
                reward -= energy_change * 0.5  # Jarring transition
        
        # Reward for beat synchronization
        if audio_features.get('beat_detected', False):
            reward += 0.3
        
        # Penalty for extreme crossfader positions without playing decks
        crossfader = vdj_state.get('crossfader_position', 0.5)
        deck_a_playing = vdj_state.get('deck_a_playing', False)
        deck_b_playing = vdj_state.get('deck_b_playing', False)
        
        if crossfader < 0.2 and not deck_a_playing:
            reward -= 0.5
        if crossfader > 0.8 and not deck_b_playing:
            reward -= 0.5
        
        return reward
    
    def get_statistics(self) -> Dict:
        """
        Get learning statistics.
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            'learning_mode': self.learning_mode,
            'experience_count': len(self.experience_buffer),
            'exploration_rate': self.exploration_rate,
            'q_table_size': len(self.q_table) if self.learning_mode == 'reinforcement' else 0,
        }
        
        if len(self.reward_history) > 0:
            stats['avg_reward'] = float(np.mean(self.reward_history))
            stats['total_reward'] = float(np.sum(self.reward_history))
            stats['reward_trend'] = float(np.mean(list(self.reward_history)[-10:])) if len(self.reward_history) >= 10 else 0.0
        
        return stats
    
    def save(self):
        """Save agent state and models."""
        self._save_models()
    
    def reset(self):
        """Reset agent state."""
        self.state_history.clear()
        self.action_history.clear()
        self.reward_history.clear()
        self.experience_buffer.clear()
        print("Agent state reset")


if __name__ == "__main__":
    # Example usage
    print("VirtualDJ Adaptive Agent - Test Mode")
    print("=" * 50)
    
    # Test heuristic mode
    print("\n1. Testing Heuristic Mode")
    agent_heuristic = AdaptiveAgent(learning_mode='heuristic')
    
    # Simulate audio features and state
    audio_features = {
        'rms': 0.15,
        'rms_db': -12.0,
        'energy': 0.25,
        'bpm': 128.0,
        'spectral_centroid': 2000.0,
        'spectral_rolloff': 5000.0,
        'zero_crossing_rate': 0.1,
        'beat_detected': True
    }
    
    vdj_state = {
        'deck_a_playing': True,
        'deck_b_playing': False,
        'crossfader_position': 0.3,
        'master_volume': 0.8,
        'deck_a_bpm': 128.0,
        'deck_b_bpm': 0.0
    }
    
    actions = agent_heuristic.decide_action_heuristic(audio_features, vdj_state)
    print(f"Recommended actions: {actions}")
    
    # Calculate reward
    reward = agent_heuristic.calculate_reward(audio_features, vdj_state)
    print(f"Calculated reward: {reward:.2f}")
    
    # Test reinforcement learning mode
    print("\n2. Testing Reinforcement Learning Mode")
    agent_rl = AdaptiveAgent(learning_mode='reinforcement')
    
    # Simulate learning loop
    for i in range(5):
        actions = agent_rl.decide_action_reinforcement(audio_features, vdj_state)
        reward = agent_rl.calculate_reward(audio_features, vdj_state)
        agent_rl.update_q_value(reward)
        print(f"Iteration {i+1}: Actions={actions}, Reward={reward:.2f}")
    
    # Get statistics
    stats = agent_rl.get_statistics()
    print(f"\nLearning statistics: {stats}")
    
    print("\nTest complete!")
