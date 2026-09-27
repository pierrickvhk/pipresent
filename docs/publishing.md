# Publish the prepared repository

GitHub CLI (`gh`) was not installed in the build environment, so authentication could not be
checked and no public repository or remote CI result exists yet. No repository URL is claimed.

Install [GitHub CLI](https://cli.github.com/), then run these commands from this repository.
They create a **public** repository in the authenticated user's personal account. If a
`pipresent` repository already exists there, inspect it before choosing a different destination;
do not overwrite an existing repository.

```bash
gh auth login
gh auth status
export PIPRESENT_OWNER="$(gh api user --jq .login)"
python3 - <<'PY'
import os
from pathlib import Path
owner = os.environ["PIPRESENT_OWNER"]
p = Path("README.md")
text = p.read_text()
text = text.replace(
    "The repository is prepared locally but has not yet been published. After publication,\n"
    "replace `YOUR_GITHUB_OWNER` with the actual owner (see [publishing](docs/publishing.md)):\n",
    "Install on your Raspberry Pi desktop:\n",
)
text = text.replace("YOUR_GITHUB_OWNER", owner)
badge = (f"[![CI](https://github.com/{owner}/pipresent/actions/workflows/ci.yml/badge.svg)]"
         f"(https://github.com/{owner}/pipresent/actions/workflows/ci.yml)\n")
text = text.replace("# PiPresent\n", "# PiPresent\n\n" + badge, 1)
p.write_text(text)
PY
git add README.md
git commit -m "docs: set public repository URL and CI badge"
gh repo create pipresent --public --source=. --remote=origin --push \
  --description "Plug-and-play PowerPoint, PDF and video presentation player for Raspberry Pi displays."
gh repo edit "$PIPRESENT_OWNER/pipresent" \
  --add-topic raspberry-pi,python,automation,digital-signage,powerpoint,mpv,kiosk,linux
gh run list
```

The local branch is already `main`. After CI passes and the manual Raspberry Pi checklist
has been completed, record the device results in `docs/validation.md`, update release status
in README/changelog, commit and push those records, then create the release:

```bash
git tag -a v0.1.0 -m "PiPresent v0.1.0"
git push origin main --follow-tags
gh release create v0.1.0 --title "PiPresent v0.1.0" --generate-notes
```

Do not mark pending hardware checks as passed without running them.
