===
kwo
===

Python 2/3 compatible keyword only arguments.

Alternative implementations require you to duplicate the argument name in the
keyword only decorator and the argument list, this implementation reflects this
information from some special default values.

Examples
--------

Regular keyword only argument with no default
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> from kwo import with_kwonly, kwonly, vararg

   >>> @with_kwonly
   ... def f(a, b, c=kwonly()):
   ...     return a, b, c

   >>> f(1, 2)
   Traceback (most recent call last):
     ...
   TypeError: f() missing 1 required keyword-only arguments: 'c'

   >>> f(1, 2, 3)
   Traceback (most recent call last):
     ...
   TypeError: f() takes exactly 2 arguments (3 given)

   >>> f(1, 2, c=3)
   (1, 2, 3)

Keyword only argument with default
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> @with_kwonly
   ... def g(a, b, c=kwonly('default')):
   ...     return a, b, c

   >>> f(1, 2)
   (1, 2, 'default')

   >>> f(1, 2, 3)
   Traceback (most recent call last):
     ...
   TypeError: g() takes exactly 2 arguments (3 given)

   >>> f(1, 2, c=3)
   (1, 2, 3)

Keyword only argument after \*args
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   >>> @with_kwonly
   ... def h(a, b, args=vararg, c=kwonly()):
   ...     return a, b, c, args

   >>> f(1, 2, 3, 4)
   Traceback (most recent call last):
     ...
   TypeError: f() missing 1 required keyword-only argument: 'c'

   >>> f(1, 2, 3, 4, c='c')
   (1, 2, (3, 4), 'c')


License
-------

``kwo`` is licensed under the terms of the Apache 2.0.
