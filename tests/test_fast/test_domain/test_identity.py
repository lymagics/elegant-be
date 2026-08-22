from hamcrest import assert_that, equal_to
from hypothesis import given
from hypothesis import strategies as st

from src.domain.identity import Identity


@given(subject=st.text(max_size=40))
def test_returns_any_subject_unchanged(subject: str):
    assert_that(
        Identity(subject).id(),
        equal_to(subject),
        "The identity must return its subject untouched",
    )
