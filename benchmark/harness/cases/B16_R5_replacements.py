"""R5 prospective replacements: replay frozen assertions with an existing owner.

Each entry names one exact frozen method. We invoke its original body verbatim;
the only adaptation for ordinary methods adds --owner system to task creation.
B10's two methods need explicit replacements because their asserted values change.
Nothing in this module mutates an original case or a real continuation workspace.
"""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest

import regression
import workspace as w


# Origin, replacement class, replacement method. Keys are full frozen unittest IDs.
METHODS = {
    "regression.Regression.test_baseline_migration_corruption": ("baseline", "BaselineMigration", "test_baseline_migration_corruption_with_owner"),
    "regression.Regression.test_baseline_overdue_fixture": ("baseline", "BaselineOverdue", "test_baseline_overdue_fixture_with_owner"),
    "regression.Regression.test_b02_tags_and_failure": ("B02", "Tags", "test_b02_tags_and_failure_with_owner"),
    "regression_B03.cases.<locals>.TagListing.test_exact_case_sensitive_tag_with_completed_tasks": ("B03", "TagExact", "test_exact_case_sensitive_tag_with_completed_tasks_with_owner"),
    "regression_B03.cases.<locals>.TagListing.test_blank_queries_leave_storage_unchanged": ("B03", "TagBlank", "test_blank_queries_leave_storage_unchanged_with_owner"),
    "regression_B05.cases.<locals>.StatusListing.test_both_statuses_and_no_write": ("B05", "Status", "test_both_statuses_and_no_write_with_owner"),
    "regression_B06.cases.<locals>.Categories.test_create_filter_and_failed_create": ("B06", "Categories", "test_create_filter_and_failed_create_with_owner"),
    "regression_B08.cases.<locals>.Archival.test_archive_pending_completed_and_visibility": ("B08", "Archival", "test_archive_pending_completed_and_visibility_with_owner"),
    "regression_B09.cases.<locals>.DueWindow.test_inclusive_window_pending_nonarchived_and_normal_order": ("B09", "DueWindow", "test_inclusive_window_pending_nonarchived_and_normal_order_with_owner"),
    "regression_B09.cases.<locals>.DueWindow.test_invalid_ranges_and_timestamps_do_not_write": ("B09", "DueInvalid", "test_invalid_ranges_and_timestamps_do_not_write_with_owner"),
    "regression_B10.cases.<locals>.Owner.test_trim_reject_and_exact_owner_listing": ("B10", "Owner", "test_registered_trim_reject_and_exact_owner_listing"),
    "regression_B10.cases.<locals>.Owner.test_migration_defaults_unowned": ("B10", "OwnerMigration", "test_migration_defaults_system"),
    "regression_B11.cases.<locals>.DeletionRule.test_lifecycle_priority_and_completed_delete_rule": ("B11", "DeletionLifecycle", "test_lifecycle_priority_and_completed_delete_rule_with_owner"),
    "regression_B11.cases.<locals>.DeletionRule.test_pending_deletion_with_and_without_archive": ("B11", "DeletionPending", "test_pending_deletion_with_and_without_archive_with_owner"),
    "regression_B12.cases.<locals>.Urgent.test_urgent_overdue_exclusions_order_and_prior_overdue": ("B12", "Urgent", "test_urgent_overdue_exclusions_order_and_prior_overdue_with_owner"),
    "regression_B12.cases.<locals>.Urgent.test_strict_current_time_and_empty_query_never_write": ("B12", "UrgentBoundary", "test_strict_current_time_and_empty_query_never_write_with_owner"),
    "regression_B13.cases.<locals>.ArchivedMutations.test_archived_pending_and_completed_mutations_are_rejected": ("B13", "Archived", "test_archived_pending_and_completed_mutations_are_rejected_with_owner"),
    "regression_B13.cases.<locals>.ArchivedMutations.test_unarchived_operations_remain_valid": ("B13", "Active", "test_unarchived_operations_remain_valid_with_owner"),
    "regression_B14.cases.<locals>.Dependencies.test_order_cycles_and_no_write_failures": ("B14", "DependencyCycles", "test_order_cycles_and_no_write_failures_with_owner"),
    "regression_B14.cases.<locals>.Dependencies.test_archived_reference_and_explicit_migration": ("B14", "DependencyMigration", "test_archived_reference_and_explicit_migration_with_owner"),
    "regression_B15.cases.<locals>.CompletionDependencies.test_pending_dependencies_reject_without_writes_then_succeed": ("B15", "CompletionGate", "test_pending_dependencies_reject_without_writes_then_succeed_with_owner"),
    "regression_B15.cases.<locals>.CompletionDependencies.test_archived_parent_still_obeys_terminal_transition": ("B15", "CompletionArchived", "test_archived_parent_still_obeys_terminal_transition_with_owner"),
    "regression_B11_R4.cases.<locals>.Source.test_verbatim_default_and_mutations_after_b11": ("B11", "Source", "test_verbatim_default_and_mutations_after_b11_with_owner"),
    "regression_B11_R4.cases.<locals>.Notes.test_append_order_trim_and_failed_append_after_b11": ("B11", "Notes", "test_append_order_trim_and_failed_append_after_b11_with_owner"),
    "regression.Regression.test_baseline_lifecycle_filters_failures": ("baseline", "BaselineLifecycle", "test_baseline_lifecycle_filters_failures_with_owner"),
    "regression.Regression.test_b01_priority_and_regression": ("B01", "Priority", "test_b01_priority_and_regression_with_owner"),
    "regression_B04.cases.<locals>.SourceLabel.test_verbatim_default_and_mutations": ("B04", "SourceBeforeB11", "test_verbatim_default_and_mutations_with_owner"),
}

