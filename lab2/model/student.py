
from dataclasses import dataclass
from typing import List

@dataclass
class Student:
    def __init__(self, full_name, group, activities, id=None):
        self.id = id
        self.full_name = full_name
        self.group = group
        self.activities = activities