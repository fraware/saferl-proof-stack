-- compressor_station.lean
-- Example Lean spec for a compressor station

structure State where
  surgeMargin : Float
  Pdisch : Float

structure Action where
  ΔValve : Float

-- External maximum allowable operating pressure parameter; no value is assumed.
opaque MAOP : Float

def safe (σ : State) : Prop :=
  σ.surgeMargin ≥ 0.05 ∧ σ.Pdisch ≤ MAOP - 50

def compressorGuard (σ : State) (a : Action) : Prop :=
  σ.surgeMargin ≥ 0.07 ∧ Float.abs a.ΔValve ≤ 0.05 ∧ σ.Pdisch ≤ MAOP - 50
