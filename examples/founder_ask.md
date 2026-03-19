Objective:
- Convert a founder request into a structured execution artifact that engineering and product can review asynchronously.

Scope:
- Compile markdown and plain text intent inputs.
- Preserve deterministic validation and lineage fields.
- Keep outputs inspectable by humans and machines.

Exclusions:
- No remote service dependencies for compile flow.
- No deployment orchestration in this request.

Constraints:
- Local-first operation only.
- Maintain stable CLI behavior for automation use.

Assumptions:
- Team uses version-controlled markdown briefs.
- Stakeholders need readable markdown derivatives.

Success Criteria:
- Artifact validates with pass or warn readiness status.
- Scope, constraints, and output contract are populated.

Output Contract:
- Canonical artifact JSON suitable for diff and lint.
