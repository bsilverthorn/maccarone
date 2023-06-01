Maccarone: use English in your Python 🍝
========================================

Maccarone is an experimental tool that lets you write lines of English instead of Python in your Python source code. It looks like this:

```python
def add_two_numbers(x, y):
    #<<add the args>>

#<<argparse stuff>>
```

Maccarone lets you run that program like any other Python script:

```console
$ python -m examples.add 2 2
The sum of 2 and 2 is 4
```

Caution
-------

Be careful: Maccarone is an **unstable** and somewhat whimsical **experiment**.

Quickstart
----------

### Prerequisites

- Python 3.10+
- OpenAI API key with GPT-4 (`export OPENAI_API_KEY`)

### Install

- `pip install maccarone`

### Configure

Set up Maccarone in your base package `__init__.py`:

```python
import maccarone

maccarone.enable()
```

### Run

Natural-language snippets go inside special comment blocks:

```python
#<<like this>>
```

```python
#<<
# or this
#>>
```

Try it out with the `add_two_numbers()` example above.

Note that the first run of a source file can take 10+ seconds while Maccarone generates code with GPT-4.

Usage guide
-----------

### Snippet detection

Maccarone will preprocess:

- Any file that contains `#<<`, if you have `enable(py_string_matching=True)` (the default).
- Any file with extension `.mn.py`.

Modules with an `.mn.py` extension can be imported in your Python code just like regular `.py` modules.

### Distributing your code

You probably want to run Maccarone before you publish a package, but not after.

That outcome is easiest to achieve by:

- Adding `maccarone` only as a dev dependency.
- Using the `.mn.py` extension for source files containing natural language snippets.
- Running the standalone `maccarone` preprocessor during your package build process.

`maccarone` will produce a `.py` file for any `.mn.py` found under a designated path:

```
$ ls examples/
add.mn.py  fizzbuzz.mn.py  __init__.py  todo.mn.py
$ maccarone examples/
...
$ ls examples/
add.mn.py  add.py  fizzbuzz.mn.py  fizzbuzz.py  __init__.py  todo.mn.py  todo.py
```

You would typically run `maccarone` before running, e.g., `python -m build` and publishing the package.

Related work
------------

- https://github.com/bsilverthorn/vernac

FAQs
----

### What prevents my programs from behaving differently every time I recompile?

The strength of your faith in GPT-4.

### What about non-English languages?

They are likely to work, but less likely than English.

### What does "maccarone" mean?

https://en.wikipedia.org/wiki/Macaronic_language
