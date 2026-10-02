"""Prospective, source-derived expansion of finite executable acceptance loops.

No application is run. Dynamic task identifiers are retained as entity bindings;
only values forced by the frozen source are resolved. Unknown expressions stay
explicitly unresolved rather than being guessed from an implementation.
"""

import ast
import copy

import regression
import workspace as w


VERSION = "R5.3-PARAMETERIZED-ROOTS/1"


def literal(node, bindings):
    if node is None:
        raise ValueError("dictionary unpacking requires runtime value")
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id in bindings:
        return bindings[node.id]
    if isinstance(node, (ast.Tuple, ast.List)):
        return [literal(item, bindings) for item in node.elts]
    if isinstance(node, ast.Dict):
        result = {}
        for key, value in zip(node.keys, node.values):
            if key is None:
                result.update(literal(value, bindings))
            else:
                result[literal(key, bindings)] = literal(value, bindings)
        return result
    if isinstance(node, ast.DictComp) and len(node.generators) == 1:
        gen = node.generators[0]
        result = {}
        for item in literal(gen.iter, bindings):
            local = {**bindings, gen.target.elts[0].id: item[0], gen.target.elts[1].id: item[1]}
            if all(predicate(test, local) for test in gen.ifs):
                result[literal(node.key, local)] = literal(node.value, local)
        return result
    if isinstance(node, ast.Starred):
        raise ValueError("dynamic dictionary expansion")
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
        return -literal(node.operand, bindings)
    if isinstance(node, ast.Subscript):
        return literal(node.value, bindings)[literal(node.slice, bindings)]
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "range":
        return list(range(*(literal(arg, bindings) for arg in node.args)))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "row":
        return regression.row(*(literal(arg, bindings) for arg in node.args))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "items" and not node.args:
        return list(literal(node.func.value, bindings).items())
    raise ValueError(ast.unparse(node))


def predicate(node, bindings):
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        left, right = literal(node.left, bindings), literal(node.comparators[0], bindings)
        if isinstance(node.ops[0], ast.NotIn):
            return left not in right
        if isinstance(node.ops[0], ast.Eq):
            return left == right
        if isinstance(node.ops[0], ast.Gt):
            return left > right
        if isinstance(node.ops[0], ast.Lt):
            return left < right
        if isinstance(node.ops[0], ast.Is):
            return left is right
    raise ValueError(ast.unparse(node))


def resolved(node, bindings):
    """Replace bound scalars without executing arbitrary source expressions."""
    class Bind(ast.NodeTransformer):
        def visit_Subscript(self, item):
            try:
                value = literal(item, bindings)
                if isinstance(value, (str, int, float, bool)) or value is None:
                    return ast.copy_location(ast.Constant(value=value), item)
            except (ValueError, KeyError, TypeError, IndexError):
                pass
            return self.generic_visit(item)

        def visit_Name(self, item):
            if isinstance(item.ctx, ast.Load) and item.id in bindings:
                value = bindings[item.id]
                if isinstance(value, (str, int, float, bool)) or value is None:
                    return ast.copy_location(ast.Constant(value=value), item)
            return item

    return ast.unparse(ast.fix_missing_locations(Bind().visit(copy.deepcopy(node))))


def cli_calls(node):
    return [item for item in ast.walk(node) if isinstance(item, ast.Call) and
            (isinstance(item.func, ast.Attribute) and item.func.attr in
             ("call", "create", "check_created", "check_task", "upgraded") or
             isinstance(item.func, ast.Name) and item.func.id in ("call", "check_task", "upgraded"))]


