# Formal Logic Proof System
A ground-up implementation of a proof verification system, designed to formalize mathematics from basic logical axioms to calculus.

## Features
- Predicate calculus evaluation
- Variable and predicate support
- Logic operators (AND, OR, NOT, IMPLIES)
- Basic inference rules (Modus Ponens, Disjunctive Syllogism)
- Premise and variable declarations

## Example
```
# Athlete example using modus ponens
Decl (Tall(x) & Muscle(x)) -> Athlete(x)
Decl Tall(x)
Decl Muscle(x)
((Tall(x) & Muscle(x)) -> Athlete(x)) & (Tall(x) & Muscle(x))
Thus Athlete(x)
```

## Roadmap
1. **Rule System**
   - Proof by contradiction
   - Import system for theorems

2. **First Order Logic**
   - Quantifiers
   - Enhanced variable binding

3. **Mathematical Foundations**
   - Peano Axioms
   - Set Theory axioms
   - Number theory construction
   - Path to calculus

## Design Philosophy
Built using explicit rule-based verification rather than constraint solving, allowing for clear proof steps that mirror mathematical reasoning. Designed for extensibility and theorem reuse.

## Usage
```
# Import required rules
import rules/predicate_calculus/modus_ponens
import rules/predicate_calculus/dysjunctive_syllogism

# Declare premises and construct proofs
Decl P(x) : A(x) | B(x)
Decl P(y)
A(y) | B(y)
```
