import re
from typing import Dict


def parse_llvm_stats(stderr: str) -> Dict[str, dict]:
    stats = {}
    if not stderr:
        return stats  # empty dict if nothing to parse

    line_re = re.compile(r"^\s*(\d+)\s+([^\s]+)\s+-\s+(.+)$")

    for line in stderr.splitlines():
        m = line_re.match(line)
        if m:
            value, pass_name, metric = m.groups()
            value = int(value)
            if pass_name not in stats:
                stats[pass_name] = {}
            stats[pass_name][metric.strip()] = value

    return stats  # always a dict
