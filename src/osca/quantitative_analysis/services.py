from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Iterable
from itertools import pairwise
from statistics import median

from osca.analytical_data import ChartSeriesRequest, build_chart_series
from osca.quantitative_analysis.contracts import (
    DatasetComparisonPoint,
    DatasetComparisonRequest,
    DatasetComparisonResult,
    QuantitativeAnalysisPoint,
    QuantitativeAnalysisRequest,
    QuantitativeAnalysisResult,
    QuantitativeSummary,
)


def analyze_dataset(request: QuantitativeAnalysisRequest) -> QuantitativeAnalysisResult:
    chart = build_chart_series(
        ChartSeriesRequest(
            dataset_revision_id=request.dataset_revision_id,
            payload_path=request.payload_path,
            symbol=request.symbol,
            timeframe=request.timeframe,
            start=request.start,
            end=request.end,
            max_rows=50_000,
        )
    )
    rows = chart.rows
    closes = tuple(row.close for row in rows)
    highs = tuple(row.high for row in rows)
    lows = tuple(row.low for row in rows)
    volumes = tuple(row.volume for row in rows)
    returns = _returns(closes)
    cumulative = _cumulative_returns(returns)
    drawdowns = _drawdowns(closes)
    rsi = _rsi(closes, request.rsi_window)
    roc = _roc(closes, request.rsi_window)
    fast_ema = _ema(closes, request.fast_window)
    slow_ema = _ema(closes, request.slow_window)
    macd = tuple(
        None if fast is None or slow is None else fast - slow
        for fast, slow in zip(fast_ema, slow_ema, strict=True)
    )
    macd_signal = _ema_optional(macd, request.signal_window)
    macd_histogram = tuple(
        None if value is None or signal is None else value - signal
        for value, signal in zip(macd, macd_signal, strict=True)
    )
    atr = _atr(highs, lows, closes, request.atr_window)
    middle = _rolling_mean(closes, request.bollinger_window)
    rolling_std = _rolling_std(tuple(closes), request.bollinger_window)
    upper = tuple(
        None if mean is None or std is None else mean + request.bollinger_stddevs * std
        for mean, std in zip(middle, rolling_std, strict=True)
    )
    lower = tuple(
        None if mean is None or std is None else mean - request.bollinger_stddevs * std
        for mean, std in zip(middle, rolling_std, strict=True)
    )
    obv = _obv(closes, volumes)
    return_std = _rolling_std(returns, request.bollinger_window)
    valid_volatility = tuple(value for value in return_std if value is not None)
    volatility_threshold = median(valid_volatility) if valid_volatility else 0.0

    points = tuple(
        QuantitativeAnalysisPoint(
            timestamp=row.timestamp,
            close=row.close,
            simple_return=returns[index],
            cumulative_return=cumulative[index],
            drawdown=drawdowns[index],
            rsi=rsi[index],
            roc=roc[index],
            macd=macd[index],
            macd_signal=macd_signal[index],
            macd_histogram=macd_histogram[index],
            atr=atr[index],
            bollinger_middle=middle[index],
            bollinger_upper=upper[index],
            bollinger_lower=lower[index],
            obv=obv[index],
            trend_regime=_trend_regime(fast_ema[index], slow_ema[index]),
            volatility_regime=_volatility_regime(return_std[index], volatility_threshold),
        )
        for index, row in enumerate(rows)
    )
    summary = _summary(
        returns=returns,
        drawdowns=drawdowns,
        periods_per_year=request.periods_per_year,
        risk_free_rate=request.risk_free_rate,
        confidence_level=request.confidence_level,
    )
    parameters: dict[str, float | int] = {
        "periods_per_year": request.periods_per_year,
        "risk_free_rate": request.risk_free_rate,
        "confidence_level": request.confidence_level,
        "rsi_window": request.rsi_window,
        "atr_window": request.atr_window,
        "bollinger_window": request.bollinger_window,
        "bollinger_stddevs": request.bollinger_stddevs,
        "fast_window": request.fast_window,
        "slow_window": request.slow_window,
        "signal_window": request.signal_window,
    }
    assumptions = (
        "Returns are close-to-close simple returns.",
        "Annualization uses the explicitly supplied periods_per_year.",
        "Sharpe and Sortino use the explicitly supplied annual risk-free rate.",
        "Historical VaR and CVaR are descriptive empirical estimates, not forecasts.",
        "No missing timestamps are synthesized and no prices are forward-filled.",
    )
    findings = _findings(rows_count=len(rows), returns=returns, outliers=summary.outlier_count)
    input_digest = _digest(
        {
            "dataset_revision_id": str(request.dataset_revision_id),
            "payload_sha256": chart.payload_sha256,
            "parameters": parameters,
        }
    )
    output_digest = _digest(
        {
            "summary": summary.model_dump(mode="json"),
            "points": [point.model_dump(mode="json") for point in points],
        }
    )
    return QuantitativeAnalysisResult(
        dataset_revision_id=request.dataset_revision_id,
        payload_path=str(request.payload_path),
        payload_sha256=chart.payload_sha256,
        symbol=request.symbol,
        timeframe=request.timeframe,
        first_timestamp=rows[0].timestamp,
        last_timestamp=rows[-1].timestamp,
        summary=summary,
        points=points,
        parameters=parameters,
        assumptions=assumptions,
        findings=findings,
        input_digest=input_digest,
        output_digest=output_digest,
    )


