# EPIC SYSTEM - Educational Framework for Circuit Design

## 🎯 Overview

EPIC SYSTEM is a multi-layered educational framework for understanding, designing, and teaching electronic circuit design. The system structures knowledge across seven interconnected layers, each with its own objects, operations, and rules that build toward complete circuit comprehension.

The framework transforms electronics from aesthetic tribal knowledge into explicit, teachable cognition.

---

## 🏗️ The Seven Layers

### 1. Physical Layer (Física)

**Purpose**: Understanding the tangible, material properties of electronic components.

#### Objects
- **Components**: Resistors, capacitors, LEDs, transistors, ICs
- **Materials**: Copper, silicon, plastic, solder, PCB substrate
- **Physical properties**: Temperature, mass, dimension, conductivity
- **Soldering**: Joints, flux, thermal transfer
- **Wiring**: Wire gauge, insulation, connectors

#### Operations
- **Touch/Handle**: Physical manipulation of components
- **Mount**: Placing components on PCB or breadboard
- **Measure**: Using calipers, visual inspection
- **Heat**: Soldering, desoldering, thermal management
- **Assemble**: Connecting physical parts together
- **Cut/Strip**: Wire preparation

#### Rules
1. **Current causes heat**: `I²R` dissipation in conductors
2. **Plastic does not conduct**: Insulators block current flow
3. **Copper conducts electricity**: Low resistance path for current
4. **Excessive heat damages components**: Thermal limits must be respected
5. **Polarity matters**: Physical orientation affects function (LEDs, electrolytic caps)
6. **Solder creates electrical + mechanical connection**: Proper joint formation required
7. **Component bodies can store heat**: Thermal mass affects temperature response

---

### 2. Geometric Layer (Geométrica)

**Purpose**: Understanding spatial relationships, positioning, and physical constraints.

#### Objects
- **Pads**: Landing points for component leads
- **Pins**: Connection points on components
- **Distances**: Spacing between elements
- **Bounding boxes**: Component physical footprint
- **Traces**: PCB copper paths
- **Holes**: Through-hole mounting points
- **Zones**: Ground planes, power planes, keep-out areas
- **Layers**: Top, bottom, internal layers in PCB

#### Operations
- **Position**: Place component at specific coordinates
- **Rotate**: Orient component (0°, 90°, 180°, 270°)
- **Assemble**: Fit components together spatially
- **Trace/Route**: Draw electrical connections
- **Align**: Position components in relation to each other
- **Measure distance**: Calculate spacing
- **Check clearance**: Verify minimum distances

#### Rules
1. **Minimum spacing**: Components need clearance (typically 0.2-0.5mm)
2. **Trace width determines current capacity**: Wider traces carry more current
3. **No overlapping components**: Physical collision detection
4. **Pad size matches lead diameter**: Proper hole sizing for through-hole
5. **Keep-out zones must be respected**: Areas where components cannot be placed
6. **Symmetric layouts reduce noise**: Physical balance improves electrical performance
7. **Short traces reduce parasitic effects**: Minimize inductance and resistance
8. **Ground plane continuity**: No breaks in return path

---

### 3. Electrical Layer (Eléctrica)

**Purpose**: Understanding electrical behavior, energy flow, and circuit operation.

#### Objects
- **Nets**: Electrically connected nodes (VCC, GND, signal paths)
- **Voltage rails**: VCC, VDD, GND, VSS
- **Current paths**: Direction and magnitude of current flow
- **Impedances**: Resistance, capacitance, inductance
- **Polarities**: Positive/negative, anode/cathode
- **Power domains**: Different voltage levels in same circuit
- **Signals**: Digital (HIGH/LOW) or analog waveforms
- **Parasitics**: Unwanted R, L, C effects

#### Operations
- **Connect**: Join nets together
- **Isolate**: Separate electrical paths
- **Measure voltage**: Use multimeter/oscilloscope
- **Measure current**: Use ammeter or current sense
- **Limit current**: Use resistors or active circuits
- **Transfer energy**: Power delivery from source to load
- **Filter**: Remove unwanted frequencies
- **Amplify**: Increase signal amplitude
- **Switch**: Control current flow

#### Rules
1. **Ohm's Law**: `V = I × R`
2. **Kirchhoff's Current Law (KCL)**: Sum of currents at node = 0
3. **Kirchhoff's Voltage Law (KVL)**: Sum of voltages in loop = 0
4. **Forward voltage drop (Vf)**: Diodes/LEDs have minimum voltage to conduct
5. **Current limiting required**: LEDs and other components need current control
6. **ESR (Equivalent Series Resistance)**: All components have internal resistance
7. **Saturation voltage**: Transistors have minimum Vce when fully on
8. **Bias requirements**: Active components need proper operating point
9. **Power dissipation**: `P = V × I = I²R = V²/R`
10. **Voltage divider**: `Vout = Vin × R2/(R1 + R2)`
11. **RC time constant**: `τ = R × C` (charging/discharging time)
12. **Frequency response**: Components behave differently at different frequencies

