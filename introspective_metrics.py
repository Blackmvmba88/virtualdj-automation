"""
Introspective Metrics Module for VirtualDJ Automation

This module provides psychological state tracking for the AI agent,
exposing internal learning states as human-interpretable "emotions" and mental states.
"""

import numpy as np
from typing import Dict, List, Deque
from collections import deque
import time


class IntrospectiveMetrics:
    """
    Tracks and interprets agent's internal states as psychological metrics.
    
    This class exposes the agent's learning state in human-relatable terms:
    - Anxiety: How uncertain/exploratory the agent is
    - Confidence: How well the agent thinks it's performing
    - Fantasy: Willingness to try creative/unusual actions
    - Memory: Retention of past experiences
    - Focus: Consistency of decision-making
    - Excitement: Response to high-energy situations
    """
    
    def __init__(self):
        """Initialize introspective metrics tracker."""
        # Core psychological metrics
        self.anxiety = 0.5  # 0.0 (calm) to 1.0 (anxious)
        self.confidence = 0.5  # 0.0 (uncertain) to 1.0 (confident)
        self.fantasy = 0.5  # 0.0 (conservative) to 1.0 (experimental)
        self.memory_health = 1.0  # 0.0 (forgetting) to 1.0 (retaining)
        self.focus = 0.5  # 0.0 (scattered) to 1.0 (focused)
        self.excitement = 0.5  # 0.0 (calm) to 1.0 (excited)
        
        # Historical tracking
        self.reward_window = deque(maxlen=50)
        self.action_variance_window = deque(maxlen=30)
        self.energy_response_window = deque(maxlen=20)
        
        # Timestamps
        self.last_update_time = time.time()
        self.session_start_time = time.time()
        
        # State tracking
        self.total_decisions = 0
        self.exploration_decisions = 0
        self.exploitation_decisions = 0
    
    def update(self, agent_state: Dict, audio_features: Dict, action: Dict):
        """
        Update psychological metrics based on agent state and context.
        
        Args:
            agent_state: Dictionary containing agent's internal state
                - exploration_rate: Current epsilon value
                - avg_reward: Average reward
                - reward_history: Recent rewards
                - q_table_size: Size of Q-table (if RL)
                - experience_count: Number of experiences
            audio_features: Current audio features
            action: Action taken by agent
        """
        current_time = time.time()
        time_delta = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # Update anxiety from exploration rate
        # Higher exploration = more anxiety/uncertainty
        exploration_rate = agent_state.get('exploration_rate', 0.2)
        self.anxiety = exploration_rate
        
        # Update confidence from reward history
        reward_history = agent_state.get('reward_history', [])
        if len(reward_history) > 0:
            self.reward_window.extend(reward_history[-10:])  # Add recent rewards
            
            if len(self.reward_window) >= 10:
                # Confidence comes from consistent positive rewards
                avg_reward = np.mean(self.reward_window)
                reward_std = np.std(self.reward_window)
                
                # Normalize to 0-1 range
                # Assuming rewards typically range from -2 to +2
                normalized_reward = (avg_reward + 2.0) / 4.0
                normalized_reward = np.clip(normalized_reward, 0.0, 1.0)
                
                # Lower variance = higher confidence
                variance_penalty = min(reward_std / 2.0, 0.3)
                self.confidence = normalized_reward - variance_penalty
                self.confidence = np.clip(self.confidence, 0.0, 1.0)
        
        # Update fantasy (experimental tendency)
        # Combines exploration rate with reward trend
        if len(self.reward_window) >= 5:
            recent_rewards = list(self.reward_window)[-5:]
            reward_trend = np.mean(np.diff(recent_rewards)) if len(recent_rewards) > 1 else 0
            
            # If rewards are declining, increase fantasy (try new things)
            # If rewards are improving, moderate fantasy
            if reward_trend < -0.1:
                self.fantasy = min(1.0, self.fantasy + 0.05)
            elif reward_trend > 0.1:
                self.fantasy = max(0.0, self.fantasy - 0.03)
            
            # Fantasy also influenced by exploration rate
            self.fantasy = 0.7 * self.fantasy + 0.3 * exploration_rate
        else:
            self.fantasy = exploration_rate
        
        # Update memory health from experience buffer
        experience_count = agent_state.get('experience_count', 0)
        max_experience = 1000  # Typical buffer size
        self.memory_health = min(1.0, experience_count / max_experience)
        
        # Update focus from action variance
        # Track how much actions vary
        action_magnitude = self._calculate_action_magnitude(action)
        self.action_variance_window.append(action_magnitude)
        
        if len(self.action_variance_window) >= 10:
            action_variance = np.std(self.action_variance_window)
            # Lower variance = higher focus
            self.focus = 1.0 - min(1.0, action_variance / 0.5)
        
        # Update excitement from audio energy response
        energy = audio_features.get('energy', 0.5)
        self.energy_response_window.append(energy)
        
        if len(self.energy_response_window) >= 5:
            avg_energy = np.mean(self.energy_response_window)
            self.excitement = avg_energy
        
        # Track decision types
        self.total_decisions += 1
        if exploration_rate > np.random.random():
            self.exploration_decisions += 1
        else:
            self.exploitation_decisions += 1
    
    def _calculate_action_magnitude(self, action: Dict) -> float:
        """
        Calculate the magnitude of an action vector.
        
        Args:
            action: Action dictionary
            
        Returns:
            Scalar magnitude of the action
        """
        magnitude = 0.0
        
        # Crossfade
        magnitude += abs(action.get('crossfade_adjust', 0.0))
        
        # Volumes
        magnitude += abs(action.get('volume_adjust_a', 0.0))
        magnitude += abs(action.get('volume_adjust_b', 0.0))
        
        # EQ adjustments
        eq_adjust = action.get('eq_adjust', {})
        for value in eq_adjust.values():
            magnitude += abs(value)
        
        # Effects (binary)
        if action.get('effect_trigger') is not None:
            magnitude += 0.3
        
        # Transitions (binary)
        if action.get('transition_now', False):
            magnitude += 0.5
        
        return magnitude
    
    def get_state(self) -> Dict:
        """
        Get current psychological state.
        
        Returns:
            Dictionary with all psychological metrics
        """
        session_duration = time.time() - self.session_start_time
        
        return {
            # Core metrics (0.0 to 1.0)
            'anxiety': float(self.anxiety),
            'confidence': float(self.confidence),
            'fantasy': float(self.fantasy),
            'memory_health': float(self.memory_health),
            'focus': float(self.focus),
            'excitement': float(self.excitement),
            
            # Derived insights
            'mood': self._get_mood(),
            'creative_state': self._get_creative_state(),
            'learning_phase': self._get_learning_phase(),
            
            # Statistics
            'session_duration': session_duration,
            'total_decisions': self.total_decisions,
            'exploration_ratio': self.exploration_decisions / max(1, self.total_decisions),
        }
    
    def _get_mood(self) -> str:
        """
        Determine overall mood based on metrics.
        
        Returns:
            Mood descriptor string
        """
        if self.confidence > 0.7 and self.excitement > 0.7:
            return "euphoric"
        elif self.confidence > 0.6 and self.anxiety < 0.3:
            return "confident"
        elif self.anxiety > 0.7:
            return "anxious"
        elif self.fantasy > 0.7:
            return "experimental"
        elif self.focus > 0.7:
            return "focused"
        elif self.excitement < 0.3:
            return "calm"
        else:
            return "balanced"
    
    def _get_creative_state(self) -> str:
        """
        Determine creative state.
        
        Returns:
            Creative state descriptor
        """
        creativity_score = (self.fantasy * 0.5 + self.excitement * 0.3 + 
                          (1.0 - self.anxiety) * 0.2)
        
        if creativity_score > 0.75:
            return "highly_creative"
        elif creativity_score > 0.6:
            return "creative"
        elif creativity_score > 0.4:
            return "moderate"
        else:
            return "conservative"
    
    def _get_learning_phase(self) -> str:
        """
        Determine current learning phase.
        
        Returns:
            Learning phase descriptor
        """
        if self.memory_health < 0.3:
            return "early_exploration"
        elif self.anxiety > 0.6:
            return "active_learning"
        elif self.confidence > 0.7 and self.anxiety < 0.3:
            return "exploitation"
        elif self.fantasy > 0.6:
            return "experimentation"
        else:
            return "refinement"
    
    def get_narrative_description(self) -> str:
        """
        Generate a narrative description of the agent's mental state.
        
        Returns:
            Human-readable description of psychological state
        """
        state = self.get_state()
        
        descriptions = []
        
        # Mood description
        mood_texts = {
            "euphoric": "The agent is riding high, full of confidence and energy",
            "confident": "The agent feels secure in its decisions",
            "anxious": "The agent is uncertain, searching for the right path",
            "experimental": "The agent is in creative mode, trying new approaches",
            "focused": "The agent is locked in, making precise decisions",
            "calm": "The agent is in a relaxed, measured state",
            "balanced": "The agent maintains equilibrium"
        }
        descriptions.append(mood_texts.get(state['mood'], "The agent is processing"))
        
        # Anxiety level
        if self.anxiety > 0.7:
            descriptions.append("high uncertainty drives active exploration")
        elif self.anxiety < 0.3:
            descriptions.append("calm certainty guides its actions")
        
        # Confidence level
        if self.confidence > 0.7:
            descriptions.append("strong confidence in its mixing choices")
        elif self.confidence < 0.3:
            descriptions.append("still building confidence through experience")
        
        # Fantasy/creativity
        if self.fantasy > 0.7:
            descriptions.append("highly experimental, willing to take creative risks")
        elif self.fantasy < 0.3:
            descriptions.append("conservative approach, sticking to proven strategies")
        
        # Memory
        if self.memory_health < 0.3:
            descriptions.append("limited experience to draw upon")
        elif self.memory_health > 0.8:
            descriptions.append("rich memory of past experiences")
        
        return ". ".join(descriptions) + "."
    
    def reset(self):
        """Reset all metrics to initial state."""
        self.anxiety = 0.5
        self.confidence = 0.5
        self.fantasy = 0.5
        self.memory_health = 1.0
        self.focus = 0.5
        self.excitement = 0.5
        
        self.reward_window.clear()
        self.action_variance_window.clear()
        self.energy_response_window.clear()
        
        self.session_start_time = time.time()
        self.last_update_time = time.time()
        
        self.total_decisions = 0
        self.exploration_decisions = 0
        self.exploitation_decisions = 0


