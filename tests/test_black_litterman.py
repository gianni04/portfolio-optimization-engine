import numpy as np
import pandas as pd

import portfolio_optimizer as po


def test_posterior_is_total_return():
    # Views equal to what the prior implies leave the excess posterior at Pi,
    # so the returned total return must be Pi + risk-free rate.
    tickers = ["A", "B", "C"]
    cov = pd.DataFrame(
        [[0.09, 0.02, 0.01], [0.02, 0.04, 0.00], [0.01, 0.00, 0.16]],
        index=tickers, columns=tickers,
    )
    w_m = np.repeat(1.0 / 3, 3)
    pi = 2.5 * cov.values @ w_m
    p = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, -1.0]])
    bl = po.black_litterman(cov, w_m, p, p @ pi)
    assert np.allclose(bl.values - po.RISK_FREE_RATE, pi)
