// Runtime Guard Code for SafeRL ProofStack
// Generated from specification hash: ce5d9e94a9d9f73fd5d15a970ef840309dc0fb7eb57b1d64e003bac4ceaf6abe

#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdbool.h>

// State structure
typedef struct {
    double cart_position;
    double cart_velocity;
    double pole_angle;
    double pole_angular_velocity;
} State;

// Action structure
typedef struct {
    double force;
} Action;

// Constants
#define MAX_POSITION 2.4
#define MAX_ANGLE 0.2095
#define MAX_FORCE 10.0

// Safety predicate
bool safe(State* state) {
    return fabs(state->cart_position) <= MAX_POSITION && 
           fabs(state->pole_angle) <= MAX_ANGLE;
}

// Guard predicate
bool guard(State* state, Action* action) {
    return fabs(state->cart_position) <= MAX_POSITION - 0.1 && 
           fabs(state->pole_angle) <= MAX_ANGLE - 0.01 &&
           fabs(action->force) <= MAX_FORCE;
}

// Runtime guard function
bool runtime_guard(State* state, Action* action) {
    if (!guard(state, action)) {
        printf("Safety guard violation detected!\n");
        return false;
    }
    return true;
}

// Main guard interface
extern "C" bool check_safety(State* state, Action* action) {
    return runtime_guard(state, action);
}
