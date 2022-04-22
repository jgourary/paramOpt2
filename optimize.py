from scipy.optimize import least_squares
from single_point import *
from subMM import *
import numpy as np
import math


def func(math_params):
    phys_params = math_params / scaling_vector
    with open("parameter", "w") as f:
        for k, p in zip(types, phys_params):
            f.write(f"{k:10s}{p:15.10f}\n")

    #  Cost from hydration free energy from BAR vs experimental HFE
    calc_hfes = np.array(getHFE())
    hfeCost = abs(hfes - calc_hfes)  # this may be wrong for multiple experiments
    print("hfe cost = " + str(hfeCost))

    #  Cost from QM vs MM interaction energy curves
    QM = np.loadtxt('QM-energy.dat', usecols=(-1,), unpack=True)
    MM = getEnergy('filelist', True)
    IEcost = 0
    i = 0
    while i < len(QM):
        IEcost += ((QM[i] - MM[i]) ** 2)
        i += 1
    IEcost = math.sqrt(IEcost / len(MM))
    print("Interaction energy cost = " + str(IEcost))
    totalCost = 0.75 * hfeCost + 0.25 * IEcost
    print("Total cost = " + str(totalCost))
    return totalCost


def main():
    global p_ref, weights
    p_ref, weights = np.loadtxt("ref.prm", usecols=(1, 2), unpack=True, dtype="float")
    p0 = np.loadtxt("parameter", usecols=(1,), unpack=True, dtype="float")
    global scaling_vector
    scaling_vector = np.array([1.0, 1.0])
    p0_math = p0 * scaling_vector
    global hfes
    hfes = np.loadtxt("hfe_expt.txt", usecols=(1,), unpack=True, dtype="float")
    global types
    types = np.loadtxt("parameter", usecols=(0,), unpack=True, dtype="str")
    lower, upper = np.loadtxt("ref.prm", usecols=(2, 3), unpack=True, dtype="float")
    print("p0_math:" + str(p0_math))
    ret = least_squares(func, p0_math, verbose=2, diff_step=0.000001, ftol=0.000001, gtol=0.000001, xtol=0.000001,
                        bounds=(lower, upper))
    return


# execute
if __name__ == "__main__":
    main()
