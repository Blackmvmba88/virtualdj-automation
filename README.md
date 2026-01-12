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
- **Estimación de calidad**: Score de calidad de mezcla en tiempo real
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
├── midi_controller.py      # Control MIDI de VirtualDJ
├── audio_observer.py        # Captura y análisis de audio
├── adaptive_agent.py        # Agente de aprendizaje adaptativo
├── test_script.py          # Script de prueba y demostración
├── requirements.txt        # Dependencias Python
├── .gitignore             # Archivos ignorados por Git
└── README.md              # Esta documentación
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

## 🚧 Desarrollo Futuro

### Mejoras Planeadas
- [ ] Integración directa con VirtualDJ API
- [ ] Soporte para más controladores MIDI físicos
- [ ] Deep Q-Network (DQN) para aprendizaje profundo
- [ ] Interfaz gráfica (GUI)
- [ ] Análisis de género musical
- [ ] Recomendación de próxima pista
- [ ] Grabación y replay de sesiones
- [ ] Visualización en tiempo real
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
