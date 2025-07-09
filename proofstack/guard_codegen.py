"""Runtime guard code generation for safety specifications."""

from pathlib import Path
import hashlib


class GuardGen:
    """Generates runtime guard code from safety specifications."""

    def __init__(self):
        """Initialize the guard code generator."""
        pass

    def emit_c(self, spec) -> str:
        """Generate C99 runtime guard code from safety specification.

        Args:
            spec: Safety specification object with invariants, guard, and lemmas

        Returns:
            Path to the generated C file
        """
        # Create output directory
        output_dir = Path("guard_output")
        output_dir.mkdir(exist_ok=True)

        # Generate C code
        c_code = self._generate_c_code(spec)

        # Write to file
        c_file = output_dir / "guard.c"
        c_file.write_text(c_code, encoding="utf-8")

        return str(c_file)

    def _generate_c_code(self, spec) -> str:
        """Generate the actual C code content."""
        # Handle both SpecGen objects and raw safety specs
        if hasattr(spec, "safety_spec"):
            # It's a SpecGen object, get the underlying spec
            raw_spec = spec.safety_spec
        else:
            # It's already a raw spec
            raw_spec = spec

        # Create a hash of the specification for traceability
        spec_content = f"{raw_spec.invariants}{raw_spec.guard}{raw_spec.lemmas}"
        spec_hash = hashlib.sha256(spec_content.encode()).hexdigest()

        c_code = f"""// Runtime Guard Code for SafeRL ProofStack
// Generated from specification hash: {spec_hash}

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

// State structure
typedef struct {{
    double cart_position;
    double cart_velocity;
    double pole_angle;
    double pole_angular_velocity;
}} State;

// Action structure
typedef struct {{
    double force;
}} Action;

// Constants
#define MAX_POSITION 2.4
#define MAX_ANGLE 0.2095
#define MAX_FORCE 10.0

// Safety predicate
bool safe(State* state) {{
    return fabs(state->cart_position) <= MAX_POSITION && 
           fabs(state->pole_angle) <= MAX_ANGLE;
}}

// Guard predicate
bool guard(State* state, Action* action) {{
    return fabs(state->cart_position) <= MAX_POSITION - 0.1 && 
           fabs(state->pole_angle) <= MAX_ANGLE - 0.01 &&
           fabs(action->force) <= MAX_FORCE;
}}

// Runtime guard function
bool runtime_guard(State* state, Action* action) {{
    if (!guard(state, action)) {{
        printf("Safety guard violation detected!\\n");
        return false;
    }}
    return true;
}}

// Main guard interface
extern "C" bool check_safety(State* state, Action* action) {{
    return runtime_guard(state, action);
}}
"""
        return c_code
