# Reference exploration — technical scaffold only

Authorized by the user's **« go »** on 2026-10-05 in session
`ses_ef27d5cdcffefU62W3ufHMHm2L`, responding to the request for technical
adaptation. **Not paid-generation consent.** No completed production stage,
scene, shot, media output or approval is implied.

This is a new project-owned API graph. Its newly declared node IDs are `10`
(LoadImage), `20` (OpenRouterStudioImage), and `30` (SaveImage). They are not
guesses about a supplied user graph. Existing JSON/PNG files remain unchanged.
The adapter must preserve these nodes and links and update configured literals
only. A single ordered portrait reference is wired to the first live slot.

Live descriptors were read with comfy-mcp `nodes(get)` on 2026-10-05. Files
named `*.live.json` are descriptor evidence, not a generation test. The input
filename was staged only after the separate user answer **« Oui, copier et
valider »**. The original PNG remains unchanged. Never substitute another
server input merely because its name looks similar. The fresh LoadImage
descriptor confirms the staged name. The exact batch's prepared graph has
passed live validation; evidence is in the batch's `validation-results.json`.
This is a validation result, not generation testing or paid-job approval.

## Selected model options

| Option | Recommendation | Cost/availability |
| --- | --- | --- |
| Model | Seedream `bytedance-seed/seedream-5-0-flash` only | Live branch exists; cloud output paid |
| Resolution / ratio | 1K / 16:9 | Preparation defaults; no upgrade |
| `n` | 1 | One output image, not four generation calls |
| Reference slots | One approved adult portrait in slot 1 | 14 live slots available; source order preserved |
| `size` | Empty | Avoid overriding resolution/ratio |
| Seed | Keep scaffold's provider default `-1` | No explicit seed capability enabled in central config |
| Provider options JSON | `only: [seed]`, `allow_fallbacks: false` | No model/provider fallback; verify current route price separately |
| Negative prompt | Exclusions in normal prompt | No native negative input in this live model branch |
| Guidance / enhance / conditioning slider | Not used | Not present in this live model branch |
| Strict validation / raw artifact audit | Live defaults: enabled | No extra model call; maintain validation and provider evidence |
| Reference max megapixels | Live default 16 | Approved 1024×1536 portrait is below the limit; no intended resize |
| Request timeout / rerun nonce | Live defaults: 600 s / 0 | No automatic retry or additional job authorized |
| ColorTransfer | Available core node, **not enabled** | Local postprocess; unnecessary for neutral reference lighting |
| Upscale / alternate image editor | Not enabled | Outside this one-image scope; no installation or model substitution |

Public route pricing was checked on 2026-10-05: the Seed endpoint publishes
USD 0.018 per output and USD 0 for the one portrait input. Evidence is in
`references/technical-pricing.json` and `references/technical-pricing.md`.
This is not an actual invoice or sufficient authorization: reconcile ledger
opening liabilities and validate exact prompt/plan/workflow hashes, budget and
specific consent. No available balance is inferred from the USD 30 ceiling.
