"""
Portfolio Optimizer
--------------------
Student project: build an equity portfolio using 3 classic portfolio
management techniques and compare them.

1) Markowitz Mean-Variance Optimization (efficient frontier)
2) Black-Litterman model (market equilibrium + investor views)
3) Risk Parity (equal risk contribution)

Data source: Yahoo Finance (real prices, daily).
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from scipy.optimize import minimize


# a small diversified universe: tech, banks, energy, healthcare, consumer
TICKERS = ["AAPL", "MSFT", "JPM", "XOM", "JNJ", "PG", "V", "NVDA", "KO", "UNH"]
START_DATE = "2019-01-01"
END_DATE = "2026-08-01"
RISK_FREE_RATE = 0.03  # annualized, approx T-bill rate used for Sharpe ratio
TRADING_DAYS = 252

OUTPUT_DIR = "output"


def load_prices():
    """Download adjusted close prices for the universe."""
    raw = yf.download(TICKERS, start=START_DATE, end=END_DATE, progress=False)["Close"]
    raw = raw.dropna()
    return raw


def compute_stats(prices):
    """Daily returns -> annualized mean vector and covariance matrix."""
    daily_returns = prices.pct_change().dropna()
    mean_returns = daily_returns.mean() * TRADING_DAYS
    cov_matrix = daily_returns.cov() * TRADING_DAYS
    return daily_returns, mean_returns, cov_matrix


def portfolio_return(weights, mean_returns):
    return float(np.dot(weights, mean_returns))


def portfolio_volatility(weights, cov_matrix):
    return float(np.sqrt(weights.T @ cov_matrix @ weights))


def portfolio_sharpe(weights, mean_returns, cov_matrix):
    ret = portfolio_return(weights, mean_returns)
    vol = portfolio_volatility(weights, cov_matrix)
    return (ret - RISK_FREE_RATE) / vol


def max_sharpe_portfolio(mean_returns, cov_matrix):
    """Find the weights that maximize the Sharpe ratio (tangency portfolio)."""
    n = len(mean_returns)
    bounds = tuple((0.0, 1.0) for _ in range(n))  # long-only
    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    init_guess = np.repeat(1.0 / n, n)

    # minimize negative Sharpe = maximize Sharpe
    neg_sharpe = lambda w: -portfolio_sharpe(w, mean_returns, cov_matrix)
    result = minimize(neg_sharpe, init_guess, method="SLSQP",
                       bounds=bounds, constraints=constraints)
    return result.x


def min_variance_portfolio(cov_matrix):
    """Find the weights that minimize portfolio variance."""
    n = cov_matrix.shape[0]
    bounds = tuple((0.0, 1.0) for _ in range(n))
    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    init_guess = np.repeat(1.0 / n, n)

    var_fn = lambda w: portfolio_volatility(w, cov_matrix) ** 2
    result = minimize(var_fn, init_guess, method="SLSQP",
                       bounds=bounds, constraints=constraints)
    return result.x


def efficient_frontier(mean_returns, cov_matrix, n_points=40):
    """Trace the frontier by minimizing variance for a range of target returns."""
    n = len(mean_returns)
    bounds = tuple((0.0, 1.0) for _ in range(n))
    target_returns = np.linspace(mean_returns.min(), mean_returns.max(), n_points)

    frontier_vol = []
    for target in target_returns:
        constraints = (
            {"type": "eq", "fun": lambda w: np.sum(w) - 1.0},
            {"type": "eq", "fun": lambda w, t=target: portfolio_return(w, mean_returns) - t},
        )
        init_guess = np.repeat(1.0 / n, n)
        var_fn = lambda w: portfolio_volatility(w, cov_matrix) ** 2
        result = minimize(var_fn, init_guess, method="SLSQP",
                           bounds=bounds, constraints=constraints)
        frontier_vol.append(portfolio_volatility(result.x, cov_matrix))

    return target_returns, np.array(frontier_vol)


def black_litterman(cov_matrix, market_weights, views_p, views_q, tau=0.05, risk_aversion=2.5):
    """
    Combine market-implied equilibrium returns with subjective investor views.

    cov_matrix     : covariance matrix (Sigma)
    market_weights : market-cap-proxy weights used to back out equilibrium returns
    views_p        : P matrix, each row picks the assets involved in a view
    views_q        : Q vector, the expected return of each view
    tau            : scalar controlling uncertainty of the prior (small = trust market)
    risk_aversion  : lambda, market risk-aversion coefficient
    """
    sigma = cov_matrix.values

    # implied equilibrium excess returns (pi)
    pi = risk_aversion * sigma @ market_weights

    # view uncertainty (Omega), diagonal
    omega = np.diag(np.diag(views_p @ (tau * sigma) @ views_p.T))

    tau_sigma_inv = np.linalg.inv(tau * sigma)
    middle = np.linalg.inv(tau_sigma_inv + views_p.T @ np.linalg.inv(omega) @ views_p)
    bl_returns = middle @ (tau_sigma_inv @ pi + views_p.T @ np.linalg.inv(omega) @ views_q)

    return pd.Series(bl_returns, index=cov_matrix.index)


def risk_contribution(weights, cov_matrix):
    """Each asset's contribution to total portfolio variance."""
    portfolio_var = weights.T @ cov_matrix @ weights
    marginal_contrib = cov_matrix @ weights
    return weights * marginal_contrib / portfolio_var


