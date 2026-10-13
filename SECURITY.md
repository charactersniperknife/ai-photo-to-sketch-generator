# Security Policy

## Supported versions

| Version | Supported          |
|---------|--------------------|
| 0.4.x   | :white_check_mark: |
| 0.3.x   | :white_check_mark: |
| < 0.3   | :x:                |

## Scope

This project is a **local, offline desktop tool**. It does not phone home, it
does not upload your photos anywhere, and it does not require an account. If
you find code that does any of those things, that is a security bug and we
want to hear about it immediately.

In scope:

- Arbitrary code execution via a maliciously crafted image file (Pillow /
  OpenCV parsing paths).
- Path traversal in the batch-conversion CLI when a user passes a directory
  with symlinks.
- Deserialization of a tampered checkpoint file (`.pt` / `.onnx`) leading to
  code execution — we load with `weights_only=True` and document the
  boundary, but report anything you find.
- Dependency confusion through the `sketchforge-models` optional extra.

Out of scope:

- Denial of service from feeding a 500-megapixel TIFF into the pipeline. That
  is expected; use `--max-dimension`.
- Anything requiring an attacker who already has local write access to your
  config directory.

## Reporting a vulnerability

Email `security@sketchforge.dev` with a description, a minimal reproducer,
and the affected version. We aim to acknowledge within 72 hours and to ship a
patch within 14 days for confirmed issues. Please do not open a public issue
for an unpatched vulnerability.

## Hardening notes for users

- Run the CLI with `--max-dimension 4096` when processing untrusted images.
- Keep Pillow and OpenCV updated — most image-parsing CVEs land there.
- Only load checkpoint files from the official release page or a source you
  trust.