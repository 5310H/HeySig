# Tasker XML static validation — 2026-10-10

Checked 82 XML files and 5371 task actions. Found 0 failures.

Action numbers were compared with [Tasker’s official definitions](https://tasker.joaoapps.com/code/ActionCodes.java). Checks include XML parsing, task IDs, action numbering, nested control flow, explicit condition fields, selected built-in argument layouts, plugin bundle presence, and JSON syntax.

This is not full schema certification. Static checks do not establish Android runtime behavior; selected live checks are recorded in [phone verification notes](HeySig3-verified-usb-drags.md). The selected argument layouts are repository-derived checks, not an official XSD. Plugin settings, Android components, scene/profile layouts, unresolved external task references, and all remaining action arguments need runtime or authoritative format verification.
