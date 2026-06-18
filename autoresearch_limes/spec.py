from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .config import _load_mapping


_DIRECTIONS = {"higher", "lower"}


@dataclass(frozen=True)
class MetricSpec:
    name: str
    direction: str
    primary: bool = False


@dataclass(frozen=True)
class CostSpec:
    max_runtime_minutes: float | None = None
    max_budget_eur: float | None = None
    hardware: str | None = None


@dataclass(frozen=True)
class DataBoundaries:
    train: str
    validation: str
    heldout: str


@dataclass(frozen=True)
class PromotionGate:
    metric: str
    threshold: float
    direction: str
    requires_replay: bool = False


@dataclass(frozen=True)
class ResearchSpec:
    identifier: str
    objective: str
    hypothesis: str
    method: str
    baselines: list[str]
    metrics: list[MetricSpec]
    costs: CostSpec
    data_boundaries: DataBoundaries
    promotion_gate: PromotionGate
    expected_artifact: str

    @property
    def primary_metric(self) -> MetricSpec:
        for metric in self.metrics:
            if metric.primary:
                return metric
        return self.metrics[0]

    def summary(self) -> dict[str, Any]:
        return {
            "id": self.identifier,
            "objective": self.objective,
            "primary_metric": self.primary_metric.name,
            "promotion_metric": self.promotion_gate.metric,
            "expected_artifact": self.expected_artifact,
        }


def load_research_spec(path: str | Path) -> ResearchSpec:
    spec_path = Path(path)
    data = _load_mapping(spec_path)
    identifier = str(data.get("id") or spec_path.stem)

    return ResearchSpec(
        identifier=identifier,
        objective=_required_text(data, "objective"),
        hypothesis=_required_text(data, "hypothesis"),
        method=_required_text(data, "method"),
        baselines=_required_text_list(data, "baselines"),
        metrics=_load_metrics(data.get("metrics")),
        costs=_load_costs(data.get("costs")),
        data_boundaries=_load_boundaries(data.get("data_boundaries")),
        promotion_gate=_load_promotion_gate(data.get("promotion_gate")),
        expected_artifact=_required_text(data, "expected_artifact"),
    )


def _required_text(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Research spec requires non-empty {key}")
    return value.strip()


def _required_text_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list) or not value:
        raise ValueError(f"Research spec requires non-empty {key}")
    items = [str(item).strip() for item in value]
    if any(not item for item in items):
        raise ValueError(f"Research spec {key} cannot contain empty values")
    return items


def _load_metrics(value: Any) -> list[MetricSpec]:
    if not isinstance(value, list) or not value:
        raise ValueError("Research spec requires non-empty metrics")

    metrics = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("Each metric must be a mapping")
        name = _required_text(item, "name")
        direction = _direction(item.get("direction"), f"metric {name}")
        metrics.append(
            MetricSpec(
                name=name,
                direction=direction,
                primary=bool(item.get("primary", False)),
            )
        )
    return metrics


def _load_costs(value: Any) -> CostSpec:
    if not isinstance(value, dict):
        raise ValueError("Research spec requires costs")

    runtime = value.get("max_runtime_minutes")
    budget = value.get("max_budget_eur")
    return CostSpec(
        max_runtime_minutes=float(runtime) if runtime is not None else None,
        max_budget_eur=float(budget) if budget is not None else None,
        hardware=str(value["hardware"]) if value.get("hardware") is not None else None,
    )


def _load_boundaries(value: Any) -> DataBoundaries:
    if not isinstance(value, dict):
        raise ValueError("Research spec requires data_boundaries")
    return DataBoundaries(
        train=_required_text(value, "train"),
        validation=_required_text(value, "validation"),
        heldout=_required_text(value, "heldout"),
    )


def _load_promotion_gate(value: Any) -> PromotionGate:
    if not isinstance(value, dict):
        raise ValueError("Research spec requires promotion_gate")

    threshold = value.get("threshold")
    if not isinstance(threshold, int | float):
        raise ValueError("promotion_gate threshold must be numeric")

    return PromotionGate(
        metric=_required_text(value, "metric"),
        threshold=float(threshold),
        direction=_direction(value.get("direction"), "promotion_gate"),
        requires_replay=bool(value.get("requires_replay", False)),
    )


def _direction(value: Any, context: str) -> str:
    direction = str(value).strip() if value is not None else ""
    if direction not in _DIRECTIONS:
        raise ValueError(f"{context} direction must be one of {sorted(_DIRECTIONS)}")
    return direction
