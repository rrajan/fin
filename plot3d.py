#!/usr/bin/python

import sys
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print "need input"
        sys.exit(1)

    df = pd.read_csv(sys.argv[1])
    threedee = plt.figure().gca(projection='3d')
    threedee.scatter(df['Tau'], df['Strike'], df['IV'])
    threedee.set_xlabel('Tau')
    threedee.set_ylabel('Strike')
    threedee.set_zlabel('IV')
    plt.show()
