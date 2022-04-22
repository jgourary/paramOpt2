import time, sys
import numpy as np
import subprocess
import os
from multiprocessing import Pool

os.system("rm -rf ./out/*.out ")


def subOneAnalyzeJob(filename):
    analyze_exe = "/home/jtg2769/lanthanides/Parametrization/analyze"
    cmd_str = "%s ./txyz/%s.txyz -key tinker.key E> ./out/%s.out" % (analyze_exe, filename, filename)
    subprocess.run(cmd_str, shell=True)
    return


def subParallelJobs(filelist):
    filenames = [line.split(".txyz")[0] for line in open(filelist).readlines()]
    p = Pool(20)
    p.map(subOneAnalyzeJob, filenames)
    p.close()
    return


def getEnergy(filelist, savetxt):
    print("Submitting analyze jobs...")
    subParallelJobs(filelist)
    # Check whether all analyze jobs finished!
    print("Waiting for analyze jobs...")
    files = [line.split(".txyz")[0] for line in open(filelist).readlines()]
    nFile = len(files)
    readFlag = 0
    while readFlag == 0:
        cmdstr1 = "grep 'Total Potential Energy' out/*.out > result.p"
        subprocess.run(cmdstr1, shell=True)
        nLines1 = sum(1 for line in open("result.p"))
        if nLines1 == nFile:
            readFlag = 1
            break
        else:
            time.sleep(0.5)

    MM_inter = []
    if readFlag == 1:
        for eachFile in files:
            filename = "out/%s.out" % eachFile
            for line1 in open(filename).readlines():
                if "Intermolecular Energy " in line1:
                    inter = float(line1.split()[-2])
                    MM_inter.append(inter)
        MM_inter = np.array(MM_inter)
        if savetxt:
            np.savetxt("MM-energy.dat", np.transpose([MM_inter]), fmt="%15.4f")
    return MM_inter
