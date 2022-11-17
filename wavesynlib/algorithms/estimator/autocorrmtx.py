from numpy import correlate, c_, r_


def autocorrelate(x):
    return correlate(x, x, mode='full')


def Rx(x, m=None):
    """Estimate autocorrelation matrix of vector x.
x: signal vector;
m: size of Rx
return value: estimated autocorrelation matrix."""
    N = len(x)
    if m is None:
        m = N
    else:
        raise ValueError(
            'The number of rows/columns of R should less than or equal to vector lenght N.'
        )
    # generate a indices matrix, as
    # 0 -1 -2 -3 ...
    # 1  0 -1 -2 ...
    # 2  1  0 -1 ...
    # 3  2  1  0 ...
    # ... 
    indices = c_[:m] - r_[:m]
    ac = autocorrelate(x)
    # using autocorrelation samples and indices matrix to create Rx
    # Rx =
    #   r[ 0] r[-1] r[-2] r[-3] ...
    #   r[ 1] r[ 0] r[-1] r[-2] ...
    #   r[ 2] r[ 1] r[ 0] r[-1] ...
    #   r[ 3] r[ 2] r[ 1] r[ 0] ...
    #  ... 
    return ac[indices + N - 1] / N
