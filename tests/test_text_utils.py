from vlrdevapi._utils.text import normalize_whitespace, split_stage_bracket


class TestNormalizeWhitespace:
    def test_collapses_tabs_and_newlines(self):
        raw = "Playoffs \u22c5\n\t\t\t\n\t\t\tLBF"
        assert normalize_whitespace(raw) == "Playoffs \u22c5 LBF"

    def test_collapses_repeated_spaces(self):
        assert normalize_whitespace("  VCT EMEA S2:  Challengers  ") == (
            "VCT EMEA S2: Challengers"
        )

    def test_empty(self):
        assert normalize_whitespace(" \n\t ") == ""


class TestSplitStageBracket:
    def test_stage_and_bracket(self):
        assert split_stage_bracket("Playoffs \u22c5 LBF") == ("Playoffs", "LBF")

    def test_bracket_only(self):
        assert split_stage_bracket("Ro16") == ("", "Ro16")

    def test_normalizes_whitespace(self):
        assert split_stage_bracket(
            "Group Stage \u22c5\n\t\t\t\n\t\t\tWinner's (D)"
        ) == ("Group Stage", "Winner's (D)")

    def test_empty(self):
        assert split_stage_bracket(" \n\t ") == ("", "")
