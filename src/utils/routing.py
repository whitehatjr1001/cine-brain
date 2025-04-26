# routing.py

import random
import logging
from typing import Any, Callable, List, Dict, Tuple

class ChainOfThoughtRouter:
    def __init__(self, actions: List[Callable], state: Dict[str, Any] = None, max_steps: int = 10, temperature: float = 1.0):
        self.actions = actions
        self.state = state or {}
        self.max_steps = max_steps
        self.temperature = temperature
        self.plan = []
        self.log = []

    def propose_action(self, current_state: Dict[str, Any]) -> Callable:
        # Heuristic: Prefer actions that modify the least-used state key
        action_scores = []
        for action in self.actions:
            # Try to infer which key the action modifies by simulating on a copy
            state_copy = current_state.copy()
            try:
                action(state_copy)
                changed_keys = [k for k in state_copy if state_copy[k] != current_state.get(k)]
            except Exception:
                changed_keys = []
            # Score: prefer actions that change keys not yet present or least changed
            score = sum(1 for k in changed_keys if k not in current_state)
            action_scores.append((score, action))
        # Pick the action with the highest score (break ties randomly)
        max_score = max(score for score, _ in action_scores)
        best_actions = [action for score, action in action_scores if score == max_score]
        return random.choice(best_actions)

    def evaluate_plan(self, plan: List[Callable], state: Dict[str, Any]) -> float:
        # Heuristic: Score by number of unique state keys affected by the plan
        state_copy = state.copy()
        affected_keys = set()
        for action in plan:
            before = state_copy.copy()
            try:
                action(state_copy)
            except Exception:
                continue
            for k in state_copy:
                if state_copy[k] != before.get(k):
                    affected_keys.add(k)
        # Score: more unique keys affected is better
        return len(affected_keys)

    def run_chain_of_thought(self):
        current_state = self.state.copy()
        plan = []
        best_score = float('-inf')
        best_plan = []
        for step in range(self.max_steps):
            action = self.propose_action(current_state)
            plan.append(action)
            # Simulate action (here, just log it)
            self.log.append(f"Step {step}: Proposed {action.__name__}")
            score = self.evaluate_plan(plan, current_state)
            self.log.append(f"Step {step}: Plan score {score}")
            if score > best_score:
                best_score = score
                best_plan = plan.copy()
            # Optionally, add MCMC-like acceptance/rejection here
            if random.random() < self.temperature:
                continue  # Accept new plan
            else:
                break  # Stop early
        self.plan = best_plan
        return best_plan, best_score

    def execute_plan(self):
        for action in self.plan:
            self.log.append(f"Executing {action.__name__}")
            action(self.state)

    def get_log(self):
        return self.log

# Example usage (to be replaced with real agent actions)
def dummy_action_1(state):
    state['a'] = state.get('a', 0) + 1

def dummy_action_2(state):
    state['b'] = state.get('b', 0) + 2

# For integration:
# router = ChainOfThoughtRouter(actions=[dummy_action_1, dummy_action_2])
# plan, score = router.run_chain_of_thought()
# router.execute_plan()
# print(router.get_log())