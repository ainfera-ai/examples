# AGENTS.md — operating contract for ainfera-letta

Audience: the Ainfera fleet (Aulë and peers) and any agent operating this repo. Read before touching code.

## Identity
- **Adapter** — Letta (MemGPT) + **Ainfera Routing**. One of the public framework adapters (siblings: `ainfera-langchain`, `ainfera-langgraph`, `ainfera-crewai`, …). A *customer-integration* surface, not core infra.
- Inference is routed through Ainfera; every turn carries a signed, hash-chained audit receipt.
- Source of truth for names: the Naming law (`hizrianraz/obsidian/_ontology/Naming.md`, v1.3).

## Naming (law v1.3) — use these exactly
- Wire model string: **`ainfera-inference`** (canonical). `ainfera-mithril` / `ainfera-auto` are **silent legacy aliases** — accept them, prefer the canonical string in new code/docs.
- API base `https://api.ainfera.ai/v1` · signup/keys `https://app.ainfera.ai/signup` · agent roster `https://ainfera.ai/agents`.
- This repo is **not** "Ainfera OS" (a future product) and **not** Valinor (the internal fleet substrate). It is a public adapter.

## §0 Premise verification (mandatory)
Open every change with an explicit PASS/FAIL probe of current state (clean tree? correct remote? `AINFERA_API_KEY` present?) **before** editing. A failed premise → halt and surface; never fix-forward.

## Definition of done — curl proof, not PR proof
```bash
./curl-example.sh        # signup → routed inference → audit verify (no Letta server needed)
# or the same transport Letta uses:
export AINFERA_API_KEY=ainfera_...   # https://app.ainfera.ai/signup
pip install -r requirements.txt && python main.py
```
Done = the example returns a routed completion **and** an audit receipt the `verify` tool accepts. PR opened ≠ shipped.

## Secrets — hard rules
- `AINFERA_API_KEY` (`ainfera_*`) comes from the environment only. Never commit it; never echo its value. `.env` is gitignored.
- No service-role / provider keys belong in an adapter repo.

## License
Apache-2.0 (code & adapters). © Ainfera Inc. 2026.