def compare_datasets(request: DatasetComparisonRequest) -> DatasetComparisonResult:
    primary = analyze_dataset(request.primary)
    benchmark = analyze_dataset(request.benchmark)
    primary_returns = {
        point.timestamp: point.simple_return
        for point in primary.points
        if point.simple_return is not None
    }
    benchmark_returns = {
        point.timestamp: point.simple_return
        for point in benchmark.points
        if point.simple_return is not None
    }
    timestamps = tuple(sorted(primary_returns.keys() & benchmark_returns.keys()))
    x = tuple(float(primary_returns[timestamp]) for timestamp in timestamps)
    y = tuple(float(benchmark_returns[timestamp]) for timestamp in timestamps)
    rolling = _rolling_correlation(x, y, request.rolling_window)
    points = tuple(
        DatasetComparisonPoint(
            timestamp=timestamp,
            primary_return=x[index],
            benchmark_return=y[index],
            rolling_correlation=rolling[index],
        )
        for index, timestamp in enumerate(timestamps)
    )
    correlation = _correlation(x, y)
    benchmark_variance = _variance(y)
    beta = None if benchmark_variance in {None, 0.0} else _covariance(x, y) / benchmark_variance
    assumptions = (
        "Datasets are aligned only on exact shared timestamps.",
        "No resampling, interpolation, timezone conversion, or forward filling is performed.",
        "Beta is covariance(primary, benchmark) divided by benchmark population variance.",
    )
    input_digest = _digest(
        {
            "primary": primary.input_digest,
            "benchmark": benchmark.input_digest,
            "rolling_window": request.rolling_window,
        }
    )
    output_digest = _digest(
        {
            "correlation": correlation,
            "beta": beta,
            "points": [point.model_dump(mode="json") for point in points],
        }
    )
    return DatasetComparisonResult(
        primary_revision_id=request.primary.dataset_revision_id,
        benchmark_revision_id=request.benchmark.dataset_revision_id,
        aligned_return_count=len(points),
        correlation=correlation,
        beta=beta,
        points=points,
        assumptions=assumptions,
        input_digest=input_digest,
        output_digest=output_digest,
    )


def _returns(values: tuple[float, ...]) -> tuple[float | None, ...]:
    result: list[float | None] = [None]
    for previous, current in pairwise(values):
        result.append(None if previous == 0 else current / previous - 1.0)
    return tuple(result)


def _cumulative_returns(values: tuple[float | None, ...]) -> tuple[float | None, ...]:
    wealth = 1.0
    result: list[float | None] = []
    for value in values:
        if value is None:
            result.append(None)
        else:
            wealth *= 1.0 + value
            result.append(wealth - 1.0)
    return tuple(result)


def _drawdowns(values: tuple[float, ...]) -> tuple[float, ...]:
    peak = values[0]
    result: list[float] = []
    for value in values:
        peak = max(peak, value)
        result.append(value / peak - 1.0)
    return tuple(result)


def _rolling_mean(values: tuple[float, ...], window: int) -> tuple[float | None, ...]:
    result: list[float | None] = []
    running = 0.0
    for index, value in enumerate(values):
        running += value
        if index >= window:
            running -= values[index - window]
        result.append(running / window if index + 1 >= window else None)
    return tuple(result)


def _rolling_std(
    values: tuple[float | None, ...],
    window: int,
) -> tuple[float | None, ...]:
    result: list[float | None] = []
    for index in range(len(values)):
        segment = values[max(0, index - window + 1) : index + 1]
        if len(segment) < window or any(value is None for value in segment):
            result.append(None)
            continue
        numeric = tuple(float(value) for value in segment if value is not None)
        result.append(math.sqrt(_population_variance(numeric)))
    return tuple(result)


