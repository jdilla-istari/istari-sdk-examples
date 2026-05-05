"""
Demo 2 — Grant a user editor permissions on a system.

`create_access` is the one call for sharing anything. Swap
`resource_type` to share a model, artifact, job, document, etc.
instead — the call shape is identical.

What this script will do to your account:
  - look up a user by email (or use a hard-coded user id)
  - grant them the `editor` role on a given system
  - list the system's current access list to confirm
  - print the SDK call that undoes it

Run:
    pip install -r requirements.txt
    python 02_grant_access.py
"""

import istari_digital_client as idc

# ── Fill these in ─────────────────────────────────────────────────
# PAT: https://dev.istari.app/settings?tab=developer-settings
# Don't commit this file with your PAT in it.
PAT = "<your personal access token>"
REGISTRY_URL = "https://fileservice-v2.dev.istari.app"

SYSTEM_ID = "<system uuid>"

# Either set USER_EMAIL (script will look up the id) OR USER_ID directly.
USER_EMAIL: str | None = "<colleague@yourcompany.com>"
USER_ID: str | None = None
# ──────────────────────────────────────────────────────────────────


def resolve_user_id(client: idc.Client) -> str:
    if USER_ID:
        return USER_ID
    if not USER_EMAIL:
        raise SystemExit("Set USER_EMAIL or USER_ID at the top of the file.")
    for u in client.list_users():
        if getattr(u, "email", None) == USER_EMAIL:
            return u.id
    raise SystemExit(f"No user found with email {USER_EMAIL!r}")


def main() -> None:
    client = idc.Client(idc.Configuration(
        registry_url=REGISTRY_URL,
        registry_auth_token=PAT,
    ))

    user_id = resolve_user_id(client)
    system = client.get_system(SYSTEM_ID)
    print(f"System: {system.id}  {system.name!r}")
    print(f"User:   {user_id}\n")

    # The whole sharing API is this one call.
    #
    # AccessRelation values:
    #   VIEWER, EDITOR, ADMINISTRATOR, EXECUTOR, OWNER
    # AccessResourceType values:
    #   SYSTEM, MODEL, ARTIFACT, JOB, FILE, DOCUMENT, TENANT, …
    client.create_access(idc.AccessRelationship(
        subject_type=idc.AccessSubjectType.USER,
        subject_id=user_id,
        relation=idc.AccessRelation.EDITOR,
        resource_type=idc.AccessResourceType.SYSTEM,
        resource_id=system.id,
    ))
    print("Granted editor.\n")

    print("Current access on the system:")
    for rel in client.list_access(idc.AccessResourceType.SYSTEM, system.id):
        info = getattr(rel, "subject_info", None)
        email = getattr(info, "email", "?") if info else "?"
        print(f"  - {rel.relation.value:14} {email}  ({rel.subject_id})")

    print(
        "\nClean up (revokes the grant):\n"
        f"    client.remove_access(\n"
        f"        idc.AccessSubjectType.USER, {user_id!r},\n"
        f"        idc.AccessResourceType.SYSTEM, {system.id!r},\n"
        f"    )"
    )


if __name__ == "__main__":
    main()
