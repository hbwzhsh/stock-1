import util.lppltool as lppltool
from matplotlib import pyplot as plt
import datetime
import numpy as np
import pandas as pd
import seaborn as sns

sns.set_style('white')

limits = ([8.4, 8.8], [-1, -0.1], [350, 400], [.1, .9], [-1, 1], [12, 18], [0, 2 * np.pi])
x = lppltool.Population(limits, 20, 0.3, 1.5, .05, 4)
for i in range(2):
    x.Fitness()
    x.Eliminate()
    x.Mate()
    x.Mutate()

x.Fitness()
values = x.BestSolutions(3)
for x in values:
    print
    x.PrintIndividual()