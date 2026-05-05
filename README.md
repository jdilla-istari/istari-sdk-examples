# Istari Python SDK examples

Three minimal, runnable examples of the [Istari Python SDK](https://pypi.org/project/istari-digital-client/):

1. **`01_nest_systems.py`** — put one system inside another (via a configuration). Uses `Client` (v2).
2. **`02_grant_access.py`** — give another user editor permissions on a system. Uses `Client` (v2).
3. **`03_relationships.py`** — link two resource revisions with a typed relationship. Uses `V3Client`.

Each script is self-contained: edit the constants at the top, run, watch.

### v2 vs v3, in one paragraph

The SDK ships two clients sharing the same `Configuration`. **`Client`** (v2) covers systems, configurations, jobs, agents, access control, and users — the bulk of what's exposed today. **`V3Client`** is the newer surface where models / artifacts / files are unified under a single **Resource** abstraction with first-class **revisions** and typed **revision relationships** (no v2 equivalent). You'll mix both in the same program; resource ids are shared.

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

### v2 — `Client`

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

### v3 — `V3Client`

| Task                                       | SDK call                                                            |
| ------------------------------------------ | ------------------------------------------------------------------- |
| List resources                             | `v3.list_resources(cursor=, size=, type_name=["model"], …)`         |
| Get a resource                             | `v3.get_resource(resource_id)`                                      |
| List revisions of a resource               | `v3.list_resource_revisions(resource_id, cursor=, size=)`           |
| List available relationship types          | `v3.list_revision_relationship_types()`                             |
| Create a relationship between two revisions | `v3.create_revision_relationship(NewRevisionRelationshipDto(...))` |
| List relationships touching a revision     | `v3.list_revision_relationships(revision_id, …)`                    |

### Enums you'll touch

- `AccessRelation`: `viewer`, `editor`, `administrator`, `executor`, `owner`
- `AccessResourceType` (v2 sharing): `system`, `model`, `artifact`, `job`, `document`, `file`, `filerevision`, `tool`, `function`, `tenant`, …
- `AccessSubjectType`: `user`
- `ResourceTypeDto` (v3): `model`, `artifact`, `file`

### Mental models

**Nesting (v2):** there is no "attach subsystem" call. A parent system has many *configurations*; each configuration is a named snapshot of which child systems it tracks (with optional version tags). Nest B inside A by creating a configuration on A whose `tracked_systems` includes B's id.

**Relationships (v3):** they connect *revisions*, not resources, so links are precise to a version pair. Each link has a server-configured **type** carrying directionality (e.g. `produces` ↔ `derived_from`). Read as "left {type} right". The SDK has no delete method today — relationships persist once created.

## Reference

- Docs PR with v3 reference: <https://github.com/Istari-digital/istari-documentation/pull/568>
- PyPI: <https://pypi.org/project/istari-digital-client/>
