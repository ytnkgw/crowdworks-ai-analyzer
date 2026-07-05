import json
from pathlib import Path
from models import Client, Job, JobMetadata, JobSourceMetadata


def load_jobs_from_json(file_path: str | Path) -> list[Job]:
    path = Path(file_path)
    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if not isinstance(payload, list):
        raise ValueError("JSON root must be a list")

    jobs: list[Job] = []
    for item in payload:
        if not isinstance(item, dict):
            continue

        client_data = item.get("client")
        client = None
        if isinstance(client_data, dict):
            client = Client(
                id=client_data.get("id"),
                name=client_data.get("name"),
                rating=client_data.get("rating"),
                identity_verified=client_data.get("identity_verified"),
                rule_checked=client_data.get("rule_checked"),
                jobs_posted_count=client_data.get("jobs_posted_count"),
                project_finished_rate=client_data.get("project_finished_rate"),
                profile_description=client_data.get("profile_description"),
            )

        metadata_data = item.get("metadata")
        metadata = None
        if isinstance(metadata_data, dict):
            sources_data = metadata_data.get("sources")
            sources: list[JobSourceMetadata] = []
            if isinstance(sources_data, list):
                for source in sources_data:
                    if not isinstance(source, dict):
                        continue
                    sources.append(
                        JobSourceMetadata(
                            url=source["url"],
                            first_seen_at=source["first_seen_at"],
                            last_seen_at=source["last_seen_at"],
                            seen_count=source.get("seen_count", 1),
                        )
                    )

            metadata = JobMetadata(
                first_seen_at=metadata_data.get("first_seen_at"),
                last_seen_at=metadata_data.get("last_seen_at"),
                updated_at=metadata_data.get("updated_at"),
                sources=sources,
            )

        jobs.append(
            Job(
                id=item["id"],
                title=item["title"],
                url=item["url"],
                category=item.get("category"),
                sub_category=item.get("sub_category"),
                description=item.get("description"),
                reward=item.get("reward"),
                application_deadline=item.get("application_deadline"),
                published_at=item.get("published_at"),
                delivery_deadline=item.get("delivery_deadline"),
                is_remote=item.get("is_remote"),
                application_count=item.get("application_count"),
                contract_count=item.get("contract_count"),
                recruitment_count=item.get("recruitment_count"),
                favorite_count=item.get("favorite_count"),
                client=client,
                metadata=metadata,
            )
        )

    return jobs
