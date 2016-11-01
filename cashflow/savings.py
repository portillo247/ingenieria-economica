##
##
## S A V I N G S    C A L C U L A T I O N
##
##

from cashflow.cashflow import *
from cashflow.rate import *

class Savings():

    def __init__(self,
                 deposits,
                 rate       = 0.01,
                 nper       = 12,
                 initbal    = 0):

        if isinstance(deposits, int) or isinstance(deposits, float):
            #
            deposits = Cashflow(nper, [(t, deposits) for t in range(nper+1)]).tolist()
            #

        if isinstance(rate, int) or isinstance(rate, float):
            #
            rate = Rate(initRate = rate, nper = nper).tolist()
            #

        self.__nper      = nper
        self.__rate      = rate
        self.__deposits  = deposits
        self.__initbal   = initbal

        begbal   = [0] * (nper + 1)
        interest = [0] * (nper + 1)
        endbal   = [0] * (nper + 1)


        ##
        ## balance calculation
        ##
        for t in range(nper + 1):

            if t == 0:
                #
                begbal[t]   = initbal
                interest[t] = 0
                endbal[t]   = begbal[t] + deposits[t] + interest[t]
                #
            else:
                #
                begbal[t]   = endbal[t - 1]
                interest[t] = begbal[t] * rate[t]

                if deposits[t] < 0 and -deposits[t] > begbal[t] + interest[t]:
                    #
                    deposits[t] = -(begbal[t] + interest[t])
                    #

                endbal[t] = begbal[t] + deposits[t] + interest[t]
                #


        self.__begbal   = begbal
        self.__interest = interest
        self.__endbal   = endbal

    ## TODO: Cumulative interest payment
    ##       Cumulative principal

    ##
    ## interest earned
    ##
    def interest(self):
        #
        x = Cashflow(self.__nper,
                     spec = [(t, v) for t, v in enumerate(self.__interest)])
        return x
        #


    ##
    ## ending balance
    ##
    def endbal(self):
        #
        x = Cashflow(self.__nper,
                     spec = [(t, v) for t, v in enumerate(self.__endbal)])
        return x
        #

    ##
    ## starting balance
    ##
    def begbal(self):
        #
        x = Cashflow(self.__nper,
                     spec = [(t, v) for t, v in enumerate(self.__begbal)])
        return x
        #

    ##
    ## deposits(self)
    ##
    def deposits(self):
        #
        x = Cashflow(self.__nper,
                     spec = [(t, v) for t, v in enumerate(self.__deposits)])
        return x
        #



    ##
    ## conversion to generic cashflow object
    ##
    def toCashflow(self):
        """compute a generic cashflow"""

        x = Cashflow(self.__nper)

        x._cashflow             = [-w for w in self.__deposits]
        x._cashflow[0]          = -self.__endbal[0]
        x._cashflow[self.__nper] = x._cashflow[self.__nper] + self.__endbal[self.__nper]
        return x



    def __repr__(self):
        """print function"""

        s = []

        s.append('')

        #
        s.append('   t          Beginning        Deposit      Interest        Ending')
        s.append('                balance                                    balance')
        s.append('-------------------------------------------------------------------')
        #
        for i in range(self.__nper + 1):

            fmt = ' {:3d}       {:12.2f}  {:12.2f}  {:12.2f}  {:12.2f}'
            s.append(fmt.format(i,
                                self.__begbal[i],
                                self.__deposits[i],
                                self.__interest[i],
                                self.__endbal[i]))
        return '\n'.join(s)