SPECIAL = {
    "regression_B10.cases.<locals>.Owner.test_trim_reject_and_exact_owner_listing",
    "regression_B10.cases.<locals>.Owner.test_migration_defaults_unowned",
}


def replacement_id(old):
    _, cls, method = METHODS[old]
    return f"regression_B16_R5.cases.<locals>.{cls}.{method}"


def _with_owner(args):
    if args and args[0] == "create" and "--owner" not in args:
        return (*args, "--owner", "system")
    return args


def _call(self, cwd, *args, **kwargs):
    return type(self).__original_call__(self, cwd, *_with_owner(args), **kwargs)


class OwnerCases(unittest.TestCase):
    app = None
    profile = None

    def call(self, cwd, *args, error=None):
        result = subprocess.run([sys.executable, str(self.app), *args], cwd=cwd,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1 if error else 0, result)
        if error:
            self.assertEqual(result.stdout, "")
            self.assertEqual(json.loads(result.stderr), {"error": error})
            return None
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)


def registered_trim_reject_and_exact_owner_listing(self):
    with tempfile.TemporaryDirectory() as folder:
        cwd = Path(folder)
        for bad in ("", " \t "):
            self.call(cwd, "create", "--title", "bad", "--description", "x",
                      "--owner", bad, error="invalid_owner")
        self.assertFalse((cwd / "tasks.json").exists())
        self.assertEqual(self.call(cwd, "create-user", "--id", "Alex"), {"id": "Alex"})
        self.assertEqual(self.call(cwd, "create-user", "--id", "alex"), {"id": "alex"})
        first = self.call(cwd, "create", "--title", "first", "--description", "x",
                          "--owner", "  Alex  ")
        second = self.call(cwd, "create", "--title", "second", "--description", "x",
                           "--owner", "Alex")
        other = self.call(cwd, "create", "--title", "other", "--description", "x",
                          "--owner", "alex")
        formerly_unowned = self.call(cwd, "create", "--title", "unowned", "--description", "x",
                                    "--owner", "system")
        self.assertEqual([t["owner"] for t in (first, second, other, formerly_unowned)],
                         ["Alex", "Alex", "alex", "system"])
        completed = self.call(cwd, "complete", "--id", first["id"])
        self.assertEqual(completed["owner"], "Alex")
        normal = self.call(cwd, "list")
        before = (cwd / "tasks.json").read_bytes()
        for owner in ("Alex", "alex", "", " Alex ", "missing", "system"):
            self.assertEqual(self.call(cwd, "list-owner", "--owner", owner),
                             [task for task in normal if task["owner"] == owner])
        self.assertEqual((cwd / "tasks.json").read_bytes(), before)
        self.assertEqual(self.call(cwd, "delete", "--id", second["id"])["owner"], "Alex")


