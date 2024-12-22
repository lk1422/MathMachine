import rules/predicate_calculus/modus_ponens
import rules/predicate_calculus/dysjunctive_syllogism
import rules/predicate_calculus/and_elimination

Decl (Tall(x) & Muscle(x)) -> Athlete(x)
Decl Tall(x)
Decl Muscle(x)
((Tall(x) & Muscle(x)) -> Athlete(x)) & (Tall(x) & Muscle(x))
Thus Athlete(x)


Decl ~Tall(x)
Decl Tall(x) | Short(x)
(Tall(x) | Short(x)) & ~Tall(x)
Thus Short(x)

Decl F(x) & G(x)
Thus F(x)

Decl P(x) : A(x) | B(x)
Decl P(y)
A(y) | B(y)

Decl x
Decl x -> P(z)
(x -> P(z)) & x
Thus P(z)
A(z) | B(z)
