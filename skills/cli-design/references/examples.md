# Examples

One command rendered through each contract. Generic `tool`; adapt names, never copy as framework code.

## Parent help (bare `tool tasks`, exit 0, stdout)

```console
Manage tasks.

Commands:
  list    List tasks matching filters
  get     Show one task by ID or URL
  create  Create a task

Run `tool tasks <command> --help` for details.
```

## Human mode

```console
$ tool tasks list --limit 2
Inbox · 2 of 14 tasks
  Pay invoice     due 2026-11-05   id 8812
  Renew domain    due 2026-11-09   id 8815
```

stderr: `More: tool tasks list --limit 2 --cursor c2`

## Machine mode (stdout, exit 0)

```json
{"data":[{"id":"8812","title":"Pay invoice","due":"2026-11-05"},{"id":"8815","title":"Renew domain","due":"2026-11-09"}],"meta":{"returned":2,"has_more":true,"next_cursor":"c2"}}
```

## Machine error (stderr, stdout empty, exit 2)

```console
$ tool tasks list --status sideways --json
```

```json
{"error":{"code":"invalid_usage","message":"Invalid --status value \"sideways\"","allowed_values":["open","done"],"usage":"tool tasks list --status open","retryable":false}}
```

## Destructive write without confirmation (non-interactive)

```console
$ tool tasks delete 8812 --json
```

stderr: `{"error":{"code":"confirmation_required","message":"Deleting a task is irreversible","hints":["tool tasks delete 8812 --yes"],"retryable":false}}`, non-zero exit, no change.
