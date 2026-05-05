# Istari Python SDK examples

Two minimal, runnable examples of the [Istari Python SDK](https://pypi.org/project/istari-digital-client/):

1. **`01_nest_systems.py`** — put one system inside another (via a configuration).
2. **`02_grant_access.py`** — give another user editor permissions on a system.

Each script is self-contained: edit the constants at the top, run, watch.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

For each script:

1. Open the file.
2. Fill in the `── Fill these in ──` block at the top:
   - `PAT` — generate one at <https://dev.istari.app/settings?tab=developer-settings>
   - `REGISTRY_URL` — `https://fileservice-v2.dev.istari.app` for dev (already set)
   - The system / user IDs the demo references
3. `python 01_nest_systems.py` (or `02_grant_access.py`)
4. The script prints a `Clean up:` line at the end with the exact SDK call to undo what it did.

> **Don't commit your PAT.** The PAT lives in the file only because that's the
> shortest path to a working demo. Move it to an env var (`registry_auth_token=os.environ["ISTARI_REGISTRY_AUTH_TOKEN"]`) before checking anything in.

## SDK quick reference

| Task                                  | SDK call                                                                       |
| ------------------------------------- | ------------------------------------------------------------------------------ |
| List systems on the account           | `client.list_systems(page=1, size=10)`                                         |
| Look up a system by id                | `client.get_system(system_id)`                                                 |
| Create a configuration on a system    | `client.create_configuration(system_id, NewSystemConfiguration(...))`          |
| List subsystems of a configuration    | `client.list_configuration_subsystems(configuration_id)`                       |
| Archive (undo) a configuration        | `client.archive_configuration(configuration_id)`                               |
| Grant access on a resource            | `client.create_access(AccessRelationship(...))`                                |
| List access on a resource             | `client.list_access(resource_type, resource_id)`                               |
| Revoke access                         | `client.remove_access(subject_type, subject_id, resource_type, resource_id)`   |
| Look up the calling user              | `client.get_current_user()`                                                    |
| List all users on the tenant          | `client.list_users()`                                                          |

### Enums you'll touch

- `AccessRelation`: `viewer`, `editor`, `administrator`, `executor`, `owner`
- `AccessResourceType`: `system`, `model`, `artifact`, `job`, `document`, `file`, `filerevision`, `tool`, `function`, `tenant`, …
- `AccessSubjectType`: `user`

### Mental model for nesting

There is no "attach subsystem" call. A parent system has many **configurations**; each configuration is a named snapshot of which child systems it tracks (with optional version tags). To nest B inside A, you create a configuration on A whose `tracked_systems` includes B's id.