---

### 4. Semantic Layer (Semántica)

**Purpose**: Understanding cause-and-effect relationships and conditional behavior.

#### Objects
- **Causal statements**: "If VCC < Vf then LED does not illuminate"
- **Conditions**: Logical predicates about circuit state
- **Consequences**: What happens as a result of conditions
- **Dependencies**: Component A requires component B
- **State transitions**: Circuit moving between operating modes
- **Failure modes**: What goes wrong and why
- **Operating regions**: Normal, marginal, failed
- **Behaviors**: Expected vs actual circuit response

#### Operations
- **Cause → Consequence**: Trace logical implications
- **Evaluate condition**: Check if predicate is true
- **Diagnose**: Determine root cause of behavior
- **Predict**: Anticipate circuit response to changes
- **Validate**: Confirm expected behavior
- **Troubleshoot**: Systematic fault isolation

#### Rules
1. **IF VCC < Vf THEN LED does not illuminate**
2. **IF R missing THEN LED burns out** (no current limiting)
3. **IF Vf increases THEN current decreases** (at constant VCC)
4. **IF temperature increases THEN Vf decreases** (LED characteristic)
5. **IF current exceeds max rating THEN component fails**
6. **IF voltage reverses THEN LED blocks** (reverse bias)
7. **IF load increases THEN voltage drops** (regulator dropout)
8. **IF input exceeds rating THEN protection activates or damage occurs**
9. **IF bypass capacitor missing THEN noise increases**
10. **IF ground loop exists THEN interference occurs**

---

### 5. Cognitive Layer (Cognitiva)

**Purpose**: Higher-order reasoning about circuits - explanations, hypotheses, and diagnostic thinking.

#### Objects
- **Explanations**: Why circuit works or doesn't work
- **Hypotheses**: Potential causes of observed behavior
- **Mental models**: Internal representation of circuit operation
- **Temporal consequences**: How circuit evolves over time
- **Diagnostic trees**: Structured troubleshooting paths
- **Design rationale**: Why designer made specific choices
- **Confidence levels**: Certainty about diagnosis or prediction
- **Learning paths**: Progressive understanding stages

#### Operations
- **Diagnose**: Identify root cause systematically
- **Predict**: Forecast circuit behavior under new conditions
- **Justify**: Explain reasoning behind conclusion
- **Hypothesize**: Generate potential explanations
- **Test hypothesis**: Design measurement to validate/invalidate
- **Rank by likelihood**: Prioritize probable causes
- **Explain**: Teach concept to another person
- **Design**: Create circuit to meet specifications

#### Rules
1. **Severity classification**: Critical, major, minor, informational
2. **Probability ranking**: Most likely cause should be tested first
3. **Minimal change principle**: Test one variable at a time
4. **Measurement validates hypothesis**: Data over intuition
5. **Multiple symptoms suggest root cause**: Look for common factors
6. **Intermittent failures need statistical analysis**: Reproduce reliably
7. **Design margins prevent failures**: Don't operate at limits
8. **Simplest explanation often correct**: Occam's razor
9. **Document assumptions**: Make implicit knowledge explicit
10. **Known-good comparison**: Compare to working reference

---

### 6. Pedagogical Layer (Pedagógica)

**Purpose**: Teaching, learning, and skill development in circuit design.

#### Objects
- **Tutorials**: Step-by-step learning modules
- **Workflows**: Standard procedures for common tasks
- **Feedback**: Corrective guidance for learner
- **Exercises**: Practice problems with increasing difficulty
- **Knowledge prerequisites**: What must be learned first
- **Learning objectives**: Specific skills to acquire
- **Assessment criteria**: How to measure understanding
- **Hints/Tips**: Contextual help when stuck
- **Example circuits**: Reference designs for learning
- **Progression levels**: Beginner, intermediate, advanced, expert

#### Operations
- **Guide**: Lead learner through process
- **Teach**: Explain concept or technique
- **Evaluate**: Assess learner understanding
- **Provide feedback**: Give corrective input
- **Unlock content**: Grant access to next level
- **Scaffold**: Provide support structure that gradually removes
- **Demonstrate**: Show working example
- **Challenge**: Present problem to solve
- **Review**: Reinforce learned material

#### Rules
1. **Prerequisites must be completed first**: Ordered learning path
2. **Progressive difficulty**: Start simple, increase complexity
3. **Immediate feedback**: Correct mistakes right away
4. **Multiple representations**: Show concept different ways
5. **Active learning**: Hands-on practice beats passive reading
6. **Spaced repetition**: Review at increasing intervals
7. **Concrete before abstract**: Start with examples, then theory
8. **Error-based learning**: Mistakes are learning opportunities
9. **Zone of proximal development**: Challenge just beyond current level
10. **Mastery required**: Don't advance without understanding
11. **Context matters**: Teach concepts in relevant situations
12. **Hint progression**: Start subtle, get more explicit if needed

