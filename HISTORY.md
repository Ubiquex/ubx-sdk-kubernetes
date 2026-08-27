# HISTORY.md — narrative archive

> Consulted only when a session needs to know why a decision was made, not on
> every open. For what's current, read `STATE.md` instead.

This file is new as of UBI-183 (2026-08-27). Real history predating it lives
in `ubiquex`'s own `HISTORY.md` (search `UBI-138`, `UBI-139`, `UBI-151`,
`UBI-185`) and in this repo's own real `git log`/merged-PR history, which is
authoritative for what actually shipped and when.

## Real, known decisions worth carrying forward

**UBI-138/UBI-139: this repo's own real shape.** Consolidated from a
12-repos-total layout into one combined repo per provider (this one included)
carrying all three languages, then the shared runtime code moved out again
into its own separate `ubx-sdk-go`/`ubx-sdk-typescript`/`ubx-sdk-python`
repos so it wasn't duplicated per provider.
