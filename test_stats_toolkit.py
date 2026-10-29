"""Unit tests for the toolkit. Run with:  python -m unittest -v   (or pytest)."""
import tempfile
import unittest
from pathlib import Path

from stats_toolkit import (
    mean, median, mode, variance, std_dev, quartiles, iqr_outliers,
    load_column, StatisticsAnalyzer,
)


class TestCentralTendency(unittest.TestCase):
    def test_mean_of_known_values(self):
        self.assertAlmostEqual(mean([1, 2, 3, 4]), 2.5)

    def test_median_even_and_odd_lengths(self):
        self.assertEqual(median([3, 1, 2]), 2)          
        self.assertEqual(median([4, 1, 3, 2]), 2.5)     

    def test_mode_with_ties(self):
        self.assertEqual(mode([1, 1, 2, 2, 3]), [1, 2])  
        self.assertEqual(mode([1, 2, 2, 3]), [2])        
        self.assertEqual(mode([1, 2, 3]), [])            

    def test_empty_input_raises(self):
        for fn in (mean, median, mode, variance, std_dev, quartiles, iqr_outliers):
            with self.assertRaises(ValueError, msg=fn.__name__):
                fn([])


class TestSpread(unittest.TestCase):
    DATA = [2, 4, 4, 4, 5, 5, 7, 9]  # mean 5, sum of squared differences 32

    def test_sample_vs_population_variance(self):
        self.assertAlmostEqual(variance(self.DATA, sample=False), 4.0)       # 32 / 8
        self.assertAlmostEqual(variance(self.DATA, sample=True), 32 / 7)     # 32 / (8 - 1)
        self.assertAlmostEqual(std_dev(self.DATA, sample=False), 2.0)

    def test_std_dev_single_value(self):
        self.assertEqual(std_dev([5], sample=False), 0.0)
        with self.assertRaises(ValueError):
            std_dev([5], sample=True)  # n - 1 = 0, so a sample std dev is undefined


class TestQuartiles(unittest.TestCase):
    def test_quartiles_linear_method(self):
        self.assertEqual(quartiles([1, 2, 3, 4, 5]), (2, 3, 4))
        q1, q2, q3 = quartiles([1, 2, 3, 4])
        self.assertAlmostEqual(q1, 1.75)
        self.assertAlmostEqual(q2, 2.5)
        self.assertAlmostEqual(q3, 3.25)


class TestOutliers(unittest.TestCase):
    def test_no_outliers_in_uniform_data(self):
        self.assertEqual(iqr_outliers([5, 5, 5, 5])["outliers"], [])
        self.assertEqual(iqr_outliers(list(range(1, 11)))["outliers"], [])

    def test_detects_obvious_outlier(self):
        result = iqr_outliers([10, 12, 11, 13, 12, 11, 100])
        self.assertEqual(result["outliers"], [100])
        self.assertAlmostEqual(result["iqr"], 1.5)
        self.assertAlmostEqual(result["upper_fence"], 14.75)
        self.assertAlmostEqual(result["lower_fence"], 8.75)

    def test_without_outliers_returns_new_analyzer(self):
        original = StatisticsAnalyzer([10, 12, 11, 13, 12, 11, 100])
        cleaned = original.without_outliers()
        self.assertIsNot(cleaned, original)                 # a NEW object
        self.assertEqual(original.summary()["count"], 7)    # original untouched
        self.assertEqual(cleaned.summary()["count"], 6)
        self.assertEqual(cleaned.summary()["max"], 13)


class TestLoading(unittest.TestCase):
    def test_invalid_and_missing_values_are_rejected(self):
        csv_text = (
            "date,agent_id,amount\n"
            "2026-01-01,A1,1000\n"      # line 2 valid
            "2026-01-02,A1,\n"          # line 3 empty
            "2026-01-03,A1,N/A\n"       # line 4 placeholder
            "2026-01-04,A1,12O0\n"      # line 5 typo (letter O)
            "2026-01-05,A1,-50\n"       # line 6 negative
            "2026-01-06,A1,2500.5\n"    # line 7 valid
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.csv"
            path.write_text(csv_text, encoding="utf-8")
            values, rejected = load_column(path, "amount")
            analyzer = StatisticsAnalyzer.from_csv(path, "amount")
        self.assertEqual(values, [1000.0, 2500.5])
        self.assertEqual(rejected, [(3, ""), (4, "N/A"), (5, "12O0"), (6, "-50")])
        self.assertEqual(analyzer.rows_read, 6)
        self.assertIn("row 4: 'N/A' (placeholder text)", analyzer.report())

    def test_missing_column_raises_helpful_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.csv"
            path.write_text("a,b\n1,2\n", encoding="utf-8")
            with self.assertRaises(KeyError):
                load_column(path, "nope")


if __name__ == "__main__":
    unittest.main()
