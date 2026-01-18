# Rule Engine 0.1 - Causal Inference for Circuit Design

## 🎯 Overview

The Rule Engine is the computational core of the EPIC SYSTEM's Semantic and Cognitive layers. It implements forward and backward chaining inference over circuit knowledge, enabling:

- **Causal reasoning**: "If VCC < Vf, then LED won't light"
- **Diagnostic inference**: "LED is off, possible causes are..."
- **Design validation**: "Given these requirements, this circuit will/won't work"
- **Automated teaching**: "To fix this, you should..."

This document specifies **Rule Engine 0.1**, a minimal viable implementation focused on the LED + R circuit, expandable to more complex circuits.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  Rule Engine Core                    │
│                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │   Knowledge  │  │   Inference  │  │  Explainer│ │
│  │     Base     │  │    Engine    │  │           │ │
│  └──────┬───────┘  └──────┬───────┘  └─────┬─────┘ │
│         │                 │                 │       │
└─────────┼─────────────────┼─────────────────┼───────┘
          │                 │                 │
          ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐      ┌─────────┐
    │  Rules   │      │  Facts   │      │ Queries │
    │ Database │      │ Database │      │         │
    └──────────┘      └──────────┘      └─────────┘
```

**Components:**

1. **Knowledge Base**: Stores rules about circuit behavior
2. **Inference Engine**: Applies rules to facts to derive new knowledge
3. **Explainer**: Generates human-readable explanations of reasoning
4. **Rules Database**: Persistent storage of if-then rules
5. **Facts Database**: Current state of circuit (measurements, observations)
6. **Query Interface**: User asks questions, engine answers

---

## 📋 Rule Format

### Basic Rule Structure

```python
Rule {
    id: "rule_001",
    name: "LED_requires_forward_voltage",
    layer: "electrical",  # physical, geometric, electrical, semantic, cognitive
    
    conditions: [
        Condition("VCC", ">=", "Vf"),
        Condition("polarity", "==", "correct"),
        Condition("R", "exists", True)
    ],
    
    consequences: [
        Fact("current_flows", True),
        Fact("LED_state", "can_illuminate")
    ],
    
    confidence: 1.0,  # 0.0 to 1.0, certainty of rule
    
    explanation: "An LED requires forward voltage (Vf) to conduct. 
                  When VCC >= Vf and polarity is correct, current can flow.",
    
    references: ["LED datasheet", "semiconductor physics"]
}
```

### Condition Types

**Comparison Conditions:**
```python
Condition(variable, operator, value)
# Operators: ==, !=, <, >, <=, >=, ~= (approximately equal)

Examples:
Condition("VCC", ">", "Vf")           # VCC must exceed Vf
Condition("I", "<=", "If_max")        # Current within limit
Condition("temperature", "~=", 25.0)  # Room temperature (±5°C)
```

**Existence Conditions:**
```python
Condition(component, "exists", bool)
Condition(component, "connected", bool)

Examples:
Condition("R", "exists", True)         # Resistor present
Condition("LED", "connected", True)    # LED in circuit
```

**State Conditions:**
```python
Condition(variable, "in", [list_of_values])
Condition(variable, "state", state_name)

Examples:
Condition("LED_color", "in", ["red", "yellow"])  # Color check
Condition("circuit", "state", "powered")         # Circuit energized
```

**Composite Conditions:**
```python
Condition([cond1, cond2], "AND")  # All must be true
Condition([cond1, cond2], "OR")   # At least one true
Condition(cond1, "NOT")           # Negation

