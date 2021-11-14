import re
from typing import Pattern


def make_sub_pattern(package, version) -> Pattern:
    return re.compile(
        fr'(^\s*source\s*=\s*"{re.escape(package)}"\s*\n\s*version\s*=\s"){re.escape(version)}("\s*$)',
        re.MULTILINE,
    )


def parse_versions(s, package, old_version, new_version) -> str:
    pat = make_sub_pattern(package, old_version)
    return pat.sub(fr"\g<1>{new_version}\g<2>", s)
