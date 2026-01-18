"""
Enhanced Demo Script for VirtualDJ Psychedelic Features

Demonstrates all the new psychedelic features:
- DJ Personas
- Introspective Metrics
- Musical Semantic Analysis
- Real-time Visualization
- Machine Spirit Poetry
"""

import time
import sys
import numpy as np
from typing import Optional

# Import core modules
try:
    from midi_controller import VirtualDJMIDIController
    from audio_observer import AudioObserver
    from adaptive_agent import AdaptiveAgent
except ImportError as e:
    print(f"Error importing core modules: {e}")
    sys.exit(1)

# Import psychedelic modules
try:
    from dj_persona import PersonaAgent
    from introspective_metrics import IntrospectiveMetrics
    from semantic_analyzer import MusicalSemanticAnalyzer
    from psychedelic_visualizer import create_visualizer
    from machine_spirit import MachineSpiritPoet
except ImportError as e:
    print(f"Error importing psychedelic modules: {e}")
    sys.exit(1)


class PsychedelicDJSystem:
    """
    Enhanced automation system with psychedelic features.
    """
    
    def __init__(self, midi_port: Optional[str] = None, 
                 persona: str = 'techno_detroit',
                 enable_visualization: bool = True,
                 enable_poetry: bool = True):
        """
        Initialize psychedelic DJ system.
        
        Args:
            midi_port: MIDI port name
            persona: DJ persona to use
            enable_visualization: Enable visual effects
            enable_poetry: Enable machine spirit poetry
        """
        print("=" * 70)
        print("🌈 VirtualDJ Psychedelic Automation System 🌈")
        print("=" * 70)
        
        # Initialize core components
        print("\n[1/7] Initializing MIDI Controller...")
        self.controller = VirtualDJMIDIController(port_name=midi_port)
        
        print("\n[2/7] Initializing Audio Observer...")
        self.observer = AudioObserver()
        
        print("\n[3/7] Initializing Persona Agent...")
        self.agent = PersonaAgent(learning_mode='reinforcement', persona=persona)
        
        print("\n[4/7] Initializing Introspective Metrics...")
        self.metrics = IntrospectiveMetrics()
        
        print("\n[5/7] Initializing Semantic Analyzer...")
        self.semantic = MusicalSemanticAnalyzer()
        
        print("\n[6/7] Initializing Visualization...")
        self.enable_visualization = enable_visualization
        if enable_visualization:
            try:
                self.visualizer = create_visualizer(mode='auto', width=800, height=600)
                print("  ✓ Visualizer created")
            except Exception as e:
                print(f"  ⚠ Visualization disabled: {e}")
                self.visualizer = None
        else:
            self.visualizer = None
        
        print("\n[7/7] Initializing Machine Spirit...")
        self.enable_poetry = enable_poetry
        if enable_poetry:
            self.poet = MachineSpiritPoet()
            print(f"  ✓ Machine Spirit awakens")
            print(f"  💭 \"{self.poet.get_random_wisdom()}\"")
        else:
            self.poet = None
        
        # System state
        self.is_running = False
        self.prev_audio_features = None
        self.iteration = 0
        
        print("\n✓ Psychedelic system initialized!")
        print(f"  Active Persona: {self.agent.get_persona_info()['name']}")
    
    def start(self):
        """Start the system."""
        print("\n" + "=" * 70)
        print("Starting Psychedelic Automation")
        print("=" * 70)
        
        # Start audio observation
        self.observer.start_streaming()
        
        # Start visualization if enabled
        if self.visualizer:
            self.visualizer.start()
            print("✓ Visualization started")
        
        self.is_running = True
        print("\n✓ System running!")
        if self.poet:
            print(f"💭 Machine Spirit says: \"{self.poet.get_random_wisdom()}\"")
    
    def stop(self):
        """Stop the system."""
        print("\n\nStopping psychedelic system...")
        self.is_running = False
        
        # Stop components
        self.observer.stop_streaming()
        if self.visualizer:
            self.visualizer.stop()
        self.controller.close()
        self.agent.save()
        
        # Generate final poetry
        if self.poet:
            stats = self.agent.get_statistics()
            epilogue = self.poet.generate_session_epilogue(stats)
            print("\n" + epilogue)
        
        print("\n✓ System stopped gracefully")
    
    def run_psychedelic_loop(self, duration: float = 60.0, update_interval: float = 2.0):
        """
        Run the main psychedelic loop.
        
        Args:
            duration: Total duration (seconds)
            update_interval: Time between updates (seconds)
        """
        self.start()
        
        start_time = time.time()
        
        try:
            while self.is_running and (time.time() - start_time) < duration:
                self.iteration += 1
                elapsed = time.time() - start_time
                
                print(f"\n{'=' * 70}")
                print(f"🎵 Iteration {self.iteration} | Elapsed: {elapsed:.1f}s / {duration:.1f}s")
                print(f"{'=' * 70}")
                
                # Get current state
                audio_features = self.observer.get_features()
                vdj_state = self.observer.get_vdj_state()
                
                # Perform semantic analysis
                audio_buffer = list(self.observer.audio_buffer)
                if len(audio_buffer) > 1000:
                    semantic_features = self.semantic.analyze(
                        np.array(audio_buffer[-44100:]),  # Last second
                        audio_features
                    )
                else:
                    semantic_features = self.semantic.last_analysis
                
                # Agent decides action with persona
                actions = self.agent.decide_action(audio_features, vdj_state)
                
                # Calculate reward and update
                reward = self.agent.calculate_reward(audio_features, vdj_state, 
                                                     self.prev_audio_features)
                self.agent.update_q_value(reward)
                
                # Update introspective metrics
                agent_stats = self.agent.get_statistics()
                self.metrics.update(agent_stats, audio_features, actions)
                psychological_state = self.metrics.get_state()
                
                # Update visualization
                if self.visualizer:
                    self.visualizer.update(audio_features, psychological_state, vdj_state)
                
                # Display comprehensive status
                self._display_psychedelic_status(
                    audio_features, vdj_state, actions, semantic_features,
                    psychological_state, reward
                )
                
                # Generate poetry occasionally
                if self.poet and self.iteration % 3 == 0:
                    poem = self.poet.generate_action_poem(
                        actions, audio_features, psychological_state
                    )
                    print("\n💭 Machine Spirit speaks:")
                    print("─" * 50)
                    for line in poem.split('\n'):
                        print(f"  {line}")
                    print("─" * 50)
                
                # Execute actions (simulated)
                self._execute_actions_simulated(actions, vdj_state)
                
                # Store for next iteration
                self.prev_audio_features = audio_features.copy()
                
                time.sleep(update_interval)
            
            # Final summary
            self._display_final_summary()
            
        except KeyboardInterrupt:
            print("\n\n⚠ Interrupted by user")
        finally:
            self.stop()
    
    def _execute_actions_simulated(self, actions: dict, vdj_state: dict):
        """Simulate action execution."""
        # Update crossfader in simulated state
        if actions.get('crossfade_adjust', 0.0) != 0.0:
            current_pos = vdj_state.get('crossfader_position', 0.5)
            new_pos = np.clip(current_pos + actions['crossfade_adjust'], 0.0, 1.0)
            self.observer.update_vdj_state({'crossfader_position': new_pos})
    
    def _display_psychedelic_status(self, audio_features, vdj_state, actions,
                                    semantic_features, psychological_state, reward):
        """Display comprehensive psychedelic status."""
        
        # Audio Features
        print("\n🎵 Audio Features:")
        print(f"  Energy: {audio_features.get('energy', 0.0):.2f} | "
              f"RMS: {audio_features.get('rms_db', -80):.1f} dB | "
              f"BPM: {audio_features.get('bpm', 0):.1f}")
        print(f"  Beat: {'💥 YES' if audio_features.get('beat_detected') else 'No'} | "
              f"Quality: {self.observer.estimate_mix_quality():.2f}")
        
        # Semantic Analysis
        print("\n🎼 Musical Semantics:")
        print(f"  Percussive: {semantic_features['percussive_density']:.2f} | "
              f"Harmonic: {semantic_features['harmonicity']:.2f} | "
              f"Vocals: {semantic_features['vocal_presence']:.2f}")
        print(f"  Scene: {semantic_features['harmonic_scene']} | "
              f"Mood: {semantic_features['emotional_tone']} | "
              f"Texture: {semantic_features['texture']}")
        
        # Persona Info
        persona_info = self.agent.get_persona_info()
        print(f"\n👤 DJ Persona: {persona_info['name']}")
        print(f"  Mood: {persona_info['current_mood']} | "
              f"Energy Target: {persona_info['energy_target']:.2f} | "
              f"Experimental: {persona_info['experimental_factor']:.2f}")
        
        # Psychological State
        print("\n🧠 Agent Psychology:")
        print(f"  Anxiety: {psychological_state['anxiety']:.2f} | "
              f"Confidence: {psychological_state['confidence']:.2f} | "
              f"Fantasy: {psychological_state['fantasy']:.2f}")
        print(f"  Focus: {psychological_state['focus']:.2f} | "
              f"Excitement: {psychological_state['excitement']:.2f} | "
              f"Memory: {psychological_state['memory_health']:.2f}")
        print(f"  Overall Mood: {psychological_state['mood'].upper()} | "
              f"Creative State: {psychological_state['creative_state']} | "
              f"Phase: {psychological_state['learning_phase']}")
        
        # Learning Stats
        print(f"\n📊 Learning Stats:")
        print(f"  Reward: {reward:+.2f} | "
              f"Decisions: {psychological_state['total_decisions']} | "
              f"Exploration: {psychological_state['exploration_ratio']:.2%}")
        
        # VDJ State
        print(f"\n🎚️  VirtualDJ State:")
        print(f"  Crossfader: [{'█' * int(vdj_state['crossfader_position'] * 20)}"
              f"{' ' * (20 - int(vdj_state['crossfader_position'] * 20))}] "
              f"{vdj_state['crossfader_position']:.2f}")
        print(f"  Deck A: {'▶️ Playing' if vdj_state.get('deck_a_playing') else '⏸️  Stopped'} | "
              f"Deck B: {'▶️ Playing' if vdj_state.get('deck_b_playing') else '⏸️  Stopped'}")
        
        # Actions
        significant_actions = {k: v for k, v in actions.items() 
                              if v and v != 0.0 and v != {}}
        if significant_actions:
            print(f"\n⚡ Actions:")
            for key, value in significant_actions.items():
                print(f"  {key}: {value}")
    
    def _display_final_summary(self):
        """Display final summary."""
        print("\n" + "=" * 70)
        print("🌈 Final Psychedelic Summary 🌈")
        print("=" * 70)
        
        # Agent stats
        stats = self.agent.get_statistics()
        print(f"\nLearning Stats:")
        print(f"  Total Decisions: {self.metrics.total_decisions}")
        print(f"  Average Reward: {stats.get('avg_reward', 0.0):.2f}")
        print(f"  Q-Table Size: {stats.get('q_table_size', 0)}")
        print(f"  Exploration Rate: {stats.get('exploration_rate', 0.0):.2%}")
        
        # Psychological state
        final_state = self.metrics.get_state()
        print(f"\nFinal Psychological State:")
        print(f"  Mood: {final_state['mood'].upper()}")
        print(f"  Confidence: {final_state['confidence']:.2f}")
        print(f"  Anxiety: {final_state['anxiety']:.2f}")
        print(f"  Creative State: {final_state['creative_state']}")
        
        # Narrative
        print(f"\n💭 Agent's Journey:")
        print(self.metrics.get_narrative_description())
        
        # Persona info
        persona_info = self.agent.get_persona_info()
        print(f"\nPersona: {persona_info['name']}")
        print(f"  Transitions: {persona_info['transition_count']}")
        
        # Visualization stats
        if self.visualizer:
            viz_stats = self.visualizer.get_status()
            print(f"\nVisualization:")
            print(f"  Frames Rendered: {viz_stats.get('frame_count', 0)}")


