"""
Test Script for VirtualDJ MIDI Automation System

This script demonstrates the complete system using loopMIDI for MIDI communication.
It integrates the MIDI controller, audio observer, and adaptive agent.
"""

import time
import sys
import numpy as np
from typing import Optional

# Import our modules
try:
    from midi_controller import VirtualDJMIDIController
    from audio_observer import AudioObserver
    from adaptive_agent import AdaptiveAgent
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all required modules are in the same directory.")
    sys.exit(1)


class VirtualDJAutomationSystem:
    """
    Complete automation system integrating all components.
    """
    
    def __init__(self, midi_port: Optional[str] = None, learning_mode: str = 'heuristic'):
        """
        Initialize the automation system.
        
        Args:
            midi_port: MIDI port name (None for auto-detect)
            learning_mode: Learning mode for adaptive agent
        """
        print("=" * 60)
        print("VirtualDJ Automation System")
        print("=" * 60)
        
        # Initialize components
        print("\n[1/3] Initializing MIDI Controller...")
        self.controller = VirtualDJMIDIController(port_name=midi_port)
        
        print("\n[2/3] Initializing Audio Observer...")
        self.observer = AudioObserver()
        
        print("\n[3/3] Initializing Adaptive Agent...")
        self.agent = AdaptiveAgent(learning_mode=learning_mode)
        
        # System state
        self.is_running = False
        self.prev_audio_features = None
        
        print("\n✓ System initialized successfully!")
    
    def start(self):
        """Start the automation system."""
        print("\n" + "=" * 60)
        print("Starting Automation System")
        print("=" * 60)
        
        if not self.controller.is_connected:
            print("⚠ Warning: MIDI controller not connected!")
            print("  Make sure loopMIDI or similar virtual MIDI port is running.")
            response = input("Continue without MIDI? (y/n): ")
            if response.lower() != 'y':
                return
        
        self.observer.start_streaming()
        self.is_running = True
        
        print("\n✓ System is running!")
        print("  Press Ctrl+C to stop\n")
    
    def stop(self):
        """Stop the automation system."""
        print("\n\nStopping system...")
        self.is_running = False
        self.observer.stop_streaming()
        self.controller.close()
        self.agent.save()
        print("✓ System stopped")
    
    def run_automation_loop(self, duration: float = 30.0, update_interval: float = 1.0):
        """
        Run the main automation loop.
        
        Args:
            duration: Total duration to run (seconds)
            update_interval: Time between decision updates (seconds)
        """
        self.start()
        
        start_time = time.time()
        iteration = 0
        
        try:
            while self.is_running and (time.time() - start_time) < duration:
                iteration += 1
                print(f"\n--- Iteration {iteration} ---")
                
                # Get current state
                audio_features = self.observer.get_features()
                vdj_state = self.observer.get_vdj_state()
                
                # Agent decides action based on learning mode
                if self.agent.learning_mode == 'heuristic':
                    actions = self.agent.decide_action_heuristic(audio_features, vdj_state)
                elif self.agent.learning_mode == 'supervised':
                    actions = self.agent.decide_action_supervised(audio_features, vdj_state)
                elif self.agent.learning_mode == 'reinforcement':
                    actions = self.agent.decide_action_reinforcement(audio_features, vdj_state)
                else:
                    actions = {}
                
                # Execute actions via MIDI controller
                self._execute_actions(actions, audio_features, vdj_state)
                
                # Calculate reward and update learning (for RL mode)
                if self.agent.learning_mode == 'reinforcement':
                    reward = self.agent.calculate_reward(audio_features, vdj_state, self.prev_audio_features)
                    self.agent.update_q_value(reward)
                    print(f"Reward: {reward:.2f}")
                
                # Display current state
                self._display_status(audio_features, vdj_state, actions)
                
                # Store for next iteration
                self.prev_audio_features = audio_features.copy()
                
                # Wait before next update
                time.sleep(update_interval)
            
            # Display final statistics
            self._display_final_stats()
            
        except KeyboardInterrupt:
            print("\n\n⚠ Interrupted by user")
        
        finally:
            self.stop()
    
    def _update_crossfader_position(self, adjustment: float, vdj_state: dict) -> float:
        """
        Helper method to update crossfader position consistently.
        
        Args:
            adjustment: Amount to adjust crossfader by
            vdj_state: Current VirtualDJ state
            
        Returns:
            New crossfader position
        """
        current_pos = vdj_state.get('crossfader_position', 0.5)
        new_pos = np.clip(current_pos + adjustment, 0.0, 1.0)
        
        if self.controller.is_connected:
            self.controller.set_crossfader(new_pos)
        
        # Update simulated state
        self.observer.update_vdj_state({'crossfader_position': new_pos})
        
        return new_pos
    
    def _execute_actions(self, actions: dict, audio_features: dict, vdj_state: dict):
        """
        Execute actions through MIDI controller.
        
        Args:
            actions: Action dictionary from agent
            audio_features: Current audio features
            vdj_state: Current VirtualDJ state
        """
        if not self.controller.is_connected:
            return
        
        # Crossfader adjustment
        if actions.get('crossfade_adjust', 0.0) != 0.0:
            self._update_crossfader_position(actions['crossfade_adjust'], vdj_state)
        
        # Volume adjustments
        if actions.get('volume_adjust_a', 0.0) != 0.0:
            self.controller.set_volume('A', 0.8 + actions['volume_adjust_a'])
        
        if actions.get('volume_adjust_b', 0.0) != 0.0:
            self.controller.set_volume('B', 0.8 + actions['volume_adjust_b'])
        
        # EQ adjustments
        eq_adjust = actions.get('eq_adjust', {})
        for band, value in eq_adjust.items():
            deck = 'A' if vdj_state.get('crossfader_position', 0.5) < 0.5 else 'B'
            current_eq = 0.5
            new_eq = np.clip(current_eq + value, 0.0, 1.0)
            self.controller.set_eq(deck, band, new_eq)
        
        # Effect trigger
        if actions.get('effect_trigger') is not None:
            self.controller.activate_effect(actions['effect_trigger'], 0.7)
        
        # Transition
        if actions.get('transition_now', False):
            crossfader_pos = vdj_state.get('crossfader_position', 0.5)
            if crossfader_pos < 0.5:
                print("  → Initiating transition from Deck A to Deck B")
                self.controller.play_pause_deck('B')
                time.sleep(0.5)
                self.controller.sync_deck('B')
                self.observer.update_vdj_state({'deck_b_playing': True})
            else:
                print("  → Initiating transition from Deck B to Deck A")
                self.controller.play_pause_deck('A')
                time.sleep(0.5)
                self.controller.sync_deck('A')
                self.observer.update_vdj_state({'deck_a_playing': True})
    
    def _display_status(self, audio_features: dict, vdj_state: dict, actions: dict):
        """Display current status."""
        print("\nAudio Features:")
        print(f"  RMS: {audio_features.get('rms', 0.0):.4f} ({audio_features.get('rms_db', -80.0):.1f} dB)")
        print(f"  Energy: {audio_features.get('energy', 0.0):.4f}")
        print(f"  BPM: {audio_features.get('bpm', 0.0):.1f}")
        print(f"  Beat: {'Yes' if audio_features.get('beat_detected', False) else 'No'}")
        print(f"  Quality: {self.observer.estimate_mix_quality():.2f}")
        
        print("\nVirtualDJ State:")
        print(f"  Deck A: {'Playing' if vdj_state.get('deck_a_playing', False) else 'Stopped'}")
        print(f"  Deck B: {'Playing' if vdj_state.get('deck_b_playing', False) else 'Stopped'}")
        print(f"  Crossfader: {vdj_state.get('crossfader_position', 0.5):.2f}")
        
        print("\nActions Taken:")
        for key, value in actions.items():
            if value and value != 0.0 and value != {}:
                print(f"  {key}: {value}")
    
    def _display_final_stats(self):
        """Display final statistics."""
        print("\n" + "=" * 60)
        print("Final Statistics")
        print("=" * 60)
        
        stats = self.agent.get_statistics()
        print(f"\nLearning Mode: {stats['learning_mode']}")
        
        if self.agent.learning_mode == 'reinforcement':
            print(f"Experience Count: {stats['experience_count']}")
            print(f"Q-Table Size: {stats['q_table_size']}")
            print(f"Exploration Rate: {stats['exploration_rate']:.4f}")
            
            if 'avg_reward' in stats:
                print(f"Average Reward: {stats['avg_reward']:.2f}")
                print(f"Total Reward: {stats['total_reward']:.2f}")
                print(f"Recent Reward Trend: {stats['reward_trend']:.2f}")
        
        print("\n✓ Session complete!")