---

### 7. Aesthetic Layer (Estética)

**Purpose**: Visual representation, clarity, and human-friendly presentation of circuit information.

#### Objects
- **Visual representation**: Schematic symbols, PCB layout views
- **Color coding**: Voltage levels, net classes, component types
- **Netlist visibility**: Show/hide connection information
- **Annotations**: Labels, notes, measurements
- **Highlighting**: Emphasis on important elements
- **Grouping**: Visual organization of related components
- **Layers visibility**: Show/hide PCB layers
- **Zoom levels**: Detail vs overview
- **Themes**: Dark mode, light mode, high contrast
- **Clarity metrics**: Readability, information density

#### Operations
- **Highlight**: Draw attention to specific element
- **Group**: Organize related components visually
- **Hide/Show**: Toggle visibility of elements
- **Color-code**: Apply consistent color scheme
- **Annotate**: Add explanatory text
- **Zoom**: Change detail level
- **Rotate view**: Change perspective (2D/3D)
- **Compare**: Show before/after or expected/actual
- **Animate**: Show signal flow or temporal behavior
- **Simplify**: Remove unnecessary detail for clarity

#### Rules
1. **Legibility first**: Must be readable at target scale
2. **Consistent symbolism**: Use standard schematic symbols
3. **Color has meaning**: Don't use color arbitrarily
4. **VCC at top, GND at bottom**: Follow conventions
5. **Left-to-right signal flow**: Input left, output right
6. **Group related functions**: Keep functional blocks together
7. **Minimize wire crossings**: Reduce visual complexity
8. **Label all nets**: No mystery connections
9. **Show reference designators**: U1, R1, C1, etc.
10. **Symmetry implies relationship**: Visual balance shows electrical balance
11. **White space matters**: Don't overcrowd
12. **High contrast for emphasis**: Important elements stand out
13. **Avoid confusion**: Similar elements should look different
14. **Progressive disclosure**: Show detail on demand

---

## 🔄 Layer Interactions

The layers are not isolated - they interact and inform each other:

```
Aesthetic ←→ Pedagogical
    ↑            ↑
    ↓            ↓
Cognitive ←→ Semantic
    ↑            ↑
    ↓            ↓
Electrical ←→ Geometric
    ↑            ↑
    ↓            ↓
  Physical
```

**Example flow**: A learner (Pedagogical) observes a circuit diagram (Aesthetic), thinks about why it works (Cognitive), traces cause-effect (Semantic), measures voltages (Electrical), checks component placement (Geometric), and solders connections (Physical).

---

## 🎓 Using the EPIC SYSTEM

### For Learning
1. Start at Physical layer - touch real components
2. Progress to Geometric - understand layout
3. Move to Electrical - measure and calculate
4. Advance to Semantic - trace causality
5. Develop Cognitive - diagnose and design
6. Use Pedagogical - structured learning path
7. Apply Aesthetic - clear communication

### For Teaching
1. Define clear learning objectives (Pedagogical)
2. Create visual aids (Aesthetic)
3. Explain cause-effect (Semantic)
4. Demonstrate measurements (Electrical)
5. Show physical assembly (Physical + Geometric)
6. Guide diagnostic thinking (Cognitive)

### For Tool Development
1. Physical: Component database, thermal simulation
2. Geometric: CAD tools, DRC (Design Rule Check)
3. Electrical: SPICE simulation, power analysis
4. Semantic: Rule engine, fault simulation
5. Cognitive: Interactive troubleshooting, AI tutoring
6. Pedagogical: Adaptive learning system, progress tracking
7. Aesthetic: Visualization engine, schematic beautification

---

## 🚀 Next Steps

1. **Populate with real circuits**: Start with LED+R, expand to regulators, transistors
2. **Build rule engine**: Implement semantic and cognitive reasoning
3. **Create diagnostic tools**: Interactive troubleshooting assistants
4. **Develop pedagogy**: Structured curriculum with assessments
5. **Integrate hardware**: BLE/USB measurement integration
6. **Add CV capabilities**: Component detection, net tracing from images
7. **Enable 2D/3D sync**: Connect schematic to physical board

---

## 📚 Philosophy

This framework acknowledges that electronics is not just calculation - it's a multi-dimensional discipline requiring:

- **Physical intuition**: How things feel and behave
- **Spatial reasoning**: Where things go and why
- **Mathematical rigor**: Calculating correct values
- **Causal understanding**: Why things happen
- **Diagnostic skill**: Finding and fixing problems
- **Teaching ability**: Transferring knowledge
- **Communication clarity**: Explaining clearly

By making these layers explicit, we transform electronics from tribal knowledge into teachable science.

---

*"Electronics becomes language, and language becomes inference."*
