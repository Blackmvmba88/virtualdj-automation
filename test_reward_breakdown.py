"""
Demo script showing the reward breakdown functionality.
This helps understand how each component contributes to the total reward.
"""

from adaptive_agent import AdaptiveAgent


def demo_reward_breakdown():
    """Demonstrate detailed reward breakdown for analysis"""
    print("=" * 70)
    print("Reward System Breakdown Demo")
    print("=" * 70)
    
    agent = AdaptiveAgent(learning_mode='reinforcement', random_seed=42)
    
    # Scenario 1: Excellent mixing
    print("\n" + "=" * 70)
    print("Scenario 1: Excellent Mixing")
    print("=" * 70)
    
    audio_features = {
        'rms_db': -14.0,
        'energy': 0.6,
        'bpm': 128.0,
        'beat_detected': True,
        'low_band_balance': 0.05,
        'mid_band_balance': -0.02,
        'high_band_balance': 0.03,
        'quality_score': 0.90
    }
    vdj_state = {
        'crossfader_position': 0.5,
        'deck_a_bpm': 128.0,
        'deck_b_bpm': 128.5
    }
    
    breakdown = agent.get_reward_breakdown(audio_features, vdj_state)
    
    print("\nAudio State:")
    print(f"  RMS: {audio_features['rms_db']:.1f} dB")
    print(f"  Energy: {audio_features['energy']:.2f}")
    print(f"  BPM: {audio_features['bpm']:.0f}")
    print(f"  Beat Detected: {audio_features['beat_detected']}")
    print(f"  Quality Score: {audio_features['quality_score']:.2f}")
    
    print("\nSub-Rewards (0.0 - 1.0 scale):")
    for key, value in breakdown['sub_rewards'].items():
        bar = "█" * int(value * 20) if value > 0 else ""
        print(f"  {key:20s}: {value:6.3f} {bar}")
    
    print("\nWeighted Contributions to Total:")
    for key, value in breakdown['weighted_contributions'].items():
        bar = "█" * int(abs(value) * 30) if value != 0 else ""
        sign = "+" if value >= 0 else ""
        print(f"  {key:20s}: {sign}{value:6.3f} {bar}")
    
    print("\nPenalties:")
    for key, value in breakdown['penalties'].items():
        if value != 0:
            print(f"  {key:20s}: {value:6.3f}")
    
    print(f"\nTotal Reward: {breakdown['total']:.3f}")
    print(f"  (Before penalties: {breakdown['total_before_penalties']:.3f})")
    
    # Scenario 2: Poor mixing - clipping
    print("\n" + "=" * 70)
    print("Scenario 2: Poor Mixing - Clipping")
    print("=" * 70)
    
    audio_features = {
        'rms_db': -1.5,  # Clipping!
        'energy': 0.95,
        'bpm': 130.0,
        'beat_detected': False,
        'low_band_balance': 0.8,  # Bass heavy
        'mid_band_balance': -0.4,
        'high_band_balance': -0.3,
        'quality_score': 0.25
    }
    vdj_state = {
        'crossfader_position': 0.5,
        'deck_a_bpm': 128.0,
        'deck_b_bpm': 136.0  # BPM mismatch
    }
    
    breakdown = agent.get_reward_breakdown(audio_features, vdj_state)
    
    print("\nAudio State:")
    print(f"  RMS: {audio_features['rms_db']:.1f} dB ⚠️  CLIPPING!")
    print(f"  Energy: {audio_features['energy']:.2f}")
    print(f"  BPM Mismatch: {vdj_state['deck_a_bpm']:.0f} vs {vdj_state['deck_b_bpm']:.0f}")
    print(f"  Beat Detected: {audio_features['beat_detected']}")
    print(f"  Quality Score: {audio_features['quality_score']:.2f}")
    
    print("\nSub-Rewards (0.0 - 1.0 scale):")
    for key, value in breakdown['sub_rewards'].items():
        if value < 0:
            bar = "▓" * int(abs(value) * 20)
            print(f"  {key:20s}: {value:6.3f} {bar} (negative)")
        else:
            bar = "█" * int(value * 20)
            print(f"  {key:20s}: {value:6.3f} {bar}")
    
    print("\nWeighted Contributions to Total:")
    for key, value in breakdown['weighted_contributions'].items():
        if value < 0:
            bar = "▓" * int(abs(value) * 30)
            print(f"  {key:20s}: {value:6.3f} {bar} (penalty)")
        else:
            bar = "█" * int(value * 30)
            print(f"  {key:20s}: +{value:6.3f} {bar}")
    
    print("\nPenalties:")
    for key, value in breakdown['penalties'].items():
        if value != 0:
            print(f"  {key:20s}: {value:6.3f} ⚠️")
    
    print(f"\nTotal Reward: {breakdown['total']:.3f} ❌ POOR")
    print(f"  (Before penalties: {breakdown['total_before_penalties']:.3f})")
    
    # Scenario 3: Beat-synced transition
    print("\n" + "=" * 70)
    print("Scenario 3: Beat-Synced Crossfader Transition")
    print("=" * 70)
    
    # First state
    audio_features = {
        'rms_db': -13.0,
        'energy': 0.55,
        'bpm': 128.0,
        'beat_detected': True,
        'low_band_balance': 0.0,
        'mid_band_balance': 0.0,
        'high_band_balance': 0.0,
        'quality_score': 0.80
    }
    vdj_state = {
        'crossfader_position': 0.3,
        'deck_a_bpm': 128.0,
        'deck_b_bpm': 128.0
    }
    
    breakdown1 = agent.get_reward_breakdown(audio_features, vdj_state)
    
    # Update agent state
    agent.calculate_reward(audio_features, vdj_state)
    
    # Second state - crossfader moved on beat
    vdj_state['crossfader_position'] = 0.5
    breakdown2 = agent.get_reward_breakdown(audio_features, vdj_state)
    
    print("\nBefore Crossfader Movement:")
    print(f"  Crossfader: {0.3:.1f}")
    print(f"  Total Reward: {breakdown1['total']:.3f}")
    print(f"  Crossfader Sub-Reward: {breakdown1['sub_rewards']['crossfader']:.3f}")
    
    print("\nAfter Crossfader Movement (on beat):")
    print(f"  Crossfader: {0.5:.1f}")
    print(f"  Total Reward: {breakdown2['total']:.3f}")
    print(f"  Crossfader Sub-Reward: {breakdown2['sub_rewards']['crossfader']:.3f}")
    
    improvement = breakdown2['total'] - breakdown1['total']
    print(f"\nReward Improvement: {improvement:+.3f} ✓")
    
    print("\n" + "=" * 70)
    print("Demo Complete!")
    print("=" * 70)
    print("\nKey Takeaways:")
    print("  • The reward system evaluates multiple aspects of mixing quality")
    print("  • Each sub-reward contributes according to its weight")
    print("  • Good practices (beat-synced transitions, BPM matching) are rewarded")
    print("  • Bad practices (clipping, silence, imbalance) are penalized")
    print("  • The breakdown helps understand and tune the agent's behavior")


if __name__ == "__main__":
    demo_reward_breakdown()
