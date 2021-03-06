import re
from re import Pattern


def make_sub_pattern(package: str, version: str) -> Pattern[str]:
    return re.compile(
        fr'(^\s*source\s*=\s*"{re.escape(package)}"\s*\n\s*version\s*=\s"){re.escape(version)}("\s*$)',
        re.MULTILINE,
    )


def parse_versions(
    versions_tf: str, package: str, old_version: str, new_version: str
) -> str:
    pat = make_sub_pattern(package, old_version)
    return pat.sub(fr"\g<1>{new_version}\g<2>", versions_tf)
