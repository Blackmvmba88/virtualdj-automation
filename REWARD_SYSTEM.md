# Sistema de Recompensas del Agente de Refuerzo

## Descripción General

El sistema de recompensas del agente de aprendizaje por refuerzo (Q-Learning) evalúa la calidad de la mezcla en tiempo real mediante múltiples componentes que capturan diferentes aspectos del DJing profesional.

## Fórmula de Recompensa Total

```
R_total = w_rms × R_mix + w_bpm × R_bpm + w_energy × R_energy + 
          w_xfade × R_xfade + w_spectral × R_spectral - P_clipping - P_silence
```

Donde todos los términos están normalizados y los pesos son ajustables.

## Componentes de Recompensa

### 1. R_mix - Nivel RMS y Calidad (w_rms = 0.25)

**Objetivo**: Mantener el nivel de audio en un "sweet spot" óptimo.

**Cálculo**:
- Target: -16 dB ± 8 dB (rango óptimo)
- Recompensa máxima (1.0) cuando está dentro del rango
- Penalización por desviación fuera del rango
- Penalización fuerte (-0.7) si RMS > -1 dB (casi clipping)
- Penalización (-0.5) si RMS < -40 dB (demasiado bajo)

**Combinación**:
```
R_mix = 0.5 × R_rms + 0.5 × R_quality
```

### 2. R_bpm - Match de BPM (w_bpm = 0.20)

**Objetivo**: Mantener los BPMs de ambos decks sincronizados.

**Cálculo**:
- Recompensa máxima (1.0) cuando BPMs son idénticos
- Penalización lineal hasta diferencia de 6 BPM (max_diff)
- Recompensa 0.0 para diferencias ≥ 6 BPM
- Si algún deck está detenido (BPM = 0), recompensa = 0.0

**Ejemplo**:
- BPM A = 128, BPM B = 128 → R = 1.0
- BPM A = 128, BPM B = 130 → R = 0.67
- BPM A = 128, BPM B = 135 → R = 0.0

### 3. R_energy - Flujo de Energía (w_energy = 0.15)

**Objetivo**: Evitar cambios bruscos de energía entre pasos.

**Cálculo**:
- Compara energía actual con energía previa
- Recompensa máxima (1.0) para cambios mínimos
- Penalización lineal hasta max_delta = 0.4
- Recompensa neutral (0.5) al inicio (sin energía previa)

**Ejemplo**:
- Energy 0.5 → 0.5 → R = 1.0 (sin cambio)
- Energy 0.5 → 0.6 → R = 0.75 (cambio pequeño)
- Energy 0.5 → 0.9 → R = 0.0 (cambio grande)

### 4. R_xfade - Comportamiento del Crossfader (w_xfade = 0.20)

**Objetivo**: Recompensar transiciones coherentes y beat-aligned.

**Cálculo**:
- Sin movimiento (< min_move = 0.02) → R = 0.0 (neutral)
- Movimiento moderado (0.02 - 0.3) → R proporcional
- Movimiento excesivo (> max_move = 0.3) → R = -0.5 (penalización)
- **Bonus (+0.3)** si el movimiento coincide con un beat

**Ejemplo**:
- XF 0.5 → 0.5 → R = 0.0 (sin movimiento)
- XF 0.5 → 0.6, no beat → R = 0.33
- XF 0.5 → 0.6, en beat → R = 0.63 (con bonus)
- XF 0.5 → 0.9 → R = -0.5 (cambio muy brusco)

### 5. R_spectral - Balance Espectral (w_spectral = 0.20)

**Objetivo**: Mantener un balance equilibrado de frecuencias.

**Cálculo**:
- Evalúa tres bandas: bajos (20-250 Hz), medios (250-2000 Hz), agudos (2000-8000 Hz)
- Recompensa máxima cuando cada banda tiene balance cercano a 0.0
- Penalización por desbalances > max_diff = 0.8

**Bandas**:
```
low_balance: -1.0 (solo graves) ← → +1.0 (sin graves)
mid_balance: -1.0 (solo medios) ← → +1.0 (sin medios)
high_balance: -1.0 (solo agudos) ← → +1.0 (sin agudos)
```

**Recompensa promedio** de las tres bandas:
```
R_spectral = (R_low + R_mid + R_high) / 3.0
```

## Penalizaciones Duras

### P_silence - Silencio

- Activación: RMS < -55 dB
- Penalización: -0.7
- **No** se aplica durante transiciones naturales

### P_clipping - Clipping

- Activación: RMS > -3 dB
- Penalización: -0.5
- Indica que la señal está saturando

## Pesos Configurables

Los pesos por defecto están balanceados para mezclas generales:

```python
reward_weights = {
    'w_rms': 0.25,      # Calidad de nivel
    'w_bpm': 0.20,      # Sincronización
    'w_energy': 0.15,   # Fluidez
    'w_xfade': 0.20,    # Transiciones
    'w_spectral': 0.20  # Balance tonal
}
```

**Suma total**: 1.0

### Ajuste de Pesos según Estilo

