##
##
##  L O A N    C A L C U L A T I O N
##
##
import numpy as np
from cashflow.cashflow import *
from cashflow.rate import *


##
## base class for computations
##
class Loan():

    ##
    ## class constructor
    ##
    def __init__(self):
        #
        self._life   = None
        self._grace  = None
        self._amount = None
        self._intpmt = None
        self._capint = None

    ##
    ## conversion to generic cashflow object
    ##
    def toCashflow(self, taxRate = 0):

        if isinstance(taxRate, int) or isinstance(taxRate, float):
            #
            taxRate = Rate(initRate = taxRate, nper = self._life + self._grace)
            #

        r = Cashflow(self._grace + self._life)

        ##
        ## payments per period
        ##
        for t in range(self._grace + self._life + 1):
            #
            if t == 0:
                #
                r[t] =  self._amount
                # 
            r[t] += -self._totpmt[t] + self._intpmt[t] * taxRate[t]
            #

        return r

    def trueRate(self, taxRate = 0):
        ##
        ## internal rate of return
        ##
        return irr(self.toCashflow(taxRate))



    ##
    ## string representation
    ##
    def __repr__(self):
        """print function"""

        s = []

        s.append('')

        #
        s.append('   t          Beginning         Total      Interest     Principal        Ending')
        s.append('              Principal       Payment       Payment       Payment     Principal')
        s.append('--------------------------------------------------------------------------------')
        #
        for i in range(self._grace + self._life + 1):

            fmt = ' {:3d}       {:12.2f}  {:12.2f}  {:12.2f}  {:12.2f}  {:12.2f}'
            s.append(fmt.format(i,
                                self._begppalbal[i],
                                self._totpmt[i],
                                self._intpmt[i],
                                self._ppalpmt[i],
                                self._endppalbal[i]))
        return '\n'.join(s)

    def interest(self):
        x = Cashflow(self._life + self._grace,
                     spec = [(t, v) for t, v in enumerate(self._intpmt)])
        return x

    def begbal(self):
        x = Cashflow(self._life + self._grace,
                     spec = [(t, v) for t, v in enumerate(self._begppalbal)])
        return x

    def endbal(self):
        x = Cashflow(self._life + self._grace,
                     spec = [(t, v) for t, v in enumerate(self._endppalbal)])
        return x

    def ppalpmt(self):
        x = Cashflow(self._life + self._grace,
                     spec = [(t, v) for t, v in enumerate(self._ppalpmt)])
        return x





def _checklength(cashflow, n):
    #
    # verify the length of the seies
    #
    if cashflow is None:
        return Cashflow(n)

    if cashflow is not None and cashflow.nper() < n:
        #
        cashflow.timeOffset(end = n - cashflow.nper())
        #
    return cashflow



class bulletLoan(Loan):

    def __init__(self,
                 amount,             # 
                 rate,               # interest rate
                 life,               # number of payments
                 dispoints  = 0,     # discount points
                 orgpoints  = 0,     # origination points
                 prepmt     = None): # prepayments       (cashflow)


        if isinstance(rate, int) or isinstance(rate, float):
            #
            rate = Rate(initRate = rate, nper = life)
            #

        ##
        ## length adjustment
        ##
        prepmt    = _checklength(prepmt, life)

        ## balance
        begppalbal  = [0] * (life + 1)
        intpmt      = [0] * (life + 1)
        capint      = [0] * (life + 1)
        ppalpmt     = [0] * (life + 1)
        totpmt      = [0] * (life + 1)
        endppalbal  = [0] * (life + 1)


        ##
        ## balance calculation
        ##
        for t in range(life + 1):

            if t == 0:
                #
                begppalbal[t] = amount - prepmt[t]
                endppalbal[t] = amount - prepmt[t]
                totpmt[t]     = amount * (dispoints + orgpoints)
                intpmt[t]     = amount * dispoints
                #
            else:
                #
                begppalbal[t]  = endppalbal[t - 1]
                intpmt[t]      = begppalbal[t] * rate[t]
                if t == life :
                    ppalpmt[t] = begppalbal[t] + prepmt[t]
                else:
                    ppalpmt[t] = prepmt[t]
                totpmt[t]     = intpmt[t] + ppalpmt[t]
                endppalbal[t] = begppalbal[t] - ppalpmt[t]

                if endppalbal[t] < 0:
                    #
                    totpmt[t]     = begppalbal[t] + intpmt[t]
                    ppalpmt[t]    = begppalbal[t]
                    endppalbal[t] = begppalbal[t] - ppalpmt[t]
                    prepmt[t]     = 0


        ##
        ## loan data
        ##
        self._amount    = amount
        self._rate      = rate
        self._life      = life
        self._grace     = 0
        self._dispoints = dispoints
        self._orgpoints = orgpoints
        self._prepmt    = prepmt

        ##
        ## resuls
        ##
        self._begppalbal  = begppalbal
        self._totpmt      = totpmt
        self._intpmt      = intpmt
        self._capint      = capint
        self._ppalpmt     = ppalpmt
        self._endppalbal  = endppalbal



