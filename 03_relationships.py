"""
Demo 3 — Create a typed relationship between two resource revisions (v3).

In v2, models / artifacts / files are separate types. v3 unifies them
under a single Resource, and adds *relationships* — directed, typed
links between specific revisions of two resources. Typical use:
"this artifact revision was *produced by* that model revision."

Two things to know before you run:

  1. Relationships connect REVISIONS, not resources. Each resource
     has many revisions; the link is precise to a version pair.

  2. Relationship types are dynamic and configured server-side.
     You can't invent a type name on the fly — fetch the available
     ones via `list_revision_relationship_types()`. As of writing,
     dev has one: `produces` (inverse `derived_from`).

  3. There is no `delete_revision_relationship` in the SDK today.
     Once created, a relationship persists. Pick demo resources you
     don't mind keeping linked.

What this script will do to your account:
  - resolve a relationship type (first available, or the one you set)
  - look up the latest revision of each of two resources
  - create one relationship: left --(type)--> right
  - list relationships on the left revision to confirm

Run:
    pip install -r requirements.txt
    python 03_relationships.py
"""

import istari_digital_client as idc
from istari_digital_client.v3.models.new_revision_relationship_dto import (
    NewRevisionRelationshipDto,
)

# ── Fill these in ─────────────────────────────────────────────────
# PAT: https://dev.istari.app/settings?tab=developer-settings
# Don't commit this file with your PAT in it.
PAT = "<your personal access token>"
REGISTRY_URL = "https://fileservice-v2.dev.istari.app"

# Two resources (model / artifact / file) on your account.
# The script uses the latest revision of each.
RESOURCE_ID_LEFT = "<resource uuid — the 'producer' side>"
RESOURCE_ID_RIGHT = "<resource uuid — the 'derived' side>"

# Leave as None to use the first available relationship type.
# Or paste a specific type id from `list_revision_relationship_types()`.
RELATIONSHIP_TYPE_ID: str | None = None
# ──────────────────────────────────────────────────────────────────


def latest_revision_id(v3: idc.V3Client, resource_id: str) -> str:
    page = v3.list_resource_revisions(resource_id, size=1)
    if not page.items:
        raise SystemExit(f"Resource {resource_id} has no revisions.")
    return page.items[0].file_revision_id


def resolve_relationship_type(v3: idc.V3Client) -> tuple[str, str, str]:
    if RELATIONSHIP_TYPE_ID:
        for t in v3.list_revision_relationship_types(size=100).items:
            if t.id == RELATIONSHIP_TYPE_ID:
                return t.id, t.name, t.name_inverse
        raise SystemExit(f"Relationship type {RELATIONSHIP_TYPE_ID!r} not found.")

    page = v3.list_revision_relationship_types(size=1)
    if not page.items:
        raise SystemExit("No relationship types configured on this server.")
    t = page.items[0]
    return t.id, t.name, t.name_inverse


def main() -> None:
    cfg = idc.Configuration(registry_url=REGISTRY_URL, registry_auth_token=PAT)
    v3 = idc.V3Client(cfg)

    type_id, type_name, type_inverse = resolve_relationship_type(v3)
    print(f"Relationship type: {type_name!r} (inverse {type_inverse!r})")
    print(f"  id: {type_id}\n")

    left_rev = latest_revision_id(v3, RESOURCE_ID_LEFT)
    right_rev = latest_revision_id(v3, RESOURCE_ID_RIGHT)
    print(f"Left  revision: {left_rev}  (resource {RESOURCE_ID_LEFT})")
    print(f"Right revision: {right_rev}  (resource {RESOURCE_ID_RIGHT})\n")

    # The mutation. Reads as: "left {type_name} right",
    # equivalently "right {type_inverse} left".
    rel = v3.create_revision_relationship(
        new_revision_relationship_dto=NewRevisionRelationshipDto(
            left_revision_id=left_rev,
            right_revision_id=right_rev,
            relationship_type_id=type_id,
        ),
    )
    print(f"Created relationship: {rel.id}")
    print(f"  {rel.left_revision.file_revision_id} "
          f"--({rel.relationship_type_name})--> "
          f"{rel.right_revision.file_revision_id}\n")

    print(f"All relationships on the left revision:")
    page = v3.list_revision_relationships(left_rev, size=20, include_total=True)
    for r in page.items:
        direction = (
            f"--({r.relationship_type_name})-->"
            if r.left_revision.file_revision_id == left_rev
            else f"<--({r.relationship_type_name_inverse})--"
        )
        other = (
            r.right_revision.file_revision_id
            if r.left_revision.file_revision_id == left_rev
            else r.left_revision.file_revision_id
        )
        print(f"  - {direction} {other}")
    print(f"\n(total: {page.total})")

    print(
        "\nNote: the v3 SDK has no `delete_revision_relationship` today. "
        "Once created, the link persists."
    )


if __name__ == "__main__":
    main()