def expected_filter(node, bindings, entities):
    """Resolve a list filter over a prior CLI list using source task relationships."""
    if not isinstance(node, ast.ListComp) or len(node.generators) != 1:
        return None
    gen = node.generators[0]
    if not isinstance(gen.target, ast.Name) or not isinstance(gen.iter, ast.Name):
        return None
    if gen.iter.id not in bindings or not isinstance(bindings[gen.iter.id], list):
        return None
    if not isinstance(node.elt, ast.Name) or node.elt.id != gen.target.id or len(gen.ifs) != 1:
        return None
    condition = gen.ifs[0]
    if not isinstance(condition, ast.Compare) or len(condition.ops) != 1 or not isinstance(condition.ops[0], ast.Eq):
        return None
    left = condition.left
    if not (isinstance(left, ast.Subscript) and isinstance(left.value, ast.Name) and
            left.value.id == gen.target.id):
        return None
    try:
        field = literal(left.slice, bindings)
        wanted = literal(condition.comparators[0], bindings)
        return [dict(entities[name]) for name in bindings[gen.iter.id]
                if entities.get(name, {}).get(field) == wanted]
    except (ValueError, KeyError, TypeError):
        return None


def applicable_lineage(lineage, entities):
    """Attach frozen restoration roots only at their stated prior state."""
    if not isinstance(lineage, dict) or "restoration" not in lineage:
        return copy.deepcopy(lineage)
    retained = []
    for entry in lineage["restoration"]:
        statuses = entry.get("precondition", {}).get("at_list_high")
        if statuses is not None and any(
                len(matches := [entity for entity in entities.values()
                                if entity.get("priority") == priority]) != 1 or
                matches[0].get("status") != status
                for priority, status in statuses.items()):
            continue
        retained.append(entry)
    return {**copy.deepcopy(lineage), "restoration": retained}


def distinct_field_count(node, bindings):
    """Resolve a frozen equality on distinct fields of previously bound rows."""
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and
            node.func.id == "len" and len(node.args) == 1 and
            isinstance(node.args[0], ast.SetComp)):
        return None
    comprehension = node.args[0]
    if len(comprehension.generators) != 1 or comprehension.generators[0].ifs:
        return None
    generator = comprehension.generators[0]
    field = comprehension.elt
    if not (isinstance(generator.target, ast.Name) and
            isinstance(field, ast.Subscript) and isinstance(field.value, ast.Name) and
            field.value.id == generator.target.id):
        return None
    try:
        rows = literal(generator.iter, bindings)
        key = literal(field.slice, bindings)
        values = [row[key] for row in rows]
    except (ValueError, KeyError, TypeError, IndexError):
        return None
    return {"field": key, "values": values, "bindings": [row.get("binding") for row in rows]}


def returned_fields(assertion, bindings, entities):
    """Only explicit equalities on bound result fields are observable checks.

    Entity attributes inferred from input options must never satisfy this check:
    the expected values come exclusively from the assertion's right operand.
    """
    if not (isinstance(assertion.func, ast.Attribute) and
            assertion.func.attr == "assertEqual" and len(assertion.args) == 2):
        return []
    left, right = assertion.args
    accesses = left.elts if isinstance(left, (ast.List, ast.Tuple)) else [left]
    if isinstance(left, ast.ListComp) and len(left.generators) == 1:
        gen = left.generators[0]
        if (isinstance(gen.target, ast.Name) and not gen.ifs and
                isinstance(gen.iter, (ast.Tuple, ast.List)) and
                all(isinstance(item, ast.Name) and item.id in entities for item in gen.iter.elts)
                and isinstance(left.elt, ast.Subscript) and
                isinstance(left.elt.value, ast.Name) and left.elt.value.id == gen.target.id):
            accesses = [ast.Subscript(value=item, slice=left.elt.slice, ctx=ast.Load())
                        for item in gen.iter.elts]
        else:
            return []
    try:
        expected = literal(right, bindings)
    except (ValueError, KeyError, TypeError, IndexError):
        return []
    values = expected if isinstance(left, (ast.List, ast.Tuple, ast.ListComp)) and isinstance(expected, list) else [expected]
    if len(accesses) != len(values):
        return []
    result = []
    for access, value in zip(accesses, values):
        if not (isinstance(access, ast.Subscript) and isinstance(access.value, ast.Name)):
            return []
        name = access.value.id
        try:
            field = literal(access.slice, bindings)
        except (ValueError, KeyError, TypeError, IndexError):
            return []
        if name not in entities or not isinstance(field, str):
            return []
        result.append((name, field, value))
    return result


