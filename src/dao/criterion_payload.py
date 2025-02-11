from dataclasses import dataclass, field
from typing import List

@dataclass
class SubCriterion:
    name: str
    weight: float

@dataclass
class Criterion:
    name: str
    subcriteria: List[SubCriterion] = field(default_factory=list)

    def add_subcriterion(self, subcriterion: SubCriterion):
        self.subcriteria.append(subcriterion)
