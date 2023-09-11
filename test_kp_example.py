from knapsack_example import KnapsackProblem, BranchAndBoundSolver
from docplex.mp.model import Model


def test_agree():
    # Create problem instance
    n = 100
    kp = KnapsackProblem(n)

    # Solve using cplex
    m = Model()
    x = m.binary_var_list(n)
    m.add_constraint(m.dot(x, kp.w) <= kp.c)
    m.maximize(m.dot(x, kp.p))
    m.solve()
    cplex_obj = m.objective_value

    # Solve using branch and bound
    bnb = BranchAndBoundSolver(kp)
    bnb.solve()
    bnb_obj = bnb.solution.objective_value

    # Make sure they agree
    assert cplex_obj == bnb_obj
