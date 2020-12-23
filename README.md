# QuantConnect Python Trading Bot

This is a just-for-fun project implementing a trading strategy on the QuantConnect platform, and my first experience with building a trading bot more broadly. It goes without saying that this bot is not to be used for live trading, unless you have more money than sense. 

I have chosen to use Python because of its many excellent data-related libraries, such as Pandas and Numpy, and the language's relative slowness is not a concern, given the strategy used. Additionally, Python is the language I am most comfortable with and there is an extensive support community for algorithmic trading using Python and its libraries.

The logging is mostly commented out because of log limits on QuantConnect, so do uncomment these at your discretion. 

## Alpha model

This model adopts a factor investing approach, focused on free cash flow yield amongst S&P 500 stocks. This follows the idea that those companies with strong FCFY relative to their enterprise value are efficient allocators of capital with room for further growth. 

## Dependencies

- Python 3
- Pandas
- Numpy
- CVXPY

The complete list can be found in requirements.txt, and can be installed with 'pip install -r requirements.txt'.

## To run

This is designed to run on the QuantConnect platform, built on top of their LEAN engine and using their method/class infrastructure. To run, create a QuantConnect account, navigate to the Algorithm Lab, select 'Create New Algorithm', and add the files in this repository. Make sure to backtest it!