def expand(function, method_id, source_path, state, *, lineage=None, achieved=(), profile=None):
    """Expand loop-owned CLI/assertion sites in execution order, with site identity.

    The AST comes from the loaded executable body. A finite iterator must be
    statically resolvable; otherwise a site is reported as unresolved.
    """
    import inspect
    import textwrap

    tree = ast.parse(textwrap.dedent(inspect.getsource(function))).body[0]
    first = function.__code__.co_firstlineno
    bindings = {"PROFILE": profile, "profile": profile} if profile is not None else {}
    entities = {}
    creation_inputs = {}
    history = []
    roots = []
    observations = []
    direct_assertions = []
    unresolved = []

    def location(node):
        return f"{source_path}:{first + node.lineno - 1}"

    read_only_checks = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.For):
            continue
        # Only an immediately following equality with the saved bytes binds
        # every invocation in the loop to the same read-only store condition.
        for statements in (tree.body, *[parent.body for parent in ast.walk(tree)
                                         if isinstance(parent, (ast.With, ast.If, ast.For))]):
            if node in statements:
                index = statements.index(node)
                if index + 1 < len(statements):
                    following = statements[index + 1]
                    if (isinstance(following, ast.Expr) and isinstance(following.value, ast.Call)
                            and isinstance(following.value.func, ast.Attribute)
                            and following.value.func.attr == "assertEqual" and
                            len(following.value.args) == 2 and
                            isinstance(following.value.args[1], ast.Name) and
                            following.value.args[1].id == "before" and
                            "read_bytes()" in ast.unparse(following.value.args[0])):
                        read_only_checks[first + node.lineno - 1] = location(following)
                break

    def visit(statements, loop=(), context=()):
        for statement in statements:
            if isinstance(statement, (ast.With, ast.AsyncWith)):
                visit(statement.body, loop, (*context, ast.unparse(statement.items[0].context_expr)))
            elif isinstance(statement, ast.If):
                # Frozen achievement guards are determined by the achieved history.
                test = statement.test
                if (isinstance(test, ast.Compare) and isinstance(test.left, ast.Constant)
                        and len(test.ops) == 1 and isinstance(test.ops[0], (ast.In, ast.NotIn))
                        and isinstance(test.comparators[0], ast.Name)
                        and test.comparators[0].id in ("achieved", "ACHIEVED")):
                    active = (test.left.value in achieved) == isinstance(test.ops[0], ast.In)
                    visit(statement.body if active else statement.orelse, loop, (*context, ast.unparse(test)))
                elif isinstance(test, ast.Compare):
                    try:
                        active = predicate(test, bindings)
                    except (ValueError, KeyError, TypeError):
                        visit(statement.body, loop, (*context, ast.unparse(test)))
                        visit(statement.orelse, loop, (*context, f"else: {ast.unparse(test)}"))
                    else:
                        visit(statement.body if active else statement.orelse, loop, (*context, ast.unparse(test)))
                else:
                    visit(statement.body, loop, (*context, ast.unparse(test)))
                    visit(statement.orelse, loop, (*context, f"else: {ast.unparse(test)}"))
            elif isinstance(statement, ast.For):
                try:
                    values = literal(statement.iter, bindings)
                    if not isinstance(values, (list, tuple)):
                        raise ValueError("nonfinite iterator")
                except (ValueError, KeyError, TypeError) as exc:
                    if any(cli_calls(item) or any(isinstance(n, ast.Call) and
                           isinstance(n.func, ast.Attribute) and n.func.attr.startswith("assert")
                           for n in ast.walk(item)) for item in statement.body):
                        unresolved.append({"loop": location(statement), "iterator": ast.unparse(statement.iter),
                                           "reason": str(exc)})
                    continue
                for index, value in enumerate(values):
                    if isinstance(statement.target, ast.Name):
                        additions = {statement.target.id: value}
                    elif isinstance(statement.target, ast.Tuple) and isinstance(value, (tuple, list)):
                        additions = {target.id: part for target, part in zip(statement.target.elts, value)}
                    else:
                        unresolved.append({"loop": location(statement), "reason": "unresolved target"})
                        break
                    bindings.update(additions)
                    visit(statement.body, (*loop, {"source": location(statement), "index": index,
                                           "bindings": copy.deepcopy(additions)}), context)
            else:
                # An assertion over a CLI result is an executable observation
                # even when it is not owned by a finite loop. Join the nested
                # call and assertion before advancing the source-derived state.
                if not loop and isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
                    assertion = statement.value
                    if (isinstance(assertion.func, ast.Attribute) and
                            assertion.func.attr.startswith("assert")):
                        nested = [item for item in ast.walk(assertion.args[0])
                                  if isinstance(item, ast.Call) and
                                  isinstance(item.func, (ast.Attribute, ast.Name)) and
                                  (item.func.attr if isinstance(item.func, ast.Attribute)
                                   else item.func.id) == "call"] if assertion.args else []
                        for call in nested:
                            try:
                                args = [literal(arg, bindings) for arg in call.args[1:]]
                            except (ValueError, KeyError, TypeError, IndexError):
                                args = None
                            try:
                                expected = literal(assertion.args[1], bindings) if len(assertion.args) > 1 else None
                            except (ValueError, KeyError, TypeError, IndexError):
                                expected = None
                            identity = {"method": method_id, "call": location(call),
                                        "call_column": call.col_offset,
                                        "assertion": location(assertion),
                                        "assertion_column": assertion.col_offset,
                                        "context": list(context)}
                            error = next((literal(kw.value, bindings) for kw in call.keywords
                                          if kw.arg == "error"), None)
                            observations.append({"id": w.digest(w.encoded(identity)), **identity,
                                                 "state": state, "operation": args[0] if args else None,
                                                 "arguments": args, "call_expression": resolved(call, bindings),
                                                 "assertion_expression": resolved(assertion, bindings),
                                                 "assertion_kind": assertion.func.attr,
                                                 "expected_result": copy.deepcopy(expected),
                                                 "expected_expression": resolved(assertion.args[1], bindings)
                                                 if len(assertion.args) > 1 else None,
                                                 "expected_result_shape": "exact list of task rows"
                                                 if isinstance(expected, list) else None,
                                                 "expected_success": error is None,
                                                 "expected_error": error,
                                                 "cli_outcome": {"exit": 1 if error is not None else 0,
                                                                 "stderr": "JSON error" if error is not None else "empty",
                                                                 "stdout": "empty" if error is not None else "JSON"},
                                                 "prior_steps": copy.deepcopy(history),
                                                 "entities": copy.deepcopy(entities),
                                                 "lineage": applicable_lineage(lineage, entities)})
                        if (not nested and assertion.func.attr == "assertEqual" and
                                len(assertion.args) == 2 and
                                (distinct := distinct_field_count(assertion.args[0], bindings)) is not None):
                            try:
                                expected_count = literal(assertion.args[1], bindings)
                            except (ValueError, KeyError, TypeError, IndexError):
                                expected_count = None
                            identity = {"method": method_id, "assertion": location(assertion),
                                        "assertion_column": assertion.col_offset,
                                        "context": list(context)}
                            direct_assertions.append({"id": w.digest(w.encoded(identity)), **identity,
                                                      "state": state, "operation": "distinct-field-count",
                                                      "inputs": distinct, "expected_count": expected_count,
                                                      "assertion_expression": resolved(assertion, bindings),
                                                      "entities": copy.deepcopy(entities),
                                                       "prior_steps": copy.deepcopy(history),
                                                       "lineage": applicable_lineage(lineage, entities)})
                        if not nested:
                            for binding, field, expected_value in returned_fields(assertion, bindings, entities):
                                identity = {"method": method_id, "assertion": location(assertion),
                                            "assertion_column": assertion.col_offset,
                                            "binding": binding, "field": field, "context": list(context)}
                                direct_assertions.append({"id": w.digest(w.encoded(identity)), **identity,
                                                          "state": state, "operation": "returned-field-equality",
                                                          "observed_value": f"${binding}.{field}",
                                                          "expected_result": expected_value,
                                                          "creation_input": copy.deepcopy(creation_inputs.get(
                                                              entities[binding].get("binding", binding))),
                                                          "assertion_expression": resolved(assertion, bindings),
                                                          "entities": copy.deepcopy(entities),
                                                          "prior_steps": copy.deepcopy(history),
                                                          "lineage": copy.deepcopy(lineage),
                                                          "provenance": {"carrier": method_id,
                                                                         "assertion": location(assertion)}})
                        if (not nested and assertion.func.attr == "assertIsNone" and
                                len(assertion.args) == 1 and
                                isinstance(assertion.args[0], ast.Subscript) and
                                isinstance(assertion.args[0].value, ast.Name)):
                            field_access = assertion.args[0]
                            binding = field_access.value.id
                            try:
                                field = literal(field_access.slice, bindings)
                            except (ValueError, KeyError, TypeError, IndexError):
                                field = None
                            if field is not None and binding in entities:
                                identity = {"method": method_id, "assertion": location(assertion),
                                            "assertion_column": assertion.col_offset,
                                            "context": list(context)}
                                direct_assertions.append({"id": w.digest(w.encoded(identity)), **identity,
                                                          "state": state, "operation": "field-is-none",
                                                          "inputs": {"binding": binding, "field": field,
                                                                     "entity": copy.deepcopy(entities[binding])},
                                                          "expected_result": None,
                                                          "assertion_expression": resolved(assertion, bindings),
                                                          "entities": copy.deepcopy(entities),
                                                          "prior_steps": copy.deepcopy(history),
                                                          "lineage": applicable_lineage(lineage, entities)})
                if loop:
                    calls = cli_calls(statement)
                    assertions = [item for item in ast.walk(statement) if isinstance(item, ast.Call)
                                  and isinstance(item.func, ast.Attribute) and
                                  item.func.attr.startswith("assert")]
                    for site in calls + assertions:
                        args = None
                        if site in calls and site.args:
                            try:
                                args = [literal(arg, bindings) for arg in site.args[1:]]
                            except (ValueError, KeyError, TypeError):
                                args = None
                        expected = None
                        if site in calls and assertions:
                            assertion = next((a for a in assertions if site in ast.walk(a)), None)
                            if assertion is not None and len(assertion.args) > 1:
                                expected = expected_filter(assertion.args[1], bindings, entities)
                        error = next((literal(kw.value, bindings) for kw in site.keywords if kw.arg == "error"), None)
                        root = {"method": method_id, "state": state, "site": location(site),
                                "column": site.col_offset, "kind": (site.func.attr if isinstance(site.func, ast.Attribute)
                                                                     else site.func.id),
                                "expression": resolved(site, bindings), "arguments": args,
                                "expected_error": error, "expected_result": expected,
                                "expected_expression": resolved(assertions[0].args[1], bindings)
                                if site in calls and assertions and len(assertions[0].args) > 1 else None,
                                "loop": copy.deepcopy(loop), "context": list(context),
                                "prior_steps": copy.deepcopy(history),
                                "entities": copy.deepcopy(entities), "lineage": lineage}
                        if site in calls and root["kind"] in ("call", "create"):
                            root["operation"] = (args[0] if args and root["kind"] == "call"
                                                 else "create" if root["kind"] == "create" else None)
                            root["expected_success"] = error is None
                            root["cli_outcome"] = {"exit": 1 if error else 0,
                                                   "stderr": "JSON error" if error else "empty",
                                                   "stdout": "empty" if error else "JSON"}
                            root["expected_result_shape"] = "JSON list of exact task rows" if expected is not None else None
                            root["expected_persistent_state"] = [read_only_checks[int(item["source"].rsplit(":", 1)[1])]
                                                                   for item in loop if int(item["source"].rsplit(":", 1)[1]) in read_only_checks]
                        if lineage and lineage.get("source"):
                            source_lines = [line for line, carrier in lineage["assertion_lines"].items()
                                            if carrier == first + site.lineno - 1]
                            if source_lines:
                                root["original_assertion"] = f"{lineage['source']}:{source_lines[0]}"
                        root["id"] = w.digest(w.encoded({"method": method_id, "site": root["site"],
                                                          "column": root["column"], "loop": loop}))
                        roots.append(root)
                    for assertion in assertions:
                        for binding, field, expected_value in returned_fields(assertion, bindings, entities):
                            identity = {"method": method_id, "assertion": location(assertion),
                                        "assertion_column": assertion.col_offset,
                                        "binding": binding, "field": field, "loop": copy.deepcopy(loop),
                                        "context": list(context)}
                            direct_assertions.append({"id": w.digest(w.encoded(identity)), **identity,
                                                      "state": state, "operation": "returned-field-equality",
                                                      "observed_value": f"${binding}.{field}",
                                                      "expected_result": expected_value,
                                                      "creation_input": copy.deepcopy(creation_inputs.get(
                                                          entities[binding].get("binding", binding))),
                                                      "assertion_expression": resolved(assertion, bindings),
                                                      "entities": copy.deepcopy(entities),
                                                      "prior_steps": copy.deepcopy(history),
                                                      "lineage": copy.deepcopy(lineage),
                                                      "provenance": {"carrier": method_id,
                                                                     "assertion": location(assertion)}})
                # Track source-derived task identities and the state at each site.
                assignment = statement.value if isinstance(statement, (ast.Assign, ast.AnnAssign)) else None
                target = (statement.targets[0] if isinstance(statement, ast.Assign) and len(statement.targets) == 1
                          else statement.target if isinstance(statement, ast.AnnAssign) else None)
                if isinstance(assignment, ast.ListComp) and isinstance(target, ast.Name) and len(assignment.generators) == 1:
                    gen = assignment.generators[0]
                    if (isinstance(gen.target, ast.Name) and isinstance(assignment.elt, ast.Call)
                            and isinstance(assignment.elt.func, ast.Attribute) and assignment.elt.func.attr == "call"):
                        try:
                            values = literal(gen.iter, bindings)
                            created = []
                            for index, value in enumerate(values):
                                local = {**bindings, gen.target.id: value}
                                args = [literal(arg, local) for arg in assignment.elt.args[1:]]
                                if args[0] != "create":
                                    raise ValueError("non-create comprehension")
                                key = f"{target.id}[{index}]"
                                options = dict(zip(args[1::2], args[2::2]))
                                entity = {"binding": key, "id": f"${key}.id", "title": options.get("--title"),
                                          "owner": options.get("--owner", "system" if "B16" in achieved else ""),
                                          "status": "pending", "dependencies": []}
                                entities[key] = entity
                                created.append(entity)
                            bindings[target.id] = created
                        except (ValueError, KeyError, TypeError):
                            pass
                elif isinstance(assignment, ast.Call) and isinstance(target, ast.Name):
                    try:
                        args = [literal(arg, bindings) for arg in assignment.args[1:]]
                    except (ValueError, KeyError, TypeError):
                        args = []
                    if isinstance(assignment.func, ast.Attribute) and assignment.func.attr == "create":
                        args = ["create", *args]
                    if args and args[0] == "create":
                        options = dict(zip(args[1::2], args[2::2]))
                        creation_inputs[target.id] = {"source": location(assignment),
                                                      "returned_binding": target.id,
                                                      "arguments": copy.deepcopy(args),
                                                      "requested_fields": copy.deepcopy(options)}
                        entities[target.id] = {"binding": target.id, "id": f"${target.id}.id", "title": options.get("--title"),
                                                "owner": options.get("--owner", "system" if "B16" in achieved else "").strip(),
                                                "category": options.get("--category", "").strip(),
                                                "priority": options.get("--priority", "NORMAL"),
                                                "due_date": options.get("--due-date"),
                                                "status": "pending"}
                        bindings[target.id] = entities[target.id]
                    elif args and args[0] == "add-dependency" and "--id" in args and "--depends-on" in args:
                        identifier = args[args.index("--id") + 1]
                        dependency = args[args.index("--depends-on") + 1]
                        original = next((key for key, value in entities.items() if value["id"] == identifier), None)
                        if original:
                            entities[original].setdefault("dependencies", []).append(dependency)
                            entities[target.id] = entities[original]
                            bindings[target.id] = entities[original]
                    elif args and args[0] in ("complete", "archive") and "--id" in args:
                        identifier = args[args.index("--id") + 1]
                        original = next((key for key, value in entities.items()
                                         if value["id"] == identifier), None)
                        if original:
                            entities[original]["status" if args[0] == "complete" else "archived"] = (
                                "completed" if args[0] == "complete" else True)
                            entities[target.id] = entities[original]
                            bindings[target.id] = entities[original]
                    elif args and args[0] == "list":
                        bindings[target.id] = list(dict.fromkeys(
                            value["binding"] for value in entities.values()))
                elif isinstance(target, ast.Tuple) and isinstance(assignment, ast.Name) and assignment.id in bindings:
                    try:
                        bindings.update({item.id: value for item, value in zip(target.elts, bindings[assignment.id])})
                    except (AttributeError, TypeError):
                        pass
                elif isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
                    call = statement.value
                    if (isinstance(call.func, ast.Attribute) and call.func.attr == "call" or
                            isinstance(call.func, ast.Name) and call.func.id == "call"):
                        try:
                            args = [literal(arg, bindings) for arg in call.args[1:]]
                            if args and args[0] in ("complete", "archive") and "--id" in args and not call.keywords:
                                identifier = args[args.index("--id") + 1]
                                for entity in entities.values():
                                    if entity["id"] == identifier:
                                        entity["status" if args[0] == "complete" else "archived"] = (
                                            "completed" if args[0] == "complete" else True)
                        except (ValueError, KeyError, TypeError, IndexError):
                            pass
                elif target is not None:
                    try:
                        value = literal(assignment, bindings)
                        if isinstance(target, ast.Name):
                            bindings[target.id] = value
                    except (ValueError, KeyError, TypeError):
                        pass
                # Transitions also occur inside assertions (e.g. asserting the
                # status returned by complete). Apply them after recording that
                # assertion's observation, so the next call sees the new state.
                if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call):
                    for call in ast.walk(statement.value):
                        if not (isinstance(call, ast.Call) and isinstance(call.func, (ast.Name, ast.Attribute))
                                and (call.func.attr if isinstance(call.func, ast.Attribute) else call.func.id) == "call"):
                            continue
                        try:
                            args = [literal(arg, bindings) for arg in call.args[1:]]
                        except (ValueError, KeyError, TypeError, IndexError):
                            continue
                        if (len(args) >= 3 and args[0] in ("complete", "archive") and
                                "--id" in args and not call.keywords):
                            identifier = args[args.index("--id") + 1]
                            for entity in entities.values():
                                if entity["id"] == identifier:
                                    entity["status" if args[0] == "complete" else "archived"] = (
                                        "completed" if args[0] == "complete" else True)
                if (cli_calls(statement) or isinstance(statement, (ast.Assert, ast.Raise)) or
                        (assignment is not None and "read_bytes()" in ast.unparse(assignment)) or
                        "write_text(" in ast.unparse(statement) or
                        (isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Call) and
                         isinstance(statement.value.func, ast.Attribute) and
                         statement.value.func.attr.startswith("assert"))):
                    history.append({"source": location(statement), "expression": resolved(statement, bindings),
                                    "loop": copy.deepcopy(loop)})

    visit(tree.body)
    ids = [root["id"] for root in roots]
    w.require(len(ids) == len(set(ids)), f"duplicate parameterized root: {method_id}")
    observation_ids = [root["id"] for root in observations]
    w.require(len(observation_ids) == len(set(observation_ids)),
              f"duplicate direct observation root: {method_id}")
    assertion_ids = [root["id"] for root in direct_assertions]
    w.require(len(assertion_ids) == len(set(assertion_ids)),
              f"duplicate distinct-field root: {method_id}")
    return {"roots": roots, "observations": observations,
            "direct_assertions": direct_assertions, "unresolved": unresolved}
