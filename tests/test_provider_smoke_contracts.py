from sr8.adapters import list_provider_descriptors, probe_providers


def test_provider_descriptors_and_probes_match() -> None:
    descriptors = {descriptor.name: descriptor for descriptor in list_provider_descriptors()}
    probes = {probe.provider: probe for probe in probe_providers()}

    assert descriptors.keys() == probes.keys()
    assert all(probe.capabilities for probe in probes.values())
