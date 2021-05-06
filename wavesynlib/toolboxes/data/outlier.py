from numpy import empty
from sklearn.cluster import DBSCAN



def dbscan_detect_outliers(*args, **kwargs):
    len_args = len(args)
    samples = None
    if len_args == 0:
        raise TypeError("Missing sample input.")
    elif len_args == 1:
        samples = args[0]
    else:
        samples = empty((len(args[0]), len_args))
        for i in range(len_args):
            samples[:, i] = args[i]
    clustering = DBSCAN(**kwargs).fit(samples)
    return clustering.labels_ == -1
