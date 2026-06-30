from dataclasses import dataclass


@dataclass
class Job:
    id: int
    title: str
    url: str

    description: str | None = None
    reward: str | None = None

    application_deadline: str | None = None
    published_at: str | None = None

    application_count: int | None = None
    recruitment_count: int | None = None
