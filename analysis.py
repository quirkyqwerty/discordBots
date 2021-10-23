from pycoingecko import CoinGeckoAPI
import pandas as pd
import time
import os

WAIT_TIME = 0.1
CRITERIA = {
  "small_caps": "({0} > 2*1e6) & ({0} < 10*1e6)"
}
BASEPATH = "./data"

cg = CoinGeckoAPI()

class BotModules():
  
  def __init__(self):
    self.all_prices = None
    self.caps_comparison = {}
    pass

  def is_supported(self, asset):
    return asset in self.all_prices["id"].unique()

  def get_prices(self, asset, currency="usd"):
    return cg.get_price(asset, vs_currencies=currency)[asset][currency]

  def get_all_coins(self, filepath):
    prices_json = []
    next_json = ""
    i = 1

    while next_json != []:
      next_json = cg.get_coins_markets(vs_currency="USD", per_page="250", page=str(i))
      prices_json += next_json
      i += 1
      time.sleep(WAIT_TIME)

    self.all_prices = pd.DataFrame(prices_json)
    self.all_prices.to_csv(filepath)

  def _get_range_caps(self, criteria):
    condition = eval(criteria.format("self.all_prices['market_cap']"))
    return self.all_prices[condition]

  def compare_range_caps(self, criteria, filepath):
    previous = pd.read_csv(filepath)
    current = self._get_range_caps(criteria)
    current.to_csv(filepath)
    
    merge = current.merge(previous[["id", "last_updated"]], how="left", on="id", suffixes=("", "_left"))
    
    new = merge[merge["last_updated_left"].isnull()]
    
    return new

  def routine(self):
    # self.all_prices = self.get_all_coins(os.path.join(BASEPATH, "prices.csv"))
    self.all_prices = pd.read_csv(os.path.join(BASEPATH, "prices.csv"))
    
    for crt in CRITERIA.keys():
      path = os.path.join(BASEPATH, "{}.csv".format(crt))
      self.caps_comparison[crt] = self.compare_range_caps(CRITERIA[crt], path)

    return self.all_prices, self.caps_comparison



if __name__ == "__main__":
  data = pd.read_csv(os.path.join(BASEPATH, "small_caps.csv"))
  print(data)



  