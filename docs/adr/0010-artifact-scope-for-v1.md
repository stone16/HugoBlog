---
status: accepted
---
# Artifact scope for v1: HTML and PDF, with expiry and view tracking

An Artifact may be a self-contained HTML page or a PDF. Each carries an optional
expiry and records views, so a link that was sent can be known to have been
opened and a page that has outlived its purpose can be retired rather than
silently accumulating.

## Consequences

- PDF forces a viewer decision HTML does not: inline render versus attachment
  download. Default to inline so a shared link opens rather than downloads.
- View tracking on a `password`/`invited` Artifact is a record of who looked at
  private material; it is telemetry about other people and should record no more
  than timestamp and coarse client information.
- Expiry is optional, never automatic. An Artifact that has expired returns 410
  Gone rather than 404, so the recipient learns the link was real and is over.
- **`invited` visibility is deferred.** The `visibility` column still admits the
  value so no migration is needed later, but v1 implements only `public` and
  `password`. See [ADR-0005](0005-artifact-address-is-decoupled-from-artifact-access.md).
