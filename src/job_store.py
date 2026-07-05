from models import Job


def build_job_index(jobs: list[Job]) -> dict[int, Job]:
    index: dict[int, Job] = {}

    for job in jobs:
        if job.id in index:
            raise ValueError(f"Duplicate job id found: {job.id}")
        index[job.id] = job

    return index


def has_meaningful_changes(existing_job: Job, new_job: Job) -> bool:
    fields_to_compare = (
        "title",
        "url",
        "category",
        "sub_category",
        "description",
        "reward",
        "application_deadline",
        "published_at",
        "delivery_deadline",
        "is_remote",
        "application_count",
        "contract_count",
        "recruitment_count",
        "favorite_count",
        "client",
    )

    for field_name in fields_to_compare:
        if getattr(existing_job, field_name) != getattr(new_job, field_name):
            return True

    return False
