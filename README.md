# Portfolio Optimization Engine

Portfolio optimisation in Python: Markowitz efficient frontier (Markowitz,
1952), Black-Litterman (Black and Litterman, 1992) and risk parity (Maillard
et al., 2010), compared on 10 US stocks.

A short note with the method and results: [note/portfolio-optimization-engine.pdf](note/portfolio-optimization-engine.pdf).

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Data](https://img.shields.io/badge/data-Yahoo%20Finance-purple) ![License](https://img.shields.io/badge/License-MIT-green)

## What it does

| Method | Idea |
|---|---|
| Markowitz, max Sharpe | tangency portfolio on the efficient frontier |
| Markowitz, min variance | lowest-variance portfolio |
| Black-Litterman | market equilibrium returns combined with investor views (tau = 0.05, risk aversion 2.5) |
| Risk parity | equal risk contribution: each stock contributes the same share of total risk |

Black-Litterman views: NVDA outperforms the average of AAPL and MSFT by 5% a
year; JPM returns 8% a year. Equilibrium returns and views are excess returns:
the 3% risk-free rate is added back to the posterior before the max-Sharpe
step, which subtracts it once.

Data: daily prices 2019 to 2026, risk-free rate 3%.

## Run

```bash
pip install -r requirements.txt
python portfolio_optimizer.py
```

## Results

![Efficient frontier](output/efficient_frontier.png)

| Portfolio | Expected return | Volatility | Sharpe |
|---|---:|---:|---:|
| Max Sharpe (Markowitz) | 37.4% | 25.1% | **1.37** |
| Black-Litterman | 23.7% | 18.8% | 1.10 |
| Risk parity | 20.9% | 17.5% | 1.02 |
| Min variance (Markowitz) | 15.6% | 15.8% | 0.79 |

### Weights

| | Max Sharpe | Min variance | Black-Litterman | Risk parity |
|---|---:|---:|---:|---:|
| AAPL | 10.4% | 0.0% | 10.6% | 8.0% |
| MSFT | 0.0% | 10.3% | 10.6% | 8.6% |
| JPM | 2.5% | 0.3% | 6.0% | 8.5% |
| XOM | 10.3% | 9.7% | 10.5% | 10.0% |
| JNJ | 31.2% | 33.8% | 10.4% | 14.7% |
| PG | 0.0% | 21.9% | 10.5% | 13.4% |
| V | 0.0% | 0.0% | 10.4% | 8.7% |
| NVDA | 39.2% | 1.3% | 10.1% | 6.1% |
| KO | 6.4% | 20.5% | 10.4% | 12.9% |
| UNH | 0.0% | 2.2% | 10.4% | 9.1% |

Markowitz puts the portfolio in 6 stocks (NVDA + JNJ = 70%), which shows how
sensitive it is to the estimated returns. Risk parity stays diversified
(every stock between 6% and 15%) with a lower Sharpe. Without views,
Black-Litterman holds the 10% equal weights it starts from. The NVDA view
barely moves it (10.1% with the views) because the 5% view is close to the 5.4%
spread that the equilibrium returns already imply. The JPM view does move it:
8% is below the 9.8% implied, so JPM falls from 10% to 6.0%.

## Limitations

- Equal weights are used as a proxy for market-cap weights in Black-Litterman.
- Expected returns are estimated on the same history (in-sample), so the
  Sharpe ratios shown are optimistic.

## Stack

Python, NumPy, pandas, SciPy, Matplotlib, yfinance

## License

MIT, see [LICENSE](LICENSE).

## References

Black, F. and Litterman, R. (1992). Global portfolio optimization. Financial Analysts Journal, 48(5), 28-43. https://doi.org/10.2469/faj.v48.n5.28

Maillard, S., Roncalli, T. and Teiletche, J. (2010). The properties of equally weighted risk contribution portfolios. The Journal of Portfolio Management, 36(4), 60-70. https://doi.org/10.3905/jpm.2010.36.4.060

Markowitz, H. (1952). Portfolio selection. The Journal of Finance, 7(1), 77-91. https://doi.org/10.2307/2975974