def _ema(values: tuple[float, ...], window: int) -> tuple[float | None, ...]:
    alpha = 2.0 / (window + 1.0)
    current: float | None = None
    result: list[float | None] = []
    for value in values:
        current = value if current is None else alpha * value + (1.0 - alpha) * current
        result.append(current)
    return tuple(result)


def _ema_optional(values: tuple[float | None, ...], window: int) -> tuple[float | None, ...]:
    alpha = 2.0 / (window + 1.0)
    current: float | None = None
    result: list[float | None] = []
    for value in values:
        if value is None:
            result.append(None)
            continue
        current = value if current is None else alpha * value + (1.0 - alpha) * current
        result.append(current)
    return tuple(result)


def _rsi(values: tuple[float, ...], window: int) -> tuple[float | None, ...]:
    changes = (None, *(current - previous for previous, current in pairwise(values)))
    gains = tuple(None if value is None else max(value, 0.0) for value in changes)
    losses = tuple(None if value is None else max(-value, 0.0) for value in changes)
    result: list[float | None] = []
    for index in range(len(values)):
        gain_segment = gains[max(0, index - window + 1) : index + 1]
        loss_segment = losses[max(0, index - window + 1) : index + 1]
        if len(gain_segment) < window or any(value is None for value in gain_segment):
            result.append(None)
            continue
        average_gain = sum(float(value) for value in gain_segment if value is not None) / window
        average_loss = sum(float(value) for value in loss_segment if value is not None) / window
        result.append(100.0 if average_loss == 0 else 100.0 - 100.0 / (1.0 + average_gain / average_loss))
    return tuple(result)


def _roc(values: tuple[float, ...], window: int) -> tuple[float | None, ...]:
    return tuple(
        None if index < window or values[index - window] == 0 else values[index] / values[index - window] - 1.0
        for index in range(len(values))
    )


def _atr(
    highs: tuple[float, ...],
    lows: tuple[float, ...],
    closes: tuple[float, ...],
    window: int,
) -> tuple[float | None, ...]:
    true_ranges = tuple(
        highs[index] - lows[index]
        if index == 0
        else max(
            highs[index] - lows[index],
            abs(highs[index] - closes[index - 1]),
            abs(lows[index] - closes[index - 1]),
        )
        for index in range(len(closes))
    )
    return _rolling_mean(true_ranges, window)


def _obv(closes: tuple[float, ...], volumes: tuple[float, ...]) -> tuple[float, ...]:
    result = [0.0]
    for index in range(1, len(closes)):
        direction = 1.0 if closes[index] > closes[index - 1] else -1.0 if closes[index] < closes[index - 1] else 0.0
        result.append(result[-1] + direction * volumes[index])
    return tuple(result)


def _trend_regime(fast: float | None, slow: float | None) -> str:
    if fast is None or slow is None:
        return "warmup"
    if fast > slow:
        return "uptrend"
    if fast < slow:
        return "downtrend"
    return "flat"


def _volatility_regime(value: float | None, threshold: float) -> str:
    if value is None:
        return "warmup"
    return "high" if value > threshold else "low"