**Para mezclas suaves (House, Deep House)**:
```python
reward_weights = {
    'w_rms': 0.20,
    'w_bpm': 0.25,      # Más énfasis en sync
    'w_energy': 0.25,   # Más énfasis en fluidez
    'w_xfade': 0.15,
    'w_spectral': 0.15
}
```

**Para mezclas energéticas (Techno, Trance)**:
```python
reward_weights = {
    'w_rms': 0.30,      # Más énfasis en nivel
    'w_bpm': 0.20,
    'w_energy': 0.10,
    'w_xfade': 0.25,    # Más énfasis en transiciones
    'w_spectral': 0.15
}
```

**Para mezclas técnicas (Drum & Bass, Hip Hop)**:
```python
reward_weights = {
    'w_rms': 0.25,
    'w_bpm': 0.15,
    'w_energy': 0.15,
    'w_xfade': 0.20,
    'w_spectral': 0.25  # Más énfasis en balance espectral
}
```

## Uso Programático

### Obtener Breakdown de Recompensa

```python
from adaptive_agent import AdaptiveAgent

agent = AdaptiveAgent(learning_mode='reinforcement')

# Obtener breakdown detallado
breakdown = agent.get_reward_breakdown(audio_features, vdj_state)

# Acceder a componentes
print(f"Sub-rewards: {breakdown['sub_rewards']}")
print(f"Weighted contributions: {breakdown['weighted_contributions']}")
print(f"Penalties: {breakdown['penalties']}")
print(f"Total: {breakdown['total']:.3f}")
```

### Ajustar Pesos

```python
# Modificar pesos para tu estilo
agent.reward_weights = {
    'w_rms': 0.30,
    'w_bpm': 0.25,
    'w_energy': 0.20,
    'w_xfade': 0.15,
    'w_spectral': 0.10
}
```

### Logging de Recompensas

```python
# Durante el loop de automatización
reward = agent.calculate_reward(audio_features, vdj_state)
breakdown = agent.get_reward_breakdown(audio_features, vdj_state)

# Log para análisis
print(f"Reward: {reward:.3f}")
for component, value in breakdown['weighted_contributions'].items():
    print(f"  {component}: {value:+.3f}")
```

## Análisis y Debugging

### Scripts de Prueba Incluidos

1. **test_reward_system.py**: Prueba todos los componentes individuales
2. **test_reward_breakdown.py**: Demo visual de cómo funciona el sistema
3. **test_integration.py**: Prueba ciclo completo del agente

### Ejecutar Demos

```bash
# Demo completo con visualización
python test_reward_breakdown.py

# Test unitario de componentes
python test_reward_system.py
```

### Interpretar Resultados

**Reward Total > 0.7**: Mezcla excelente
- Todos los componentes están bien optimizados
- Nivel apropiado, BPMs sincronizados, transiciones suaves

**Reward Total 0.3 - 0.7**: Mezcla aceptable
- Algunos componentes necesitan mejora
- Revisa breakdown para identificar debilidades

**Reward Total < 0.3**: Mezcla pobre
- Múltiples problemas simultáneos
- Posible clipping, desincronización o silencio

**Reward Total < 0**: Mezcla muy pobre
- Penalizaciones activadas (clipping o silencio)
- Requiere corrección inmediata

## Mejores Prácticas

### 1. Monitoreo Continuo

```python
# Guardar histórico de recompensas
rewards_history = []
for iteration in range(num_iterations):
    reward = agent.calculate_reward(audio_features, vdj_state)
    rewards_history.append(reward)
    agent.update_q_value(reward)

# Analizar tendencia
import numpy as np
avg_reward = np.mean(rewards_history[-100:])  # Últimas 100 iteraciones
print(f"Average reward (recent): {avg_reward:.3f}")
```

### 2. Ajuste Iterativo

1. Ejecutar sesión de prueba con pesos por defecto
2. Revisar breakdown para identificar componentes débiles
3. Ajustar pesos incrementalmente (±0.05)
4. Re-evaluar y repetir

### 3. Validación de Comportamiento

```python
# Verificar que el agente está aprendiendo
stats = agent.get_statistics()
print(f"Q-table size: {stats['q_table_size']}")
print(f"Exploration rate: {stats['exploration_rate']:.3f}")
print(f"Reward trend: {stats['reward_trend']:.3f}")

# Reward trend > 0 indica que el agente está mejorando
```

## Extensión del Sistema

### Agregar Nuevo Componente de Recompensa

```python
def _reward_custom(self, feature_value: float, threshold: float) -> float:
    """Tu nuevo componente de recompensa"""
    if feature_value > threshold:
        return 1.0
    return feature_value / threshold

# En calculate_reward(), agregar:
r_custom = self._reward_custom(audio_features.get('custom_feature', 0.0), 0.5)

# Agregar peso
self.reward_weights['w_custom'] = 0.1

# Ajustar otros pesos para mantener suma = 1.0
```

## Referencias

- Paper original de Q-Learning: Watkins & Dayan (1992)
- Reward shaping: Ng, Harada & Russell (1999)
- DJ mixing theory: Various DJ education resources

## Soporte

Para preguntas o issues con el sistema de recompensas, por favor abrir un issue en GitHub con:
- Configuración de pesos utilizada
- Logs de rewards y breakdown
- Descripción del comportamiento esperado vs observado
