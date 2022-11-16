from __future__ import annotations

from typing import Tuple, Final
from itertools import combinations_with_replacement, product

from numpy import (
    log10, eye, zeros, r_, ndarray,
    atleast_1d, real, sin, exp, radians, kron, outer, pi as π,
    concatenate, sum
)
from numpy.linalg import eigvals
import cvxpy as cp
import quantities as pq

jπ: Final = 1j * π



def make_steering_matrix(M: int, θvec: ndarray | pq.Quantity) -> ndarray:
    """Make steering matrix.
M:    The number of array elements.
θvec: The angle samples (default unit is degree)."""
    θvec = atleast_1d(θvec)
    if isinstance(θvec, pq.Quantity):
        θvec = θvec.rescale(pq.rad).magnitude
    else: 
        # If no unit specified, assume the input is in degree.
        θvec = radians(θvec)
    # outer will auto flatten the two inputs. 
    return exp(jπ * outer(r_[:M], sin(θvec)))



def make_permutation_matrix(M: int) -> ndarray:
    """Return a complex M²xM² permutation matrix which satisfies vec(R)=Jr.
M: The number of array elements."""
    P = zeros((M*M,)*2, complex)
    k = 0
    addr_table = {}
    for q, p in combinations_with_replacement(range(M), 2):
        addr_table[p, q] = k
        k += (1 if p == q else 2)
    for q, p in product(range(M), repeat=2):
        row = q * M + p
        addr = addr_table[max(p, q), min(p, q)]
        if p == q:
            P[row, addr] = 1
        else:
            P[row, addr] = 1
            P[row, addr+1] = (1j if p > q else -1j)
    return P



def make_quadform_matrix(M: int, pattern: Tuple[ndarray|pq.Quantity, ndarray]) -> ndarray:
    θvec, avec = pattern
    N = θvec.size
    A = make_steering_matrix(M, θvec)
    P = make_permutation_matrix(M)
    G = 0
    for a, m in zip(A.T, avec):
        t = -(P.T @ kron(a, a.conj()))
        # Axis = None means flatten and concat
        g = concatenate((m, t), axis=None)
        G += outer(g, g).real
    
    G /= N
    # Insure that G is positive semi-definite.
    min_ev = min(real(eigvals(G)))
    if min_ev < 0.0:
        δ = 10 ** (2/3 * log10(-min_ev))
        G += δ * eye(M*M + 1)
    return G



def corrmtx2pattern(R: ndarray, θvec: ndarray | pq.Quantity) -> ndarray:
    M = R.shape[0]
    A = make_steering_matrix(M, θvec)
    p = sum((A.conj() * (R @ A)).real, axis=0)
    return p / max(p)



def make_problem(M: int, quadform_matrix: ndarray) -> Tuple[cp.Problem, cp.Variable]:
    Γ = quadform_matrix
    P = make_permutation_matrix(M)
    R = cp.Variable((M, M), hermitian=True)
    ρ = cp.Variable((M*M+1,))
    α, r = ρ[0], ρ[1:]
    ρᴴΓρ = cp.quad_form(ρ, Γ)
    problem = cp.Problem(
        cp.Minimize(ρᴴΓρ), [
            R >> 0, # Positive-Semidefinite
            α >= 0, 
            cp.vec(R) == P @ r, 
            cp.diag(cp.real(R)) == 1
        ]
    )
    return problem, R
