# JSON contract and examples
A batch is `{ "jobs": [...], "profile": {...} }`; profile optional. Save batch outside installation.
Job required: company, title, location, url (actually observed), relevance, relevance_reason. Optional requisition_id, merge_into, published_at (ISO sourced date), published_evidence, requirements, observations, fit, fit_reason.
Requirements: key, category, kind(skill/education/experience), criticality(Mandatory/Preferred/Contextual), evidence (short JD fact), url, decision_impact(boolean), assessment(Met/Unknown/Not Met), candidate_evidence, hard_exclusion(boolean). Only explicit official education or documented mandatory capability failures justify hard_exclusion. Unknown cannot exclude. In Discovery assessments are ignored.
Observation: url, kind(official/third_party), outcome(open/closed/unknown), checked_at(ISO datetime with timezone), evidence, method. evidence is a concise observed fact, not copied full JD. unknown evidence describes limitation. An actual observation may be old; helper freshness defaults to 7 days.
Profile: matching_ready boolean, experience list of `{summary,evidence}`, skills mapping canonical key to `{state,level,evidence}`, broad_discovery boolean. Matching needs matching_ready plus referenced experience. Skills with state Met/Not Met require evidence.
CLI examples:
```
python3 jobmatch.py --state private/state.json init
python3 jobmatch.py --state private/state.json ingest batch.json
python3 jobmatch.py --state private/state.json recommend --sort relevance --limit 10
python3 jobmatch.py --state private/state.json clarify
python3 jobmatch.py --state private/state.json question SQL --result skipped
python3 jobmatch.py --state private/state.json status J001 rejected
python3 jobmatch.py --state private/state.json source company-x https://example.com/careers --kind official --enabled true
python3 jobmatch.py --state private/state.json export-data export.json
node export.mjs export.json jobs.xlsx
python3 jobmatch.py --state private/state.json import-tracker jobs.xlsx
python3 jobmatch.py --state private/state.json resolve CONFLICT_ID --choice incoming
```
`extract resume.pdf text.txt` extracts text only; Agent builds and confirms semantic profile. Never infer proficiency automatically from extraction. Import JSON is a list of `{id,url,application_status}`; XLSX reads Application Tracker with either those legacy headers or Chinese 编号/职位链接/公司/岗位/投递状态 headers; Chinese status values are normalized back to stable machine values. State schema version 1; unknown versions fail with no write. Local status history and pending imports are preserved.

## Required intake and coverage (0.1.1)
Profile additionally requires target (nonblank role/direction), locations (nonempty list, may explicitly contain “全国/不限”), experience_years (number >=0), education (highest credential, nonblank). `intake` returns ready=false and missing_required until complete. This gate is evaluated by the invoking Agent before calling external search tools; helper cannot intercept arbitrary host browsing.
`search-log record.json` appends `{source_id,kind,query,checked_at,outcome,notes}`. kind is official/third_party; outcome searched/blocked/unavailable. Store actual attempted methods and stopping observations in notes. `coverage` returns recorded sources/channels, unique job counts, Top10 count, verification counts and warnings. It does not certify exhaustive coverage. Use a separate state per distinct search session so prior logs do not masquerade as current coverage.

0.1.2: CLI recommend/clarify/export-data refuse incomplete required intake. This is a downstream safeguard, not interception of host browsing. Export defaults to Chinese headers/status display; four sheet names remain stable; English display can be requested with fourth positional argument en. broad_discovery=true requires explicit user exploration intent, not Discovery mode alone.

Job jd_completeness is full/partial/unavailable; omit means partial. Strong overall fit requires full, with all material qualifications analyzed and cited by Agent. This helper validates the declaration but cannot independently prove the actual page was fully read. Skills with absent evidence use level unknown.

0.1.2 workbook: All Jobs uses a compact job table plus a complete RequirementEvidenceTable below it, linked by stable job ID. Recommended is a compact Top10 snapshot. Same observation replay is idempotent, not a new check. jd_limitations stores missing source information; legacy jd_limitation is normalized.

0.1.4: recommend defaults to eligible jobs with at least one source observation containing a URL and evidence, including third-party jobs without official confirmation. Preserve Unverified/Conflict status; no-observation records require an explicit exploratory view. This supersedes 0.1.3 official-only recommendations. Unknown candidate skills do not exclude jobs. `search_policy` stores local `{priority_groups: string[], allow_expansion: boolean}`; `search-policy file.json` saves it and `search-plan` reads enabled sources after local overrides. Planning does not append search evidence or change match ranking. Main workbook uses concrete unknown_items, a single context mode explanation and human-readable status; Verification Log retains provenance. Tracker accepts 岗位链接 and legacy 职位链接.
