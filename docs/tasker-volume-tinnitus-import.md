# Volume and Tinnitus import audit — 2026-10-07

The reported Tasker 6.6.20 import stops after Launch App (action 3).
This checkout has 63 SIG_VolumeCurrent actions (act0–act62), rather than
67. No actions were removed by this repair. Action 4 is the first
generated error-check If.

The audit compared all twelve Volume/Tinnitus exports with the working
Balance counterparts and with the original Tasker exports in commit
9622f23. Generated If actions lacked the original export's `coll` child,
and generated actions used inconsistent attribute order. Continue After
Error (`se`) appeared after arguments rather than before them as in the
original exports. The repair restores explicit `coll` metadata, places
`se` immediately after `code`, and consistently writes `sr` before `ve`.
It retains explicit empty RHS fields for unary conditions, matching the
current working Balance tasks. Original exports also demonstrate that
unary conditions can omit RHS, so the general validator allows that form.

These changes normalize the serialization at the reported truncation
boundary; they do not establish which difference triggers Tasker's parser.
Current Balance tasks import despite some of the same metadata differences.
Attribute order has no semantic meaning in standard XML. The exact
67-action phone artifact and Android importer are unavailable here, so
successful import must still be confirmed on the phone.

Current, Up, Down, and Set needed normalization in both families. Max and
Mute are two-action wrappers and already passed the structural audit.
Matching project and historical backup copies were normalized too. Action
codes, argument values, conditions, nesting, and counts were preserved.

`python3 tests/check_tasker_import_structure.py` compares complete argument
and condition shapes with the working Balance equivalents, checks canonical
metadata placement, physical contiguous action numbering, nested If / Else /
End If and For / End For structure, expected counts, and project parity.
It also rejects a deliberately removed condition RHS in these normalized
standalone exports. The general validator accepts both repository-observed
unary condition layouts. Behavior simulations cover slider transitions,
readback, bounds, and plugin failure paths independently.

On Tasker 6.6.20, import the repaired SIG_VolumeCurrent and confirm all
63 actions appear, including action 4 and the final success assignment.
Expected counts in each family: Current 63, Up/Down/Set 87, Max/Mute 2.
Confirm project import and execution as well. If truncation persists, the
exact phone file and a Tasker export of the partially loaded task are needed
to diagnose the remaining parser difference.