def demo_basic_commands():
    """Demonstrate basic MIDI commands."""
    print("\n" + "=" * 60)
    print("Demo: Basic MIDI Commands")
    print("=" * 60)
    
    controller = VirtualDJMIDIController()
    
    if not controller.is_connected:
        print("⚠ MIDI not connected. Skipping demo.")
        return
    
    print("\n1. Play/Pause Deck A")
    controller.play_pause_deck('A')
    time.sleep(1)
    
    print("\n2. Set volume levels")
    controller.set_volume('A', 0.8)
    controller.set_volume('B', 0.6)
    time.sleep(1)
    
    print("\n3. Crossfader sweep")
    for pos in [0.0, 0.25, 0.5, 0.75, 1.0]:
        controller.set_crossfader(pos)
        time.sleep(0.5)
    
    print("\n4. EQ adjustments")
    controller.set_eq('A', 'low', 0.7)
    controller.set_eq('A', 'mid', 0.5)
    controller.set_eq('A', 'high', 0.6)
    time.sleep(1)
    
    print("\n5. Activate effect")
    controller.activate_effect(1, 0.8)
    time.sleep(1)
    
    print("\n✓ Demo complete!")
    controller.close()


def demo_audio_analysis():
    """Demonstrate audio analysis features."""
    print("\n" + "=" * 60)
    print("Demo: Audio Analysis")
    print("=" * 60)
    
    observer = AudioObserver()
    
    print("\nStarting audio capture for 5 seconds...")
    observer.start_streaming()
    
    try:
        for i in range(5):
            time.sleep(1)
            features = observer.get_features()
            quality = observer.estimate_mix_quality()
            
            print(f"\nSecond {i+1}:")
            print(f"  RMS: {features['rms']:.4f} ({features['rms_db']:.1f} dB)")
            print(f"  Energy: {features['energy']:.4f}")
            print(f"  BPM: {features['bpm']:.1f}")
            print(f"  Quality: {quality:.2f}")
    
    finally:
        observer.stop_streaming()
    
    print("\n✓ Demo complete!")