if __name__ == "__main__":
    # Example usage
    print("Introspective Metrics System - Test Mode")
    print("=" * 60)
    
    metrics = IntrospectiveMetrics()
    
    # Simulate agent learning over time
    print("\nSimulating agent learning progression...\n")
    
    for iteration in range(10):
        # Simulate agent state at different learning stages
        if iteration < 3:
            # Early exploration phase
            agent_state = {
                'exploration_rate': 0.8,
                'avg_reward': -0.5,
                'reward_history': [-0.5, -0.3, -0.4, -0.6, -0.2],
                'experience_count': iteration * 50,
            }
        elif iteration < 7:
            # Learning phase
            agent_state = {
                'exploration_rate': 0.4,
                'avg_reward': 0.5,
                'reward_history': [0.3, 0.5, 0.6, 0.4, 0.7],
                'experience_count': iteration * 100,
            }
        else:
            # Exploitation phase
            agent_state = {
                'exploration_rate': 0.1,
                'avg_reward': 1.2,
                'reward_history': [1.0, 1.2, 1.3, 1.1, 1.4],
                'experience_count': iteration * 100,
            }
        
        audio_features = {
            'energy': 0.5 + (iteration * 0.05),
            'rms': 0.15,
            'beat_detected': True
        }
        
        action = {
            'crossfade_adjust': np.random.uniform(-0.1, 0.1),
            'volume_adjust_a': np.random.uniform(-0.05, 0.05),
            'eq_adjust': {'low': 0.05},
            'effect_trigger': 1 if iteration % 3 == 0 else None
        }
        
        metrics.update(agent_state, audio_features, action)
        
        print(f"Iteration {iteration + 1}:")
        state = metrics.get_state()
        print(f"  Anxiety: {state['anxiety']:.2f}")
        print(f"  Confidence: {state['confidence']:.2f}")
        print(f"  Fantasy: {state['fantasy']:.2f}")
        print(f"  Memory: {state['memory_health']:.2f}")
        print(f"  Focus: {state['focus']:.2f}")
        print(f"  Excitement: {state['excitement']:.2f}")
        print(f"  Mood: {state['mood']}")
        print(f"  Creative State: {state['creative_state']}")
        print(f"  Learning Phase: {state['learning_phase']}")
        print()
        
        import time
        time.sleep(0.1)
    
    print("\n" + "=" * 60)
    print("Narrative Description:")
    print("=" * 60)
    print(metrics.get_narrative_description())
    
    print("\nTest complete!")
