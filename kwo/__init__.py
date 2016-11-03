"""A python2/3 compatible interface to keyword only arguments.
"""
from functools import wraps
import inspect
import itertools
import operator as op
import sys
from textwrap import dedent
from types import CodeType
from uuid import uuid4


PY3 = sys.version_info[0] >= 3

_code_argorder = (
    ('co_argcount', 'co_kwonlyargcount') if PY3 else ('co_argcount',)
) + (
    'co_nlocals',
    'co_stacksize',
    'co_flags',
    'co_code',
    'co_consts',
    'co_names',
    'co_varnames',
    'co_filename',
    'co_name',
    'co_firstlineno',
    'co_lnotab',
    'co_freevars',
    'co_cellvars',
)

if PY3:  # pragma: no cover
    zip_longest = itertools.zip_longest
else:  # pragma: no cover
    zip_longest = itertools.izip_longest


def private_namespace(name):
    """Prefix a name with a random string so it doesn't collide with other
    names.

    Parameters
    ----------
    name : str
        The name to hide.

    Returns
    -------
    hidden : str
        The mangled name.
    """
    return '_%s_%s' % (uuid4().hex, name)


def no_default():
    """A marker indicating that a kwonly argument does not have a default
    argument. This is implemented as a function to serialize correctly.

    Note
    ----
    Don't call this function, it is just a sentinel value.
    """
    raise AssertionError(
        'no_default is just a sentinel, why are you calling this?',
    )


def vararg():
    """A markeer indicating that an argument is a variadic argument,
    like *args.

    Note
    ----
    Don't call this function, it is just a sentinel value.

    See Also
    --------
    :func:`~kwonly.with_kwonly`
    :func:`~kwonly.kwonly`
    """
    raise AssertionError(
        'vararg is just a sentinel, why are you calling this?',
    )


class kwonly(object):
    """Mark that an argument is keyword only.

    Parameters
    ----------
    default : any, optional
        The default argument for this keyword only argument. If not provided,
        the argument will not have a default value.

    Examples
    --------
    >>> from __future__ import print_function
    >>> from kwo import with_kwonly, kwonly, vararg
    >>> @with_kwonly
    ... def f(a, args=vararg, b=kwonly(), c=kwonly('default'), **kwargs):
    ...     return (a, b, c, args, kwargs)
    ...
    >>> f(1, 2, 3, b='b', f='f')
    (1, 'b', 'default', (2, 3), {'f': 'f'})

    See Also
    --------
    :func:`~kwonly.with_kwonly`
    :func:`~kwonly.vararg`
    """
    def __init__(self, default=no_default):
        object.__setattr__(self, 'default', default)

    def __setattr__(self, attr, value):
        raise AttributeError('kwonly objects are immutable')


def _format_syntax_error(f, msg):
    code = f.__code__
    filename = code.co_filename
    lno = code.co_firstlineno
    try:
        with open(filename) as f:
            line = f.readlines()[lno - 1]
    except IOError:  # pragma: no cover
        line = '???'

    return SyntaxError(msg, (filename, lno, len(line), line))


