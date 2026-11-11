from app.services.competitor_research import _normalise_names


def test_normalise_names_deduplicates_and_excludes_subject():
    assert _normalise_names(
        [" Acme ", "ACME", "Beta Inc", "", "Beta Inc"],
        "Acme",
    ) == ["Beta Inc"]


def test_normalise_names_limits_output():
    names = [f"Competitor {i}" for i in range(20)]
    assert len(_normalise_names(names, "Subject")) == 10
