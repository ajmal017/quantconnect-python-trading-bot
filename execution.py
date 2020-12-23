class Execution():
    
    def __init__(self, liquidity_tolerance):
        self.liquidity_tolerance = liquidity_tolerance
    

    # Filter for securities for liquidating and for holding, and pass these into relevant functions
    def ExecutePortfolio(self, algorithm, portfolio):
        # algorithm.Log("Executing portfolio trades...")
        # Liquidate securities where weight < liquidity tolerance
        liquidate_securities = portfolio[abs(portfolio) < self.liquidity_tolerance].index
        held_securities = portfolio[abs(portfolio) >= self.liquidity_tolerance]
        self.LiquidateSecurities(algorithm, liquidate_securities)
        self.SetHoldings(algorithm, held_securities)
    

    # Liquidate securities passed into this function from ExecutePortfolio
    def LiquidateSecurities(self, algorithm, securities):
        liquidated_count = 0

        for security in securities:
            if algorithm.Securities[security].Invested:
                algorithm.Liquidate(security)
                liquidated_count += 1
                
        # algorithm.Log(f"Successfully liquidated {liquidated_count} securities")
    

    # Set weight of each security passed into this function
    def SetHoldings(self, algorithm, portfolio):
        # algorithm.Log(f"Setting portfolio holdings for {len(portfolio)} securities...")
        for security, weight in portfolio.iteritems():
            algorithm.SetHoldings(security, weight)
