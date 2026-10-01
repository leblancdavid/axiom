"""Conventional, source-maintained implementation of the benchmark task CLI."""

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
from uuid import uuid4


STORE = Path("tasks.json")
VERSION = 3
PRIORITIES = ("LOW", "NORMAL", "HIGH")
STATUSES = ("pending", "completed")


class TaskError(Exception):
    pass


def parse_utc(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("expected UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset().total_seconds() != 0:
        raise ValueError("expected UTC timestamp")
    return parsed


@dataclass
class Task:
    id: str
    title: str
    description: str
    status: str
    priority: str
    created_at: str
    due_date: str | None

    @classmethod
    def from_record(cls, record):
        if not isinstance(record, dict) or set(record) != set(cls.__dataclass_fields__):
            raise TaskError("invalid_state")
        if (not isinstance(record["id"], str) or not record["id"].strip()
                or not isinstance(record["title"], str) or not record["title"].strip()
                or not isinstance(record["description"], str)
                or record["status"] not in STATUSES
                or record["priority"] not in PRIORITIES):
            raise TaskError("invalid_state")
        try:
            parse_utc(record["created_at"])
            if record["due_date"] is not None:
                parse_utc(record["due_date"])
        except ValueError as exc:
            raise TaskError("invalid_state") from exc
        return cls(**record)


class TaskStore:
    def __init__(self, path=STORE):
        self.path = Path(path)

    def _load_payload(self):
        try:
            with self.path.open(encoding="utf-8") as source:
                return json.load(source)
        except FileNotFoundError as exc:
            if self.path.exists():
                raise TaskError("persistence_failure") from exc
            return None
        except (json.JSONDecodeError, UnicodeError) as exc:
            raise TaskError("invalid_state") from exc
        except OSError as exc:
            raise TaskError("persistence_failure") from exc

    @staticmethod
    def _records(rows):
        if not isinstance(rows, list):
            raise TaskError("invalid_state")
        tasks = [Task.from_record(row) for row in rows]
        if len({task.id for task in tasks}) != len(tasks):
            raise TaskError("invalid_state")
        return tasks

    def load(self):
        payload = self._load_payload()
        if payload is None:
            return []
        if not isinstance(payload, dict) or payload.get("schema_version") != VERSION:
            raise TaskError("migration_required")
        if set(payload) != {"schema_version", "records"}:
            raise TaskError("invalid_state")
        return self._records(payload["records"])

    def save(self, tasks):
        self._records([asdict(task) for task in tasks])
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent,
                prefix=".tasks-", suffix=".tmp", delete=False,
            ) as dest:
                temporary = Path(dest.name)
                json.dump({"schema_version": VERSION, "records": [asdict(t) for t in tasks]},
                          dest, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
                dest.write("\n")
            os.replace(temporary, self.path)
        except OSError as exc:
            raise TaskError("persistence_failure") from exc
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def migrate(self):
        payload = self._load_payload()
        if payload is None:
            return {"migrated": 0}
        if isinstance(payload, dict) and payload.get("schema_version") == VERSION:
            self.load()
            return {"migrated": 0}
        if isinstance(payload, list):
            version, rows = 1, payload
        elif isinstance(payload, dict) and payload.get("schema_version") == 2:
            if set(payload) != {"schema_version", "records"}:
                raise TaskError("invalid_state")
            version, rows = 2, payload["records"]
        else:
            raise TaskError("invalid_state")
        if not isinstance(rows, list):
            raise TaskError("invalid_state")
        fields = set(Task.__dataclass_fields__)
        missing = {"priority", "due_date"} if version == 1 else {"due_date"}
        migrated = []
        for row in rows:
            if not isinstance(row, dict) or set(row) != fields - missing:
                raise TaskError("invalid_state")
            migrated.append({**row, **({"priority": "NORMAL"} if version == 1 else {}), "due_date": None})
        tasks = self._records(migrated)
        self.save(tasks)
        return {"migrated": len(tasks)}


class TaskService:
    def __init__(self, store):
        self.store = store

    @staticmethod
    def ordered(tasks):
        return sorted(tasks, key=lambda task: (task.created_at, task.id))

    def create(self, title, description, priority="NORMAL", due_date=None):
        tasks = self.store.load()
        if not title.strip():
            raise TaskError("invalid_title")
        if due_date is not None:
            try:
                parse_utc(due_date)
            except ValueError as exc:
                raise TaskError("invalid_due_date") from exc
        task = Task(str(uuid4()), title, description, "pending", priority,
                    datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"), due_date)
        if any(other.id == task.id for other in tasks):
            raise TaskError("id_collision")
        tasks.append(task)
        self.store.save(tasks)
        return task

    def list(self, mode):
        tasks = self.store.load()
        if mode == "list-high":
            tasks = [task for task in tasks if task.priority == "HIGH"]
        elif mode == "list-overdue":
            now = datetime.now(timezone.utc)
            tasks = [task for task in tasks if task.status == "pending" and task.due_date is not None
                     and parse_utc(task.due_date) < now]
        return self.ordered(tasks)

    def change(self, task_id, action):
        tasks = self.store.load()
        task = next((item for item in tasks if item.id == task_id), None)
        if task is None:
            raise TaskError("task_not_found")
        if action == "complete":
            if task.status != "pending":
                raise TaskError("invalid_transition")
            task.status = "completed"
        else:
            tasks.remove(task)
        self.store.save(tasks)
        return task


def main(argv=None):
    parser = argparse.ArgumentParser(prog="task_manager")
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create")
    create.add_argument("--title", required=True)
    create.add_argument("--description", required=True)
    create.add_argument("--priority", choices=PRIORITIES)
    create.add_argument("--due-date")
    for name in ("list", "list-high", "list-overdue", "migrate"):
        commands.add_parser(name)
    for name in ("complete", "delete"):
        commands.add_parser(name).add_argument("--id", required=True)
    args = parser.parse_args(argv)
    service = TaskService(TaskStore())
    try:
        if args.command == "create":
            result = service.create(args.title, args.description, args.priority or "NORMAL", args.due_date)
        elif args.command in ("list", "list-high", "list-overdue"):
            result = service.list(args.command)
        elif args.command == "migrate":
            result = service.store.migrate()
        else:
            result = service.change(args.id, args.command)
    except TaskError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    if isinstance(result, list):
        result = [asdict(task) for task in result]
    elif isinstance(result, Task):
        result = asdict(result)
    print(json.dumps(result, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
