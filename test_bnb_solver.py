from branch_and_bound import Problem, RootProblem, Node, BranchAndBoundSolver


def test_problem_example_generator():
    problem = Problem.example_generator()
    assert isinstance(problem, Problem)
    assert problem.sense in ["min", "max"]


def test_root_problem_initialization():
    problem = Problem()
    root_problem = RootProblem(problem)
    assert root_problem.problem == problem


def test_node_initialization():
    node = Node(None)
    assert node._parent_node is None


def test_node_make_children():
    problem = Problem()
    node = Node.get_root_node(problem)
    child = Node.create_child(node)
    assert isinstance(child, Node)
    assert child._parent_node == node


def test_node_fixed_var():
    problem = Problem()
    node = Node.get_root_node(problem)
    assert node._fixed_var == None
    assert node.get_fixed_vars() == []
    node.add_fixed_var("var1", 1)
    assert node._fixed_var == ("var1", 1)
    assert node.get_fixed_vars() == [("var1", 1)]


def test_node_get_fixed_vars():
    problem = Problem()
    node1 = Node.get_root_node(problem)
    node1.add_fixed_var("var1", 1)
    node2 = Node.create_child(node1)
    node2.add_fixed_var("var2", 2)

    assert node1.get_fixed_vars() == [("var1", 1)]
    assert node2.get_fixed_vars() == [("var2", 2), ("var1", 1)]


def test_solver_initialization():
    problem = Problem()
    solver = BranchAndBoundSolver(problem)
    assert solver.problem == problem
