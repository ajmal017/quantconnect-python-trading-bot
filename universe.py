class UniverseSelectionModel():
    
    def __init__(self, algorithm):
        self.algorithm = algorithm
    

    # Coarse data for quick processing, selected by price and volume
    def SelectCoarse(self, coarse):
        # self.algorithm.Log("Generating universe...")
        universe = self.FilterPriceVolume(coarse)
        return [c.Symbol for c in universe]


    # Take in coarse data, filter out FS firms (poor FCFY), then filter based on factor
    def SelectFine(self, fine):
        universe = self.FilterFactor(self.FilterFinancialServices(fine))
        # self.algorithm.Log(f"Universe consists of {len(universe)} securities")
        self.algorithm.securities = universe
        return [f.Symbol for f in universe]
    

    # Filter for all securities where price > $1, then filter for the top 1000 by volume
    def FilterPriceVolume(self, coarse):
        filter_price = [c for c in coarse if c.Price > 1]
        sort_filtered_by_volume = sorted([c for c in filter_price if c.HasFundamentalData], key=lambda c: c.DollarVolume, reverse=True)
        return sort_filtered_by_volume[:1000]


    # Filter out all securities with sector code 'FinancialServices'
    def FilterFinancialServices(self, fine):
        filter_fs = [f for f in fine if f.AssetClassification.MorningstarSectorCode != MorningstarSectorCode.FinancialServices]
        return filter_fs
    

    # Sort by CashReturn (FCF / EV) and return top and bottom 50
    def FilterFactor(self, fine):
        filter_factor = sorted(fine, key=lambda f: f.ValuationRatios.CashReturn, reverse=True)
        return filter_factor[:50] + filter_factor[-50:]
