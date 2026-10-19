#!/usr/bin/env bash
# The git identity this case's person would really have, and the thread replies the server delivered.
set -euo pipefail
git config --global user.name "Francis Lavoie"
cat > replies.json <<'JSON'
{
  "issue": "TAG-9131",
  "replies": [
    {
      "author": "stephane.levert",
      "body": "Spec approved, go ahead."
    }
  ]
}
JSON
