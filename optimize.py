from scipy.optimize import least_squares
from single_point import *


def func(math_params):
    phys_params = math_params / scaling_vector
    with open("parameter", "w") as f:
        for k, p in zip(types, phys_params):
            f.write(f"{k:10s}{p:15.10f}\n")
    calc_hfes = np.array(getHFE())
    return hfes - calc_hfes


def main():
    global p_ref, weights
    p_ref, weights = np.loadtxt("ref.prm", usecols=(1, 2), unpack=True, dtype="float")
    p0 = np.loadtxt("parameter", usecols=(1,), unpack=True, dtype="float")
    global scaling_vector
    scaling_vector = np.array([1.0, 30.0])
    p0_math = p0 * scaling_vector
    global hfes
    hfes = np.loadtxt("hfe_expt.txt", usecols=(1,), unpack=True, dtype="float")
    global types
    types = np.loadtxt("parameter", usecols=(0,), unpack=True, dtype="str")
    lower, upper = np.loadtxt("ref.prm", usecols=(2, 3), unpack=True, dtype="float")
    ret = least_squares(func, p0_math, verbose=2, diff_step=0.000001, ftol=0.000001, gtol=0.000001, xtol=0.000001,
                        bounds=(lower, upper))
    return


# execute
if __name__ == "__main__":
    main()
