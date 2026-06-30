from dataclasses import dataclass


@dataclass
class Job:
    id: int
    title: str
    url: str