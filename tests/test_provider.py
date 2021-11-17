import unittest

from provider import Provider


class TestProvider(unittest.TestCase):
    def test_is_latest_version(self) -> None:
        provider = Provider(
            name="test",
            namespace="test",
            latest_version="0.2.3",
            source="https://github.com/test/test",
            versions=["0.2.0", "0.2.1", "0.2.2", "0.2.3"],
            current_version="0.2.3",
        )

        self.assertEqual(provider.is_latest_version(), True, "Should be True")

    def test_is_not_latest_version(self) -> None:
        provider = Provider(
            name="test",
            namespace="test",
            latest_version="0.2.3",
            source="https://github.com/test/test",
            versions=["0.2.0", "0.2.1", "0.2.2", "0.2.3"],
            current_version="0.2.2",
        )

        self.assertEqual(provider.is_latest_version(), False, "Should be False")

    def test_get_all_versions_between_current_and_latest(self) -> None:
        provider = Provider(
            name="test",
            namespace="test",
            latest_version="0.2.3",
            source="https://github.com/test/test",
            versions=["0.2.0", "0.2.1", "0.2.2", "0.2.3"],
            current_version="0.2.1",
        )

        self.assertListEqual(
            provider.get_all_versions_between_current_and_latest(),
            ["0.2.2", "0.2.3"],
            'Should be ["0.2.2", "0.2.3"]',
        )

    def test_get_provider_repository_info(self) -> None:
        provider = Provider(
            name="test",
            namespace="test",
            latest_version="0.2.3",
            source="https://github.com/test/test",
            versions=["0.2.0", "0.2.1", "0.2.2", "0.2.3"],
            current_version="0.2.1",
        )

        self.assertTupleEqual(
            provider.get_provider_repository_info(),
            ("test", "test"),
            'Should be ("test", "test")',
        )


if __name__ == "__main__":
    unittest.main()
