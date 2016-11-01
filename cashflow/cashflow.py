##
##
## G E N E R I C    C A S H F L O W     S P E C I F I C A T I O N
##
##

from cashflow.rate import *
from cashflow.tvm  import *
import numpy as np

class Cashflow:

    def __init__(self,            # 
                 nper,            # number of periods
                 spec  = None):   # specification
        """initialize all internal variables (registers)"""

        self.__nper = nper                  # number of periods
        self.__cashflow = [0] * (nper + 1)  # cashflow of zeros

        if spec is not None:
            self.add(spec)

    def copy(self):
        #
        x = Cashflow(self.__nper)
        x.__cashflow = [w for w in self.__cashflow]
        return x


    def nper(self):
        return self.__nper

    # def cashflow(self):
    #    return [x for x in self.__cashflow]

    def timeOffset(self, start = None, end = None):
        #
        if start is not None and start > 0:
            #
            self.__cashflow = [0] * start + self.__cashflow
            self.__nper += start
            #

        if end is not None and end > 0:
            #
            self.__cashflow = self.__cashflow + [0] * end
            self.__nper += end

    ##
    ## conversion to list
    ##
    def tolist(self):
        #
        return [w for w in self.__cashflow]
        #

    ##
    ## adds the specification to the current casflow
    ##
    def add(self, spec):

        ##
        ## spec is a number
        ##
        if isinstance(spec, int) or isinstance(spec, float):
            self.__cashflow = [w + spec for w in self.__cashflow]
            return self

        ##
        ## spec is a tuple (time, value)
        ##
        if isinstance(spec, tuple):

            ## tuple
            t, value = spec
            if t <= self.__nper:
                self.__cashflow[t] = value
            return self

        ##
        ## spec is a list of tuples (time, value)
        ##
        if isinstance(spec, list):
            #
            for t, value in spec:
                #
                if t <= self.__nper:
                    self.__cashflow[t] += value
                #
            return self

        raise

    ##
    ## substracts the specification to the current casflow
    ##
    def sub(self, spec):
        #
        if isinstance(spec, int) or isinstance(spec, float):
            #
            # spec is a number
            #
            spec = -spec
            #
        elif isinstance(spec, tuple):
            #
            # spec is a tuple (time, value)
            #
            spec = (spec[0], -spec[1])
            #
        elif isinstance(spec, list):
            #
            # spec is a list of tuples (time, value)
            #
            spec = [(t, -v) for t, v in spec]
            #
        return self.add(spec)



    ##
    ## cashflow print function
    ##
    def __repr__(self):
        """print function"""

        s = []

        #
        s.append('  time                Values')
        s.append('-----------------------------')
        #

        cashflow = [round(x, 2) for x in self.__cashflow]

        i = 0
        while i < len(cashflow):

            freq = 1

            ## count the number of times
            while i + freq < len(cashflow) and cashflow[i] == cashflow[i + freq]:
                #
                freq += 1
                #

            if freq == 1:
                #
                time = ' {:d} '.format(i)
                #
            else:
                #
                time = ' {:d}-{:d} '.format(i, i + freq - 1)
                #

            s.append(' {:7s}        {:12.2f}'.format(time, cashflow[i]))

            i += freq

        return '\n'.join(s)


    ##
    ## cashflow chart function
    ##
    def textchart(self):
        """print function"""

        s = []
        s.append('  time         (-)     |        (+)')
        s.append('-----------------------------------------')

        cashflow = [round(x, 2) for x in self.__cashflow]

        i = 0
        while i < len(cashflow):

            freq = 1

            ## count the number of times
            while i + freq < len(cashflow) and cashflow[i] == cashflow[i + freq]:
                #
                freq += 1
                #

            if freq == 1:
                #
                time = ' {:d} '.format(i)
                #
            else:
                #
                time = ' {:d}-{:d} '.format(i, i + freq - 1)
                #

            if cashflow[i] > 0:
                s.append(' {:7s}               |  {:12.2f}'.format(time, cashflow[i]))
            elif cashflow[i] < 0:
                s.append(' {:7s} {:12.2f}  |  '.format(time, -cashflow[i]))
            else:
                s.append(' {:7s}               |  '.format(time))


            i += freq

        return '\n'.join(s)

    ##
    def __add__(self, other):

        ##
        if isinstance(other, int) or isinstance(other, float):
            #
            x = self.copy()
            x.__cashflow = [v + other for v in x.__cashflow]
            return x

        if self.__nper > other.__nper:

            x = self.copy()
            for n in range(len(other.__cashflow)):
                #
                x.__cashflow[n] += other.__cashflow[n]
                #

        else:

            x = other.copy()
            for n in range(len(self.__cashflow)):
                #
                x.__cashflow[n] += self.__cashflow[n]
                #

        return x

    ##
    def __radd__(self, other):

        if other == 0:
            return self
        else:
            return self.__add__(other)

    ##
    def __sub__(self, other):
        #
        if isinstance(other, (int, float)):
            #
            return self.__add__(-other)
            #
        other.__cashflow = [-w for w in other.__cashflow]
        return self.__add__(other)

    ##
    def __mul__(self, other):

        ##
        if isinstance(other, int) or isinstance(other, float):
            #
            x = self.copy()
            for t in range(len(self.__cashflow)):
                #
                x.__cashflow[t] *= other
                #
            return x


        if self.__nper > other._nper:

            x = self.copy()
            for n in range(len(other.__cashflow)):
                #
                x.__cashflow[n] *= other.__cashflow[n]
                #

        else:

            x = self.copy()
            for n in range(len(self.__cashflow)):
                #
                x.__cashflow[n] *= self.__cashflow[n]
                #

        return x

    ##
    def __div__(self, other):
        #
        if isinstance(other, int) or isinstance(other, float):
            #
            return self.__mul__(1.0 / other)
            #
        other.__cashflow = [1 / w for w in other.__cashflow]
        return self.__mul__(other)

    ##
    def __len__(self):
        #
        return len(self.__cashflow)
        #

    ##
    def __setitem__(self, key, value):
        #
        self.__cashflow[key] = value
        #

    ##
    def __getitem__(self, key):
        #
        return self.__cashflow[key]
        #







