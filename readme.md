# Abstract Branch and Bound

This repository contains a structured template for a branch and bound algorithm.
This allows for rapid testing and experimentation of your B&B ideas.

**The purpose is not for performance! The purpose is quick implementation for prototyping branch and bound ideas!**

So copy or fork this repo, and apply it to your own problem by filling in the blank lines.

> *fail fast* -someone clever

## Contents

The main part of the code consists 5 Python classes within `branch_and_bound.py`.
Here is a brief introduction, however for more information please read the documentation within `branch_and_bound.py`.

### 1. `Problem`

`Problem` should contain all the relevant information for you specific problem instance.
This includes all parameters required to generate & solve an instance of this problem.
For ease of use, consider using this object in one of the following ways:

1. As an inheritance of a common algebraic modelling package, such as a `docplex.mp.model.Model` object.
See [example here](https://github.com/sandyspiers/euclidean_maximisation/blob/main/emsca/model.py).
2. Use class methods as instance generators.
Great for generating instances of a particular structure.

### 2. `Solution`

This should just be a basic container for a solution.
Can be considered as only a dataclass if need.
But it **must** always contain feasible solution!
And it **must** always have an `objective_value` attribute!

### 3. `RootProblem`

In many cases, implementation is far easier when we have a so called *root problem*.
This is essentially an optimisation problem formulation of the problem instance, before any variable fixings.
This class shall handle that model, and then also has a `solve(fixings)` method that can solve the root problem, with given variable fixings.
For example, this could be the base MIP created from a problem instance.
Then variable fixings are added based on the branch and bound tree.
After the node problem is solved, these fixings are removed from the root problem.

### 4. `Node`

The node object contains all information to generate a specific node.
This includes which variables are fixed, which are free etc.
This could either contain itself an entire model, or simply a reference to the root problem.

### 5. `Solver`

This is the main part of the code.
Realistically, any user of this code should only ever interface with this object to either

1. Set any `parameters`,
2. Call the `solve()` method,
3. Retrieve the `solution`.

Everything else should be considered as private.

For the branch and bound process, the object has the following important attributes,

* `_node_list`
* `_incumbent_solution`

The main branch and bound iterations are handled inside `solve()`.
Within these iterations, we call the following important methods,

* `_get_next_node()`
* `_heuristic_repair()`
* `_make_children()`

All should be self explanatory, however for more information on the purpose of each method see documentation inside `branch_and_bound.py`.

## Usage

This repo is designed as a template.
Therefore, the idea is to grab the code within `branch_and_bound.py`, and fill in the blanks for your own purpose.
An example of this is shown in `knapsack_example.py`, where we fill in the branch and bound solver to solve a basic 0-1 knapsack problem.
The implementation simply fills in the code from `branch_and_bound.py`.

## Tests

There are several test provided in `test_bnb_solver.py`.
These should be appropriate for any implementation, and can be used to ensure you don't break any of the code when adjusting for your own implementation.
It's a good idea to also check your implementation against another method to solve the problem.  For the knapsack example, we test that the branch and bound solver matches the solution found from `cplex`.

## Contributions

We welcome and appreciate all contributions!
Especially any changes that might make the template easier to understand / use / implement / extend.
