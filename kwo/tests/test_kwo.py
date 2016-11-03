import pytest

from kwo import kwonly, vararg, with_kwonly, no_default


def test_no_default_raises():
    with pytest.raises(AssertionError) as e:
        no_default()

    assert (
        str(e.value) ==
        'no_default is just a sentinel, why are you calling this?'
    )


def test_vararg_raises():
    with pytest.raises(AssertionError) as e:
        vararg()

    assert (
        str(e.value) ==
        'vararg is just a sentinel, why are you calling this?'
    )


def test_kwonly_immutable():
    attr = kwonly()
    with pytest.raises(AttributeError) as e:
        attr.default = 1

    assert str(e.value) == 'kwonly objects are immutable'


def test_non_kwonly_after_kwonly():
    with pytest.raises(SyntaxError) as e:
        @with_kwonly
        def f(a=kwonly(), b=2):  # pragma: no cover
            pass

    assert str(e.value).startswith(
        "non keyword only argument 'b' follows keyword argument 'a'"
    )


def test_non_kwonly_after_vararg():
    with pytest.raises(SyntaxError) as e:
        @with_kwonly
        def f(a=vararg, b=2):  # pragma: no cover
            pass

    assert str(e.value).startswith(
        "non keyword only argument 'b' follows vararg 'a'"
    )


def test_duplicate_vararg():
    with pytest.raises(SyntaxError) as e:
        @with_kwonly
        def f(a=vararg, b=vararg):  # pragma: no cover
            pass

    assert str(e.value).startswith("duplicate 'vararg' arguments")


def test_kwonly_no_default():
    @with_kwonly
    def f(a, b=kwonly()):
        return a, b

    assert f.__name__ == 'f'

    with pytest.raises(TypeError):
        f(1, 2)

    with pytest.raises(TypeError) as e:
        f(1)

    assert str(e.value) == "f() missing 1 required keyword-only argument: 'b'"

    assert f(1, b=2) == (1, 2)

    @with_kwonly
    def g(a, b=kwonly(), c=kwonly()):
        return a, b, c

    assert g.__name__ == 'g'

    with pytest.raises(TypeError):
        g(1, 2, 3)

    with pytest.raises(TypeError) as e:
        g(1)

    assert (
        str(e.value) ==
        "g() missing 2 required keyword-only arguments: 'b' and 'c'"
    )

    assert g(1, b=2, c=3) == (1, 2, 3)

    @with_kwonly
    def h(a, b=kwonly(), c=kwonly(), d=kwonly()):
        return a, b, c, d

    assert h.__name__ == 'h'

    with pytest.raises(TypeError):
        h(1, 2, 3, 4)

    with pytest.raises(TypeError) as e:
        h(1)

    assert (
        str(e.value) ==
        "h() missing 3 required keyword-only arguments: 'b', 'c', and 'd'"
    )

    assert h(1, b=2, c=3, d=4) == (1, 2, 3, 4)


def test_no_work_fast_path():
    def f():  # pragma: no cover
        pass

    assert with_kwonly(f) is f
