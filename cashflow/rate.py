##
##
##  R A T E    S P E C I F I C A T I O N
##
##

class Rate():

    def __init__(self,                   #
                 initRate,               # constant rate
                 nper,                   # number of periods
                 modifications = None):  # modifications (time, value)

        self.__initRate      = initRate
        self.__nper          = nper
        self.__modifications = modifications
        self.__rate          = [self.__initRate] + [self.__initRate] * (self.__nper)

        if self.__modifications is None:
            #
            return
            #

        if isinstance(self.__modifications, tuple):
            #
            modifications = [modifications]
            #

        nummod   = len(modifications)
        starting = [1]               * (nummod + 1)
        ending   = [self.__nper + 1] * (nummod + 1)
        values   = [self.__initRate] * (nummod + 1)

        for i, x in enumerate(modifications):
            #
            t, v            = x
            starting[i + 1] = t
            ending[i]       = t
            values[i + 1]   = v
            #

        for i in range(nummod+1):
            #
            for n in range(starting[i], ending[i]):
                #
                self.__rate[n] = values[i]
                #
            #

    def nper(self):
        return self.__nper

    ##
    ## fresh copy of the object
    ##
    def copy(self):
        return Rate(initRate      = self.__initRate,
                    nper          = self.__nper,
                    modifications = self.__modifications)

    ##
    def tolist(self):
        #
        return [x for x in self.__rate]
        #

    ##
    def toCurrent(self, t0 = 0):
        #
        f = self.toConstant(t0)
        return [1/x for x in f]

    ##
    def toConstant(self, t0 = 0):
        #
        f = [1] * (self.__nper + 1)
        for t in range(1, self.__nper + 1):
            #
            f[t] = f[t-1] / (1 + self.__rate[t])
            #
        if t0 > 0:
            r = f[t0]
            f = [x/r for x in f]
        #
        return f



    ##
    ##
    ##
    def __repr__(self):

        s = []

        #
        s.append('  time          rate    ')
        s.append('------------------------')
        #

        rate = [round(x, 4) for x in self.__rate]

        i = 0
        while i < len(rate):

            freq = 1

            ## count the number of times
            while i + freq < len(rate) and rate[i] == rate[i + freq]:
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

            s.append(' {:7s}    {:8.4f}'.format(time, rate[i]))

            i += freq

        return '\n'.join(s)


    ##
    def __len__(self):
        #
        return len(self.__rate)
        #

    ##
    def __setitem__(self, key, value):
        #
        self.__rate[key] = value
        #

    ##
    def __getitem__(self, key):
        #
        return self.__rate[key]
        #


    def meanrate(self):
        x = self.tolist()
        p = 1
        for y in x[1:]:
            p *= (1 + y)
        return p**(1/(len(x) - 1)) - 1


    def timeOffset(self, start = None, end = None):
        #
        if start is not None and start != 0:
            #
            self.__rate = [0] + [self.__initRate] * start + self.__rate[1:]
            self.__nper += start
            if self.__modifications is not None:
                #
                if isinstance(self.__modifications, tuple):
                    t, v = self.__modifications
                    self.__modifications = (t+start, v)
                else:
                    self.__modifications = [(t+start, v) for t, v in self.__modifications]

        if end is not None:

            self.__rate += [self.__rate[-1]] * end
            self.__nper += end

        #