Example:
Condition([
    Condition("VCC", ">", 0),
    Condition("LED", "connected", True)
], "AND")
```

---

## 📚 Rule Categories for LED Circuit

### Category 1: Electrical Laws (High Confidence)

**Rule E001: Ohm's Law**
```python
Rule {
    id: "E001",
    name: "ohms_law",
    layer: "electrical",
    conditions: [
        Condition("R", "exists", True),
        Condition("R", ">", 0)
    ],
    consequences: [
        Derived("I", "V / R"),
        Derived("V", "I * R"),
        Derived("R", "V / I")
    ],
    confidence: 1.0,
    explanation: "Ohm's Law: Voltage, current, and resistance are related by V = I × R"
}
```

**Rule E002: Kirchhoff's Voltage Law**
```python
Rule {
    id: "E002",
    name: "kvl_series_circuit",
    layer: "electrical",
    conditions: [
        Condition("circuit_type", "==", "series")
    ],
    consequences: [
        Constraint("VCC == VR + V_LED"),
        Derived("VR", "VCC - V_LED")
    ],
    confidence: 1.0,
    explanation: "In series circuit, supply voltage equals sum of voltage drops"
}
```

**Rule E003: LED Forward Voltage**
```python
Rule {
    id: "E003",
    name: "led_forward_voltage_required",
    layer: "electrical",
    conditions: [
        Condition("VCC", ">=", "Vf"),
        Condition("LED_polarity", "==", "forward")
    ],
    consequences: [
        Fact("LED_can_conduct", True),
        Fact("V_LED", "Vf")  # When conducting, V_LED ≈ Vf
    ],
    confidence: 0.95,  # Slight variation in real Vf
    explanation: "LED requires forward voltage Vf to conduct current"
}
```

### Category 2: Causal Relationships (Semantic Layer)

**Rule S001: Insufficient Voltage**
```python
Rule {
    id: "S001",
    name: "insufficient_voltage_no_conduction",
    layer: "semantic",
    conditions: [
        Condition("VCC", "<", "Vf")
    ],
    consequences: [
        Fact("I", 0),
        Fact("LED_state", "off"),
        Fact("LED_brightness", 0)
    ],
    confidence: 1.0,
    explanation: "When supply voltage is less than forward voltage, 
                  LED cannot conduct and will not light"
}
```

**Rule S002: Missing Current Limiting**
```python
Rule {
    id: "S002",
    name: "no_resistor_damage_risk",
    layer: "semantic",
    conditions: [
        Condition("R", "exists", False),
        Condition("VCC", ">", "Vf")
    ],
    consequences: [
        Fact("I", "very_high"),  # Limited only by LED internal R
        Fact("damage_risk", "critical"),
        Fault("LED_burnout_imminent", True)
    ],
    confidence: 1.0,
    explanation: "Without current limiting resistor, LED will draw excessive 
                  current and burn out"
}
```

**Rule S003: Current-Brightness Relationship**
```python
Rule {
    id: "S003",
    name: "current_determines_brightness",
    layer: "semantic",
    conditions: [
        Condition("LED_state", "==", "on"),
        Condition("I", "in_range", [5, 30])  # mA
    ],
    consequences: [
        Derived("brightness", "f(I)"),  # Monotonic function
        Fact("visible", True)
    ],
    confidence: 0.9,
    explanation: "LED brightness increases with current (5-30mA range)"
}
```

**Rule S004: Reverse Polarity Protection**
```python
Rule {
    id: "S004",
    name: "reverse_polarity_blocks",
    layer: "semantic",
    conditions: [
        Condition("LED_polarity", "==", "reverse")
    ],
    consequences: [
        Fact("I", 0),
        Fact("LED_state", "blocking"),
        Fact("V_LED", "~VCC")  # Full voltage across LED
    ],
    confidence: 1.0,
    explanation: "Reversed LED blocks current (acts as open circuit)"
}
```

### Category 3: Diagnostic Rules (Cognitive Layer)

**Rule C001: LED Off - Diagnostic Tree**
```python
Rule {
    id: "C001",
    name: "diagnose_led_off",
    layer: "cognitive",
    conditions: [
        Observation("LED_brightness", "==", 0),
        Observation("VCC", ">", 0)  # Supply is on
    ],
    consequences: [
        Hypothesis("H1_voltage_too_low", priority=1),
        Hypothesis("H2_led_reversed", priority=2),
        Hypothesis("H3_led_damaged", priority=3),
        Hypothesis("H4_open_connection", priority=4),
        Hypothesis("H5_resistor_too_large", priority=5)
    ],
    next_steps: [
        Measurement("Measure VCC at resistor"),
        Measurement("Measure V_LED"),
        Test("Check LED polarity")
    ],
    explanation: "If LED is off but power is present, systematically check 
                  voltage, polarity, and connections"
}
```

**Rule C002: Test Hypothesis - Voltage Too Low**
```python
Rule {
    id: "C002",
    name: "test_voltage_hypothesis",
    layer: "cognitive",
    conditions: [
        Hypothesis("H1_voltage_too_low", active=True),
        Measurement("VCC_measured", "<", "Vf")
    ],
    consequences: [
        Conclusion("H1_voltage_too_low", confirmed=True),
        Recommendation("Increase VCC or use LED with lower Vf"),
        Explanation("Supply voltage insufficient for LED conduction")
    ],
    confidence: 1.0,
    explanation: "Measured VCC below Vf confirms insufficient voltage hypothesis"
}
```

**Rule C003: Test Hypothesis - Reversed LED**
```python
Rule {
    id: "C003",
    name: "test_polarity_hypothesis",
    layer: "cognitive",
    conditions: [
        Hypothesis("H2_led_reversed", active=True),
        Measurement("V_LED", "~=", "VCC")  # Full voltage across LED
    ],
    consequences: [
        Conclusion("H2_led_reversed", confirmed=True),
        Recommendation("Reverse LED (anode to VCC side, cathode to GND side)"),
        Explanation("LED blocking full voltage indicates reverse polarity")
    ],
    confidence: 0.95,
    explanation: "High voltage across LED with no current suggests reversed polarity"
}
```

### Category 4: Design Rules (Cognitive Layer)

**Rule D001: Calculate Required Resistance**
```python
Rule {
    id: "D001",
    name: "calculate_current_limiting_resistor",
    layer: "cognitive",
    conditions: [
        Given("VCC"),
        Given("Vf"),
        Given("I_desired")
    ],
    consequences: [
        Derived("R_calculated", "(VCC - Vf) / I_desired"),
        Derived("R_standard", "nearest_standard_value(R_calculated, round_up=True)"),
        Derived("I_actual", "(VCC - Vf) / R_standard")
    ],
    validation: [
        Check("I_actual <= If_max", "Current within LED rating"),
        Check("P_R <= P_R_rating", "Resistor power rating adequate")
    ],
    confidence: 1.0,
    explanation: "Calculate resistor value to achieve desired LED current"
}
```

**Rule D002: Verify Power Dissipation**
```python
Rule {
    id: "D002",
    name: "verify_power_ratings",
    layer: "cognitive",
    conditions: [
        Calculated("I"),
        Calculated("R")
    ],
    consequences: [
        Derived("P_R", "I^2 * R"),
        Derived("P_LED", "Vf * I"),
        Check("P_R < 0.5 * P_R_rating", "50% safety margin on resistor"),
        Check("P_LED < P_LED_max", "LED power within rating")
    ],
    confidence: 1.0,
    explanation: "Verify all components operate within power ratings with margin"
}
```

### Category 5: Pedagogical Rules (Teaching Layer)

**Rule P001: Prerequisite Check**
```python
Rule {
    id: "P001",
    name: "check_prerequisites",
    layer: "pedagogical",
    conditions: [
        Student("starting_led_circuit")
    ],
    consequences: [
        Require("knows_polarity", True),
        Require("can_use_multimeter", True),
        Require("understands_voltage_current", True)
    ],
    if_not_met: [
        Redirect("tutorial_polarity"),
        Redirect("tutorial_multimeter"),
        Redirect("tutorial_basic_electricity")
    ],
    explanation: "Student must understand basic concepts before building LED circuit"
}
```

**Rule P002: Provide Contextual Hint**
```python
Rule {
    id: "P002",
    name: "hint_for_dim_led",
    layer: "pedagogical",
    conditions: [
        Observation("LED_state", "==", "dim"),
        Student("confused", True)
    ],
    consequences: [
        Hint("Check if resistor value is too large", level=1),
        Hint("Calculate actual current: I = (VCC - Vf) / R", level=2),
        Hint("Try 220Ω resistor for brighter operation", level=3)
    ],
    explanation: "Progressive hints guide student to solution without giving answer"
}
```

---

## 🔧 Inference Engine

### Forward Chaining (Data-Driven)

**Algorithm:**
```
Given: Facts (measurements, observations)
Goal: Derive all possible conclusions

