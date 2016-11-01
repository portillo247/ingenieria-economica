##
##
## D E P R E C I A T I O N S
##
##

from cashflow.cashflow import *

class Depreciation():

    def __init__(self,
                 assetsdata,
                 nper     = None,
                 method   = 'SL'):


        if isinstance(assetsdata, tuple):

            ## converts assetsdata to list
            assetsdata = [assetsdata]

        if nper is None:
            #
            for x in assetsdata:
                #
                if nper is None:
                    #
                    nper = x[1] + x[2] # purchase + life
                    #
                else:
                    #
                    nper = max(nper, x[1] + x[2])
                    #

        startbookvalue  = [0] * (nper + 1)
        depreciation    = [0] * (nper + 1)
        endbookvalue    = [0] * (nper + 1)
        investment      = [0] * (nper + 1)

        ## depreciation for each asset
        for asset in assetsdata:

            cost, ppur, life, salvalue = asset

            if method == 'SL':
                #
                assetdep = [((cost - salvalue)/life) for _ in range(life)]
                #
            elif method == 'SOYD':
                #
                sumdig = life * (life + 1) / 2
                assetdep = [(cost - salvalue) * x / sumdig for x in range(life, 0, -1)]
            else:
                #
                raise
                #

            for i in range(life+1):
                #
                t = ppur + i
                if t < nper + 1:
                    if i == 0:
                        investment[t] += cost
                    else:
                        depreciation[t]   += assetdep[i-1]
                        startbookvalue[t] = endbookvalue[t - 1]
                    endbookvalue[t] = startbookvalue[t] + investment[t] - depreciation[t]

            for t in range(ppur+life + 1, nper + 1):
                startbookvalue[t] = endbookvalue[t - 1]
                endbookvalue[t] = startbookvalue[t]

        self._nper           = nper
        self._startbookvalue = startbookvalue
        self._investment     = investment
        self._depreciation   = depreciation
        self._endbookvalue   = endbookvalue


    def depreciation(self):
        """gets depreciation"""
        return Cashflow(self._nper,
                        [(t, -self._depreciation[t]) for t in range(self._nper + 1)])
    def investment(self):
        """gets depreciation"""

        return Cashflow(self._nper,
                        [(t, -self._investment[t]) for t in range(self._nper + 1)])




    def __repr__(self):
        """print function"""

        s = []

        # s.append('Cost:          {:12.2f}'.format(self._cost))
        # s.append('Salvage Value: {:12.2f}'.format(self._salvalue))
        # s.append('Useful Life:   {:9d}'.format(self._life))
        # s.append('')

        #
        s.append('   t     StartBookValue     Investment   Depreciation   EndBookValue')
        s.append('----------------------------------------------------------------------')
        #
        for i in range(self._nper + 1):

            fmt = ' {:3d}       {:12.2f}   {:12.2f}   {:12.2f}   {:12.2f}'
            s.append(fmt.format(i,
                                self._startbookvalue[i],
                                self._investment[i],
                                self._depreciation[i],
                                self._endbookvalue[i]))
        return '\n'.join(s)