def _summary(
    *,
    returns: tuple[float | None, ...],
    drawdowns: tuple[float, ...],
    periods_per_year: int,
    risk_free_rate: float,
    confidence_level: float,
) -> QuantitativeSummary:
    numeric = tuple(float(value) for value in returns if value is not None)
    if not numeric:
        return QuantitativeSummary(
            observation_count=len(returns),
            return_count=0,
            total_return=None,
            annualized_return=None,
            annualized_volatility=None,
            downside_volatility=None,
            sharpe_ratio=None,
            sortino_ratio=None,
            maximum_drawdown=min(drawdowns),
            maximum_drawdown_duration=_maximum_drawdown_duration(drawdowns),
            historical_var=None,
            historical_cvar=None,
            mean_return=None,
            median_return=None,
            standard_deviation=None,
            skewness=None,
            excess_kurtosis=None,
            minimum_return=None,
            maximum_return=None,
            q05=None,
            q25=None,
            q75=None,
            q95=None,
            autocorrelation_lag1=None,
            outlier_count=0,
        )
    mean = sum(numeric) / len(numeric)
    variance = _population_variance(numeric)
    std = math.sqrt(variance)
    downside = tuple(min(value, 0.0) for value in numeric)
    downside_std = math.sqrt(sum(value * value for value in downside) / len(downside))
    period_risk_free = (1.0 + risk_free_rate) ** (1.0 / periods_per_year) - 1.0
    excess_mean = mean - period_risk_free
    annualized_volatility = std * math.sqrt(periods_per_year)
    annualized_return = (math.prod(1.0 + value for value in numeric) ** (periods_per_year / len(numeric))) - 1.0
    sorted_returns = tuple(sorted(numeric))
    var_index = max(0, min(len(sorted_returns) - 1, math.ceil((1.0 - confidence_level) * len(sorted_returns)) - 1))
    historical_var = sorted_returns[var_index]
    tail = tuple(value for value in sorted_returns if value <= historical_var)
    zscores = tuple(0.0 if std == 0 else abs((value - mean) / std) for value in numeric)
    return QuantitativeSummary(
        observation_count=len(returns),
        return_count=len(numeric),
        total_return=math.prod(1.0 + value for value in numeric) - 1.0,
        annualized_return=annualized_return,
        annualized_volatility=annualized_volatility,
        downside_volatility=downside_std * math.sqrt(periods_per_year),
        sharpe_ratio=None if std == 0 else excess_mean / std * math.sqrt(periods_per_year),
        sortino_ratio=None if downside_std == 0 else excess_mean / downside_std * math.sqrt(periods_per_year),
        maximum_drawdown=min(drawdowns),
        maximum_drawdown_duration=_maximum_drawdown_duration(drawdowns),
        historical_var=historical_var,
        historical_cvar=sum(tail) / len(tail),
        mean_return=mean,
        median_return=median(numeric),
        standard_deviation=std,
        skewness=_skewness(numeric, mean, std),
        excess_kurtosis=_excess_kurtosis(numeric, mean, std),
        minimum_return=min(numeric),
        maximum_return=max(numeric),
        q05=_quantile(sorted_returns, 0.05),
        q25=_quantile(sorted_returns, 0.25),
        q75=_quantile(sorted_returns, 0.75),
        q95=_quantile(sorted_returns, 0.95),
        autocorrelation_lag1=_correlation(numeric[:-1], numeric[1:]),
        outlier_count=sum(value > 3.0 for value in zscores),
    )


def _maximum_drawdown_duration(drawdowns: tuple[float, ...]) -> int:
    longest = 0
    current = 0
    for value in drawdowns:
        current = current + 1 if value < 0 else 0
        longest = max(longest, current)
    return longest


def _population_variance(values: tuple[float, ...]) -> float:
    mean = sum(values) / len(values)
    return sum((value - mean) ** 2 for value in values) / len(values)


def _variance(values: tuple[float, ...]) -> float | None:
    return None if not values else _population_variance(values)


def _covariance(x: tuple[float, ...], y: tuple[float, ...]) -> float:
    if not x or len(x) != len(y):
        return 0.0
    mean_x = sum(x) / len(x)
    mean_y = sum(y) / len(y)
    return sum((a - mean_x) * (b - mean_y) for a, b in zip(x, y, strict=True)) / len(x)


def _correlation(x: tuple[float, ...], y: tuple[float, ...]) -> float | None:
    if len(x) < 2 or len(x) != len(y):
        return None
    variance_x = _population_variance(x)
    variance_y = _population_variance(y)
    if variance_x == 0 or variance_y == 0:
        return None
    return _covariance(x, y) / math.sqrt(variance_x * variance_y)


def _rolling_correlation(
    x: tuple[float, ...],
    y: tuple[float, ...],
    window: int,
) -> tuple[float | None, ...]:
    return tuple(
        None if index + 1 < window else _correlation(x[index - window + 1 : index + 1], y[index - window + 1 : index + 1])
        for index in range(len(x))
    )


def _quantile(sorted_values: tuple[float, ...], probability: float) -> float:
    if len(sorted_values) == 1:
        return sorted_values[0]
    position = probability * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def _skewness(values: tuple[float, ...], mean: float, std: float) -> float | None:
    return None if std == 0 else sum(((value - mean) / std) ** 3 for value in values) / len(values)


def _excess_kurtosis(values: tuple[float, ...], mean: float, std: float) -> float | None:
    return None if std == 0 else sum(((value - mean) / std) ** 4 for value in values) / len(values) - 3.0


def _findings(
    *, rows_count: int,
    returns: tuple[float | None, ...],
    outliers: int,
) -> tuple[str, ...]:
    findings: list[str] = []
    if rows_count < 30:
        findings.append("Small sample: many statistical estimates are unstable below 30 observations.")
    if outliers:
        findings.append(f"Detected {outliers} return observations beyond three population standard deviations.")
    if any(value is None for value in returns[1:]):
        findings.append("One or more returns were unavailable because a previous close was zero.")
    return tuple(findings)


def _digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(payload.encode()).hexdigest()
