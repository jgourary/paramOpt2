import os
import time
import subprocess
import numpy as np
import concurrent.futures


def writeprm():
    types, params = np.loadtxt("parameter", dtype="str", unpack=True)
    prmdict = dict(zip(types, params))
    lines = open("amoeba09_template_unused.prm").readlines()
    with open("amoeba09.prm_", "w") as f:
        for line in lines:
            if "PRM_" in line:
                for k, v in prmdict:
                    search = "PRM_" + k + "_"
                    if search in line and (line[0:1] != "#"):
                        replaceStr = "%10.8f" % (float(v))
                        line = line.replace(search, replaceStr)
            f.write(line)
    return


def submit(dirname):
    os.system(f"cp amoeba09.prm_ {dirname}")
    homedir = "/home/jtg2769/software/paramOpt2"
    os.chdir(os.path.join(homedir, dirname))
    subcmd = "python /home/jtg2769/lanthanides/autoBAR/autoBAR.py auto"
    subprocess.run(subcmd, shell=True)
    return


def getFirstElementOfFileAsList(filename):
    with open(filename) as f:
        first_line = f.readline()
        first_element = first_line.split()[0]
    return [first_element]


def getHFE():
    homedir = "/home/jtg2769/software/paramOpt2"
    #  dirnames = list(np.loadtxt("hfe_expt.txt", usecols=(0,), dtype="str", unpack=True))
    dirnames = getFirstElementOfFileAsList("hfe_expt.txt")
    for dirname in dirnames:
        os.system(
            f"rm -f {homedir}/amoeba09.prm_ {homedir}/{dirname}/amoeba09.prm_ {homedir}/{dirname}/result.txt; wait")
        os.system(
            f"rm -f {homedir}/{dirname}/gas/gas-e200-v200.* {homedir}/{dirname}/liquid/liquid-e200-v200.* {homedir}/{dirname}/liquid/liquid-e100-v100.bar {homedir}/{dirname}/liquid/liquid-e100-v100.ene; wait")
    writeprm()

    jobs = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        results = [executor.submit(submit, dirname) for dirname in dirnames]
        for f in concurrent.futures.as_completed(results):
            jobs.append(f.result())

    while True:
        hfes_calc = []
        for dirname in dirnames:

            resultfile = os.path.join(homedir, dirname, "result.txt")
            print("looking for " + resultfile)
            if os.path.isfile(resultfile):
                print("found " + resultfile)
                lines = open(resultfile).readlines()
                for line in lines:
                    if "SUMMARY OF THE TOTAL FREE ENERGY" in line:
                        print(line)
                        fields = line.split()
                        hfes_calc.append(float(fields[6]))
        if len(hfes_calc) == len(dirnames):
            break
        else:
            print("Length of HFEs = " + str(len(hfes_calc)))
            print("Length of dirs = " + str(len(dirnames)))
            time.sleep(300)
    print("Current HFEs", hfes_calc)
    return hfes_calc
