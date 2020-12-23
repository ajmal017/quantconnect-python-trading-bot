import pandas as pd


class AlphaModel():
    
    def __init__(self):
        pass
    

    # Take in securities, generate df with ticker and FCFY, then create alpha score by normalising FCFY value
    def GenerateAlphas(self, algorithm, securities):
        # algorithm.Log(f"Generating alpha scores for {len(securities)} securities...")
        fcfy = pd.DataFrame.from_records(
            [
                {
                    'symbol': str(security.Symbol),
                    'fcfy': security.ValuationRatios.CashReturn
                } for security in securities
            ]).set_index('symbol')
        
        fcfy['alpha_score'] = normalise(fcfy['fcfy'], True)
        
        return fcfy


def normalise(series, equal_ls=True):
    if equal_ls:
        series -= series.mean()
    sum = series.abs().sum()
    return series.apply(lambda x: x/sum)
    