def with_kwonly(f):
    """Process any :class:`~kwonly.kwonly` arguments and rewrite the signature.

    Parameters
    ----------
    f : callable
        The function which may have :class:`~kwonly.kwonly` arguments to
        process.

    Returns
    -------
    processed_f : callable
        The function with :class:`~kwonly.kwonly` arguments rewritten to the
        python 2 or python 3 keyword only version.

    Notes
    -----
    This function is most often used as a decorator.

    See Also
    --------
    :class:`~kwonly.kwonly`
    :func:`~kwonly.vararg`
    """
    argspec = inspect.getargspec(f)
    defaults = reversed(list(zip_longest(
        reversed(argspec.args),
        reversed(argspec.defaults or ()),
        fillvalue=no_default,
    )))

    kwonly_defaults = []
    found_kwonly = None
    found_vararg = argspec.varargs
    real_vararg = argspec.varargs is not None

    for name, value in defaults:
        if isinstance(value, kwonly):
            found_kwonly = name
            kwonly_defaults.append((name, value.default))
        elif value is vararg:
            if found_vararg is not None:
                raise _format_syntax_error(f, "duplicate 'vararg' arguments")
            found_vararg = name
            real_vararg = False
        elif found_vararg is not None and not real_vararg:
            raise _format_syntax_error(
                f,
                'non keyword only argument %r follows vararg %r' % (
                    name,
                    found_vararg,
                ),
            )
        elif found_kwonly:
            raise _format_syntax_error(
                f,
                'non keyword only argument %r follows keyword argument %r' % (
                    name,
                    found_kwonly,
                ),
            )

    if found_kwonly is None and found_vararg is argspec.varargs:
        # fast path when we have no kwonly args to process
        return f

    kwonly_names = list(map(op.itemgetter(0), kwonly_defaults))

    def extract_kwonlies(kwargs,
                         kwonly_defaults=kwonly_defaults,
                         no_default=no_default):
        ret = []
        missing_kwonlies = []
        for name, default in kwonly_defaults:
            value = kwargs.pop(name, default)
            if value is no_default:
                missing_kwonlies.append(name)
            else:
                ret.append(value)

        if missing_kwonlies:
            n_missing = len(missing_kwonlies)
            plural = 's'
            if n_missing == 1:
                args = repr(missing_kwonlies[0])
                plural = ''
            elif n_missing == 2:
                args = '%r and %r' % tuple(missing_kwonlies)
            else:
                args = ', and '.join((
                    ', '.join(map(repr, missing_kwonlies[:-1])),
                    repr(missing_kwonlies[-1]),
                ))
            raise TypeError(
                '%s() missing %d required keyword-only argument%s: %s' % (
                    f.__name__,
                    n_missing,
                    plural,
                    args,
                ),
            )

        return ret

    wrapper_argspec_str = ', '.join(
        arg for arg in argspec.args
        if arg not in kwonly_names and arg != found_vararg
    )
    call_sig_str = wrapper_argspec_str
    if found_vararg:
        added = ', *' + found_vararg
        call_sig_str += ', ' + found_vararg
        wrapper_argspec_str += added

    call_sig_str += ', ' + ', '.join(map('{0}={0}'.format, kwonly_names))

    if argspec.keywords:
        kwargname = argspec.keywords
    else:
        kwargname = private_namespace('kwargs')

    added = ', **' + kwargname
    call_sig_str += added
    wrapper_argspec_str += added

    extract_kwonlies_name = private_namespace('extract_kwonlies')
    source_code = dedent(
        """\
        def make_function({extract_kwonlies}=extract_kwonlies):
            def function({wrapper_argspec}):
                {assign_kwonlies}
                return f({call_sig})
            return function
        """,
    ).format(
        extract_kwonlies=extract_kwonlies_name,
        wrapper_argspec=wrapper_argspec_str,
        assign_kwonlies='{kwonlies}, = {extract_kwonlies}({kwargname})'.format(
            extract_kwonlies=extract_kwonlies_name,
            kwonlies=', '.join(kwonly_names),
            kwargname=kwargname,
        ) if kwonly_defaults else '',
        call_sig=call_sig_str,
    )

    ns = {'f': f, 'extract_kwonlies': extract_kwonlies}
    compiled = compile(source_code, f.__code__.co_filename, 'exec')
    exec(compiled, ns)
    new_f = wraps(f)(ns['make_function']())
    code = new_f.__code__
    args = {
        attr: getattr(code, attr)
        for attr in dir(code)
        if attr.startswith('co_')
    }
    args['co_name'] = f.__code__.co_name
    args['co_firstlineno'] = f.__code__.co_firstlineno
    new_f.__code__ = CodeType(*(args[arg] for arg in _code_argorder))
    return new_f

__all__ = [
    'kwonly',
    'no_default',
    'with_kwonly',
    'vararg',
]