def afterTaxCashflow(x,         # cashflow
                     taxRate):  # tax rate
    #
    if isinstance(taxRate, int) or isinstance(taxRate, float):
        #
        r = taxRate
        taxRate = Rate(taxRate, x.nper())
        taxRate[0] = r
        #
    r = x.copy()
    for t in range(r.nper()+1):
        if r[t] > 0:
            r[t] *= -taxRate[t]
        else:
            r[t] = 0
    return r



def const2curr(x,                  # cashflow
               inflationRate = 0,  #
               t0 = 0):            # 

    if isinstance(inflationRate, (int, float)):
        #
        inflationRate = Rate(inflationRate, x.nper())
        #

    factor = inflationRate.toCurrent(t0)

    r = x.copy()

    for t in range(r.nper() + 1):
        #
        r[t] *= factor[t]
        #

    return r


def curr2const(x,                  # cashflow
               inflationRate = 0,  # rate obj
               t0 = 0):            #

    if isinstance(inflationRate, int) or isinstance(inflationRate, float):
        #
        inflationRate = Rate(inflationRate, x.nper())
        #

    factor = inflationRate.toConstant(t0)

    r = x.copy()

    for t in range(r.nper() + 1):
        #
        r[t] *= factor[t]
        #

    return r

def currencyConv(x,                  # cashflow
                 exchangeRate = 1,   #
                 devaluation  = 0,   # external inflation rate
                 t0           = 0):  # time

    if isinstance(devaluation, int) or isinstance(devaluation, float):
        #
        devaluation = Rate(devaluation, x.nper())
        #

    factor = devaluation.toCurrent(t0)

    r = x.copy()

    for t in range(r.nper() + 1):
        #
        r[t] *= exchangeRate * factor[t]
        #

    return r


##
## Discounted cash flow analysis
##
def _timevalue(rate, cashflow, t0 = 0, nper = None):

    def calc_net_value(r, y):
        # r -- rate object
        # y -- cashflow object
        nv = 0
        factor = r.toConstant(t0)
        for t in range(y.nper() + 1):
            nv += y[t] * factor[t]
        return nv

    if nper is not None:
        #
        t0 = 0
        #

    m = 1

    if isinstance(rate, list) and isinstance(cashflow, list):
        #
        if len(rate) != len(cashflow):
            #
            print("list must be the same length")
            raise
            #
        m = len(rate)
        #
    elif isinstance(rate, list):
        #
        m = len(rate)
        #
    elif isinstance(cashflow, list):
        #
        m = len(cashflow)
        #

    if isinstance(cashflow, Cashflow):
        #
        cashflow = [cashflow] * m
        #

    if isinstance(rate, (int, float, Rate)):
        #
        rate = [rate] * m
        #

    for i in range(len(rate)):
        #
        if isinstance(rate[i], (int, float)):
            #
            rate[i] = Rate(initRate = rate[i], nper = cashflow[0].nper())
            #

    result_npv = []
    result_pmt = []
    result_bca = []

    for i in range(m):
        #
        # npv
        #
        r = calc_net_value(rate[i], cashflow[i])
        result_npv.append(r)
        #
        # bca
        #
        poscf = Cashflow(cashflow[i].nper())
        poscf.add([(t, max(0, w)) for t, w in enumerate(cashflow[i].tolist())])

        negcf = Cashflow(cashflow[i].nper())
        negcf.add([(t, min(0, w)) for t, w in enumerate(cashflow[i].tolist())])

        num = calc_net_value(rate[i], poscf)
        den = calc_net_value(rate[i], negcf)

        if den != 0:
            result_bca.append( -num /  den)
        else:
            result_bca.append(0)
        #
        # nus
        #
        if nper is not None:
            mrate = rate[i].meanrate()
            result_pmt.append(-tvm(rate = mrate, nper = nper, pv = r).PMT())
        else:
            result_pmt.append(None)

    if len(result_npv) == 1:
        return (result_npv[0], result_pmt[0], result_bca[0])

    return (result_npv, result_pmt, result_bca)


def npv(rate, x, t0 = 0):
     r, _, _ = _timevalue(rate, cashflow = x, t0 = t0)
     return r

def nus(rate, x, nper):
    _, r, _ = _timevalue(rate, cashflow = x, nper = nper)
    return r

def bca(rate, x):
    _, _, r = _timevalue(rate, cashflow = x)
    return r


## calculate the periodic internal rate of return
def irr(x):
    if isinstance(x, Cashflow):
        x = [x]
    r = []
    for f in x:
        r.append(np.irr(f.tolist()))
    if len(r) == 1:
        return r[0]
    return r

## modified internal rate of return
def mirr(x, finance_rate = 0, reinvest_rate = 0):
    # negativos: finance_rate
    # positivos: reinvest_rate
    if isinstance(x, Cashflow):
        x = [x]
    r = []
    for f in x:
        r.append(np.mirr(f.tolist(), finance_rate, reinvest_rate))
    if len(r) == 1:
        return r[0]
    return r

def table(x):

    print(' #               Value    ')
    print('------------------------')
    #
    x = [round(w, 4) for w in x]

    for i in range(len(x)):
        print(' {:<3d}    {:14.4f}'.format(i, x[i]))
