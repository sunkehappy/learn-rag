from entity_resolver import EntityInfo, resolve_from_path, resolve_from_section


def test_resolve_from_path_spain():
    info = resolve_from_path("gitlab_handbook/entity/iberia-srl-spain.md")
    assert info.entity == "GitLab Iberia s.r.l."
    assert info.country_code == "ES"


def test_resolve_from_path_global_expansion():
    path = "gitlab_handbook/total-rewards/benefits/general-and-entity-benefits/global-expansion.md"
    info = resolve_from_path(path)
    assert info.entity == "Global Expansion"
    assert info.country_code == ""


def test_resolve_from_path_generic():
    info = resolve_from_path("gitlab_handbook/engineering/foo.md")
    assert info.entity == ""
    assert info.country_code == ""


def test_resolve_from_section_austria():
    path = "gitlab_handbook/total-rewards/benefits/general-and-entity-benefits/global-expansion.md"
    base = resolve_from_path(path)
    info = resolve_from_section(base, "Austria 🇦🇹", path)
    assert info.entity == "Global Expansion"
    assert info.country_code == "AT"


def test_resolve_from_section_non_country():
    path = "gitlab_handbook/total-rewards/benefits/general-and-entity-benefits/remote-com.md"
    base = resolve_from_path(path)
    info = resolve_from_section(base, "**Questions?**", path)
    assert info.entity == "Remote.com"
    assert info.country_code == ""


def test_resolve_from_section_preserves_existing_country():
    base = EntityInfo(entity="GitLab GmbH", country_code="DE")
    info = resolve_from_section(base, "Some Other Section", "gitlab_handbook/entity/gmbh-germany.md")
    assert info.country_code == "DE"