def risk_parity_portfolio(cov_matrix):
    """Find weights so every asset contributes the same amount of risk."""
    n = cov_matrix.shape[0]
    target_contrib = np.repeat(1.0 / n, n)

    def objective(w):
        rc = risk_contribution(w, cov_matrix.values)
        return np.sum((rc - target_contrib) ** 2)

    bounds = tuple((0.001, 1.0) for _ in range(n))  # small floor avoids div-by-zero
    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1.0}
    init_guess = np.repeat(1.0 / n, n)

    result = minimize(objective, init_guess, method="SLSQP",
                       bounds=bounds, constraints=constraints)
    return result.x


def main():
    print("Downloading price history for:", TICKERS)
    prices = load_prices()
    daily_returns, mean_returns, cov_matrix = compute_stats(prices)

    w_max_sharpe = max_sharpe_portfolio(mean_returns.values, cov_matrix.values)
    w_min_var = min_variance_portfolio(cov_matrix.values)
    frontier_returns, frontier_vols = efficient_frontier(mean_returns.values, cov_matrix.values)

    # equal weights used as a simple market-cap proxy (student-project simplification)
    market_weights = np.repeat(1.0 / len(TICKERS), len(TICKERS))

    # two illustrative views:
    #   view 1: NVDA will outperform the average of AAPL/MSFT by 5%/year
    #   view 2: JPM will return 8%/year in absolute terms
    p_matrix = np.zeros((2, len(TICKERS)))
    idx = {t: i for i, t in enumerate(TICKERS)}
    p_matrix[0, idx["NVDA"]] = 1.0
    p_matrix[0, idx["AAPL"]] = -0.5
    p_matrix[0, idx["MSFT"]] = -0.5
    p_matrix[1, idx["JPM"]] = 1.0
    q_vector = np.array([0.05, 0.08])

    bl_returns = black_litterman(cov_matrix, market_weights, p_matrix, q_vector)
    w_bl = max_sharpe_portfolio(bl_returns.values, cov_matrix.values)

    w_risk_parity = risk_parity_portfolio(cov_matrix)

    summary = pd.DataFrame({
        "Max Sharpe (Markowitz)": w_max_sharpe,
        "Min Variance (Markowitz)": w_min_var,
        "Black-Litterman": w_bl,
        "Risk Parity": w_risk_parity,
    }, index=TICKERS).round(4)

    print("\nPortfolio weights:\n", summary)

    stats_rows = []
    for name, w in summary.items():
        w = w.values
        ret = portfolio_return(w, mean_returns.values)
        vol = portfolio_volatility(w, cov_matrix.values)
        sharpe = (ret - RISK_FREE_RATE) / vol
        stats_rows.append([name, ret, vol, sharpe])

    stats = pd.DataFrame(stats_rows, columns=["Portfolio", "Exp. Return", "Volatility", "Sharpe"])
    print("\nPortfolio stats:\n", stats.round(4))

    summary.to_csv(f"{OUTPUT_DIR}/portfolio_weights.csv")
    stats.to_csv(f"{OUTPUT_DIR}/portfolio_stats.csv", index=False)

    plt.figure(figsize=(9, 6))
    plt.plot(frontier_vols, frontier_returns, "b--", label="Efficient Frontier")

    for name, w in summary.items():
        w = w.values
        vol = portfolio_volatility(w, cov_matrix.values)
        ret = portfolio_return(w, mean_returns.values)
        plt.scatter(vol, ret, s=90, label=name)

    plt.xlabel("Annualized Volatility")
    plt.ylabel("Annualized Expected Return")
    plt.title("Efficient Frontier - Markowitz vs Black-Litterman vs Risk Parity")
    plt.legend()
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/efficient_frontier.png", dpi=150)
    print(f"\nSaved chart to {OUTPUT_DIR}/efficient_frontier.png")


if __name__ == "__main__":
    main()