1. Load all rules
2. For each fact in fact database:
   3. Find rules where conditions match facts
   4. For each matching rule:
      5. Evaluate all conditions
      6. If all conditions true:
         7. Add consequences to fact database
         8. Mark rule as fired
         9. Record inference chain (for explanation)
   10. Repeat until no new facts derived (fixed point)
11. Return fact database + inference chains
```

**Example: Forward Chaining for LED Circuit**
```
Initial Facts:
- VCC = 5.0V
- Vf = 2.0V (red LED)
- R = 220Ω
- LED_polarity = forward
- R exists = True

Iteration 1:
- Rule E002 fires → VR = VCC - Vf = 3.0V
- Rule E003 fires → LED_can_conduct = True

Iteration 2:
- Rule E001 fires → I = VR / R = 3.0/220 = 13.6mA
- Rule S003 fires → brightness = f(13.6mA), visible = True

Iteration 3:
- Rule D002 fires → P_R = (0.0136)^2 * 220 = 40.7mW ✓ Safe
- No new rules fire

Result: Circuit will work, LED will light at medium brightness
```

### Backward Chaining (Goal-Driven)

**Algorithm:**
```
Given: Goal (query, desired fact)
Goal: Find if goal is provable from known facts

1. If goal in fact database → Return True + evidence chain
2. Find rules that produce goal as consequence
3. For each such rule:
   4. Set conditions as subgoals
   5. Recursively prove each subgoal
   6. If all subgoals proven → Goal proven
