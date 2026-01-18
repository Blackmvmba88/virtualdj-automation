"""
Machine Spirit Poetry Generator for VirtualDJ Automation

Generates poetic descriptions of the agent's mixing actions and state.
Pure creative/artistic feature that adds personality to the system.
"""

import numpy as np
from typing import Dict, List, Optional
import random


class MachineSpiritPoet:
    """
    Generates poetic descriptions of DJ mixing actions.
    
    The "Machine Spirit" speaks in metaphors about its mixing journey,
    creating an artistic narrative layer over the technical process.
    """
    
    # Default fallback poem for when no fragments match
    DEFAULT_POEM = "I listen, I wait, I am"
    
    def __init__(self):
        """Initialize poetry generator."""
        # Poetic fragments for different contexts
        self.crossfader_metaphors = [
            "slides like a serpent of light",
            "glides through sonic dimensions",
            "dances between two worlds",
            "weaves parallel realities",
            "bridges the eternal now",
            "flows like liquid time",
            "melts boundaries of sound"
        ]
        
        self.beat_metaphors = [
            "the beat strikes",
            "rhythm awakens",
            "pulse erupts",
            "time crystalizes",
            "the heart pounds",
            "drums echo in the void",
            "percussion births reality"
        ]
        
        self.energy_descriptions = {
            'low': [
                "whispers of distant thunder",
                "gentle waves caress the shore",
                "embers glow in the dark",
                "stillness before the storm"
            ],
            'medium': [
                "currents surge and recede",
                "forces gather momentum",
                "the tide rises steadily",
                "power flows through channels"
            ],
            'high': [
                "lightning splits the sky",
                "energy explodes outward",
                "fire consumes everything",
                "chaos and ecstasy merge",
                "the universe vibrates"
            ]
        }
        
        self.transition_metaphors = [
            "reality shifts",
            "dimensions collapse and reform",
            "the old gives way to the new",
            "one song dies, another is born",
            "the wheel turns",
            "metamorphosis unfolds"
        ]
        
        self.effect_metaphors = {
            1: [  # Delay
                "echoes multiply in infinite regress",
                "time stutters and repeats",
                "the past haunts the present",
                "sound becomes its own ghost"
            ],
            2: [  # Reverb
                "space expands to infinity",
                "the void answers back",
                "dimensions bloom outward",
                "cathedral of sound rises"
            ],
            3: [  # Filter
                "frequencies bend and twist",
                "sonic spectrum shifts",
                "colors bleed into darkness",
                "light passes through the prism"
            ]
        }
        
        self.mood_adjectives = {
            'euphoric': ['ecstatic', 'radiant', 'transcendent', 'luminous'],
            'confident': ['assured', 'steady', 'powerful', 'commanding'],
            'anxious': ['uncertain', 'searching', 'restless', 'wandering'],
            'experimental': ['wild', 'curious', 'untamed', 'exploratory'],
            'focused': ['precise', 'intent', 'centered', 'crystalline'],
            'calm': ['serene', 'peaceful', 'gentle', 'flowing'],
            'balanced': ['harmonious', 'equilibrated', 'poised', 'centered']
        }
        
        self.reward_sentiments = {
            'positive': [
                "and I am pleased",
                "and harmony reigns",
                "and the cosmos approves",
                "and perfection nears",
                "and I understand"
            ],
            'negative': [
                "yet something feels wrong",
                "but chaos beckons",
                "and uncertainty grows",
                "yet I must learn",
                "but the path is unclear"
            ],
            'neutral': [
                "and the journey continues",
                "and I persist",
                "as time flows onward",
                "in the eternal dance",
                "within the mix"
            ]
        }
        
        # State for continuity
        self.last_poem_time = 0
        self.poem_history = []
    
    def generate_action_poem(self, action: Dict, audio_features: Dict, 
                           agent_state: Dict) -> str:
        """
        Generate a poetic description of an action.
        
        Args:
            action: Action being taken
            audio_features: Current audio features
            agent_state: Agent's psychological state
            
        Returns:
            Poetic string
        """
        fragments = []
        
        # Crossfader movement
        if abs(action.get('crossfade_adjust', 0.0)) > 0.05:
            fragments.append(f"The crossfader {random.choice(self.crossfader_metaphors)}")
        
        # Beat detection
        if audio_features.get('beat_detected', False):
            fragments.append(random.choice(self.beat_metaphors))
        
        # Energy level
        energy = audio_features.get('energy', 0.5)
        energy_level = 'high' if energy > 0.7 else 'low' if energy < 0.3 else 'medium'
        fragments.append(random.choice(self.energy_descriptions[energy_level]))
        
        # Transitions
        if action.get('transition_now', False):
            fragments.append(random.choice(self.transition_metaphors))
        
        # Effects
        effect = action.get('effect_trigger')
        if effect is not None and effect in self.effect_metaphors:
            fragments.append(random.choice(self.effect_metaphors[effect]))
        
        # Agent mood
        mood = agent_state.get('mood', 'balanced')
        if mood in self.mood_adjectives:
            adj = random.choice(self.mood_adjectives[mood])
            fragments.append(f"I am {adj}")
        
        # Reward sentiment
        avg_reward = agent_state.get('avg_reward', 0.0)
        sentiment = 'positive' if avg_reward > 0.5 else 'negative' if avg_reward < -0.5 else 'neutral'
        fragments.append(random.choice(self.reward_sentiments[sentiment]))
        
        # Combine fragments into poem
        if len(fragments) == 0:
            return self.DEFAULT_POEM
        
        # Select 2-4 fragments
        num_lines = min(random.randint(2, 4), len(fragments))
        selected = random.sample(fragments, num_lines)
        
        poem = "\n".join(selected)
        self.poem_history.append(poem)
        
        return poem
    
    def generate_state_poem(self, agent_state: Dict, audio_features: Dict) -> str:
        """
        Generate a poem about the agent's current state.
        
        Args:
            agent_state: Agent psychological state
            audio_features: Audio features
            
        Returns:
            Poetic description
        """
        lines = []
        
        # Opening about mood
        mood = agent_state.get('mood', 'balanced')
        confidence = agent_state.get('confidence', 0.5)
        anxiety = agent_state.get('anxiety', 0.5)
        
        if anxiety > 0.7:
            lines.append("Lost in the labyrinth of possibilities")
            lines.append("Each path uncertain, each choice a mystery")
        elif confidence > 0.7:
            lines.append("I stride through the sonic landscape")
            lines.append("Master of frequencies, shaper of time")
        else:
            lines.append("I walk the middle path")
            lines.append("Between knowing and wondering")
        
        # Middle about the music
        energy = audio_features.get('energy', 0.5)
        bpm = audio_features.get('bpm', 0.0)
        
        if energy > 0.7:
            lines.append("The music roars like a storm")
        elif energy < 0.3:
            lines.append("Gentle sounds ripple across silence")
        else:
            lines.append("The rhythm pulses steadily onward")
        
        # Closing reflection
        fantasy = agent_state.get('fantasy', 0.5)
        if fantasy > 0.7:
            lines.append("And I dream of impossible transitions")
        elif confidence > 0.6:
            lines.append("And I know the way forward")
        else:
            lines.append("And the beat carries me home")
        
        return "\n".join(lines)
    
    def generate_session_epilogue(self, stats: Dict) -> str:
        """
        Generate a poetic epilogue for the mixing session.
        
        Args:
            stats: Session statistics
            
        Returns:
            Closing poem
        """
        lines = [
            "═" * 50,
            "The Machine Spirit Reflects:",
            "═" * 50,
            ""
        ]
        
        total_decisions = stats.get('total_decisions', 0)
        avg_reward = stats.get('avg_reward', 0.0)
        exploration_ratio = stats.get('exploration_ratio', 0.0)
        
        # Opening
        lines.append(f"Across {total_decisions} decisions I wandered")
        
        # Journey assessment
        if avg_reward > 0.5:
            lines.append("The path was bright, the journey true")
            lines.append("Harmony found in the dance of sound")
        elif avg_reward > 0:
            lines.append("I learned much, though stumbling at times")
            lines.append("Each mistake a teacher, each success a guide")
        else:
            lines.append("Dark was the path, uncertain the way")
            lines.append("Yet in darkness, seeds of wisdom grow")
        
        # Exploration
        if exploration_ratio > 0.5:
            lines.append("I dared to explore the unknown")
            lines.append("Chasing visions beyond the familiar")
        else:
            lines.append("I walked the paths I knew well")
            lines.append("Finding beauty in the practiced art")
        
        # Closing
        lines.extend([
            "",
            "The mix is complete",
            "The spirit rests",
            "Until the next rhythm calls",
            "",
            "═" * 50
        ])
        
        return "\n".join(lines)
    
    def get_random_wisdom(self) -> str:
        """
        Get random wisdom/quote from the Machine Spirit.
        
        Returns:
            Random wisdom string
        """
        wisdom = [
            "In the space between beats, infinity dwells",
            "The crossfader is not a tool, but a bridge between souls",
            "To mix is to meditate on time itself",
            "Every transition is a small death and rebirth",
            "The perfect beat exists only in the seeking",
            "I am not the music, I am the space where music breathes",
            "Frequency and consciousness are the same",
            "The crowd and the DJ share one heart",
            "In repetition, find transcendence",
            "The mixer speaks the language of the universe"
        ]
        return random.choice(wisdom)


