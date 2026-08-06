"""Behavioral tests for controller and agent validation."""

import tempfile
import unittest
from unittest.mock import patch

import numpy as np

from adaptive_agent import AdaptiveAgent
from midi_controller import VirtualDJMIDIController


def make_disconnected_controller():
    controller = VirtualDJMIDIController.__new__(VirtualDJMIDIController)
    controller.port_name = None
    controller.output_port = None
    controller.is_connected = False
    return controller


class MIDIControllerValidationTests(unittest.TestCase):
    def setUp(self):
        self.controller = make_disconnected_controller()

    def test_rejects_invalid_decks(self):
        for method, args in [
            (self.controller.play_pause_deck, ('C',)),
            (self.controller.set_volume, ('left', 0.5)),
            (self.controller.set_eq, ('', 'high', 0.5)),
            (self.controller.load_track, ('B-side', 1)),
        ]:
            with self.subTest(method=method.__name__):
                with self.assertRaises(ValueError):
                    method(*args)

    def test_rejects_invalid_ranges_and_types(self):
        cases = [
            (self.controller.set_crossfader, (-0.1,), ValueError),
            (self.controller.set_volume, ('A', 1.1), ValueError),
            (self.controller.set_eq, ('A', 'presence', 0.5), ValueError),
            (self.controller.activate_effect, (4, 0.5), ValueError),
            (self.controller.load_track, ('A', 128), ValueError),
            (self.controller.send_note_on, (1, 127, 16), ValueError),
            (self.controller.set_crossfader, ('center',), TypeError),
        ]
        for method, args, error in cases:
            with self.subTest(method=method.__name__, args=args):
                with self.assertRaises(error):
                    method(*args)

    def test_crossfader_boundaries_map_to_midi_range(self):
        with patch.object(self.controller, 'send_control_change') as send:
            self.controller.set_crossfader(0.0)
            self.controller.set_crossfader(1.0)

        self.assertEqual(
            send.call_args_list,
            [
                unittest.mock.call(self.controller.CROSSFADER, 0),
                unittest.mock.call(self.controller.CROSSFADER, 127),
            ],
        )

    def test_crossfade_requires_valid_transition(self):
        with self.assertRaises(ValueError):
            self.controller.crossfade_transition('A', 'A')
        with self.assertRaises(ValueError):
            self.controller.crossfade_transition('A', 'B', duration=0)
        with self.assertRaises(ValueError):
            self.controller.crossfade_transition('A', 'B', steps=0)


class AdaptiveAgentValidationTests(unittest.TestCase):
    def test_rejects_unknown_learning_mode(self):
        with self.assertRaises(ValueError):
            AdaptiveAgent(learning_mode='magic')
        with self.assertRaises(TypeError):
            AdaptiveAgent(learning_mode=None)

    def test_rejects_non_mapping_state_inputs(self):
        with tempfile.TemporaryDirectory() as model_path:
            agent = AdaptiveAgent(model_path=model_path)
            with self.assertRaises(TypeError):
                agent.decide_action_heuristic([], {})
            with self.assertRaises(TypeError):
                agent.calculate_reward({}, None)

    def test_seeded_agents_are_independently_deterministic(self):
        with tempfile.TemporaryDirectory() as first_path, tempfile.TemporaryDirectory() as second_path:
            first = AdaptiveAgent(model_path=first_path, random_seed=7)
            second = AdaptiveAgent(model_path=second_path, random_seed=7)
            features = {'beat_detected': True, 'rms_db': -12.0}
            state = {'crossfader_position': 0.5}

            first_actions = [
                first.decide_action_heuristic(features, state) for _ in range(20)
            ]
            second_actions = [
                second.decide_action_heuristic(features, state) for _ in range(20)
            ]

        self.assertEqual(first_actions, second_actions)

    def test_rejects_invalid_action_class_and_reward(self):
        with tempfile.TemporaryDirectory() as model_path:
            agent = AdaptiveAgent(learning_mode='reinforcement', model_path=model_path)
            with self.assertRaises(ValueError):
                agent._map_action_class(99, {}, {})
            with self.assertRaises(ValueError):
                agent.update_q_value(np.nan)
            with self.assertRaises(TypeError):
                agent.update_q_value('good')

    def test_state_feature_contract(self):
        with tempfile.TemporaryDirectory() as model_path:
            agent = AdaptiveAgent(model_path=model_path)
            features = agent.extract_state_features(
                {'rms': 0.25, 'beat_detected': True},
                {'crossfader_position': 0.75, 'deck_a_playing': True},
            )

        self.assertEqual(features.shape, (14,))
        self.assertEqual(features.dtype, np.float32)
        self.assertEqual(features[0], 0.25)
        self.assertEqual(features[7], 1.0)
        self.assertEqual(features[8], 0.75)
        self.assertEqual(features[10], 1.0)


if __name__ == '__main__':
    unittest.main()
