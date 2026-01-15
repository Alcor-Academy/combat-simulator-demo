#!/usr/bin/env python3
"""nWave Bypass Detector - Post-commit hook."""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path


def main() -> int:
    """Log commit for audit purposes."""
    audit_file = Path(".nwave-audit.log")

    try:
        # Get commit info
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H|%s|%an"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            parts = result.stdout.strip().split("|", 2)
            if len(parts) >= 3:
                commit_hash, subject, author = parts
            else:
                commit_hash = parts[0] if parts else "unknown"
                subject = parts[1] if len(parts) > 1 else "unknown"
                author = "unknown"

            log_entry = {
                "timestamp": datetime.now(tz=UTC).isoformat(),
                "commit": commit_hash[:8],
                "subject": subject[:50],
                "author": author,
                "no_verify": os.environ.get("PRE_COMMIT_ALLOW_NO_CONFIG", "") == "1",
            }

            # Append to audit log
            with open(audit_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")

        return 0

    except Exception:
        # Never block on audit failures
        return 0


if __name__ == "__main__":
    sys.exit(main())
