from math import cos
import sympy
import quantities as pq



def beam_width(lambda_, N, d, theta=0, k=0.886):
    """
See https://www.analog.com/en/analog-dialogue/articles/phased-array-antenna-patterns-part1.html#
"""
    if isinstance(lambda_, pq.Quantity):
        lambda_ = lambda_.rescale(pq.meter).magnitude
    if isinstance(d, pq.Quantity):
        d = d.rescale(pq.meter).magnitude
    if isinstance(theta, pq.Quantity):
        theta = theta.rescale(pq.rad).magnitude
    return k*lambda_/(N*d*cos(theta))



def beam_width_equation(lambda_=None, N=None, d=None, theta=None, thetaB=None, k=0.886):
    """
See https://www.analog.com/en/analog-dialogue/articles/phased-array-antenna-patterns-part1.html#
"""
    if lambda_ is None:
        lambda_ = sympy.var("λ")
    elif isinstance(lambda_, pq.Quantity):
        lambda_ = lambda_.rescale(pq.meter).magnitude
    else:
        pass

    if N is None:
        N = sympy.var("N")

    if d is None:
        d = sympy.var("d")
    elif isinstance(d, pq.Quantity):
        d = d.rescale(pq.meter).magnitude

    if theta is None:
        theta = sympy.var("θ")
    elif isinstance(theta, pq.Quantity):
        theta = theta.rescale(pq.rad).magnitude

    if thetaB is None:
        thetaB = sympy.var("θ_B")
    elif isinstance(thetaB, pq.Quantity):
        thetaB = thetaB.rescale(pq.rad).magnitude

    eq = k*lambda_/(N*d*sympy.cos(theta)) - thetaB

    return sympy.solve(eq, set=True)




if __name__ == "__main__":
    result = beam_width_equation(lambda_=0.2*pq.meter, d=0.1*pq.meter, theta=0, thetaB=1*pq.degree)
    print(result)
