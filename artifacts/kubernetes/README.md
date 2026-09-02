# artifacts/kubernetes

UBI-240 slice 5: the canonical home for this provider's own docs/codegen
artifacts, moved here from `ubiquex-docs` so a description-authoring
change and the bindings regen it should accompany land in the same
commit, against the same schema.

- **`descriptions.json`** — field-level prose, keyed by dotted path
  (`resource.field.path` / `data_resource.field.path`). The real source
  of truth. Read by `ubx-docs-providers` at build time and by
  `export_raw_descriptions.py` below.
- **`intros.json`** / **`categories.json`** / **`exclusions.json`** —
  resource intros, nav category labels, and deliberate skip decisions.
  Read only by `ubx-docs-providers`.
- **`kubernetes.json`** — codegen-ready export: `descriptions.json`
  reshaped to `{resource: {relPath: text}}`, qualifier suffix stripped,
  HTML entities unescaped. This is what `ubx sdk gen --descriptions-dir
  artifacts/kubernetes` actually reads (`hash-watch.yml`'s own real
  invocation). Never edited directly.

To update `descriptions.json`: edit it here, then regenerate
`kubernetes.json` from a sibling `ubiquex-docs` checkout (the
authoring scripts stay there, pointed at this repo):

```bash
ubx sdk gen --only kubernetes --dump-ir /tmp/dump --out /tmp/unused
cd ~/Ubiquex/ubiquex-docs/scripts/resource-reference-gen
python3 export_raw_descriptions.py kubernetes Kubernetes \
    --dump-root /tmp/dump/kubernetes \
    --descriptions-path ~/Ubiquex/ubx-sdk-kubernetes/artifacts/kubernetes/descriptions.json \
    --nested-out ~/Ubiquex/ubx-sdk-kubernetes/artifacts/kubernetes/kubernetes.json
```

Commit both files together. See `ubiquex-internals`' own
[Docs Pipeline](https://github.com/Ubiquex/ubiquex-internals/blob/main/docs-pipeline.mdx)
page and UBI-102's own comment thread for the full account of why this
moved and what it fixes.
