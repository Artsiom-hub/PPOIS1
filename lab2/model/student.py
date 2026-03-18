# model/student.py
from dataclasses import dataclass
from typing import List

@dataclass
class Student:
    full_name: str
    group: str
    activities: List[int]  