7. If no rules produce goal → Ask user or measure
8. Return proof tree (for explanation)
```

**Example: Backward Chaining - "Why won't LED light?"**
```
Query: Why is LED_brightness = 0?

Backward chain:
Goal: LED_brightness > 0
  ← Requires: LED_state = on (Rule S003)
    ← Requires: I > I_threshold (Rule S001)
      ← Requires: VCC >= Vf (Rule E003)
        ← Measure: VCC = 1.5V, Vf = 2.0V
        ← Conclusion: VCC < Vf → FAILS

Diagnosis: VCC insufficient (1.5V < 2.0V required)
Recommendation: Increase VCC to at least 2.5V (with margin)
```

---

## 🧠 Query Interface

### Query Types

**1. Factual Query**
```python
query("What is the current?")
→ Engine calculates: I = (VCC - Vf) / R = 13.6mA
```

**2. Causal Query**
```python
query("Why is the LED off?")
→ Engine performs backward chaining
→ Returns: "VCC (1.5V) < Vf (2.0V), insufficient voltage"
```

**3. Hypothetical Query**
```python
query("What if I change R to 100Ω?")
→ Engine creates temporary fact: R = 100Ω
→ Forward chains: I = 30mA → exceeds safe limit
→ Returns: "Current would be 30mA, exceeding recommended 20mA"
```

**4. Design Query**
```python
query("What resistor do I need for 15mA with 9V supply?")
→ Engine applies Rule D001
→ Returns: "R = (9-2)/0.015 = 467Ω, use 470Ω standard value"
```

**5. Diagnostic Query**
```python
query("LED is dim, what are possible causes?")
→ Engine finds relevant diagnostic rules
→ Returns ranked hypotheses:
   1. R too large (check if R > 1kΩ)
   2. VCC too low (measure at LED)
   3. LED degraded (test with known circuit)