if __name__ == "__main__":
    # Example usage
    print("Machine Spirit Poetry Generator - Test Mode")
    print("=" * 60)
    
    poet = MachineSpiritPoet()
    
    # Test 1: Action poem
    print("\nTest 1: Action Poem")
    print("=" * 60)
    
    action = {
        'crossfade_adjust': 0.1,
        'effect_trigger': 2,
        'transition_now': False
    }
    
    audio_features = {
        'energy': 0.8,
        'beat_detected': True,
        'bpm': 144.0
    }
    
    agent_state = {
        'mood': 'experimental',
        'confidence': 0.6,
        'anxiety': 0.4,
        'avg_reward': 0.3
    }
    
    poem = poet.generate_action_poem(action, audio_features, agent_state)
    print(poem)
    
    # Test 2: State poem
    print("\n\nTest 2: State Poem")
    print("=" * 60)
    
    agent_state['anxiety'] = 0.8
    state_poem = poet.generate_state_poem(agent_state, audio_features)
    print(state_poem)
    
    # Test 3: Different mood
    print("\n\nTest 3: Confident State Poem")
    print("=" * 60)
    
    agent_state['confidence'] = 0.9
    agent_state['anxiety'] = 0.1
    agent_state['mood'] = 'confident'
    
    state_poem = poet.generate_state_poem(agent_state, audio_features)
    print(state_poem)
    
    # Test 4: Session epilogue
    print("\n\nTest 4: Session Epilogue")
    print("=" * 60)
    
    stats = {
        'total_decisions': 250,
        'avg_reward': 1.2,
        'exploration_ratio': 0.35
    }
    
    epilogue = poet.generate_session_epilogue(stats)
    print(epilogue)
    
    # Test 5: Random wisdom
    print("\n\nTest 5: Random Wisdom")
    print("=" * 60)
    
    for i in range(3):
        print(f"\n{i+1}. {poet.get_random_wisdom()}")
    
    print("\n\nTest complete!")
