from urllib.parse import urlparse


class Provider:
    def __init__(
        self,
        name: str,
        namespace: str,
        latest_version: str,
        source: str,
        versions: list[str],
        current_version: str,
    ) -> None:
        self.name = name
        self.namespace = namespace
        self.latest_version = latest_version
        self.source = source
        self.versions = versions
        self.current_version = current_version

    def get_all_versions_between_current_and_latest(self) -> list[str]:
        """
        Find all versions between the current and
        latest and store them in a list
        """
        versions = []
        current_version_index = self.versions.index(self.current_version) + 1
        for version in self.versions[current_version_index:]:
            versions.append(version)
        return versions

    def is_latest_version(self) -> bool:
        """Check if current version is latest available version"""
        return self.current_version == self.latest_version

    def get_provider_repository_info(self) -> tuple[str, str]:
        """Get provider repository owner & name"""
        parts = urlparse(self.source)
        owner, repository_name = parts.path.strip("/").split("/")
        return owner, repository_name
