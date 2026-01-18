"""
Psychedelic Visualization Engine for VirtualDJ Automation

Real-time shader-based visualizations reactive to audio features and agent state.
Creates hypnotic, psychedelic visuals using OpenGL and fragment shaders.
"""

import numpy as np
from typing import Dict, Optional
import time
import threading

# Try to import OpenGL dependencies
try:
    import pygame
    from pygame.locals import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("Warning: PyGame/PyOpenGL not available. Visualization features disabled.")
    print("Install with: pip install pygame PyOpenGL")


class PsychedelicVisualizer:
    """
    Real-time psychedelic visualization engine.
    
    Creates visuals reactive to:
    - Beats: Visual "hits" and pulses
    - Energy: Intensity of colors and movement
    - Reward: Smoothness vs distortion
    - Crossfader: Interpolation between visual worlds
    - Agent state: Color palette and pattern selection
    """
    
    def __init__(self, width: int = 800, height: int = 600, fullscreen: bool = False):
        """
        Initialize visualizer.
        
        Args:
            width: Window width
            height: Window height
            fullscreen: Use fullscreen mode
        """
        if not OPENGL_AVAILABLE:
            raise RuntimeError("OpenGL dependencies not available")
        
        self.width = width
        self.height = height
        self.fullscreen = fullscreen
        
        # Visualization state
        self.beat_intensity = 0.0
        self.energy_level = 0.5
        self.reward_smoothness = 0.5
        self.crossfader_position = 0.5
        self.agent_mood = 'balanced'
        
        # Animation state
        self.time = 0.0
        self.beat_trigger_time = 0.0
        self.frame_count = 0
        
        # Color palettes for different moods
        self.color_palettes = {
            'euphoric': [(1.0, 0.8, 0.2), (1.0, 0.4, 0.8), (0.6, 0.2, 1.0)],  # Warm bright
            'confident': [(0.2, 0.8, 1.0), (0.4, 0.6, 1.0), (0.6, 0.4, 0.8)],  # Cool confident
            'anxious': [(1.0, 0.3, 0.3), (0.8, 0.5, 0.2), (0.6, 0.6, 0.2)],  # Agitated reds
            'experimental': [(0.8, 0.2, 1.0), (0.2, 1.0, 0.8), (1.0, 0.8, 0.2)],  # Wild contrasts
            'focused': [(0.2, 0.4, 0.8), (0.3, 0.5, 0.7), (0.4, 0.6, 0.9)],  # Focused blues
            'calm': [(0.4, 0.8, 0.6), (0.5, 0.7, 0.8), (0.6, 0.6, 0.7)],  # Peaceful greens
            'balanced': [(0.5, 0.5, 0.8), (0.6, 0.4, 0.7), (0.7, 0.5, 0.6)],  # Balanced purples
        }
        
        self.current_palette = self.color_palettes['balanced']
        
        # Threading
        self.running = False
        self.render_thread = None
        self.lock = threading.Lock()
        
        # Window
        self.screen = None
    
    def start(self):
        """Start visualization in separate thread."""
        if not OPENGL_AVAILABLE:
            print("Visualization not available")
            return
        
        self.running = True
        self.render_thread = threading.Thread(target=self._render_loop, daemon=True)
        self.render_thread.start()
    
    def stop(self):
        """Stop visualization."""
        self.running = False
        if self.render_thread:
            self.render_thread.join(timeout=2.0)
        if self.screen:
            pygame.quit()
    
    def _init_opengl(self):
        """Initialize OpenGL context."""
        pygame.init()
        
        flags = DOUBLEBUF | OPENGL
        if self.fullscreen:
            flags |= FULLSCREEN
        
        self.screen = pygame.display.set_mode((self.width, self.height), flags)
        pygame.display.set_caption("VirtualDJ Psychedelic Visualizer")
        
        # OpenGL setup
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        
        # Enable blending for transparency effects
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    def _render_loop(self):
        """Main rendering loop."""
        try:
            self._init_opengl()
            clock = pygame.time.Clock()
            
            while self.running:
                # Handle events
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.running = False
                    elif event.type == KEYDOWN:
                        if event.key == K_ESCAPE:
                            self.running = False
                
                # Update animation time
                self.time += 0.016  # Approximately 60 FPS
                self.frame_count += 1
                
                # Render frame
                with self.lock:
                    self._render_frame()
                
                pygame.display.flip()
                clock.tick(60)  # Target 60 FPS
        
        except Exception as e:
            print(f"Visualization error: {e}")
        finally:
            pygame.quit()
    
    def _render_frame(self):
        """Render a single frame."""
        # Clear with dark background
        bg_intensity = 0.05 + self.energy_level * 0.1
        glClearColor(bg_intensity, bg_intensity * 0.9, bg_intensity * 1.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        glLoadIdentity()
        
        # Render layers
        self._render_background_fractals()
        self._render_energy_circles()
        self._render_beat_pulse()
        self._render_crossfader_split()
        self._render_reward_distortion()
    
    def _render_background_fractals(self):
        """Render animated fractal-like background patterns."""
        # Create flowing geometric patterns
        num_shapes = int(10 + self.energy_level * 20)
        
        for i in range(num_shapes):
            t = self.time + i * 0.5
            
            # Position based on time and energy
            x = self.width / 2 + np.sin(t * 0.3 + i) * 200 * (1 + self.energy_level)
            y = self.height / 2 + np.cos(t * 0.4 + i) * 150 * (1 + self.energy_level)
            
            # Size pulsing with energy
            size = 30 + 20 * np.sin(t + i * 0.3) * self.energy_level
            
            # Rotation
            rotation = t * 30 + i * 45
            
            # Color from palette
            color_idx = i % len(self.current_palette)
            r, g, b = self.current_palette[color_idx]
            
            # Fade with reward smoothness
            alpha = 0.3 + 0.3 * self.reward_smoothness
            
            glPushMatrix()
            glTranslatef(x, y, 0)
            glRotatef(rotation, 0, 0, 1)
            
            # Draw polygon
            sides = 6 if self.agent_mood == 'focused' else 8
            self._draw_polygon(size, sides, (r, g, b, alpha))
            
            glPopMatrix()
    
    def _render_energy_circles(self):
        """Render pulsing circles based on energy level."""
        # Center position
        cx = self.width / 2
        cy = self.height / 2
        
        # Number of rings based on energy
        num_rings = int(3 + self.energy_level * 5)
        
        for i in range(num_rings):
            t = self.time + i * 0.2
            
            # Radius expanding with time
            radius = 50 + i * 30 + np.sin(t) * 20
            radius *= (1 + self.energy_level * 0.5)
            
            # Color fades through palette
            color_idx = (i + int(self.time * 2)) % len(self.current_palette)
            r, g, b = self.current_palette[color_idx]
            
            # Alpha fades with distance
            alpha = (1.0 - i / num_rings) * 0.4
            
            # Draw circle
            self._draw_circle(cx, cy, radius, (r, g, b, alpha), filled=False)
    
    def _render_beat_pulse(self):
        """Render visual pulse on beat."""
        # Calculate time since last beat
        time_since_beat = self.time - self.beat_trigger_time
        
        if time_since_beat < 0.3:  # Pulse lasts 0.3 seconds
            # Pulse intensity decays
            pulse_intensity = (1.0 - time_since_beat / 0.3) * self.beat_intensity
            
            # Flash effect
            cx = self.width / 2
            cy = self.height / 2
            radius = 100 + time_since_beat * 300
            
            # White flash
            alpha = pulse_intensity * 0.6
            self._draw_circle(cx, cy, radius, (1.0, 1.0, 1.0, alpha), filled=True)
    
    def _render_crossfader_split(self):
        """Render visual split based on crossfader position."""
        # Vertical line showing crossfader position
        x_pos = self.crossfader_position * self.width
        
        # Draw gradient bars
        bar_width = 40
        
        # Left side (Deck A)
        for i in range(int(x_pos)):
            alpha = (1.0 - i / max(1, x_pos)) * 0.3
            r, g, b = self.current_palette[0]
            self._draw_vertical_line(i, (r, g, b, alpha))
        
        # Right side (Deck B)
        for i in range(int(x_pos), self.width):
            alpha = (i - x_pos) / max(1, self.width - x_pos) * 0.3
            r, g, b = self.current_palette[-1]
            self._draw_vertical_line(i, (r, g, b, alpha))
    
    def _render_reward_distortion(self):
        """Render distortion effects based on reward."""
        # Low reward = more distortion/chaos
        # High reward = smooth, harmonious
        
        if self.reward_smoothness < 0.5:
            # Add chaotic elements
            distortion = (0.5 - self.reward_smoothness) * 2.0
            num_glitches = int(distortion * 10)
            
            for i in range(num_glitches):
                x = np.random.uniform(0, self.width)
                y = np.random.uniform(0, self.height)
                size = np.random.uniform(5, 30)
                
                r = np.random.uniform(0.5, 1.0)
                g = np.random.uniform(0.0, 0.5)
                b = np.random.uniform(0.0, 0.5)
                
                self._draw_circle(x, y, size, (r, g, b, 0.5), filled=True)
    
    def _draw_polygon(self, size: float, sides: int, color: tuple):
        """Draw a polygon."""
        r, g, b, a = color
        glColor4f(r, g, b, a)
        
        glBegin(GL_POLYGON)
        for i in range(sides):
            angle = 2 * np.pi * i / sides
            x = size * np.cos(angle)
            y = size * np.sin(angle)
            glVertex2f(x, y)
        glEnd()
    
    def _draw_circle(self, cx: float, cy: float, radius: float, color: tuple, 
                    filled: bool = False, segments: int = 32):
        """Draw a circle."""
        r, g, b, a = color
        glColor4f(r, g, b, a)
        
        mode = GL_POLYGON if filled else GL_LINE_LOOP
        glBegin(mode)
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            x = cx + radius * np.cos(angle)
            y = cy + radius * np.sin(angle)
            glVertex2f(x, y)
        glEnd()
    
    def _draw_vertical_line(self, x: float, color: tuple):
        """Draw a vertical line."""
        r, g, b, a = color
        glColor4f(r, g, b, a)
        
        glBegin(GL_LINES)
        glVertex2f(x, 0)
        glVertex2f(x, self.height)
        glEnd()
    
    def update(self, audio_features: Dict, agent_state: Dict, vdj_state: Dict):
        """
        Update visualization based on current state.
        
        Args:
            audio_features: Audio features from observer
            agent_state: Agent psychological state
            vdj_state: VirtualDJ state
        """
        with self.lock:
            # Update energy
            self.energy_level = audio_features.get('energy', 0.5)
            
            # Update beat
            if audio_features.get('beat_detected', False):
                self.beat_intensity = min(1.0, audio_features.get('rms', 0.5) * 2)
                self.beat_trigger_time = self.time
            
            # Update crossfader
            self.crossfader_position = vdj_state.get('crossfader_position', 0.5)
            
            # Update reward smoothness
            avg_reward = agent_state.get('avg_reward', 0.0)
            # Normalize reward (-2 to +2) to smoothness (0 to 1)
            self.reward_smoothness = (avg_reward + 2.0) / 4.0
            self.reward_smoothness = np.clip(self.reward_smoothness, 0.0, 1.0)
            
            # Update mood and color palette
            mood = agent_state.get('mood', 'balanced')
            if mood != self.agent_mood:
                self.agent_mood = mood
                if mood in self.color_palettes:
                    self.current_palette = self.color_palettes[mood]
    
    def get_status(self) -> Dict:
        """Get visualizer status."""
        return {
            'running': self.running,
            'frame_count': self.frame_count,
            'energy_level': self.energy_level,
            'agent_mood': self.agent_mood,
            'beat_intensity': self.beat_intensity
        }


# Simplified ASCII visualizer for when OpenGL is not available
class ASCIIVisualizer:
    """
    Simple ASCII-based visualization for terminals.
    
    Fallback when OpenGL is not available.
    """
    
    def __init__(self, width: int = 80, height: int = 20):
        """Initialize ASCII visualizer."""
        self.width = width
        self.height = height
        self.frame_count = 0
    
    def start(self):
        """Start (no-op for ASCII)."""
        print("ASCII Visualizer started (print-based)")
    
    def stop(self):
        """Stop (no-op for ASCII)."""
        pass
    
    def update(self, audio_features: Dict, agent_state: Dict, vdj_state: Dict):
        """Update and print ASCII visualization."""
        self.frame_count += 1
        
        # Only update every few frames to avoid spam
        if self.frame_count % 5 != 0:
            return
        
        # Clear screen (simple version)
        print("\n" * 2)
        
        # Energy bar
        energy = audio_features.get('energy', 0.5)
        energy_bar_len = int(energy * self.width)
        print("Energy: [" + "█" * energy_bar_len + " " * (self.width - energy_bar_len) + "]")
        
        # Beat indicator
        if audio_features.get('beat_detected', False):
            print("Beat:   [" + "♪" * self.width + "]")
        else:
            print("Beat:   [" + " " * self.width + "]")
        
        # Crossfader position
        crossfader = vdj_state.get('crossfader_position', 0.5)
        cf_pos = int(crossfader * self.width)
        cf_bar = " " * cf_pos + "┃" + " " * (self.width - cf_pos - 1)
        print(f"XFader: [{cf_bar}]")
        print(f"        {'A' + ' ' * (self.width - 2) + 'B'}")
        
        # Agent mood
        mood = agent_state.get('mood', 'balanced')
        confidence = agent_state.get('confidence', 0.5)
        anxiety = agent_state.get('anxiety', 0.5)
        print(f"\nAgent: {mood.upper()} | Confidence: {confidence:.2f} | Anxiety: {anxiety:.2f}")
    
    def get_status(self) -> Dict:
        """Get status."""
        return {
            'running': True,
            'frame_count': self.frame_count,
            'mode': 'ASCII'
        }


def create_visualizer(mode: str = 'auto', **kwargs) -> object:
    """
    Create appropriate visualizer based on mode and availability.
    
    Args:
        mode: 'auto', 'opengl', or 'ascii'
        **kwargs: Arguments passed to visualizer
        
    Returns:
        Visualizer instance
    """
    if mode == 'ascii':
        return ASCIIVisualizer(**kwargs)
    elif mode == 'opengl':
        if not OPENGL_AVAILABLE:
            raise RuntimeError("OpenGL not available")
        return PsychedelicVisualizer(**kwargs)
    else:  # auto
        if OPENGL_AVAILABLE:
            return PsychedelicVisualizer(**kwargs)
        else:
            return ASCIIVisualizer(**kwargs)


if __name__ == "__main__":
    print("Psychedelic Visualizer - Test Mode")
    print("=" * 60)
    
    # Create visualizer (will use ASCII if OpenGL not available)
    viz = create_visualizer(mode='auto', width=800, height=600)
    viz.start()
    
    print("\nVisualizer started!")
    print("Simulating audio and agent state updates...\n")
    
    try:
        # Simulate updates
        for i in range(100):
            # Simulate audio features
            t = i * 0.1
            audio_features = {
                'energy': 0.5 + 0.3 * np.sin(t),
                'rms': 0.15,
                'beat_detected': (i % 4 == 0),  # Beat every 4 frames
                'bpm': 128.0
            }
            
            # Simulate agent state
            agent_state = {
                'mood': 'experimental' if i < 30 else 'confident',
                'confidence': min(1.0, i / 100),
                'anxiety': max(0.1, 1.0 - i / 100),
                'avg_reward': -1.0 + (i / 50)  # Improving reward
            }
            
            # Simulate VDJ state
            vdj_state = {
                'crossfader_position': 0.3 + 0.4 * np.sin(t * 0.5),
                'deck_a_playing': True,
                'deck_b_playing': True
            }
            
            viz.update(audio_features, agent_state, vdj_state)
            
            time.sleep(0.05)  # 20 FPS update rate
    
    except KeyboardInterrupt:
        print("\nStopping visualizer...")
    
    finally:
        viz.stop()
        status = viz.get_status()
        print(f"\nVisualizer stopped. Rendered {status['frame_count']} frames.")
    
    print("\nTest complete!")
