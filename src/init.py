import os
import numpy as np


def initialise_project():
    create_directories()
    pass

def create_directories():
    empty_directories = np.array(["output",
                                  "data",
                                  "images"])
    for i in empty_directories:
        if not os.path.exists(i):
            os.makedirs(i)
    pass