```

### Query Language

**Simple Natural Language:**
```
"Why won't the LED light?"
"What is the current?"
"Is 1kΩ too large?"
"What happens if VCC = 3V?"
```

**Structured Query:**
```python
Query {
    type: "causal",
    observation: "LED_brightness == 0",
    context: { VCC: 5.0, R: 220 },
    ask: "root_cause"
}
```

**Measurement-Driven Query:**
```python
Query {
    type: "diagnose",
    measurements: {
        VCC: 5.0,
        V_LED: 5.0,  # Full voltage across LED
        I: 0
    },
    ask: "what_is_wrong"
}
→ Engine: "LED appears reversed (full voltage, no current)"
```

---

## 🎓 Explanation Generation

### Explanation Types

**1. Chain of Reasoning**
```
Why is current 13.6mA?

Because:
1. VCC = 5V and Vf = 2V (given)
2. Therefore VR = VCC - Vf = 3V (KVL, Rule E002)
3. R = 220Ω (given)
4. Therefore I = VR/R = 3/220 = 13.6mA (Ohm's Law, Rule E001)
```

**2. Counterfactual Explanation**
```
Why won't LED light?

LED won't light because VCC < Vf.

If VCC were ≥ 2V (Vf), then:
- Current would flow
- LED would illuminate
- Brightness would depend on current

But VCC = 1.5V, which is insufficient.
```

**3. Comparative Explanation**
```
Why is this LED brighter than that one?

This LED: I = 20mA (R = 150Ω)
That LED: I = 10mA (R = 330Ω)

Brightness ∝ Current (Rule S003)
20mA > 10mA → This LED brighter

To make them equal: Use same current → Same R value
```

**4. Pedagogical Explanation (Teaching)**
```
You measured V_LED = 5V and LED is off. What does this mean?

This is a diagnostic clue! When you see:
- Full supply voltage across LED
- No current flowing
- LED not lit

It usually means: LED is not conducting

Why wouldn't it conduct?
- Wrong polarity (most common) ← Check this first!
- LED damaged (open circuit)
- No connection on one side

Action: Check if LED is inserted backwards (long leg should go to + side)
```

---

## 💾 Data Structures

### Fact Representation
```python
class Fact:
    def __init__(self, variable, value, source, confidence=1.0):
        self.variable = variable    # "VCC", "I", "LED_state"
        self.value = value          # 5.0, 0.015, "on"
        self.source = source        # "measured", "calculated", "inferred"
        self.confidence = confidence # 0.0 to 1.0
        self.timestamp = now()
        self.derived_from = []      # Chain of reasoning

# Example
facts = [
    Fact("VCC", 5.0, "measured", confidence=0.99),
    Fact("Vf", 2.0, "datasheet", confidence=0.95),
    Fact("R", 220, "observed", confidence=1.0),
    Fact("I", 0.0136, "calculated", confidence=0.95)
]
```

### Rule Representation
```python
class Rule:
    def __init__(self, rule_id, name, layer, conditions, consequences, 
                 confidence, explanation):
        self.id = rule_id
        self.name = name
        self.layer = layer              # Which EPIC layer
        self.conditions = conditions    # List of Condition objects
        self.consequences = consequences # List of Fact/Action objects
        self.confidence = confidence    # 0.0 to 1.0
        self.explanation = explanation  # Human-readable why
        self.times_fired = 0
        self.success_rate = 1.0         # Historical accuracy

    def evaluate(self, fact_db):
        """Check if all conditions are met"""
        return all(cond.check(fact_db) for cond in self.conditions)
    
    def fire(self, fact_db):
        """Add consequences to fact database"""
        for consequence in self.consequences:
            fact_db.add(consequence, derived_from=self)
        self.times_fired += 1
```

### Inference Chain
```python
class InferenceChain:
    def __init__(self):
        self.steps = []  # [(rule, facts_used, facts_derived)]
    
    def add_step(self, rule, input_facts, output_facts):
        self.steps.append({
            'rule': rule,
            'inputs': input_facts,
            'outputs': output_facts
        })
    
    def explain(self):
        """Generate human-readable explanation"""
        explanation = []
        for i, step in enumerate(self.steps):
            explanation.append(f"Step {i+1}: {step['rule'].name}")
            explanation.append(f"  Given: {step['inputs']}")
            explanation.append(f"  Concluded: {step['outputs']}")
            explanation.append(f"  Because: {step['rule'].explanation}")
        return "\n".join(explanation)
```

---

## 🚀 Implementation Roadmap

### Phase 1: Core Engine (Week 1-2)
- [ ] Implement Fact and Rule classes
- [ ] Build forward chaining engine
- [ ] Load rules from file (JSON/YAML)
- [ ] Test with 10 basic LED rules

### Phase 2: Query Interface (Week 3)
- [ ] Natural language query parser
- [ ] Backward chaining for diagnostic queries
- [ ] Explanation generator

### Phase 3: Knowledge Base (Week 4)
- [ ] Complete LED circuit rule set (30+ rules)
- [ ] Add rules for common faults
- [ ] Diagnostic decision trees

### Phase 4: Integration (Week 5-6)
- [ ] Connect to measurement tools (multimeter input)
- [ ] Interactive troubleshooting UI
- [ ] Tutorial system integration

### Phase 5: Expansion (Future)
- [ ] Add transistor circuit rules
- [ ] Add voltage regulator rules
- [ ] Machine learning for rule confidence tuning
- [ ] Probabilistic reasoning (Bayesian networks)

---

## 🧪 Example Session

```python
# Initialize engine
engine = RuleEngine()
engine.load_rules("led_circuit_rules.json")

# User builds circuit and provides facts
engine.add_fact("VCC", 5.0, source="measured")
engine.add_fact("R", 220, source="observed")
engine.add_fact("LED_color", "red", source="observed")
engine.add_fact("LED_polarity", "forward", source="observed")

# Engine infers forward
results = engine.infer()
print(f"Current: {results.get('I')} A")
print(f"LED will: {results.get('LED_state')}")
print(f"Brightness: {results.get('brightness_level')}")

# User observes problem
engine.add_observation("LED_brightness", 0)

# Engine diagnoses
diagnosis = engine.query("Why is LED off?")
print(diagnosis.explanation)
# → "LED not lighting because VCC (measured 5V) but LED appears 
#    reversed (V_LED = 5V, no current). Reverse LED polarity."

# User asks design question
design = engine.query("What R for 20mA at 9V?")
print(design.answer)
# → "R = (9-2)/0.02 = 350Ω, use 360Ω standard value.
#    Actual current: 19.4mA ✓"
```

---

## 🎯 Success Criteria

Rule Engine 0.1 is successful if it can:

1. ✅ Answer "What is the current?" correctly
2. ✅ Diagnose "Why won't LED light?" with 5+ possible causes
3. ✅ Design resistor value for any VCC/LED/current combination
4. ✅ Explain reasoning in human-readable form
5. ✅ Detect common errors (reversed polarity, missing R, etc.)
6. ✅ Provide contextual hints for learning
7. ✅ Run inference in < 1 second for LED circuit
8. ✅ Handle measurement uncertainty gracefully

**Bonus:**
- Suggest "what to measure next" for efficient diagnosis
- Rank hypotheses by likelihood
- Learn from user corrections (update rule confidence)

---

*"A rule engine that teaches more than a multimeter"*
