import Mathlib

/-! From *Mathematics in Lean*, C04 "Sets and Functions": intersecting both sides
of a subset relation with the same set preserves it. -/

variable {α : Type*} (s t u : Set α)

example (h : s ⊆ t) : s ∩ u ⊆ t ∩ u := by
  sorry
