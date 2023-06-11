Maccarone: use English in your Python 🍝
========================================

Maccarone is an experimental tool that lets you write English inside Python source code:

```python
def main(path: str):
    #<<filenames = a list of filenames under path>>

    for fn in filenames:
        #<<size = size of fn in bytes>>

        print(fn, size)

#<<use argparse and call main>>
```

You can run that program like any other Python script:

```console
$ python -m examples.file_sizes /etc
…
/etc/wgetrc 4942
/etc/nsswitch.conf 542
/etc/adduser.conf 3028
/etc/ethertypes 1816
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

Try it out with the example above.

Note that the first run of a source file can take 10+ seconds while Maccarone generates code with GPT-4.

Usage guide
-----------

### Core concepts

Maccarone is a Python [preprocessor](https://en.wikipedia.org/wiki/Preprocessor). It transforms Python-and-English source code (what you write) into pure Python (what the interpreter runs).

Preprocessing can happen _ahead of time_, in an explicit build step, or _just in time_, during import:

- To preprocess automatically during import, call `maccarone.enable()` in your top-level `__init__.py`.
- To preprocess explicitly in a build step, run `maccarone your/source/dir`.

These options are not mutually exclusive. You can rely on import-time preprocessing during development and also perform explicit preprocessing before packaging, for example.

Maccarone will decide to preprocess files based on extension (usually `.mn.py`) and/or the presence of `#<<…>>` (in a plain `.py` file). Its behavior is configured via arguments to `maccarone` or `enable()`.

Maccarone caches output and metadata in an `.mn.json` file stored alongside the input source. You may want to `git add` this cache file. Full preprocessing (e.g., calls to the OpenAI API) occurs only when the input source is changed.

### Import-time preprocessing with `maccarone.enable()`

Running `enable()` in your top-level `__init__.py` will insert Maccarone into the Python import process. It offers a few config knobs:

```python
maccarone.enable(
    py_string_matching=True, # preprocess .py files containing #<<>>?
    include_pattern=None, # only preprocess matching modules, e.g., "foo.*"
    exclude_pattern=None, # never preprocess matching modules, e.g., "bar.*"
)
```

Consider setting `include_pattern="your_package.*"`.

Note that `py_string_matching` only controls whether plain `.py` files are preprocessed. Maccarone will always preprocess `.mn.py` files.

### Build-time preprocessing with `maccarone <path>`

`maccarone --write` will produce a `.py` file for any `.mn.py` found under a designated path:

```console
$ ls examples/
add.mn.py  fizzbuzz.mn.py  __init__.py  todo.mn.py
$ maccarone --write examples/
...
$ ls examples/
add.mn.py  add.py  fizzbuzz.mn.py  fizzbuzz.py  __init__.py  todo.mn.py  todo.py
```

You would typically run `maccarone` before running, e.g., `python -m build` and publishing your package.

### Debugging

Use `maccarone --print` to see the output of preprocessing:

```console
$ maccarone --print examples/add.mn.py 
INFO:maccarone.scripts.preprocess:preprocessing examples/add.mn.py
def add_two_numbers(x, y):
    return x + y

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("x", type=int)
parser.add_argument("y", type=int)
args = parser.parse_args()
print(add_two_numbers(args.x, args.y))
```

### Distributing your code

You probably want to run Maccarone during development, but not require your users to install or run it themselves.

That outcome is easiest to achieve by:

- Adding `maccarone` only as a dev dependency
- Using the `.mn.py` extension for source files containing natural language snippets
- Running `maccarone --write` during your package build process

That approach will produce pure-Python `.py` files to be picked up by your Python packaging tool.

Related work
------------

- https://github.com/bsilverthorn/vernac

FAQs
----

### It needs my OpenAI API key?

Maccarone prompts GPT-4 to write code. It will make OpenAI API calls using your key and you **will be charged** by OpenAI.

API calls are made every time Maccarone preprocesses a source file for the first time: when you use `enable()` and run your program, or you run `maccarone` explicitly, after changing a module that contains `#<<maccarone snippets>>`.

The number of tokens consumed is proportional to the size of your completed source code. You cannot predict that number in advance. A small source module might cost $0.01–0.10 to preprocess.

### What prevents my program from behaving differently after each preprocessing run?

The strength of your faith in GPT-4.

### What about non-English languages?

They are likely to work, but less likely than English.

### What does "maccarone" mean?

https://en.wikipedia.org/wiki/Macaronic_language
