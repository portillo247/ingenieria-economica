##
##
##  I N T E R E S T    R A T E    C O N V E R S I O N S
##
##

import math
import numpy as np

def eff2nom(eff,          # effective rate per year
            cyr = None):  # number of compounding periods per year

    eff = np.array(eff)

    ##
    ## continuous rate
    ##
    if cyr is None:

        return (np.log(1 + eff)).tolist()

    ##
    ## periodic rate
    ##
    cyr = np.array(cyr)

    # efective per compounding period
    r = np.power(1 + eff, 1 / abs(cyr)) - 1


    if isinstance(r, np.float64):

        if cyr < 0:

            # anticipated periodic rate
            r = r / (1 + r)

    else:

        # anticipated periodic rate
        r[r < 0] = r[r < 0] / (1 + r[r < 0])

    # nominal interest rate
    return (abs(cyr) * r).tolist()



def nom2eff(nom,           # nominal per year
            cyr = None):   # number of compounding periods per year

    nom = np.array(nom)

    ##
    ## continuous rate
    ##
    if cyr is None:

        return (np.exp(nom) - 1).tolist()

    ##
    ## periodic rate
    ##
    cyr = np.array(cyr)

    # efective per compounding period 
    r = nom / abs(cyr)

    # anticipated rate
    if isinstance(r, np.float64):

        if cyr < 0:
            r = r / (1 - r)

    else:

        r[r < 0] = r[r < 0] / (1 - r[r < 0])

    # if cyr < 0:
    #
    #    # anticipated rate
    #    r = r / (1 - r)

    return (np.power(1 + r, abs(cyr)) - 1).tolist()
