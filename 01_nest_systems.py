"""
Demo 1 — Nest one Istari system inside another.

The Istari API has no standalone "attach subsystem" call. You nest a
system by creating a *configuration* on the parent whose
`tracked_systems` list points at the child. A configuration is a
named, versioned snapshot of "which child systems live inside me, at
which versions" — every parent system can have many configurations.

What this script will do to your account:
  - read two systems (parent + child) by id
  - create one new configuration on the parent named "SDK demo nest …"
  - list the subsystems of that configuration to confirm
  - print the SDK call that undoes it

Run:
    pip install -r requirements.txt
    python 01_nest_systems.py
"""

import time

import istari_digital_client as idc

# ── Fill these in ─────────────────────────────────────────────────
# PAT: https://dev.istari.app/settings?tab=developer-settings
# Don't commit this file with your PAT in it.
PAT = "<your personal access token>"
REGISTRY_URL = "https://fileservice-v2.dev.istari.app"

# Two systems on your account. The first becomes the parent;
# the second gets nested inside it.
PARENT_SYSTEM_ID = "<parent system uuid>"
CHILD_SYSTEM_ID = "<child system uuid>"
# ──────────────────────────────────────────────────────────────────


def main() -> None:
    client = idc.Client(idc.Configuration(
        registry_url=REGISTRY_URL,
        registry_auth_token=PAT,
    ))

    parent = client.get_system(PARENT_SYSTEM_ID)
    child = client.get_system(CHILD_SYSTEM_ID)
    print(f"Parent: {parent.id}  {parent.name!r}")
    print(f"Child:  {child.id}  {child.name!r}\n")

    # The nesting happens here: a new configuration on the parent
    # whose tracked_systems list references the child.
    #
    # NewTrackedSystem accepts an optional `tag_id=` to pin the
    # child to a specific tag. Omitting it pins to the latest tag.
    config_name = f"SDK demo nest — {time.strftime('%Y-%m-%d %H:%M:%S')}"
    config = client.create_configuration(
        parent.id,
        idc.NewSystemConfiguration(
            name=config_name,
            tracked_systems=[
                idc.NewTrackedSystem(system_id=child.id),
            ],
        ),
    )
    print(f"Created configuration: {config.id}\n  name: {config.name!r}\n")

    print("Subsystems on the new configuration:")
    page = client.list_configuration_subsystems(config.id, page=1, size=10)
    for sub in page.items:
        print(f"  - {sub.name!r}  (system_id={sub.id})")

    print(
        "\nClean up (archives the configuration, doesn't touch the systems):\n"
        f"    client.archive_configuration({config.id!r})"
    )


if __name__ == "__main__":
    main()
