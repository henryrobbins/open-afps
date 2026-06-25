import Mathlib

/-! From *Mathematics in Lean*, C04 "Sets and Functions": intersection
distributes over union. -/

variable {α : Type*} (a b c : Set α)

example : a ∩ (b ∪ c) = (a ∩ b) ∪ (a ∩ c) := by
  sorry
