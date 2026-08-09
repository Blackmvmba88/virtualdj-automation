"""
MIDI Controller Module for VirtualDJ Automation

This module provides a MIDI controller interface to send commands to VirtualDJ.
Supports play/pause, track loading, cue points, crossfader, and effects control.
"""

import mido
import time
import math
from typing import Optional, List, Dict


class VirtualDJMIDIController:
    """
    Controller class to send MIDI commands to VirtualDJ.
    """
    
    # MIDI CC and Note mappings for VirtualDJ
    PLAY_PAUSE_DECK_A = 0x01
    PLAY_PAUSE_DECK_B = 0x02
    CUE_DECK_A = 0x03
    CUE_DECK_B = 0x04
    SYNC_DECK_A = 0x05
    SYNC_DECK_B = 0x06
    CROSSFADER = 0x07
    VOLUME_DECK_A = 0x08
    VOLUME_DECK_B = 0x09
    EQ_LOW_A = 0x0A
    EQ_MID_A = 0x0B
    EQ_HIGH_A = 0x0C
    EQ_LOW_B = 0x0D
    EQ_MID_B = 0x0E
    EQ_HIGH_B = 0x0F
    EFFECT_1 = 0x10
    EFFECT_2 = 0x11
    EFFECT_3 = 0x12
    LOAD_TRACK_A = 0x20
    LOAD_TRACK_B = 0x21

    @staticmethod
    def _validate_deck(deck: str) -> str:
        if not isinstance(deck, str) or deck.upper() not in {'A', 'B'}:
            raise ValueError("deck must be 'A' or 'B'")
        return deck.upper()

    @staticmethod
    def _validate_unit_value(name: str, value: float) -> float:
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{name} must be a number")
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"{name} must be between 0.0 and 1.0")
        return float(value)

    @staticmethod
    def _validate_midi_value(name: str, value: int, minimum: int, maximum: int) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{name} must be an integer")
        if not minimum <= value <= maximum:
            raise ValueError(f"{name} must be between {minimum} and {maximum}")
        return value
    
    def __init__(self, port_name: Optional[str] = None):
        """
        Initialize MIDI controller.
        
        Args:
            port_name: Name of the MIDI output port. If None, uses first available port.
        """
        self.port_name = port_name
        self.output_port = None
        self.is_connected = False
        self._connect()
    
    def _connect(self):
        """Connect to MIDI output port."""
        try:
            available_ports = mido.get_output_names()
            
            if not available_ports:
                print("Warning: No MIDI output ports available")
                return
            
            if self.port_name:
                if self.port_name in available_ports:
                    self.output_port = mido.open_output(self.port_name)
                else:
                    print(f"Port '{self.port_name}' not found. Available ports: {available_ports}")
                    return
            else:
                # Use first available port
                self.output_port = mido.open_output(available_ports[0])
                self.port_name = available_ports[0]
            
            self.is_connected = True
            print(f"Connected to MIDI port: {self.port_name}")
            
        except Exception as e:
            print(f"Error connecting to MIDI port: {e}")
            self.is_connected = False
    
    def send_control_change(self, control: int, value: int, channel: int = 0):
        """
        Send a MIDI Control Change message.
        
        Args:
            control: MIDI CC number (0-127)
            value: MIDI value (0-127)
            channel: MIDI channel (0-15)
        """
        control = self._validate_midi_value('control', control, 0, 127)
        value = self._validate_midi_value('value', value, 0, 127)
        channel = self._validate_midi_value('channel', channel, 0, 15)

        if not self.is_connected or not self.output_port:
            print("MIDI port not connected")
            return
        
        try:
            msg = mido.Message('control_change', control=control, value=value, channel=channel)
            self.output_port.send(msg)
        except Exception as e:
            print(f"Error sending MIDI message: {e}")
    
    def send_note_on(self, note: int, velocity: int = 127, channel: int = 0):
        """
        Send a MIDI Note On message.
        
        Args:
            note: MIDI note number (0-127)
            velocity: Note velocity (0-127)
            channel: MIDI channel (0-15)
        """
        note = self._validate_midi_value('note', note, 0, 127)
        velocity = self._validate_midi_value('velocity', velocity, 0, 127)
        channel = self._validate_midi_value('channel', channel, 0, 15)

        if not self.is_connected or not self.output_port:
            print("MIDI port not connected")
            return
        
        try:
            msg = mido.Message('note_on', note=note, velocity=velocity, channel=channel)
            self.output_port.send(msg)
        except Exception as e:
            print(f"Error sending MIDI message: {e}")
    
    def send_note_off(self, note: int, channel: int = 0):
        """
        Send a MIDI Note Off message.
        
        Args:
            note: MIDI note number (0-127)
            channel: MIDI channel (0-15)
        """
        note = self._validate_midi_value('note', note, 0, 127)
        channel = self._validate_midi_value('channel', channel, 0, 15)

        if not self.is_connected or not self.output_port:
            print("MIDI port not connected")
            return
        
        try:
            msg = mido.Message('note_off', note=note, velocity=0, channel=channel)
            self.output_port.send(msg)
        except Exception as e:
            print(f"Error sending MIDI message: {e}")
    
    # High-level control methods
    
    def play_pause_deck(self, deck: str):
        """
        Toggle play/pause for a deck.
        
        Args:
            deck: 'A' or 'B'
        """
        deck = self._validate_deck(deck)
        control = self.PLAY_PAUSE_DECK_A if deck == 'A' else self.PLAY_PAUSE_DECK_B
        self.send_note_on(control, 127)
        time.sleep(0.05)
        self.send_note_off(control)
        print(f"Play/Pause toggled for Deck {deck}")
    
    def cue_deck(self, deck: str):
        """
        Activate cue point for a deck.
        
        Args:
            deck: 'A' or 'B'
        """
        deck = self._validate_deck(deck)
        control = self.CUE_DECK_A if deck == 'A' else self.CUE_DECK_B
        self.send_note_on(control, 127)
        time.sleep(0.05)
        self.send_note_off(control)
        print(f"Cue activated for Deck {deck}")
    
    def sync_deck(self, deck: str):
        """
        Sync deck to master tempo.
        
        Args:
            deck: 'A' or 'B'
        """
        deck = self._validate_deck(deck)
        control = self.SYNC_DECK_A if deck == 'A' else self.SYNC_DECK_B
        self.send_note_on(control, 127)
        time.sleep(0.05)
        self.send_note_off(control)
        print(f"Sync activated for Deck {deck}")
    
    def set_crossfader(self, position: float):
        """
        Set crossfader position.
        
        Args:
            position: Crossfader position (0.0 = full A, 1.0 = full B)
        """
        position = self._validate_unit_value('position', position)
        value = int(position * 127)
        self.send_control_change(self.CROSSFADER, value)
        print(f"Crossfader set to {position:.2f} (MIDI value: {value})")
    
    def set_volume(self, deck: str, volume: float):
        """
        Set volume for a deck.
        
        Args:
            deck: 'A' or 'B'
            volume: Volume level (0.0 to 1.0)
        """
        deck = self._validate_deck(deck)
        volume = self._validate_unit_value('volume', volume)
        control = self.VOLUME_DECK_A if deck == 'A' else self.VOLUME_DECK_B
        value = int(volume * 127)
        self.send_control_change(control, value)
        print(f"Volume for Deck {deck} set to {volume:.2f}")
    
    def set_eq(self, deck: str, band: str, value: float):
        """
        Set EQ for a deck.
        
        Args:
            deck: 'A' or 'B'
            band: 'low', 'mid', or 'high'
            value: EQ value (0.0 to 1.0, 0.5 is neutral)
        """
        deck = self._validate_deck(deck)
        if not isinstance(band, str) or band.lower() not in {'low', 'mid', 'high'}:
            raise ValueError("band must be 'low', 'mid', or 'high'")
        band = band.lower()
        value = self._validate_unit_value('value', value)

        eq_map = {
            'A': {'low': self.EQ_LOW_A, 'mid': self.EQ_MID_A, 'high': self.EQ_HIGH_A},
            'B': {'low': self.EQ_LOW_B, 'mid': self.EQ_MID_B, 'high': self.EQ_HIGH_B}
        }
        
        control = eq_map[deck][band]
        midi_value = int(value * 127)
        self.send_control_change(control, midi_value)
        print(f"EQ {band} for Deck {deck} set to {value:.2f}")
    
    def activate_effect(self, effect_num: int, value: float = 1.0):
        """
        Activate an effect.
        
        Args:
            effect_num: Effect number (1-3)
            value: Effect intensity (0.0 to 1.0)
        """
        effect_num = self._validate_midi_value('effect_num', effect_num, 1, 3)
        value = self._validate_unit_value('value', value)
        effect_map = {1: self.EFFECT_1, 2: self.EFFECT_2, 3: self.EFFECT_3}
        
        control = effect_map[effect_num]
        midi_value = int(value * 127)
        self.send_control_change(control, midi_value)
        print(f"Effect {effect_num} activated with intensity {value:.2f}")
    
    def load_track(self, deck: str, track_index: int = 0):
        """
        Load a track to a deck.
        
        Args:
            deck: 'A' or 'B'
            track_index: Index of track in playlist (0-127)
        """
        deck = self._validate_deck(deck)
        track_index = self._validate_midi_value('track_index', track_index, 0, 127)
        control = self.LOAD_TRACK_A if deck == 'A' else self.LOAD_TRACK_B
        self.send_control_change(control, track_index)
        print(f"Track {track_index} loaded to Deck {deck}")
    
    def crossfade_transition(self, from_deck: str, to_deck: str, duration: float = 2.0, steps: int = 50):
        """
        Perform a smooth crossfade transition between decks.
        
        Args:
            from_deck: Source deck ('A' or 'B')
            to_deck: Target deck ('A' or 'B')
            duration: Transition duration in seconds
            steps: Number of steps in the transition
        """
        from_deck = self._validate_deck(from_deck)
        to_deck = self._validate_deck(to_deck)
        if from_deck == to_deck:
            raise ValueError("from_deck and to_deck must be different")
        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            raise TypeError("duration must be a number")
        if not math.isfinite(duration) or duration <= 0:
            raise ValueError("duration must be greater than zero")
        steps = self._validate_midi_value('steps', steps, 1, 10000)

        start_pos = 0.0 if from_deck == 'A' else 1.0
        end_pos = 0.0 if to_deck == 'A' else 1.0
        
        step_duration = duration / steps
        
        print(f"Starting crossfade from Deck {from_deck} to Deck {to_deck}")
        
        for i in range(steps + 1):
            position = start_pos + (end_pos - start_pos) * (i / steps)
            self.set_crossfader(position)
            time.sleep(step_duration)
        
        print("Crossfade complete")
    
    def close(self):
        """Close MIDI connection."""
        if getattr(self, 'output_port', None):
            self.output_port.close()
            self.is_connected = False
            print("MIDI connection closed")
    
    def __del__(self):
        """Destructor to ensure MIDI port is closed."""
        self.close()


if __name__ == "__main__":
    # Example usage
    print("VirtualDJ MIDI Controller - Test Mode")
    print("=" * 50)
    
    controller = VirtualDJMIDIController()
    
    if controller.is_connected:
        print("\nTesting basic commands...")
        
        # Test play/pause
        controller.play_pause_deck('A')
        time.sleep(1)
        
        # Test volume
        controller.set_volume('A', 0.8)
        time.sleep(0.5)
        
        # Test crossfader
        controller.set_crossfader(0.5)
        time.sleep(0.5)
        
        # Test EQ
        controller.set_eq('A', 'high', 0.7)
        time.sleep(0.5)
        
        # Test effect
        controller.activate_effect(1, 0.5)
        time.sleep(0.5)
        
        print("\nTest complete!")
    else:
        print("Could not connect to MIDI port. Make sure a virtual MIDI port (like loopMIDI) is running.")
    
    controller.close()
