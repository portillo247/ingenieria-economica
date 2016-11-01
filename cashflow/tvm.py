import math
import numpy as np

##
##
## T I M E   V A L U E   O F   M O N E Y    M O D E L S
##
##

class tvm():
    ## class for calculating cashflow equivalences
    ## initialize all internal variables (registers)
    def __init__(
            self,
            pmt  = 0,
            pv   = 0,
            fv   = 0,
            nper = 1,
            rate = 0,
            when = 0):

        self.__when_to_num = { 0:0, 'end':0, 'e':0, 'finish':0,
                              1:1, 'begin':1, 'b':1, 'beginning':1, 'start':1}
        #
        self.__pmt  = pmt
        self.__pv   = pv
        self.__fv   = fv
        self.__nper = nper
        self.__rate = rate
        self.__when = when
        self.__ppmt = None
        self.__ipmt = None
        #
        self._convert_when()

    ##
    def pmt(self):
        return self.__pmt

    def pv(self):
        return self.__pv

    def fv(self):
        return self.__fv

    def nper(self):
        return self.__nper

    def rate(self):
        return self.__rate

    def ppmt(self):
        return [x for x in self.__ppmt]

    def ipmt(self):
        return [x for x in self.__ipmt]


    ##
    ## from numpy/financial.py
    ##
    def _convert_when(self):
        #
        if self.__when is None:
            self.__when = 0
            return self.__when
        #
        try:
            self.__when = self.__when_to_num[self.__when]
        except (KeyError, TypeError):
            return [self.__when_to_num[x] for x in self.__when]

    ##
    ## clear all financial registers
    ##
    def clear(self):
        #
        self.__pmt      = 0       # payment
        self.__pv       = 0       # present value
        self.__fv       = 0       # future value
        self.__nper     = 1       # number of compounding periods
        self.__rate     = 0       # annual interest rate (not percent) per period
        self.__when     = 0       # when payments are due (‘begin’ (1) or ‘end’ (0))
        self.__ppmt     = None    # principal portion of a payment
        self.__ipmt     = None    # interest portion of a payment
        #

    ##
    ## update finalcial registers
    ##
    def update(
            self,
            pmt  = None,
            pv   = None,
            fv   = None,
            nper = None,
            rate = None,
            when = None):
        #
        self.__pmt  = pmt  if pmt  is not None else self.__pmt
        self.__pv   = pv   if pv   is not None else self.__pv
        self.__fv   = fv   if fv   is not None else self.__fv
        self.__nper = nper if nper is not None else self.__nper
        self.__rate = rate if rate is not None else self.__rate
        self.__when = when if when is not None else self.__when
        #
        self._convert_when()
        return self

    ##
    ## compound interest calculations
    ##

    ## compute the present value
    ## https://docs.scipy.org/doc/numpy/reference/generated/numpy.__pv.html#numpy.pv
    def PV(self):
        #
        self.__pv = np.pv( rate = self.__rate,
                           nper = self.__nper,
                           pmt  = self.__pmt,
                           fv   = self.__fv,
                           when = self.__when)
        #
        self.__pv = self.__pv.tolist() if isinstance(self.__pv, np.ndarray) else self.__pv
        return self.__pv


    ## calculate the future value
    ## https://docs.scipy.org/doc/numpy/reference/generated/numpy.__fv.html#numpy.fv
    def FV(self):
        #
        self.__fv = np.fv( rate = self.__rate,
                           nper = self.__nper,
                           pmt  = self.__pmt,
                           pv   = self.__pv,
                           when = self.__when)
        #
        self.__fv = self.__fv.tolist() if isinstance(self.__fv, np.ndarray) else self.__fv
        return self.__fv


    ## compute the rate of interest per period
    ## https://docs.scipy.org/doc/numpy/reference/generated/numpy.__rate.html#numpy.rate
    def RATE(self, maxiter = 1000):
        #
        self.__rate = np.rate( nper    = self.__nper,
                               pmt     = self.__pmt,
                               pv      = self.__pv,
                               fv      = self.__fv,
                               when    = self.__when,
                               maxiter = maxiter)
        #
        self.__rate = self.__rate.tolist() if isinstance(self.__rate, np.ndarray) else self.__rate
        return self.__rate


    ## compute the number of periodic payments
    ## https://docs.scipy.org/doc/numpy/reference/generated/numpy.__nper.html#numpy.nper
    def NPER(self):
        #
        self.__nper = np.nper( rate = self.__rate,
                               pmt  = self.__pmt if self.__pmt != 0 else 0.000001,
                               pv   = self.__pv  if self.__pv  != 0 else 0.000001,
                               fv   = self.__fv  if self.__fv  != 0 else 0.000001,
                               when = self.__when)
        #
        self.__nper = self.__nper.tolist() if isinstance(self.__nper, np.ndarray) else self.__nper
        return self.__nper


    ## compute the payment
    # https://docs.scipy.org/doc/numpy/reference/generated/numpy.__pmt.html#numpy.pmt
    def PMT(self):
        #
        self.__pmt = np.pmt( rate = self.__rate,
                             nper = self.__nper,
                             pv   = self.__pv,
                             fv   = self.__fv,
                             when = self.__when )
        #
        self.__pmt = self.__pmt.tolist() if isinstance(self.__pmt, np.ndarray) else self.__pmt
        return self.__pmt


    ## amortization table calculation
    def _calcAMRT(self):

        ## variable definition
        begbal = [0] * (self.__nper + 1)
        ipmt   = [0] * (self.__nper + 1)
        ppmt   = [0] * (self.__nper + 1)
        endbal = [0] * (self.__nper + 1)

        ## calcula el pmt periodico
        pmt  = [self.PMT()] * (self.__nper + 1)

        ## vencido
        if self.__when == 0:
            #
            pmt[0] = 0
            #
        if self.__when == 1: ## anticipado
            #
            pmt[self.__nper] = 0
            #

        begbal[0] = self.__pv

        for t in range(self.__nper + 1):

            if t == 0:
                endbal[t] = begbal[t] + pmt[0]
                ppmt[t]   = pmt[t]
            else:
                begbal[t] = endbal[t-1]
                ipmt[t]   = - begbal[t] * self.__rate
                ppmt[t]   = pmt[t] - ipmt[t]
                endbal[t] = begbal[t] + ppmt[t]


        return (begbal, ipmt, ppmt, pmt, endbal)



    ## Compute the payment against loan principal
    ## https://docs.scipy.org/doc/numpy/reference/generated/numpy.ppmt.html#numpy.ppmt
    def PPMT(self, pmt = None, pv = None, fv = None, nper = None, rate = None, when = None):
        #
        begbal, ipmt, ppmt, pmt, endbal =  self._calcAMRT()
        self.__begbal = begbal
        self.__ipmt   = ipmt
        self.__ppmt   = ppmt
        self.__endbal = endbal
        return self.__ppmt
        #

    ## Compute the interest portion of a payment
    ## https://docs.scipy.org/doc/numpy/reference/generated/numpy.ipmt.html
    def IPMT(self, pmt = None, pv = None, fv = None, nper = None, rate = None, when = None):
        #
        begbal, ipmt, ppmt, pmt, endbal =  self._calcAMRT()
        self.__begbal = begbal
        self.__ipmt   = ipmt
        self.__ppmt   = ppmt
        self.__endbal = endbal
        return self.__ipmt
        #

    ## gets the balance at the end of the period
    def ENDBAL(self, pmt = None, pv = None, fv = None, nper = None, rate = None, when = None):
        #
        begbal, ipmt, ppmt, pmt, endbal =  self._calcAMRT()
        self.__begbal = begbal
        self.__ipmt   = ipmt
        self.__ppmt   = ppmt
        self.__endbal = endbal
        return self.__endbal
        #

    ## gets the balance at the begin of the period
    def BEGBAL(self, pmt = None, pv = None, fv = None, nper = None, rate = None, when = None):
        #
        begbal, ipmt, ppmt, pmt, endbal =  self._calcAMRT()
        self.__begbal = begbal
        self.__ipmt   = ipmt
        self.__ppmt   = ppmt
        self.__endbal = endbal
        return self.__begbal
        #


    def AMRT(self):

        s = []
        begbal, ipmt, ppmt, pmt, endbal =  self._calcAMRT()

        #
        s.append('   t      Beginning      Periodic     Interest    Principal        Final')
        s.append('          Principal       Payment      Payment    Repayment    Principal')
        s.append('             Amount        Amount                                 Amount')
        s.append('--------------------------------------------------------------------------')
        #
        for i in range(self.__nper + 1):

            fmt = ' {:3d}   {:12.2f}  {:12.2f} {:12.2f} {:12.2f} {:12.2f}'

            s.append(fmt.format(i,
                                begbal[i],
                                pmt[i],
                                ipmt[i],
                                ppmt[i],
                                endbal[i]))
        print('\n'.join(s))


    ##
    ## print function
    ##
    def __repr__(self):

        s = []

        if self.__nper is not None:
            if isinstance(self.__nper, float):
                s.append('nper: {:12.2f}'.format(self.__nper))
            elif isinstance(self.__nper, int):
                s.append('nper: {:9d}'.format(self.__nper))
            else:
                s.append('nper:         {:s}'.format(repr([round(y, 2) for y in self.__nper])))

        if self.__rate is not None:
            if isinstance(self.__rate, int) or isinstance(self.__rate, float):
                s.append('rate:   {:12.4f}'.format(float(self.__rate)))
            else:
                s.append('rate:         {:s}'.format(repr([round(y, 4) for y in self.__rate])))

        if self.__pv is not None:
            if isinstance(self.__pv, int) or isinstance(self.__pv, float):
                s.append('pv:   {:12.2f}'.format(float(self.__pv)))
            else:
                s.append('pv:           {:s}'.format(repr([round(y, 2) for y in self.__pv])))

        if self.__fv is not None:
            if isinstance(self.__fv, int) or isinstance(self.__fv, float):
                s.append('fv:   {:12.2f}'.format(float(self.__fv)))
            else:
                s.append('fv:           {:s}'.format(repr([round(y, 2) for y in self.__fv])))

        if self.__pmt is not None:
            if isinstance(self.__pmt, int) or isinstance(self.__pmt, float):
                s.append('pmt:  {:12.2f}'.format(float(self.__pmt)))
            else:
                s.append('pmt:          {:s}'.format(repr([round(y, 2) for y in self.__pmt])))

        if self.__when is not None:
            if isinstance(self.__when, int):
                s.append('when: {}'.format("'end (0)'" if self.__when == 0 else "'begin (1)'"))
            elif isinstance(self.__when, float):
                s.append('when: {}'.format("'end (0)'" if self.__when == 0. else "'begin (1)'"))
            else:
                pass

        return '\n'.join(s)

    ##
    ## conversion to list
    ##
    def tolist(self):

        cashflow             = [0] * (self.__nper + 1)
        cashflow[0]          = self.__pv
        cashflow[self.__nper] = self.__fv

        for n in range(self.__nper + 1):

            if n == 0:
                if self.__when == 1: # begin
                    #
                    cashflow[n] += self.__pmt
                    #
            elif n == self.__nper:
                if self.__when == 0: # end
                    #
                    cashflow[n] += self.__pmt
                    #
            else:
                #
                cashflow[n] += self.__pmt
                #

        return cashflow

    ##
    ## conversion to generic cashflow object
    ##
    def toCashflow(self):
        #
        cashflow = self.tolist()
        return Cashflow(self.__nper + 1, [(t, cashflow[t]) for t in range(self.__nper)])
        #
