import Mathlib

/-! From *Mathematics in Lean*, C09 "Linear Algebra": scalar multiplication
distributes over vector addition in a module. -/

variable {K : Type*} [Field K] {V : Type*} [AddCommGroup V] [Module K V]

example (a : K) (u v : V) : a • (u + v) = a • u + a • v :=
  sorry
