# Tasker XML static validation — 2026-10-07

Checked 36 XML files and 3399 task actions. Found 0 failures.

Action numbers were compared with [Tasker’s official definitions](https://tasker.joaoapps.com/code/ActionCodes.java). Checks include XML parsing, task IDs, action numbering, nested control flow, explicit condition fields, selected built-in argument layouts, plugin bundle presence, and JSON syntax.

This is not full schema certification. Tasker has not parsed or executed these files here. The selected argument layouts are repository-derived checks, not an official XSD. Plugin settings, Android components, scene/profile layouts, unresolved external task references, and all remaining action arguments need runtime or authoritative format verification.