class fixedLoan(Loan):

    def __init__(self,
                 amount,             # 
                 rate,               # interest rate
                 life,               # number of payments
                 grace      = 0,     # grace periods
                 dispoints  = 0,     # discount points
                 orgpoints  = 0,     # origination points
                 prepmt     = None,  # prepayments       (cashflow)
                 balloonpmt = None): # balloon payments (cashflow)

        if isinstance(rate, int) or isinstance(rate, float):
            #
            rate = Rate(initRate = rate, nper = life + grace)
            #

        ##
        ## length adjustment
        ##
        prepmt     = _checklength(prepmt,     grace + life)
        balloonpmt = _checklength(balloonpmt, grace + life)
        rate       = _checklength(rate,       grace + life)

        ##
        ## present value of the balloon payments
        ##
        balloonpv = sum(balloonpmt)


        ## balance
        begppalbal  = [0] * (grace + life + 1)
        intpmt      = [0] * (grace + life + 1)
        capint      = [0] * (grace + life + 1)
        ppalpmt     = [0] * (grace + life + 1)
        totpmt      = [0] * (grace + life + 1)
        endppalbal  = [0] * (grace + life + 1)

        ## periodic ppal payment
        pmt = (amount - balloonpv) / life

        ##
        ## balance calculation
        ##
        for t in range(grace + life + 1):

            if t == 0:
                #
                begppalbal[t] = amount - prepmt[t]
                endppalbal[t] = amount - prepmt[t]
                totpmt[t]     = amount * (dispoints + orgpoints)
                intpmt[t]     = amount * dispoints
                #
            else:
                #
                begppalbal[t]  = endppalbal[t - 1]
                intpmt[t]      = begppalbal[t] * rate[t]
                if t <= grace:
                    ppalpmt[t]     = prepmt[t] + balloonpmt[t]
                else:
                    ppalpmt[t]     = pmt + prepmt[t] + balloonpmt[t]
                totpmt[t]      = intpmt[t] + ppalpmt[t]
                endppalbal[t]  = begppalbal[t] - ppalpmt[t]

                if endppalbal[t] < 0:
                    #
                    totpmt[t]     = begppalbal[t] + intpmt[t]
                    ppalpmt[t]    = begppalbal[t]
                    endppalbal[t] = begppalbal[t] - ppalpmt[t]
                    prepmt[t]     = 0
                    pmt           = 0


        ##
        ## loan data
        ##
        self._amount    = amount
        self._rate      = rate
        self._life      = life
        self._grace     = grace
        self._dispoints = dispoints
        self._orgpoints = orgpoints
        self._prepmt    = prepmt


        ##
        ## resuls
        ##
        self._begppalbal  = begppalbal
        self._totpmt      = totpmt
        self._intpmt      = intpmt
        self._capint      = capint
        self._ppalpmt     = ppalpmt
        self._endppalbal  = endppalbal