def demo_learning_modes():
    """Demonstrate different learning modes."""
    print("\n" + "=" * 60)
    print("Demo: Learning Modes")
    print("=" * 60)
    
    # Simulated features
    audio_features = {
        'rms': 0.15, 'rms_db': -12.0, 'energy': 0.25, 'bpm': 128.0,
        'spectral_centroid': 2000.0, 'spectral_rolloff': 5000.0,
        'zero_crossing_rate': 0.1, 'beat_detected': True
    }
    
    vdj_state = {
        'deck_a_playing': True, 'deck_b_playing': False,
        'crossfader_position': 0.3, 'master_volume': 0.8,
        'deck_a_bpm': 128.0, 'deck_b_bpm': 0.0
    }
    
    # Test each mode
    for mode in ['heuristic', 'reinforcement']:
        print(f"\n{mode.upper()} Mode:")
        agent = AdaptiveAgent(learning_mode=mode)
        
        if mode == 'heuristic':
            actions = agent.decide_action_heuristic(audio_features, vdj_state)
        else:
            actions = agent.decide_action_reinforcement(audio_features, vdj_state)
        
        print(f"  Actions: {actions}")
        
        reward = agent.calculate_reward(audio_features, vdj_state)
        print(f"  Reward: {reward:.2f}")
        
        if mode == 'reinforcement':
            agent.update_q_value(reward)
    
    print("\n✓ Demo complete!")


