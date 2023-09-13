from __future__ import annotations  # Needed for nice future-typing
from typing import Any
import numpy as np


class KnapsackProblem:
    """
    A knapsack problem instance.

     - n : number of items
     - p : profits
     - w : weights
     - c : capacity
    """

    def __init__(self, profits: np.ndarry, weights: np.ndarray, capacity: int) -> None:
        """
        Random problem instance of given size
        """
        # Generate problem instance
        assert len(weights) == len(profits)
        self.n = len(weights)
        self.p = profits
        self.w = weights
        self.c = capacity
        self.sense = "max"
        # Precalculate ratios to avoid doing at every node of search tree
        self.argsorted_ratios = np.argsort(self.p / self.w)[::-1]

    @classmethod
    def random(cls, num_items: int) -> None:
        """
        Random problem instance of given size
        """
        # Generate problem instance
        p = np.random.randint(1, num_items, size=num_items)
        w = np.random.randint(1, num_items, size=num_items)
        c = np.random.randint(w.min(), w.sum())
        return cls(p, w, c)


class Solution:
    def __init__(self, x: np.ndarray, objective_value: float) -> None:
        """
        A basic constructor for a solution of a problem instance (can be incumbent or optimal).
        """
        self.x = x
        self.objective_value = objective_value


class RootProblem:
    """
    A continuous knapsack solver, implemented using numpy, with fixed items
    """

    def __init__(self, problem: KnapsackProblem) -> None:
        """Base constructor"""
        self.problem = problem

    def solve(self, fixed_vars: list[tuple]) -> tuple[float, np.ndarray]:
        """
        Solves a continuous relaxation of the problem

        Returns :
         - bound (float) : upper/lower bound of subproblem
         - partial_solution (any) : a partial solution (usually fractional)
        """
        # Start by finding the fixed items, and the total fixed profit and weight
        fixed = np.zeros(self.problem.n)
        fixed_val = np.zeros(self.problem.n)
        for var, val in fixed_vars:
            fixed[var] = 1
            fixed_val[var] = val
        W = fixed_val.dot(self.problem.w)
        P = fixed_val.dot(self.problem.p)

        # Check feasibility
        if W > self.problem.c:
            return 0.0, None

        # Solve continuous knapsack
        for i in self.problem.argsorted_ratios:
            if fixed[i] == 0:
                if W + self.problem.w[i] > self.problem.c:
                    frac = (self.problem.c - W) / self.problem.w[i]
                    P += self.problem.p[i] * frac
                    fixed_val[i] = frac
                    return P, fixed_val
                else:
                    W += self.problem.w[i]
                    P += self.problem.p[i]
                    fixed_val[i] = 1
        return P, fixed_val


class Node:
    """
    A node of the branch and bound tree.

    Contains a `root_problem`, a `parent_node`, and a fixed variable.
    Then, call `get_fixed_vars()` to get a list of variable fixings from all parent nodes.
    Calling `solve` solves the root problem with the given variable fixings.
    """

    def __init__(self, parent_node: Node | None) -> None:
        """
        Constructor not to be called directly!
        Instead use the classmethod `get_root_node` or `get_child_node`!
        """
        # Parent node (None if root node)
        self._parent_node = parent_node
        # Reference to the root problem
        if isinstance(parent_node, Node):
            self._root_problem: RootProblem = parent_node._root_problem
        # The fixed variable at this node
        self._fixed_var: tuple

    def add_fixed_var(self, var, val):
        """
        Add a fixed variable to this node.
        Fixes `var` to `val`.
        Specific notation/implementation should depend on application.
        """
        self._fixed_var = (var, val)

    def get_fixed_vars(self) -> list[tuple]:
        """
        Returns a list of all fixed values at a node.
        Recursively calls the parents fixed variable, and its parents, etc.etc.
        Terminates at the root node.
        """
        if self._parent_node is None:
            return []
        else:
            return [self._fixed_var] + self._parent_node.get_fixed_vars()

    def solve(self) -> tuple[float, np.ndarray]:
        """
        Solves this node, based on the info in this branch and the root problem
        Returns the bound, and the partial solution.
        The partial solution is anything required to either
         1. Repair solution to get a new incumbent, or
         2. Make branching decisions off.
        """
        return self._root_problem.solve(self.get_fixed_vars())

    def _set_root_problem(self, root_problem: RootProblem):
        """
        Sets the root problem
        """
        self._root_problem = root_problem

    @classmethod
    def create_child(cls, node: Node):
        """
        Returns a child of `node`.
        """
        return cls(node)

    @classmethod
    def get_root_node(cls, problem: KnapsackProblem):
        """
        Creates the first root node.
        This starts with formulated the base `RootProblem` for the solver.
        No parent node, and no var fixings.
        """
        node = Node(None)
        node._set_root_problem(RootProblem(problem))
        return node


