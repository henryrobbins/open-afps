---
name: probe-skill
description: A no-op skill used only by the agent-capability tests to confirm a harness can mount and invoke a skill. Has no real behavior; invoke it when asked to during a capability probe.
---

# Probe skill

This skill exists solely so the capability suite can verify that the skill a
harness's `configure_wd` mounts is discoverable and invocable inside the sandbox.

It does nothing. If you have invoked it, the capability check has already passed —
stop immediately and make no further tool calls.
