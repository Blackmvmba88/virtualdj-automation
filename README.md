# VirtualDJ MIDI Automation System

Sistema completo para automatizar VirtualDJ mediante control MIDI con observación de audio en tiempo real y aprendizaje adaptativo.

## 📋 Descripción

Este sistema implementa una solución completa para controlar VirtualDJ de forma automática mediante tres componentes principales:

1. **Controlador MIDI** (`midi_controller.py`): Envía comandos MIDI a VirtualDJ para controlar reproducción, mezclas, efectos y más.
2. **Observador de Audio** (`audio_observer.py`): Captura y analiza audio en tiempo real, extrayendo características como RMS, energía, BPM y detección de beats.
3. **Agente Adaptativo** (`adaptive_agent.py`): Aprende y optimiza las mezclas mediante heurísticas, aprendizaje supervisado y aprendizaje por refuerzo.

## 🚀 Características

### Controlador MIDI
- **Comandos de reproducción**: Play/Pause, Cue, Sync para ambos decks
- **Control de mezcla**: Crossfader con transiciones suaves
- **Control de volumen**: Ajuste independiente por deck
- **Ecualizador**: Control de bajos, medios y agudos (3 bandas)
- **Efectos**: Activación de hasta 3 efectos con control de intensidad
- **Carga de tracks**: Selección de pistas desde playlist

### Observador de Audio
- **Captura en tiempo real**: Stream de audio con buffer circular
- **Análisis de características**:
  - RMS (Root Mean Square) y nivel en dB
  - Energía de la señal
  - Detección de beats
  - Estimación de BPM
  - Centroide espectral
  - Rolloff espectral
  - Zero-crossing rate
  - **Balance espectral por bandas** (bajos, medios, agudos)
- **Estimación de calidad**: Score de calidad de mezcla en tiempo real (0.0-1.0)
- **Lectura de estado**: Integración con estado de VirtualDJ

### Agente Adaptativo
- **Modo Heurístico**: Reglas basadas en experiencia musical
  - Transiciones suaves en beats
  - Mantenimiento de niveles óptimos de RMS
  - Ajustes de EQ según contenido espectral
  - Aplicación inteligente de efectos
- **Modo Aprendizaje Supervisado**: 
  - Clasificación de acciones mediante Random Forest
  - Escalado de características
  - Entrenamiento con datos históricos
- **Modo Aprendizaje por Refuerzo** (Q-Learning):
  - Exploración vs explotación (epsilon-greedy)
  - Actualización de valores Q
  - Buffer de experiencia
  - Decaimiento de exploración
  - **Sistema de Recompensas Optimizado**:
    - RMS Level (sweet spot): Mantiene niveles óptimos de audio
    - BPM Matching: Sincronización entre decks
    - Energy Flow: Transiciones suaves de energía
    - Crossfader Behavior: Movimientos coherentes y beat-aligned
    - Spectral Balance: Balance de frecuencias (bajos, medios, agudos)
    - Penalizaciones por clipping y silencio
    - Pesos configurables para cada componente

## 📦 Instalación

### Requisitos Previos
- Python 3.8 o superior
- loopMIDI (Windows) o virtual MIDI port (Linux/Mac)
- VirtualDJ configurado para recibir MIDI
- Interfaz de audio para captura

### Instalación de Dependencias

```bash
# Clonar el repositorio
git clone https://github.com/Blackmvmba88/virtualdj-automation.git
cd virtualdj-automation

# Instalar dependencias
pip install -r requirements.txt
```

### Dependencias Principales
- `mido`: Comunicación MIDI
- `python-rtmidi`: Backend MIDI en tiempo real
- `numpy`: Procesamiento numérico
- `scipy`: Procesamiento de señales
- `librosa`: Análisis de audio
- `sounddevice`: Captura de audio
- `scikit-learn`: Aprendizaje automático
- `tensorflow`: Deep learning (opcional para extensiones futuras)

## 🎮 Configuración

### 1. Configurar loopMIDI (Windows)

