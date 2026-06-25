import Mathlib

/-! From *Mathematics in Lean*, C03 "Logic": a product of two reals each smaller
in absolute value than a small `ε` is itself smaller than `ε`. -/

theorem my_lemma : ∀ x y ε : ℝ, 0 < ε → ε ≤ 1 → |x| < ε → |y| < ε → |x * y| < ε :=
  sorry
