# day3-stats-toolkit
# Statistical Analysis Toolkit

A small, dependency-free Python toolkit for descriptive statistics, built for the Wakala Plus M-Pesa agent daily deposits dataset. Every statistic is implemented by hand with the standard library, then cross-checked against NumPy.

## What it does

- Loads a numeric column from a CSV and separates valid values from bad rows
- Computes mean, median, mode, variance, standard deviation and quartiles
- Detects outliers with the IQR (interquartile range) method
- Wraps everything in a `StatisticsAnalyzer` class with a one-call report
- Verifies results against NumPy

## Project structure

```
day3-stats-toolkit/
├── data/
│   └── agent_deposits.csv      # Wakala Plus agent daily deposits
├── stats_toolkit.py            # Toolkit functions and StatisticsAnalyzer
├── stats_toolkit.ipynb         # Notebook with step-by-step development and output
├── starter.py                  # Starter file
├── test_stats_toolkit.py       # Tests
├── pyproject.toml
└── README.md
```

## Setup

This is a [uv](https://docs.astral.sh/uv/) project on Python 3.13.

```bash
uv sync
```

NumPy is only needed for the verification step (`compare_with_numpy`); the toolkit itself uses just `csv`, `math` and `pathlib`.

## Functions

| Function | Description |
| --- | --- |
| `load_column(path, column)` | Returns `(valid_floats, errors)`. `errors` is a list of `(row_number, raw_value)` for rows that could not be converted to a number. Row numbers count the header as row 1. |
| `mean(values)` | Arithmetic mean |
| `median(values)` | Middle value, or the average of the two middle values for an even count |
| `mode(values)` | List of every value that occurs most often (so ties are returned together) |
| `variance(values, sample=True)` | Sample variance (n - 1) by default; population variance (n) when `sample=False` |
| `std_dev(values, sample=True)` | Square root of the variance, same `sample` switch |
| `quartiles(values)` | Returns `(Q1, Q2, Q3)` |
| `iqr_outliers(values, k=1.5)` | Returns the IQR, lower and upper fences and the outliers outside them |

All functions raise `ValueError` on an empty list, and `variance` raises it when a sample has fewer than two points.

### Quartile method

Quartiles use a simple positional method on the sorted data: Q1 is the value at index `n // 4`, Q2 at `n // 2` and Q3 at `3n // 4`. There is no interpolation, so results can differ slightly from NumPy's `percentile` or `quantile`, which interpolate by default.

### Outlier rule

A value is an outlier if it is below `Q1 - k * IQR` or above `Q3 + k * IQR`, with `k = 1.5` by default.

## StatisticsAnalyzer

```python
from pathlib import Path

DATA_PATH = Path("data") / "agent_deposits.csv"

analyzer = StatisticsAnalyzer.from_csv(DATA_PATH, "transactions")

print(analyzer.report())     # formatted text report
print(analyzer.summary())    # same statistics as a dict

clean = analyzer.without_outliers()   # new analyzer with outliers removed
print(clean.report())
```

| Member | Description |
| --- | --- |
| `StatisticsAnalyzer(values, name)` | Build directly from a list of floats |
| `from_csv(path, column)` | Load a column, warn about invalid rows, and return an analyzer |
| `summary()` | Dict of all statistics |
| `without_outliers()` | New analyzer with IQR outliers filtered out |
| `report()` | Human-readable report string |

## NumPy check

`compare_with_numpy(analyzer)` imports NumPy inside the function, recomputes the mean, median, mode, variance and standard deviation, and returns `{statistic: matches}`. Variance and standard deviation are compared using `ddof=1` to match the sample formulas.

```python
print(compare_with_numpy(analyzer))
# {'mean': True, 'median': True, 'mode': True, 'variance': True, 'std_dev': True}
```

## Results on the `transactions` column

| Item | Value |
| --- | --- |
| Valid values | 35 |
| Invalid values | 5 (rows 7, 10, 14 and 29 are empty; row 17 contains `abc`) |
| Mean | 93.11 |
| Median | 94.0 |
| Mode | 73.0 and 132.0 (tie) |
| Variance (sample) | 502.57 |
| Standard deviation (sample) | 22.42 |
| Quartiles (Q1, Q2, Q3) | 73.0, 94.0, 110.0 |
| IQR | 37.0 |
| Fences | 17.5 to 165.5 |
| Outliers | None |

Because no values fall outside the fences, `without_outliers()` returns the same 35 values and its report is identical to the original.

## Data handling

Rows that are empty or non-numeric are skipped rather than stopping the run. They are reported with their row number so the source data can be corrected.

## Tests

```bash
uv run pytest
```