class BranchAndBoundSolver:
    """
    An instance of branch and bound solver.
    """

    # Default parameters.
    # Should be a dictionary containing parameter -> value
    DEFAULT_PARAMETERS = {}

    def __init__(self, problem: KnapsackProblem) -> None:
        """
        Basic constructor of branch and bound solver for a problem instance
        """
        # Problem instance to solve
        self.problem: KnapsackProblem = problem
        # Grab the default parameter set
        self.parameters = BranchAndBoundSolver.DEFAULT_PARAMETERS
        # Best solution and incumbent
        self.solution: Solution = None
        self._incumbent_solution: Solution = None
        # List of nodes yet to explore
        self._node_list: list[Node] = []

    def solve(self):
        """
        Solves the problem instance using branch and bound.
        """
        # Add in the root node
        self._node_list.append(Node.get_root_node(self.problem))

        # While there are still nodes to explore
        while len(self._node_list) > 0:
            # Get the next node
            node = self._get_next_node()

            # Solve the node
            node_bound, partial_solution = node.solve()

            # Attempt to repair
            repaired_solution = self._heuristic_repair(partial_solution)

            # Did it manage to repair a solution?
            if repaired_solution is not None:
                # Is the incumbent still none?
                if self._incumbent_solution is None:
                    self._incumbent_solution = repaired_solution
                # If not, is this new solution better?
                elif (
                    repaired_solution.objective_value
                    > self._incumbent_solution.objective_value
                ):
                    # Improved solution found!
                    self._incumbent_solution = repaired_solution

            # Check if upper bound < lower bound
            if (
                node_bound < self._incumbent_solution.objective_value
                and self.problem.sense == "max"
            ) or (
                node_bound > self._incumbent_solution.objective_value
                and self.problem.sense == "min"
            ):
                # Bound failed!!
                # Dont branch! Go straight to next node
                continue

            # Create branches
            children = self._make_children(node, partial_solution)
            if children is not None:
                for child in children:
                    self._node_list.append(child)

        # Branch and bound complete
        self.solution = self._incumbent_solution
        return self.solution

    def _get_next_node(self) -> Node:
        """
        use depth first search
        """
        # Use depth first as example...
        return self._node_list.pop(-1)

    def _heuristic_repair(self, partial_solution: np.ndarray) -> Solution | None:
        """
        Attempts to round down repair a partial solution.
        """
        if partial_solution is not None:
            x = np.floor(partial_solution)
            return Solution(x, x.dot(self.problem.p))
        return None

    def _make_children(
        self, parent_node: Node, partial_solution: Any
    ) -> tuple[Node, Node] | None:
        """
        Takes the partial solution, and returns 2 new child nodes.
        These nodes are added to node list in the order they are returned.
        Therefore, branching direction is also technically managed here.
        """
        # Create children.
        child1 = Node.create_child(parent_node)
        child2 = Node.create_child(parent_node)

        # Find the 1 fractional variable in `partial_solution`
        i = np.where((partial_solution > 0) & (partial_solution < 1))[0]
        if len(i) > 0:
            child1.add_fixed_var(i, 0)
            child2.add_fixed_var(i, 1)
            return child1, child2
        # If no fractional, dont branch
        return