class balloonLoan(Loan):

    def __init__(self,
                 amount,             # 
                 rate,               # interest rate
                 life,               # number of payments
                 grace      = 0,     # grace periods
                 dispoints  = 0,     # discount points
                 orgpoints  = 0,     # origination points
                 prepmt     = None,  # prepayments       (cashflow)
                 ballonpmt  = None): # ballon payments   (cashflow)

        if not isinstance(rate, (int, float)):
            print('rate must be a float number')
            raise

        ##
        ## length adjustment
        ##
        prepmt    = _checklength(prepmt,    grace + life)
        ballonpmt = _checklength(ballonpmt, grace + life)

        ##
        ## present value of the balloon payments
        ##
        balloonpv = npv(rate, ballonpmt, t0 = grace)

        ##
        ## calculation
        ##

        ## periodic payments
        pmt = -tvm(rate = rate,
                   nper = life,
                   pv   = amount - balloonpv,
                   fv   = 0,
                   when = 'end').PMT()

        pmts = Cashflow(grace + life)
        pmts.add([(t+grace, pmt) for t in range(1, life + 1)])

        ## balance
        begppalbal  = [0] * (grace + life + 1)
        intpmt      = [0] * (grace + life + 1)
        capint      = [0] * (grace + life + 1)
        ppalpmt     = [0] * (grace + life + 1)
        endppalbal  = [0] * (grace + life + 1)

        ## payments per period
        totpmt = [ x + y + z for x, y, z in zip(pmts, ballonpmt, prepmt)]

        ##
        ## balance calculation
        ##
        for t in range(grace + life + 1):

            if t == 0:
                #
                begppalbal[0] = amount
                endppalbal[0] = amount
                totpmt[t]     = amount * (dispoints + orgpoints)
                intpmt[t]     = amount * dispoints
                #
            else:
                #
                begppalbal[t]  = endppalbal[t - 1]
                #
                if t <= grace:
                    #
                    intpmt[t]     = begppalbal[t] * rate
                    totpmt[t]     = intpmt[t]
                    endppalbal[t] = begppalbal[t]
                    #
                else:
                    #
                    intpmt[t]     = begppalbal[t] * rate
                    ppalpmt[t]    = totpmt[t] - intpmt[t]

                    if ppalpmt[t] < 0:
                        capint[t]  = - ppalpmt[t]
                        ppalpmt[t] = 0

                    endppalbal[t] = begppalbal[t] - ppalpmt[t] + capint[t]
                    #
                    if endppalbal[t] < 0:
                        #
                        totpmt[t]     = begppalbal[t] + intpmt[t]
                        ppalpmt[t]    = begppalbal[t]
                        endppalbal[t] = begppalbal[t] - ppalpmt[t]
                        pmts[t]       = 0
                        prepmt[t]     = 0


        ##
        ## loan data
        ##
        self._amount    = amount
        self._rate      = rate
        self._life      = life
        self._grace     = grace
        self._totlife   = grace + life
        self._dispoints = dispoints
        self._orgpoints = orgpoints
        self._prepmt    = prepmt
        self._ballonpmt = ballonpmt

        ##
        ## resuls
        ##
        self._begppalbal  = begppalbal
        self._totpmt      = totpmt
        self._intpmt      = intpmt
        self._capint      = capint
        self._ppalpmt     = ppalpmt
        self._endppalbal  = endppalbal





class buydownLoan(Loan):

    def __init__(self,
                 amount,             # 
                 rate,               # interest rate
                 life,               # simulation length
                 grace      = 0,     # grace period
                 dispoints  = 0,     # discount points
                 orgpoints  = 0,     # origination points
                 prepmt     = None): # prepayments       (cashflow)

        ##
        ## loan data
        ##
        self._amount    = amount
        self._rate      = rate
        self._life      = life
        self._grace     = grace
        self._dispoints = dispoints
        self._orgpoints = orgpoints
        self._prepmt    = prepmt


        ##
        ## calculation
        ##

        begppalbal  = [0] * (life + 1)
        totpmt      = [0] * (life + 1)
        intpmt      = [0] * (life + 1)
        ppalpmt     = [0] * (life + 1)
        endppalbal  = [0] * (life + 1)

        if isinstance(rate, int) or isinstance(rate, float):
            #
            rate = Rate(initRate = rate, nper = grace + life)
            #

        ##
        ## prepayments
        ##
        if prepmt is None:
            prepmt = Cashflow(life + grace)

        ##
        ## total payment per period
        ##
        totpmt = Cashflow(life)

        ##
        ## balance calculation
        ##
        for t in range(life + 1):

            if t == 0:
                #
                begppalbal[t] = amount
                endppalbal[t] = amount
                totpmt[t]     = amount * (dispoints + orgpoints)
                intpmt[t]     = amount * dispoints
                #
            else:
                ##
                ## periodic payment per period
                ##
                pmt = -tvm(rate = rate[t],
                           nper = life - t + 1,
                           pv   = endppalbal[t-1],
                           fv   = 0,
                           when = 'end').PMT()

                ##
                ## total payment per period
                ##
                totpmt[t] = pmt + prepmt[t]
                ##
                ## balance
                ##
                begppalbal[t]  = endppalbal[t - 1]
                intpmt[t]      = begppalbal[t] * rate[t]
                ppalpmt[t]     = totpmt[t] - intpmt[t]
                endppalbal[t]  = begppalbal[t] - ppalpmt[t]


        self._begppalbal  = begppalbal
        self._totpmt      = totpmt
        self._intpmt      = intpmt
        self._ppalpmt     = ppalpmt
        self._endppalbal  = endppalbal
