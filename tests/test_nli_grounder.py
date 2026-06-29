import pytest
from verialign.verification.nli_grounder import NLIGrounder
from verialign.verification.source_grounder import SourceGrounder


class TestNLIGrounder:
    def test_init(self):
        grounder = NLIGrounder()
        assert grounder is not None
        assert grounder._model_name == "cross-encoder/nli-deberta-v3-base"

    def test_is_available_returns_bool(self):
        grounder = NLIGrounder()
        result = grounder.is_available()
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_score_empty_context_returns_empty(self):
        grounder = NLIGrounder()
        result = await grounder.score("Paris is in France", [])
        assert result == []

    @pytest.mark.asyncio
    async def test_ground_no_context(self):
        grounder = NLIGrounder()
        status, score, details = await grounder.ground("test claim", [])
        assert status == "unclear"
        assert score == 0.0

    @pytest.mark.asyncio
    async def test_ground_unavailable_fallback(self):
        grounder = NLIGrounder()
        grounder._model = False
        status, score, details = await grounder.ground("test", ["some context"])
        assert status == "unclear"
        assert score == 0.0


class TestSourceGrounderNLI:
    def test_source_grounder_creates_nli(self):
        grounder = SourceGrounder(use_nli=True)
        assert grounder._nli_grounder is not None

    def test_source_grounder_disabled_nli(self):
        grounder = SourceGrounder(use_nli=False)
        assert grounder._nli_grounder is None

    @pytest.mark.asyncio
    async def test_ground_with_nli_fallback_when_not_available(self):
        grounder = SourceGrounder(use_nli=True)
        status, score, sources = await grounder.ground(
            "test claim", [("ctx-1", "some context text")]
        )
        assert status in ("supported", "unsupported", "unclear")
        assert isinstance(score, float)