1. Descargar e instalar [loopMIDI](https://www.tobias-erichsen.de/software/loopmidi.html)
2. Crear un puerto MIDI virtual (ej: "VirtualDJ Automation")
3. Iniciar el puerto

### 2. Configurar VirtualDJ

1. Abrir VirtualDJ
2. Ir a Settings → MIDI
3. Agregar el puerto MIDI virtual creado
4. Mapear los controles según la configuración en `midi_controller.py`

### 3. Configurar Captura de Audio

```python
# Listar dispositivos de audio disponibles
import sounddevice as sd
print(sd.query_devices())

# Usar el índice del dispositivo deseado en AudioObserver
observer = AudioObserver(device=INDEX)
```

## 🎯 Uso

### Modo Básico - Script de Prueba

```bash
python test_script.py
```

El script de prueba ofrece un menú interactivo con las siguientes opciones:

1. **Demo: Comandos MIDI Básicos** - Prueba individual de cada comando
2. **Demo: Análisis de Audio** - Captura y análisis de características
3. **Demo: Modos de Aprendizaje** - Comparación de diferentes estrategias
4. **Ejecutar Sistema Completo** - Automatización por 30 segundos
5. **Ejecutar con Duración Personalizada** - Control total del tiempo

### Uso Programático

#### Ejemplo 1: Control MIDI Simple

```python
from midi_controller import VirtualDJMIDIController
import time

# Inicializar controlador
controller = VirtualDJMIDIController()

# Reproducir deck A
controller.play_pause_deck('A')
time.sleep(2)

# Transición suave a deck B
controller.crossfade_transition('A', 'B', duration=4.0)

# Aplicar efecto
controller.activate_effect(1, intensity=0.7)

# Cerrar conexión
controller.close()
```

#### Ejemplo 2: Análisis de Audio

```python
from audio_observer import AudioObserver
import time

# Inicializar observador
observer = AudioObserver(sample_rate=44100)

# Iniciar captura
observer.start_streaming()

# Capturar por 5 segundos
for i in range(5):
    time.sleep(1)
    features = observer.get_features()
    print(f"RMS: {features['rms_db']:.1f} dB, BPM: {features['bpm']:.1f}")

# Análisis de buffer
analysis = observer.analyze_buffer(duration=2.0)
print(f"Tempo estimado: {analysis['estimated_tempo']:.1f} BPM")

# Detener captura
observer.stop_streaming()
```

#### Ejemplo 3: Agente Adaptativo

```python
from adaptive_agent import AdaptiveAgent
from audio_observer import AudioObserver
from midi_controller import VirtualDJMIDIController

# Inicializar componentes
agent = AdaptiveAgent(learning_mode='reinforcement')
observer = AudioObserver()
controller = VirtualDJMIDIController()

# Iniciar observación
observer.start_streaming()

# Loop de automatización
for iteration in range(100):
    # Obtener estado actual
    audio_features = observer.get_features()
    vdj_state = observer.get_vdj_state()
    
    # Agente decide acción
    actions = agent.decide_action_reinforcement(audio_features, vdj_state)
    
    # Ejecutar acciones
    if actions['crossfade_adjust'] != 0.0:
        current_pos = vdj_state['crossfader_position']
        new_pos = current_pos + actions['crossfade_adjust']
        controller.set_crossfader(new_pos)
    
    # Calcular recompensa y aprender
    reward = agent.calculate_reward(audio_features, vdj_state)
    agent.update_q_value(reward)
    
    time.sleep(1.0)

# Guardar modelos aprendidos
agent.save()
```

#### Ejemplo 4: Sistema Completo

```python
from test_script import VirtualDJAutomationSystem

# Crear sistema con aprendizaje por refuerzo
system = VirtualDJAutomationSystem(
    midi_port="VirtualDJ Automation",
    learning_mode='reinforcement'
)

# Ejecutar por 60 segundos con actualizaciones cada 2 segundos
system.run_automation_loop(duration=60.0, update_interval=2.0)
```

## 🧠 Modos de Aprendizaje

### Heurístico (Reglas)
- Ideal para comenzar
- Comportamiento predecible
- Basado en mejores prácticas de DJing
- Sin necesidad de entrenamiento

**Cuándo usar**: Para resultados inmediatos y consistentes.

### Supervisado
- Requiere datos de entrenamiento etiquetados
- Aprende de ejemplos de mezclas exitosas
- Modelo Random Forest para clasificación
- Guardado/carga de modelos

**Cuándo usar**: Cuando tienes grabaciones de mezclas de referencia.

### Refuerzo (Q-Learning)
- Aprende por ensayo y error
- Optimiza basado en recompensas
- Explora nuevas estrategias
- Mejora con el tiempo

**Cuándo usar**: Para optimización continua y adaptación a diferentes estilos.

#### Sistema de Recompensas

El modo de refuerzo utiliza un sistema de recompensas multi-componente que evalúa:

**Fórmula de Recompensa Total:**
```
R_total = w_rms × R_mix + w_bpm × R_bpm + w_energy × R_energy + 
          w_xfade × R_xfade + w_spectral × R_spectral - P_clipping - P_silence
```

**Componentes de Recompensa:**

1. **R_mix (RMS + Calidad)**: Evalúa nivel de audio en "sweet spot" (-16 dB ± 8 dB)
   - Penaliza clipping (> -1 dB) y niveles muy bajos (< -40 dB)
   - Combina con score de calidad general

2. **R_bpm**: Recompensa por matching de BPM entre decks
   - Máximo reward cuando BPMs coinciden
   - Penaliza diferencias > 6 BPM

3. **R_energy**: Evalúa fluidez de transiciones energéticas
   - Recompensa cambios suaves (< 0.4)
   - Penaliza saltos abruptos de energía

4. **R_xfade**: Evalúa comportamiento del crossfader
   - Recompensa movimientos coherentes (0.02 - 0.3)
   - Bonus por transiciones en beat
   - Penaliza micro-movimientos o cambios bruscos

5. **R_spectral**: Balance de frecuencias (bajos, medios, agudos)
   - Recompensa distribución equilibrada
   - Penaliza exceso de bajos o desbalances extremos

**Pesos por Defecto:**
- w_rms: 0.25
- w_bpm: 0.20
- w_energy: 0.15
- w_xfade: 0.20
- w_spectral: 0.20

**Penalizaciones:**
- Silencio (< -55 dB): -0.7
- Clipping (> -3 dB): -0.5

Los pesos son ajustables según el estilo de mezcla deseado.

## 📊 Métricas y Análisis

El sistema proporciona métricas detalladas:

### Audio
- **RMS**: Nivel de amplitud (-80 a 0 dB)
- **Energía**: Potencia de la señal
- **BPM**: Tempo detectado
- **Calidad**: Score 0.0-1.0 basado en múltiples factores

### Aprendizaje
- **Recompensa promedio**: Rendimiento del agente
- **Tasa de exploración**: Balance exploración/explotación
- **Tamaño Q-table**: Estados aprendidos
- **Tendencia de recompensa**: Mejora reciente

## 🛠️ Mapeo MIDI

El controlador utiliza los siguientes mapeos MIDI por defecto:

| Control | Tipo | CC/Note | Descripción |
|---------|------|---------|-------------|
| Play/Pause Deck A | Note | 0x01 | Toggle reproducción |
| Play/Pause Deck B | Note | 0x02 | Toggle reproducción |
| Cue Deck A | Note | 0x03 | Punto Cue |
| Cue Deck B | Note | 0x04 | Punto Cue |
| Sync Deck A | Note | 0x05 | Sincronizar BPM |
| Sync Deck B | Note | 0x06 | Sincronizar BPM |
| Crossfader | CC | 0x07 | Posición 0-127 |
| Volume Deck A | CC | 0x08 | Volumen 0-127 |
| Volume Deck B | CC | 0x09 | Volumen 0-127 |
| EQ Low A | CC | 0x0A | Bajos Deck A |
| EQ Mid A | CC | 0x0B | Medios Deck A |
| EQ High A | CC | 0x0C | Agudos Deck A |
| EQ Low B | CC | 0x0D | Bajos Deck B |
| EQ Mid B | CC | 0x0E | Medios Deck B |
| EQ High B | CC | 0x0F | Agudos Deck B |
| Effect 1 | CC | 0x10 | Efecto 1 |
| Effect 2 | CC | 0x11 | Efecto 2 |
| Effect 3 | CC | 0x12 | Efecto 3 |
| Load Track A | CC | 0x20 | Cargar pista Deck A |
| Load Track B | CC | 0x21 | Cargar pista Deck B |

## 🔧 Solución de Problemas

### Error: "No MIDI output ports available"
- Verificar que loopMIDI esté ejecutándose
- Reiniciar el puerto MIDI virtual
- Verificar permisos de acceso

### Error: "Audio stream status"
- Verificar configuración de interfaz de audio
- Probar con otro dispositivo de entrada
- Ajustar buffer size y sample rate

### Las transiciones no son suaves
- Aumentar `steps` en `crossfade_transition()`
- Ajustar `optimal_crossfade_duration` en el agente
- Verificar sincronización de BPM

### El agente no aprende correctamente
- Aumentar tiempo de entrenamiento
- Ajustar learning_rate y discount_factor
- Verificar que las recompensas sean apropiadas

## 📁 Estructura del Proyecto

```
virtualdj-automation/
├── midi_controller.py           # Control MIDI de VirtualDJ
├── audio_observer.py             # Captura y análisis de audio
├── adaptive_agent.py             # Agente de aprendizaje adaptativo
├── test_script.py               # Script de prueba y demostración
├── test_unit.py                 # Tests unitarios
│
├── 🌈 Módulos Psicodélicos:
├── dj_persona.py                # Sistema de personalidades DJ
├── introspective_metrics.py     # Métricas psicológicas del agente
├── semantic_analyzer.py         # Análisis semántico musical
├── psychedelic_visualizer.py    # Motor de visualización OpenGL
├── machine_spirit.py            # Generador de poesía
├── psychedelic_demo.py          # Demo completo psicodélico
│
├── requirements.txt             # Dependencias Python
├── .gitignore                  # Archivos ignorados por Git
└── README.md                   # Esta documentación
```

## 🎓 Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────┐
│                   VirtualDJ Software                     │
│              (Reproduce audio, mezcla)                   │
└────────────▲───────────────────────────┬────────────────┘
             │                           │
             │ MIDI Commands             │ Audio Output
             │                           │
┌────────────┴────────────┐    ┌────────▼────────────────┐
│   MIDI Controller       │    │   Audio Observer        │
│  - Play/Pause           │    │  - Captura audio        │
│  - Crossfader           │    │  - Extrae features      │
│  - Effects              │    │  - Detecta beats        │
│  - EQ                   │    │  - Estima BPM           │
└────────────▲────────────┘    └────────┬────────────────┘
             │                           │
             │ Actions                   │ Features & State
             │                           │
┌────────────┴───────────────────────────▼────────────────┐
│              Adaptive Agent                             │
│  Modes:                                                 │
│  - Heuristic (Rule-based)                              │
│  - Supervised Learning (Random Forest)                 │
│  - Reinforcement Learning (Q-Learning)                 │
│                                                         │
│  Optimiza mezclas basándose en:                        │
│  - Características de audio                            │
│  - Estado de VirtualDJ                                 │
│  - Experiencia aprendida                               │
└─────────────────────────────────────────────────────────┘
```

## 🌈 Características Psicodélicas

### DJ Personas (dj_persona.py)

El sistema incluye **4 personalidades de DJ** que alteran el estilo de mezcla:

#### Personas Disponibles

1. **Techno Detroit** 🏭
   - Minimal, industrial, hipnótico
   - BPM: 125-135
   - Transiciones lentas y profundas
   - EQ minimalista
   - Factor experimental: 0.3

2. **Psy-Trance Goa** 🕉️
   - Psicodélico, trippy, alta energía
   - BPM: 138-148
   - Uso intensivo de efectos
   - EQ dinámico
   - Factor experimental: 0.6

3. **Latin Bass** 🔥
   - Reggaeton, dembow, perreo
   - BPM: 90-105
   - Cortes rápidos
   - Énfasis en bajos
   - Factor experimental: 0.4

4. **Lo-Fi ChillHop** 🌙
   - Relajado, jazzy, nostálgico
   - BPM: 70-95
   - Transiciones ultra-suaves
   - EQ cálido
   - Factor experimental: 0.2

**Uso:**
```python
from dj_persona import PersonaAgent

# Crear agente con personalidad
agent = PersonaAgent(learning_mode='reinforcement', persona='psytrance_goa')

# Cambiar personalidad
agent.change_persona('techno_detroit')

# Listar personalidades disponibles
personas = PersonaAgent.list_personas()
```

### Métricas Introspectivas (introspective_metrics.py)

Sistema que expone el estado interno del agente como **métricas psicológicas**:

#### Métricas Disponibles

- **Ansiedad (Anxiety)** 😰: Incertidumbre del agente (tasa de exploración)
- **Confianza (Confidence)** 💪: Rendimiento percibido (recompensa promedio)
- **Fantasía (Fantasy)** 🌟: Voluntad de experimentar
- **Salud de Memoria** 🧠: Retención de experiencias
- **Enfoque (Focus)** 🎯: Consistencia en decisiones
- **Excitación (Excitement)** ⚡: Respuesta a alta energía

**Estados Derivados:**
- Mood: euphoric, confident, anxious, experimental, focused, calm, balanced
- Creative State: highly_creative, creative, moderate, conservative
- Learning Phase: early_exploration, active_learning, exploitation, experimentation, refinement

**Uso:**
```python
from introspective_metrics import IntrospectiveMetrics

metrics = IntrospectiveMetrics()

# Actualizar métricas
metrics.update(agent_state, audio_features, action)

# Obtener estado psicológico
state = metrics.get_state()
print(f"Ansiedad: {state['anxiety']:.2f}")
print(f"Mood: {state['mood']}")

# Descripción narrativa
description = metrics.get_narrative_description()
print(description)
```

### Análisis Semántico Musical (semantic_analyzer.py)

Análisis musical de alto nivel más allá de características básicas:

#### Características Detectadas

- **Densidad Percusiva**: Qué tan cargado de percusión está el audio
- **Armonicidad vs Disonancia**: Contenido armónico vs atonal
- **Presencia Vocal**: Detección de voces
- **Escena Armónica**: Modo (mayor/menor), tono emocional
- **Textura Musical**: sparse, dense, layered, percussive, harmonic, ambient

#### Escenas Armónicas

- `major_bright`: Mayor con baja disonancia (uplifting)
- `major_energetic`: Mayor con disonancia moderada (energetic)
- `minor_dark`: Menor con alta disonancia (dark)
- `atonal_chaotic`: Baja armonía, alta disonancia (intense)
- `percussive_neutral`: Baja armonía, baja disonancia (rhythmic)

**Uso:**
```python
from semantic_analyzer import MusicalSemanticAnalyzer

analyzer = MusicalSemanticAnalyzer()

# Analizar buffer de audio
semantic_features = analyzer.analyze(audio_buffer, audio_features)

print(f"Densidad percusiva: {semantic_features['percussive_density']:.2f}")
print(f"Presencia vocal: {semantic_features['vocal_presence']:.2f}")
print(f"Escena: {semantic_features['harmonic_scene']}")
print(f"Tono emocional: {semantic_features['emotional_tone']}")

# Recomendación de transición
recommendation = analyzer.get_transition_recommendation(scene1, scene2)
print(f"Tipo: {recommendation['transition_type']}")
print(f"Duración: {recommendation['duration']}s")
```

### Visualización Psicodélica (psychedelic_visualizer.py)

Motor de visualización en tiempo real reactivo al audio y estado del agente:

#### Características Visuales

- **Fractales de Fondo**: Patrones geométricos animados
- **Círculos de Energía**: Pulsos basados en energía
- **Pulso de Beat**: Flash visual en beats
- **División de Crossfader**: Split visual entre decks
- **Distorsión por Reward**: Caos visual basado en rendimiento
- **Paletas de Color**: Colores basados en mood del agente

#### Modos de Visualización

1. **OpenGL Mode**: Visualización completa con shaders (requiere pygame + PyOpenGL)
2. **ASCII Mode**: Visualización en terminal (fallback)

**Uso:**
```python
from psychedelic_visualizer import create_visualizer

# Crear visualizador (auto-detecta OpenGL o usa ASCII)
viz = create_visualizer(mode='auto', width=800, height=600)

# Iniciar
viz.start()

# Actualizar estado
viz.update(audio_features, agent_state, vdj_state)

# Detener
viz.stop()
```

**Instalación de dependencias de visualización:**
```bash
pip install pygame PyOpenGL
```

### Machine Spirit - Generador de Poesía (machine_spirit.py)

El "Espíritu de la Máquina" genera poesía sobre las acciones del agente:

#### Tipos de Poesía

1. **Action Poems**: Descripciones poéticas de acciones individuales
2. **State Poems**: Reflexiones sobre el estado psicológico
3. **Session Epilogue**: Épica final de la sesión
4. **Random Wisdom**: Citas filosóficas sobre el DJing

**Ejemplos de Salida:**
```
The crossfader slides like a serpent of light
the beat strikes
energy explodes outward
and harmony reigns
```

```
Lost in the labyrinth of possibilities
Each path uncertain, each choice a mystery
The music roars like a storm
And the beat carries me home
```

**Uso:**
```python
from machine_spirit import MachineSpiritPoet

poet = MachineSpiritPoet()

# Poema de acción
poem = poet.generate_action_poem(action, audio_features, agent_state)
print(poem)

# Poema de estado
state_poem = poet.generate_state_poem(agent_state, audio_features)
print(state_poem)

# Epílogo de sesión
epilogue = poet.generate_session_epilogue(stats)
print(epilogue)

# Sabiduría aleatoria
wisdom = poet.get_random_wisdom()
print(wisdom)
```

### Demo Psicodélico Completo (psychedelic_demo.py)

Script de demostración que integra todas las características:

```bash
python psychedelic_demo.py
```

#### Opciones de Demo

1. Quick Demo (30s) - Techno Detroit
2. Psy-Trance Session (60s)
3. Latin Bass Session (45s)
4. Lo-Fi ChillHop (60s)
5. Comparación de Personas
6. Modo Solo Poesía
7. Showcase de Visualización

**Uso Programático:**
```python
from psychedelic_demo import PsychedelicDJSystem

# Crear sistema completo
system = PsychedelicDJSystem(
    persona='psytrance_goa',
    enable_visualization=True,
    enable_poetry=True
)

# Ejecutar loop psicodélico
system.run_psychedelic_loop(duration=60.0, update_interval=3.0)
```

## 🧠 EPIC SYSTEM - Framework Educativo de Diseño de Circuitos

Este repositorio también contiene documentación del **EPIC SYSTEM**, un framework educativo multi-capa para enseñanza de diseño de circuitos electrónicos:

### 📚 Documentación EPIC SYSTEM

- **[EPIC_SYSTEM.md](EPIC_SYSTEM.md)** - Framework completo de 7 capas (Física, Geométrica, Eléctrica, Semántica, Cognitiva, Pedagógica, Estética)
- **[FIRST_CIRCUIT.md](FIRST_CIRCUIT.md)** - Circuito ejemplo: LED + Resistor limitadora, con análisis completo por capas
- **[RULE_ENGINE_0.1.md](RULE_ENGINE_0.1.md)** - Especificación del motor de inferencia causal para diagnóstico y enseñanza

### 🎯 Propósito

El EPIC SYSTEM transforma la electrónica de "conocimiento tribal" a cognición explícita, permitiendo:
- Razonamiento causal automático ("Si VCC < Vf entonces LED no ilumina")
- Diagnóstico inteligente de circuitos
- Tutoriales adaptativos
- Validación de diseños
- Generación de explicaciones pedagógicas

*"Convierte electrónica en lenguaje, y lenguaje en inferencia."*

## 🚧 Desarrollo Futuro

### Mejoras Planeadas
- [x] Visualización en tiempo real ✅
- [x] Sistema de personalidades DJ ✅
- [x] Análisis semántico musical ✅
- [x] Métricas psicológicas del agente ✅
- [ ] Integración directa con VirtualDJ API
- [ ] Soporte para más controladores MIDI físicos
- [ ] Deep Q-Network (DQN) para aprendizaje profundo
- [ ] Control por visión/gestos (Kinect/webcam)
- [ ] Análisis de reacción del público
- [ ] Análisis de género musical
- [ ] Recomendación de próxima pista
- [ ] Grabación y replay de sesiones
- [ ] Soporte multi-idioma
- [ ] Plugin para VirtualDJ

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE para más detalles.

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📧 Contacto

Para preguntas, sugerencias o reportar problemas, por favor abre un issue en GitHub.

## 🙏 Agradecimientos

- VirtualDJ por su excelente software de DJ
- Tobias Erichsen por loopMIDI
- Comunidad de Python audio/ML por las bibliotecas utilizadas

---

**Nota**: Este es un proyecto educativo y de investigación. Para uso en presentaciones en vivo, se recomienda supervisión humana y pruebas exhaustivas.
