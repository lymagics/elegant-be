from hamcrest import assert_that, has_key, is_not

from src.aop.awaited import awaited


def test_strips_return_annotation_only():
    @awaited
    async def sample(tally: int) -> str:
        return str(tally)

    assert_that(
        sample.__annotations__,
        is_not(has_key("return")),
        "The decorator must drop the return annotation",
    )


def test_keeps_argument_annotations():
    @awaited
    async def probe(label: str) -> int:
        return len(label)

    assert_that(
        probe.__annotations__,
        has_key("label"),
        "The decorator must keep argument annotations",
    )
