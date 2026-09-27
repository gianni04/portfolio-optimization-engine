# Portfolio Optimization Engine

Optimisation de portefeuille en Python : frontière efficiente de Markowitz, modèle de Black-Litterman et allocation Risk Parity à contribution de risque égale, comparés sur un univers de 10 actions US.

![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Data](https://img.shields.io/badge/data-Yahoo%20Finance-purple) ![License](https://img.shields.io/badge/License-MIT-green)

## Ce que fait le projet

| Méthode | Principe |
|---|---|
| Markowitz — Max Sharpe | Portefeuille tangent de la frontière efficiente |
| Markowitz — Min Variance | Portefeuille de variance minimale |
| Black-Litterman | Rendements d'équilibre du marché combinés à des vues d'investisseur (τ = 0,05, aversion au risque = 2,5) |
| Risk Parity | Chaque ligne contribue à parts égales au risque total |

Vues Black-Litterman utilisées : NVDA surperforme la moyenne AAPL/MSFT de 5 %/an ; JPM rapporte 8 %/an en absolu.

Données : cours quotidiens 2019 → 2026 ; taux sans risque 3 %.

## Quickstart

```bash
pip install -r requirements.txt
python portfolio_optimizer.py
```

## Résultats

![Frontière efficiente](output/efficient_frontier.png)

| Portefeuille | Rendement espéré | Volatilité | Sharpe |
|---|---:|---:|---:|
| Max Sharpe (Markowitz) | 37,4 % | 25,1 % | **1,37** |
| Black-Litterman | 28,8 % | 23,7 % | 1,09 |
| Risk Parity | 20,9 % | 17,5 % | 1,02 |
| Min Variance (Markowitz) | 15,6 % | 15,8 % | 0,79 |

### Pondérations

| | Max Sharpe | Min Variance | Black-Litterman | Risk Parity |
|---|---:|---:|---:|---:|
| AAPL | 10,4 % | 0,0 % | 10,4 % | 8,0 % |
| MSFT | 31,2 % | 33,8 % | 0,0 % | 14,7 % |
| JPM | 2,5 % | 0,3 % | 8,5 % | 8,5 % |
| XOM | 6,4 % | 20,5 % | 0,0 % | 12,9 % |
| JNJ | 0,0 % | 10,3 % | 8,5 % | 8,6 % |
| PG | 39,2 % | 1,3 % | 18,7 % | 6,1 % |
| V | 0,0 % | 21,9 % | 0,0 % | 13,5 % |
| NVDA | 0,0 % | 2,2 % | 28,9 % | 9,1 % |
| KO | 0,0 % | 0,0 % | 16,3 % | 8,7 % |
| UNH | 10,3 % | 9,7 % | 8,8 % | 10,0 % |

**À retenir** : Markowitz concentre le portefeuille sur 6 lignes (PG + MSFT = 70 %), signe de sa sensibilité aux rendements estimés. Risk Parity reste diversifié (toutes les lignes entre 6 et 15 %) au prix d'un Sharpe plus faible. Black-Litterman reflète directement la vue positive sur NVDA (28,9 %).

## Limites

- Poids égaux utilisés comme proxy de la capitalisation boursière dans Black-Litterman.
- Rendements espérés estimés sur l'historique (in-sample) : les Sharpe affichés sont optimistes.

## Stack

`Python` · `NumPy` · `pandas` · `SciPy` · `Matplotlib` · `yfinance`

## Licence

MIT — voir [LICENSE](LICENSE).