def deterministic_demo(random_seed: int = 42, iterations: int = 5):
    """Run a short deterministic reinforcement demo to verify reproducibility.

    This uses simulated audio/state (no real audio/MIDI) and prints action sequence.
    """
    print("\n" + "=" * 60)
    print(f"Deterministic Demo (seed={random_seed}, iterations={iterations})")
    print("=" * 60)

    # Simulated features (kept constant for determinism but agent randomness is seeded)
    audio_features = {
        'rms': 0.15, 'rms_db': -12.0, 'energy': 0.25, 'bpm': 128.0,
        'spectral_centroid': 2000.0, 'spectral_rolloff': 5000.0,
        'zero_crossing_rate': 0.1, 'beat_detected': True
    }

    vdj_state = {
        'deck_a_playing': True, 'deck_b_playing': False,
        'crossfader_position': 0.3, 'master_volume': 0.8,
        'deck_a_bpm': 128.0, 'deck_b_bpm': 0.0
    }

    agent = AdaptiveAgent(learning_mode='reinforcement', random_seed=random_seed)

    actions_history = []
    for i in range(iterations):
        actions = agent.decide_action_reinforcement(audio_features, vdj_state)
        actions_history.append(actions)
        reward = agent.calculate_reward(audio_features, vdj_state)
        agent.update_q_value(reward)
        print(f"Iteration {i+1}: actions={actions}, reward={reward:.2f}")

    print("\nAction sequence (compact):")
    for i, act in enumerate(actions_history, 1):
        print(f"  {i}. {act}")

    print("\n✓ Deterministic demo complete!")


def main():
    """Main function to run tests and demos."""
    print("\n" + "=" * 60)
    print("VirtualDJ MIDI Automation - Test Suite")
    print("=" * 60)
    
    print("\nThis test suite demonstrates the VirtualDJ automation system.")
    print("Make sure you have:")
    print("  1. loopMIDI or similar virtual MIDI port running")
    print("  2. VirtualDJ configured to receive MIDI from that port")
    print("  3. An audio interface configured for capture")
    
    while True:
        print("\n" + "=" * 60)
        print("Select a test:")
        print("=" * 60)
        print("1. Demo: Basic MIDI Commands")
        print("2. Demo: Audio Analysis")
        print("3. Demo: Learning Modes")
        print("4. Run Full Automation System (30 seconds)")
        print("5. Run Full Automation System (Custom duration)")
        print("6. Deterministic Demo (short, reproducible)")
        print("0. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '1':
            demo_basic_commands()
        
        elif choice == '2':
            demo_audio_analysis()
        
        elif choice == '3':
            demo_learning_modes()
        
        elif choice == '6':
            deterministic_demo()
        
        elif choice == '4':
            print("\nSelect learning mode:")
            print("1. Heuristic (rule-based)")
            print("2. Reinforcement Learning (Q-learning)")
            mode_choice = input("Enter choice: ").strip()
            
            mode = 'heuristic' if mode_choice == '1' else 'reinforcement'
            
            system = VirtualDJAutomationSystem(learning_mode=mode)
            system.run_automation_loop(duration=30.0, update_interval=2.0)
        
        elif choice == '5':
            duration = float(input("Enter duration in seconds: ").strip())
            
            print("\nSelect learning mode:")
            print("1. Heuristic (rule-based)")
            print("2. Reinforcement Learning (Q-learning)")
            mode_choice = input("Enter choice: ").strip()
            
            mode = 'heuristic' if mode_choice == '1' else 'reinforcement'
            
            system = VirtualDJAutomationSystem(learning_mode=mode)
            system.run_automation_loop(duration=duration, update_interval=2.0)
        
        elif choice == '0':
            print("\nExiting...")
            break
        
        else:
            print("\n⚠ Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
