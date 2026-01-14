"""
Unit tests for VirtualDJ Automation System
Tests core functionality without requiring external dependencies
"""

import sys
import os

# Test 1: Module structure
def test_module_structure():
    """Test that all required modules exist"""
    required_files = [
        'midi_controller.py',
        'audio_observer.py', 
        'adaptive_agent.py',
        'test_script.py',
        'requirements.txt',
        'README.md'
    ]
    
    print("Test 1: Checking module structure...")
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✓ {file} exists")
        else:
            print(f"  ✗ {file} missing")
            return False
    return True


# Test 2: Python syntax
def test_python_syntax():
    """Test that all Python files have valid syntax"""
    python_files = [
        'midi_controller.py',
        'audio_observer.py',
        'adaptive_agent.py',
        'test_script.py'
    ]
    
    print("\nTest 2: Checking Python syntax...")
    for file in python_files:
        try:
            with open(file, 'r') as f:
                compile(f.read(), file, 'exec')
            print(f"  ✓ {file} has valid syntax")
        except SyntaxError as e:
            print(f"  ✗ {file} has syntax error: {e}")
            return False
    return True


# Test 3: Check for required classes and functions
def test_class_definitions():
    """Test that required classes are defined"""
    print("\nTest 3: Checking class definitions...")
    
    # Check midi_controller.py
    with open('midi_controller.py', 'r') as f:
        content = f.read()
        if 'class VirtualDJMIDIController' in content:
            print("  ✓ VirtualDJMIDIController class defined")
        else:
            print("  ✗ VirtualDJMIDIController class not found")
            return False
        
        required_methods = [
            'play_pause_deck',
            'set_crossfader',
            'set_volume',
            'set_eq',
            'activate_effect',
            'load_track',
            'crossfade_transition'
        ]
        
        for method in required_methods:
            if f'def {method}' in content:
                print(f"  ✓ Method {method} defined")
            else:
                print(f"  ✗ Method {method} not found")
                return False
    
    # Check audio_observer.py
    with open('audio_observer.py', 'r') as f:
        content = f.read()
        if 'class AudioObserver' in content:
            print("  ✓ AudioObserver class defined")
        else:
            print("  ✗ AudioObserver class not found")
            return False
        
        required_methods = [
            'start_streaming',
            'stop_streaming',
            'get_features',
            'get_vdj_state',
            'estimate_mix_quality'
        ]
        
        for method in required_methods:
            if f'def {method}' in content:
                print(f"  ✓ Method {method} defined")
            else:
                print(f"  ✗ Method {method} not found")
                return False
    
    # Check adaptive_agent.py
    with open('adaptive_agent.py', 'r') as f:
        content = f.read()
        if 'class AdaptiveAgent' in content:
            print("  ✓ AdaptiveAgent class defined")
        else:
            print("  ✗ AdaptiveAgent class not found")
            return False
        
        required_methods = [
            'decide_action_heuristic',
            'decide_action_supervised',
            'decide_action_reinforcement',
            'calculate_reward',
            'update_q_value'
        ]
        
        for method in required_methods:
            if f'def {method}' in content:
                print(f"  ✓ Method {method} defined")
            else:
                print(f"  ✗ Method {method} not found")
                return False
    
    # Check test_script.py
    with open('test_script.py', 'r') as f:
        content = f.read()
        if 'class VirtualDJAutomationSystem' in content:
            print("  ✓ VirtualDJAutomationSystem class defined")
        else:
            print("  ✗ VirtualDJAutomationSystem class not found")
            return False
    
    return True


# Test 4: Check documentation
def test_documentation():
    """Test that README has required sections"""
    print("\nTest 4: Checking documentation...")
    
    with open('README.md', 'r') as f:
        content = f.read()
        
        required_sections = [
            '# VirtualDJ MIDI Automation',
            'Características',
            'Instalación',
            'Uso',
            'Modos de Aprendizaje',
            'Arquitectura'
        ]
        
        for section in required_sections:
            if section in content:
                print(f"  ✓ Section '{section}' present")
            else:
                print(f"  ✗ Section '{section}' missing")
                return False
    
    return True


