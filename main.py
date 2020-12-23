from alpha import AlphaModel
from charts import InitCharts, PlotPerformanceChart, PlotConcentrationChart, PlotStockCountChart, PlotExposureChart
from execution import Execution
from portfolio import OptimisePortfolioModel
from universe import UniverseSelectionModel


class TradingBot(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2006, 1, 1)
        self.SetCash(100000)
        
        # Data resolution
        self.UniverseSettings.Resolution = Resolution.Minute
        self.AddEquity('SPY', Resolution.Daily)
        
        # Construct universe
        self.securities = []
        self.CustomUniverseSelectionModel = UniverseSelectionModel(self)
        self.AddUniverse(self.CustomUniverseSelectionModel.SelectCoarse, self.CustomUniverseSelectionModel.SelectFine)
        
        # Alpha model
        self.CustomAlphaModel = AlphaModel()
        
        # Portfolio construction model
        self.CustomPortfolioConstructionModel = OptimisePortfolioModel(turnover=0.05, max_weight=0.05, longshort=True)
        
        # Execution model
        self.CustomExecution = Execution(liquidity_tolerance=0.005)
        
        # Schedule rebalancing
        self.Schedule.On(self.DateRules.EveryDay('SPY'), self.TimeRules.At(13, 0), Action(self.RebalancePortfolio))
        
        # Initialise and schedule charting
        InitCharts(self)
        self.Schedule.On(self.DateRules.Every(DayOfWeek.Friday), self.TimeRules.BeforeMarketClose('SPY', 0), Action(self.PlotCharts))


    def OnData(self, data):
        pass
    

    def RebalancePortfolio(self): 
        alpha_df = self.CustomAlphaModel.GenerateAlphas(self, self.securities)
        portfolio = self.CustomPortfolioConstructionModel.GenerateOptimalPortfolio(self, alpha_df)
        self.CustomExecution.ExecutePortfolio(self, portfolio)
    

    def PlotCharts(self):
        PlotPerformanceChart(self)
        PlotConcentrationChart(self)
        PlotStockCountChart(self)
        PlotExposureChart(self)
