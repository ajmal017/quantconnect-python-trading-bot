import pandas as pd
import numpy as np
import cvxpy as cv


class OptimisePortfolioModel():

    def __init__(self, turnover, max_weight, longshort):
        self.turnover = turnover
        self.max_weight = max_weight
        self.longshort = longshort


    # Calculate target portfolio, consisting of security name and the weight each one should hold (normalised alpha score)
    def GenerateOptimalPortfolio(self, algorithm, alpha_df):
        # algorithm.Log("Generating optimal portfolio...")
        alphas = alpha_df['alpha_score']
        optimal_portfolio = self.Optimise(algorithm, self.AddZeroHoldings(algorithm, alphas))
        # algorithm.Log(f"Created a portfolio of {len(optimal_portfolio[optimal_portfolio != 0])} securities")
        return optimal_portfolio


    # Check if we have holdings in a security that's not in our desired portfolio. If yes, liquidate it
    def AddZeroHoldings(self, algorithm, portfolio):
        zero_holdings = [str(s.Symbol) for s in algorithm.Portfolio.Values if s.Invested and str(s.Symbol) not in portfolio.index]

        for security in zero_holdings:
            portfolio.loc[security] = 0

        return portfolio


    def Optimise(self, algorithm, alphas):
        invested_securities = [security for security in algorithm.Portfolio.Values if security.Invested]

        # For initial purchase we can buy securities until we fill our pf, then create df
        if len(invested_securities) == 0:
            # algorithm.Log("Initial portfolio rebalance")
            self.initial_rebalance = True
            turnover = 1
            initial_portfolio = pd.DataFrame(columns=['symbol', 'weight', 'alpha']).set_index('symbol')
        # Else create pf from securities we have invested, then add securities from the new universe and their alphas 
        else:
            self.initial_rebalance = False
            turnover = self.turnover
            initial_portfolio = pd.DataFrame.from_records(
                [
                    {
                        'symbol': str(security.Symbol),
                        'weight': security.HoldingsValue / algorithm.Portfolio.TotalHoldingsValue,
                        'alpha': alphas.loc[security] if security in alphas.index else 0,
                    } for security in invested_securities
                ]).set_index('symbol')

        for security, alpha in alphas.iteritems():
            if security not in initial_portfolio.index:
                initial_portfolio.loc[security, 'weight'] = 0
                initial_portfolio.loc[security, 'alpha'] = alpha
        
        # Loop through each value for turnover until we find a pf that has optimisation_status == optimal
        for i in range(int(turnover * 100), 101, 1):
            turnover_percent = i / 100
            optimiser = Optimiser(initial_portfolio, turnover=turnover_percent, max_weight=self.max_weight)
            optimal_portfolio, optimisation_status = optimiser.optimise()

            if optimisation_status != 'optimal':
                algorithm.Log(f'Optimisation with {turnover_percent} turnover not feasible: {optimisation_status}')
            else:
                break

        return optimal_portfolio


class Optimiser:

    def __init__(self, initial_portfolio, turnover, max_weight, longshort=True):
        self.symbols = np.array(initial_portfolio.index)
        self.initial_weight = np.array(initial_portfolio['weight'])
        self.optimal_weight = cv.Variable(self.initial_weight.shape)
        self.alpha = np.array(initial_portfolio['alpha'])
        self.longshort = longshort
        self.turnover = turnover
        self.max_weight = max_weight

        if self.longshort:
            # If going longshort (i.e. can short a stock as well, so weight < 0), set min weight to be negative of max weight
            self.min_weight = -self.max_weight
            # Set net exposure to 0 (i.e. long same amount that we are short)
            self.net_exposure = 0
            # Set absolute value of holdings to 1 (i.e. leverage of 1, same amount of buying power as we have capital)
            self.gross_exposure = 1
        else:
            # Prevent going short
            self.min_weight = 0
            # Set net exposure to 1 as we are only buying, not selling, securities
            self.net_exposure = 1
            self.gross_exposure = 1


    def optimise(self):
        constraints = self.get_constraints()
        # Maximise expected returns given our constraints
        optimisation = cv.Problem(cv.Maximize(cv.sum(self.optimal_weight*self.alpha)), constraints)
        optimisation.solve()
        status = optimisation.status

        # Create Pandas series. If optimisation is solved within constraints, return optimal weights array to 3dp, else return initial weights array, with symbols as index
        if status == 'optimal':
            optimal_portfolio = pd.Series(np.round(optimisation.solution.primal_vars[list(optimisation.solution.primal_vars.keys())[0]], 3), index=self.symbols)
        else:
            optimal_portfolio = pd.Series(np.round(self.initial_weight, 3), index=self.symbols)

        return optimal_portfolio, status


    def get_constraints(self):
        # Set boundaries for optimal weight
        min_weight = self.optimal_weight >= self.min_weight
        max_weight = self.optimal_weight <= self.max_weight
        # Calculate absolute value of sells/buys (optimal_weight - initial_weight), to be less than turnover * 2 (e.g. buy 10% of pf and sell 10% of pf for turnover of 10%)
        turnover = cv.sum(cv.abs(self.optimal_weight-self.initial_weight)) <= self.turnover * 2
        # Ensure sum of weights adds up to our net exposure (0 or 1)
        net_exposure = cv.sum(self.optimal_weight) == self.net_exposure
        # Ensure sum of weights does not exceed leverage
        gross_exposure = cv.sum(cv.abs(self.optimal_weight)) <= self.gross_exposure
        return [min_weight, max_weight, turnover, net_exposure, gross_exposure]