# Test 5: Check requirements.txt
def test_requirements():
    """Test that requirements.txt has necessary dependencies"""
    print("\nTest 5: Checking requirements...")
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
        
        required_deps = [
            'mido',
            'python-rtmidi',
            'numpy',
            'scipy',
            'librosa',
            'sounddevice',
            'scikit-learn'
        ]
        
        for dep in required_deps:
            if dep in content:
                print(f"  ✓ Dependency {dep} listed")
            else:
                print(f"  ✗ Dependency {dep} missing")
                return False
    
    return True


# Test 6: Check MIDI mapping constants
def test_midi_mappings():
    """Test that MIDI mappings are properly defined"""
    print("\nTest 6: Checking MIDI mappings...")
    
    with open('midi_controller.py', 'r') as f:
        content = f.read()
        
        required_mappings = [
            'PLAY_PAUSE_DECK_A',
            'PLAY_PAUSE_DECK_B',
            'CUE_DECK_A',
            'CUE_DECK_B',
            'CROSSFADER',
            'VOLUME_DECK_A',
            'VOLUME_DECK_B',
            'EQ_LOW_A',
            'EQ_MID_A',
            'EQ_HIGH_A',
            'EFFECT_1',
            'EFFECT_2',
            'EFFECT_3'
        ]
        
        for mapping in required_mappings:
            if mapping in content:
                print(f"  ✓ MIDI mapping {mapping} defined")
            else:
                print(f"  ✗ MIDI mapping {mapping} missing")
                return False
    
    return True


# Test 7: Check learning modes
def test_learning_modes():
    """Test that all learning modes are implemented"""
    print("\nTest 7: Checking learning modes...")
    
    with open('adaptive_agent.py', 'r') as f:
        content = f.read()
        
        modes = ['heuristic', 'supervised', 'reinforcement']
        
        for mode in modes:
            method_name = f'decide_action_{mode}'
            if method_name in content:
                print(f"  ✓ Learning mode '{mode}' implemented")
            else:
                print(f"  ✗ Learning mode '{mode}' not implemented")
                return False
    
    return True


# Test 8: Check audio features
def test_audio_features():
    """Test that all audio features are calculated"""
    print("\nTest 8: Checking audio features...")
    
    with open('audio_observer.py', 'r') as f:
        content = f.read()
        
        features = [
            'rms',
            'rms_db',
            'beat_detected',
            'bpm',
            'spectral_centroid',
            'spectral_rolloff',
            'zero_crossing_rate',
            'energy'
        ]
        
        for feature in features:
            if f"'{feature}'" in content:
                print(f"  ✓ Audio feature '{feature}' tracked")
            else:
                print(f"  ✗ Audio feature '{feature}' not tracked")
                return False
    
    return True


def test_model_persistence():
    """Test that reinforcement Q-table persistence (save/load) works."""
    print("\nTest 9: Checking model persistence (reinforcement Q-table)...")
    import shutil
    import os
    import numpy as np

    models_dir = 'models_test'

    # Clean up any previous test artifacts
    if os.path.exists(models_dir):
        shutil.rmtree(models_dir)

    try:
        # Create an agent in reinforcement mode and populate q_table
        from adaptive_agent import AdaptiveAgent
        agent = AdaptiveAgent(learning_mode='reinforcement', model_path=models_dir)
        agent.q_table['test_state'] = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        agent.save()

        # Load a new agent and verify q_table persisted
        agent2 = AdaptiveAgent(learning_mode='reinforcement', model_path=models_dir)
        if 'test_state' in agent2.q_table:
            loaded = np.array(agent2.q_table['test_state'])
            expected = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
            if np.allclose(loaded, expected):
                print("  ✓ Q-table persisted and loaded correctly")
                result = True
            else:
                print("  ✗ Q-table values differ after load")
                print(f"    expected: {expected}, got: {loaded}")
                result = False
        else:
            print("  ✗ Q-table key 'test_state' not found after load")
            result = False

    except Exception as e:
        print(f"  ✗ Exception during persistence test: {e}")
        result = False

    finally:
        # Clean up
        if os.path.exists(models_dir):
            shutil.rmtree(models_dir)

    return result


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 60)
    print("VirtualDJ Automation System - Unit Tests")
    print("=" * 60)
    
    tests = [
        test_module_structure,
        test_python_syntax,
        test_class_definitions,
        test_documentation,
        test_requirements,
        test_midi_mappings,
        test_learning_modes,
        test_audio_features
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
