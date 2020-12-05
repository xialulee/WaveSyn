import numpy as np



def get_cluster_slices(arr):
    bound = arr[1:] == arr[:-1]
    bound = np.where(bound==False)[0]
    bound = np.vstack((bound, bound+1))
    bound = bound.flatten("F")
    bound = np.hstack((0, bound, len(arr)-1))
    bound = bound.reshape((-1, 2))
    bound[:, 1] += 1
    slices = np.apply_along_axis(lambda row: slice(*row), axis=1, arr=bound)
    return slices



if __name__ == "__main__":
    test_array = np.array([1,1,1,1,2,3,3,4,4,4,4,5])
    print("Test array for get_cluster_indexes:")
    print(test_array)
    slices = get_cluster_slices(test_array)
    print("result:")
    for slice_ in slices:
        print(test_array[slice_])
