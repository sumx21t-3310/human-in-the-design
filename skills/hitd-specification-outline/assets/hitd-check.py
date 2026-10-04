# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""Check human-in-the-design artifacts.

Usage:
  uv run hitd-check.py state <feature-dir>
  uv run hitd-check.py artifact <artifact-file>
  uv run hitd-check.py gate <feature-dir> <phase> [--root <project-root>]
  uv run hitd-check.py snapshot <contract-snapshot.md> [--root <project-root>]

Prints "OK" and exits 0 when every check passes.
Prints one "NG: ..." line per finding and exits 1 otherwise.
"""

import datetime
import re
import sys
from pathlib import Path

import yaml

PHASES = ["outline", "specification", "design", "implementation", "verification"]
STATUSES = {"pending", "in_progress", "completed", "skipped"}
ARTIFACT_FILES = {
    "outline": "outline.md",
    "specification": "specification.md",
    "design": "design.md",
    "verification": "verification.md",
}
COMMON_HEADINGS = ["Decisions", "Authority Delegation"]
REQUIRED_HEADINGS = {
    "outline": [
        "Goal", "Background", "Scope", "Non-goals", "Primary Use Cases",
        "Major Constraints", "Expected Outcome", "Unresolved Questions",
    ],
    "specification": [
        "Functional Requirements", "Behavioral Rules", "Acceptance Criteria",
        "Edge Cases", "Error Behavior", "State Transitions",
        "Compatibility Requirements", "Constraints",
    ],
    "design": [
        "Responsibilities", "Design Stub", "Dependency Direction", "State Ownership",
    ],
    "verification": ["Verification Results", "Contract Drift", "Deviations"],
}
HEADING = re.compile(r"^##\s+(.+?)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


def read_frontmatter(path):
    """Return (data, body_lines, findings)."""
    if not path.is_file():
        return None, [], [f"{path} が見つからない"]
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return None, lines, [f"{path}: frontmatter が見つからない"]
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            try:
                data = yaml.safe_load("\n".join(lines[1:i]))
            except yaml.YAMLError as e:
                return None, lines, [f"{path}: frontmatter を YAML として読み込めない: {str(e).splitlines()[0]}"]
            if not isinstance(data, dict):
                return None, lines, [f"{path}: frontmatter がキーと値の組になっていない"]
            return data, lines[i + 1:], []
    return None, lines, [f"{path}: frontmatter が閉じていない"]


def sections(body):
    """Map each `## heading` to its text, skipping fenced code blocks for heading detection."""
    result = {}
    current = None
    in_fence = False
    for line in body:
        if FENCE.match(line):
            in_fence = not in_fence
        match = None if in_fence else HEADING.match(line)
        if match:
            current = match.group(1)
            result[current] = []
        elif current is not None:
            result[current].append(line)
    return {name: "\n".join(text).strip() for name, text in result.items()}


def check_state(feature_dir):
    path = feature_dir / "state.md"
    data, _, findings = read_frontmatter(path)
    if findings:
        return findings, None
    if not data.get("feature"):
        findings.append(f"{path}: feature が空")
    current = data.get("current_phase")
    if current not in PHASES + ["done"]:
        findings.append(f"{path}: current_phase `{current}` が {PHASES + ['done']} のどれでもない")
    phases = data.get("phases")
    if not isinstance(phases, dict) or list(phases.keys()) != PHASES:
        findings.append(f"{path}: phases のキーが {PHASES} の順に並んでいない")
        return findings, None
    for name, status in phases.items():
        if status not in STATUSES:
            findings.append(f"{path}: phases.{name} `{status}` が {sorted(STATUSES)} のどれでもない")
    if findings:
        return findings, None

    index = len(PHASES) if current == "done" else PHASES.index(current)
    for name in PHASES[:index]:
        if phases[name] not in ("completed", "skipped"):
            findings.append(f"{path}: {name} は current_phase より前なので completed か skipped にすること(現在 `{phases[name]}`)")
    if current != "done" and phases[current] not in ("in_progress", "completed"):
        findings.append(f"{path}: current_phase の {current} は in_progress か completed にすること(現在 `{phases[current]}`)")
    for name in PHASES[index + 1:]:
        if phases[name] != "pending":
            findings.append(f"{path}: {name} は current_phase より後なので pending にすること(現在 `{phases[name]}`)")
    return findings, data


def check_artifact(path):
    data, body, findings = read_frontmatter(path)
    if findings:
        return findings
    phase = data.get("phase")
    if phase not in REQUIRED_HEADINGS:
        return [f"{path}: phase `{phase}` が {sorted(REQUIRED_HEADINGS)} のどれでもない"]
    status = data.get("status")
    if status not in ("draft", "approved"):
        findings.append(f"{path}: status `{status}` が draft と approved のどちらでもない")

    found = sections(body)
    for heading in REQUIRED_HEADINGS[phase] + COMMON_HEADINGS:
        if heading not in found:
            findings.append(f"{path}: 見出し `## {heading}` がない")
    if status == "approved":
        if not isinstance(data.get("approved_at"), datetime.date):
            findings.append(f"{path}: status が approved なのに approved_at が YYYY-MM-DD の日付ではない")
        for heading in COMMON_HEADINGS:
            if heading in found and not found[heading]:
                findings.append(f"{path}: status が approved なのに `## {heading}` の本文が空")
    return findings


def check_gate(feature_dir, phase, root):
    if phase not in PHASES:
        return [f"phase `{phase}` が {PHASES} のどれでもない"]
    findings, data = check_state(feature_dir)
    if findings:
        return findings
    if data["current_phase"] != phase:
        return [f"current_phase は `{data['current_phase']}` で、`{phase}` ではない"]
    if data["phases"][phase] != "in_progress":
        findings.append(f"phases.{phase} は `{data['phases'][phase]}` で、in_progress ではない")
    for name in PHASES[:PHASES.index(phase)]:
        if data["phases"][name] != "completed" or name not in ARTIFACT_FILES:
            continue
        artifact = feature_dir / ARTIFACT_FILES[name]
        artifact_data, _, artifact_findings = read_frontmatter(artifact)
        if artifact_findings:
            findings.extend(artifact_findings)
        elif artifact_data.get("phase") != name:
            findings.append(f"{artifact}: phase が `{name}` ではない(現在 `{artifact_data.get('phase')}`)")
        elif artifact_data.get("status") != "approved":
            findings.append(f"{artifact}: status が approved ではない(現在 `{artifact_data.get('status')}`)")
        else:
            findings.extend(check_artifact(artifact))
    if PHASES.index(phase) > PHASES.index("design") and data["phases"]["design"] == "completed":
        findings.extend(check_snapshot(feature_dir / "contract-snapshot.md", root))
    return findings


def tokens(text):
    """Separate words and symbols with single spaces so that matches respect word boundaries."""
    return " " + " ".join(re.findall(r"\w+|[^\w\s]", text)) + " "


def check_snapshot(path, root):
    if not path.is_file():
        return [f"{path} が見つからない"]
    findings = []
    target = None
    in_fence = False
    count = 0
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            match = HEADING.match(line)
            if match:
                target = root / match.group(1).strip("`")
                if not target.is_file():
                    findings.append(f"{number}行目: ファイルがない `{target}`")
                    target = None
            continue
        if target is None or not line.strip():
            continue
        count += 1
        if tokens(line) not in tokens(target.read_text(encoding="utf-8")):
            findings.append(f"{number}行目: Contract Drift。`{target}` に宣言が見つからない: {line.strip()}")
    if count == 0 and not findings:
        findings.append(f"{path}: 宣言が1件も書かれていない")
    return findings


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    args = sys.argv[1:]
    root = Path(".")
    if "--root" in args:
        i = args.index("--root")
        if i + 1 >= len(args):
            print(__doc__)
            return 2
        root = Path(args[i + 1])
        del args[i:i + 2]

    if len(args) == 2 and args[0] == "state":
        findings, _ = check_state(Path(args[1]))
    elif len(args) == 2 and args[0] == "artifact":
        findings = check_artifact(Path(args[1]))
    elif len(args) == 3 and args[0] == "gate":
        findings = check_gate(Path(args[1]), args[2], root)
    elif len(args) == 2 and args[0] == "snapshot":
        findings = check_snapshot(Path(args[1]), root)
    else:
        print(__doc__)
        return 2

    if not findings:
        print("OK")
        return 0
    for finding in findings:
        print(f"NG: {finding}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
