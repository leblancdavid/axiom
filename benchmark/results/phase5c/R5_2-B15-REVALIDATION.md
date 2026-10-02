# R5.2 state-relative composer: B15 revalidation boundary

Prospective amendment `PROTOCOL_AMENDMENT_R5_2_STATE_RELATIVE.md` SHA-256
`ecdf7b72e79a0756c628a998e6ed7654b02c26e4de20191317edc64ca237d828`.
New composer SHA-256 `eb5172eab4287cad80a67e47820e8039a0ac678252a36ed40adf735c4f048f97`;
fixture SHA-256 `b76550ccfbb209ca4b734341286a1a99ffdd8ce0e7c1b4bb5add10d08224f124`.
No R5.1 historical files or implementation files were edited. Both original
R5.1 B15 checkpoint and snapshot hashes matched the pinned inventory.

Independent restores through `workspace_phase5e.py restore` into distinct
disposable locations under the approved temporary directory each passed full
checkpoint validation and snapshot/file-inventory checks: Conventional two
files; Lykoi 27 files. The unchanged pinned R5.1 external runner, executed
read-only with `phase5d.py run`, reported Conventional 30 passed + four
existing B11 supersessions (34 methods), and Lykoi seven passed + two existing
B02 skips (nine methods). Read-only internal validation reported Conventional
39/39 and Lykoi 33/33. Observer verified both workspaces unchanged across
each run. Complete repository harness discovery after the amendment freeze
passed 25/25, including five R5.2 fixture methods and the original 20/20.

The fixture inventory verifies presence/refinement; absence/introduction;
preservation of unrelated properties; identity-independent composition;
identical targets for identical prior states despite label changes; distinct
structural realizations of the same owner/default semantics; no promotion of a
hypothetical target to an achieved capability or implementation; fail-closed
prior mismatch; and unchanged B11 and R5/R5.1 acceptance selection. Both
authoritative B15 expectation SHA-256 values remained exactly the R5.1 values:
Conventional `27f67747e9a5b059fb5c3e4f0ecf4686c4e61782517f509ef1a359c77e7b61d8`,
Lykoi `9c7a4ad3103c62d13de808d01ec3af847c296b0f7f0ccbeb78ca6c4d25f46c13`.

This validates the prospective composer revision at B15 and synthetic B16
composition only. It does not freeze a B16 acceptance case, supply a B16
checkpoint/runner integration, expose B16, or classify either track. B16–B20
remain unprocessed; `PHASE_5C_COMPLETE` is not applicable.
