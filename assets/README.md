# Assets

Customer-supplied and customer-derived artwork. **Images here are not committed.**

The repository's engineering rules keep customer assets out of version control,
so `.gitignore` excludes everything in this directory except this README and
`components/manifest.json`. The manifest records component names, roles and
print sizes — metadata only, no image data.

## Regenerating the component library

```bash
python tools/extract_components.py path/to/TEMPLATE_FAT_250ML.psd \
    --outdir assets/components
```

This writes one trimmed PNG per component plus the manifest. 24 components are
expected from the supplied 250 ml master: 4 certification marks and 20 social
icons across three shape families.

## Trademarks

Several social icons are registered trademarks of their respective owners.
They are placed from the supplied files; they are never redrawn or
approximated. Confirm you hold the right to reproduce each mark before
sending artwork to production.

## Vector originals

The extracted components are raster, lifted from a PSD. If vector originals
exist, prefer them: drop them in alongside and update the manifest entry to
`"raster": false`. Raster components are resolution-bound and will soften if
scaled much above their source size.
