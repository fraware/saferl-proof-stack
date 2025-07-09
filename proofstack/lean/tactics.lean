/-!
  SafeRL ProofStack: Common Lean4 Tactics & Macro Rules
  This file collects reusable proof automation for all generated proofs.
-*/

import Mathlib.Tactic

namespace ProofStack

/--
  Macro for common proof automation: tries simp, ring, linarith, monotonicity in order.
  Usage: `by_proofstack` in generated theorems.
--/
macro_rules
  | `(tactic| by_proofstack) =>
    `(tactic|
      first
        | simp only [*] with simp_rw
        | ring
        | linarith
        | monotonicity
        | assumption
        | exact trivial
    )

/--
  Simp set for common RL and math rewrites.
  Add more as needed for generated environments.
--/
attribute [simp]
  Nat.add_zero Nat.zero_add Nat.add_comm Nat.add_assoc
  Nat.mul_zero Nat.zero_mul Nat.mul_comm Nat.mul_assoc
  add_le_add mul_le_mul

/--
  Helper tactic: try all common proof strategies.
--/
macro "auto_rl" : tactic =>
  `(tactic|
    try simp only [*] with simp_rw;
    try ring;
    try linarith;
    try monotonicity;
    try assumption;
    try exact trivial;
  )

end ProofStack