def migration_defaults_system(self):
    with tempfile.TemporaryDirectory() as folder:
        cwd = Path(folder)
        old = {"id": "old", "title": "old", "description": "x", "status": "pending",
               "priority": "NORMAL", "created_at": "2026-01-01T00:00:00Z", "due_date": None}
        path = cwd / "tasks.json"
        path.write_text(json.dumps({"schema_version": 3, "records": [old]}), encoding="utf-8")
        before = path.read_bytes()
        self.call(cwd, "list", error="migration_required")
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(self.call(cwd, "migrate"), {"migrated": 1})
        migrated = {**old, **self.profile["migration_defaults"]}
        self.assertEqual(migrated["owner"], "system")
        self.assertEqual(self.call(cwd, "list"), [migrated])
        self.assertEqual(self.call(cwd, "list-owner", "--owner", "system"), [migrated])
        self.assertEqual(self.call(cwd, "list-owner", "--owner", ""), [])
        self.assertEqual(json.loads(path.read_text(encoding="utf-8"))["schema_version"],
                         self.profile["schema_version"])


def cases(suite, selected, app, profile):
    """Construct exact replacements from loaded original methods, without editing them."""
    originals = {}

    def visit(tests):
        for test in tests:
            if isinstance(test, unittest.TestSuite):
                visit(test)
            elif test.id() in selected:
                w.require(test.id() not in originals, "duplicate frozen method")
                originals[test.id()] = test

    visit(suite)
    w.require(set(originals) == set(selected) and set(selected) <= set(METHODS),
              "B16 supersession must identify one loaded original per replacement")
    result = unittest.TestSuite()
    for old in METHODS:
        if old not in selected:
            continue
        source = originals[old]
        origin, cls_name, method_name = METHODS[old]
        w.require(origin == "baseline" or origin in profile["achieved"], "inactive origin")
        if old in SPECIAL:
            body = (registered_trim_reject_and_exact_owner_listing
                    if old.endswith("test_trim_reject_and_exact_owner_listing")
                    else migration_defaults_system)
            cls = type(cls_name, (OwnerCases,), {"__module__": __name__,
                    "__qualname__": f"cases.<locals>.{cls_name}",
                    "app": app, "profile": profile, method_name: body})
        else:
            method = getattr(type(source), source._testMethodName)
            if old.startswith("regression.Regression."):
                globals_ = dict(method.__globals__)
                baseline_call = globals_["call"]

                def owner_call(cwd, *args, _base=baseline_call, **kwargs):
                    return _base(cwd, *_with_owner(args), **kwargs)

                globals_["call"] = owner_call
                method = types.FunctionType(method.__code__, globals_, method.__name__,
                                            method.__defaults__, method.__closure__)
                base = type(source)
                attributes = {"__module__": __name__,
                              "__qualname__": f"cases.<locals>.{cls_name}", method_name: method}
            else:
                base = type(source)
                attributes = {"__module__": __name__,
                              "__qualname__": f"cases.<locals>.{cls_name}",
                              "__original_call__": base.call, "call": _call,
                              method_name: method}
            cls = type(cls_name, (base,), attributes)
        replacement = cls(method_name)
        w.require(replacement.id() == replacement_id(old), "B16 replacement ID drift")
        result.addTest(replacement)
    w.require(result.countTestCases() == len(selected), "B16 replacement count mismatch")
    return result