def demo_menu():
    """Display demo menu."""
    print("\n" + "=" * 70)
    print("🌈 Psychedelic Demo Menu 🌈")
    print("=" * 70)
    print("\n1. Quick Demo (30s) - Techno Detroit")
    print("2. Psy-Trance Session (60s) - High energy")
    print("3. Latin Bass Session (45s) - Heavy bass")
    print("4. Lo-Fi ChillHop (60s) - Relaxed vibes")
    print("5. Persona Comparison (20s each)")
    print("6. Poetry-Only Mode (No visualization)")
    print("7. Visualization Showcase (ASCII mode)")
    print("8. Exit")
    
    return input("\nSelect option (1-8): ")


def main():
    """Main entry point."""
    while True:
        choice = demo_menu()
        
        if choice == '1':
            print("\n🎵 Starting Quick Demo with Techno Detroit persona...")
            system = PsychedelicDJSystem(persona='techno_detroit')
            system.run_psychedelic_loop(duration=30.0, update_interval=3.0)
        
        elif choice == '2':
            print("\n🎵 Starting Psy-Trance Session...")
            system = PsychedelicDJSystem(persona='psytrance_goa')
            system.run_psychedelic_loop(duration=60.0, update_interval=3.0)
        
        elif choice == '3':
            print("\n🎵 Starting Latin Bass Session...")
            system = PsychedelicDJSystem(persona='latin_bass')
            system.run_psychedelic_loop(duration=45.0, update_interval=3.0)
        
        elif choice == '4':
            print("\n🎵 Starting Lo-Fi ChillHop Session...")
            system = PsychedelicDJSystem(persona='lofi_chillhop')
            system.run_psychedelic_loop(duration=60.0, update_interval=4.0)
        
        elif choice == '5':
            print("\n🎵 Comparing all personas...")
            from dj_persona import PersonaAgent
            personas = PersonaAgent.list_personas()
            for persona in personas:
                print(f"\n--- Testing {persona} ---")
                system = PsychedelicDJSystem(persona=persona, 
                                            enable_visualization=False)
                system.run_psychedelic_loop(duration=20.0, update_interval=5.0)
        
        elif choice == '6':
            print("\n🎵 Poetry-Only Mode...")
            system = PsychedelicDJSystem(persona='experimental',
                                        enable_visualization=False,
                                        enable_poetry=True)
            system.run_psychedelic_loop(duration=40.0, update_interval=4.0)
        
        elif choice == '7':
            print("\n🎵 Visualization Showcase (ASCII)...")
            system = PsychedelicDJSystem(persona='techno_detroit',
                                        enable_visualization=True)
            system.run_psychedelic_loop(duration=30.0, update_interval=2.0)
        
        elif choice == '8':
            print("\n👋 Farewell! May the beat guide you.")
            break
        
        else:
            print("\n⚠ Invalid choice. Please select 1-8.")
        
        # Ask to continue
        if choice in ['1', '2', '3', '4', '5', '6', '7']:
            cont = input("\nReturn to menu? (y/n): ")
            if cont.lower() != 'y':
                break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
