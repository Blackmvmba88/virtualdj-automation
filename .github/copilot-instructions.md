# Copilot Instructions — VirtualDJ Automation ✅

Purpose: Quick, actionable guidance to get an AI coding agent productive in this repo.

## Big picture
- Three main components:
  - `midi_controller.py` — sends MIDI commands to VirtualDJ (actions).
  - `audio_observer.py` — captures audio, extracts features (RMS, BPM, beat detection, spectral features) and _simulates_ VirtualDJ state (`vdj_state`). Uses a background thread + sounddevice callback: take care with locks and non-blocking work.
  - `adaptive_agent.py` — decision logic in three modes: **heuristic**, **supervised**, **reinforcement** (Q-learning). Agent consumes observer features and issues action dicts for the controller.

## Key files / entry points
- `README.md` — primary usage and setup; follow it for platform setup (virtual MIDI port, audio device). Examples for programmatic usage and demos live here.
- `test_script.py` — `VirtualDJAutomationSystem` integrates all components and contains demos. Use `python test_script.py` for interactive runs and `system.run_automation_loop()` for programmatic sessions.
- `test_unit.py` — lightweight file-based tests used in CI / local checks. Tests look for specific file names, class/method names, and literal strings in source docs. Avoid renaming public classes/methods without updating tests.

## Important APIs / contracts (preserve these)
- AdaptiveAgent: constructor `AdaptiveAgent(learning_mode='heuristic', model_path=None, random_seed=None)`. Key methods:
  - `decide_action_heuristic(audio_features, vdj_state)`
  - `decide_action_supervised(audio_features, vdj_state)`
  - `decide_action_reinforcement(audio_features, vdj_state)`
  - `calculate_reward(...)`, `update_q_value(...)`, `save()`, `reset()`
- Action dict format returned by agents (expected keys):
  - `crossfade_adjust`, `volume_adjust_a`, `volume_adjust_b`, `eq_adjust` (dict), `effect_trigger` (int|None), `transition_now` (bool)
  - Example: `{ 'crossfade_adjust': 0.1, 'eq_adjust': {'high': -0.1}, 'effect_trigger': 1 }`
- AudioObserver: `start_streaming()`, `stop_streaming()`, `get_features()` (returns dict with `rms`, `rms_db`, `energy`, `bpm`, `beat_detected`, `spectral_centroid`, `spectral_rolloff`, `zero_crossing_rate`), `get_vdj_state()`, `update_vdj_state()` — **thread-safety**: uses `self.lock` for shared buffers.
- VirtualDJMIDIController: `play_pause_deck`, `set_crossfader(position)`, `set_volume(deck, volume)`, `set_eq(deck, band, value)`, `activate_effect(effect_num, value)`, `crossfade_transition(from, to, duration, steps)`.
- MIDI mapping constants (do not change without updating docs/tests): `CROSSFADER = 0x07`, `VOLUME_DECK_A = 0x08`, etc. See `midi_controller.py` table.

## Project-specific conventions & patterns
- Logging is print-based; prefer minimal changes so tests/examples remain stable.
- Audio callback must remain non-blocking — heavy work belongs in the background processing thread. Use the existing `deque` + `lock` pattern (`audio_observer.py` `_audio_callback` / `_processing_loop`).
- Beat detection is energy-based and uses `beat_history` timestamps — small timing/threshold changes can dramatically affect agent behavior.
- Tests in `test_unit.py` look for exact class/method names and README headings; avoid renames without test updates.
- Models and artifacts live in `models/`: `classifier.pkl`, `scaler.pkl`, `q_table.pkl`. Do not commit large binaries; add small training fixtures when needed.
- Deterministic runs: pass `random_seed` to `AdaptiveAgent` (numpy seeded) for reproducible tests/demos.

## Workflows / commands you should rely on
- Install deps: `pip install -r requirements.txt` (on macOS ensure PortAudio is installed; e.g., `brew install portaudio` if sounddevice raises errors).
- Run unit checks: `python test_unit.py` (script prints pass/fail and exits accordingly).
- Run demos/integration: `python test_script.py` (interactive menu) or import `VirtualDJAutomationSystem` and call `run_automation_loop()` programmatically.

## Integration notes / cautions for code changes
- Audio callbacks must remain fast and non-blocking. Use the existing `deque` + `lock` pattern for audio buffering and move heavy processing to the background thread.
- Beat detection and BPM estimation are energy-based and rely on `beat_history`/timestamps — altering timing or thresholds may significantly change agent behavior.
- When changing action keys or feature vector ordering, update `extract_state_features()` and all mapping functions (`_map_action_class`, `_map_action_index`) and tests accordingly.
- If adding heavy deps (e.g., extra ML libs), update `requirements.txt` and `README.md` usage notes (e.g., platform-specific installs like PortAudio for `sounddevice`).

## Testing guidance for PRs
- Make sure `python test_unit.py` passes locally. Tests are intentionally simple and will fail if names/strings used by tests are changed.
- Add a demo snippet in `test_script.py` when introducing new end-to-end behavior and document it in `README.md`.
- Do not commit large model binaries to the repo unless necessary; prefer providing model training code and saving to `models/` at runtime.

## Example snippets (use these when writing code or tests)
- Feature vector order (from `extract_state_features`): `rms`, `rms_db`, `energy`, `bpm`, `spectral_centroid`, `spectral_rolloff`, `zero_crossing_rate`, `beat_detected`, `crossfader_position`, `master_volume`, `deck_a_playing`, `deck_b_playing`, `deck_a_bpm`, `deck_b_bpm`.
- Crossfader MIDI mapping example: `CROSSFADER = 0x07` -> `set_crossfader(position)` maps `position` (0.0-1.0) to 0-127 MIDI value.

---
If anything is unclear or you want extra targeted examples / small tests added to the repo, tell me which section to expand and I’ll iterate. 🙏
