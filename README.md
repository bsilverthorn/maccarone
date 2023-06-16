Maccarone: AI-managed code blocks in Python 🍝
==============================================

[![PyPI version](https://badge.fury.io/py/maccarone.svg)](https://badge.fury.io/py/maccarone)

Maccarone lets you _delegate_ sections of your Python program to AI ownership. You might write some code like this:

```python
def main(path: str):
    #<<filenames = a list of filenames under path>>

    for fn in filenames:
        #<<size = size of fn in bytes>>

        print(fn, size)

#<<use argparse and call main>>
```

Maccarone then fills in the sections you've delegated:

```python
def main(path: str):
    #<<filenames = list of filenames under path; no dirs>>
    import os
    filenames = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    #<</>>

    for fn in filenames:
        #<<size = size of fn in bytes>>
        size = os.path.getsize(os.path.join(path, fn))
        #<</>>
        print(fn, size)

#<<use argparse and call main>>
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("path", type=str)
args = parser.parse_args()
main(args.path)
#<</>>
```

Make a change in your code, like adding an `extension` parameter to `main`, and Maccarone keeps its sections up to date:

```python
def main(path: str, extension: str | None = None):
    #<<filenames = list of filenames under path; no dirs>>
    …
    if extension:
        filenames = [f for f in filenames if f.endswith(extension)]
    #<</>>
    …

#<<use argparse and call main>>
…
parser.add_argument("--extension", type=str, default=None)
args = parser.parse_args()
main(args.path, args.extension)
#<</>>
```

## Tangent: treating English as code

If you'd like, you can treat your English prompts _as_ the code: rather than updating your Python source to include AI-generated blocks, Maccarone can treat that output as ephemeral and feed it directly into the interpreter. This mode is fun but less practical. See [an older README](ENGLISH_AS_CODE.md) for more details.

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

### Run

Delegate a code block to Maccarone by giving it some guidance in a special comment:

```python
#<<like this>>
```

```python
#<<
# or this
#>>
```

Then run `maccarone` to generate code and update your source file:

```console
$ maccarone --rewrite examples/file_sizes.py
```

Usage notes
-----------

### Running `maccarone` on a directory

Maccarone can rewrite all files in a directory:

```console
$ maccarone --rewrite --suffix .py examples/
```

Be careful! You should probably run this only on files in source control, for example.

### Caching

Maccarone caches output and metadata in an `.mn.json` file stored alongside the input source. You may want to `git add` this cache file. Full preprocessing (e.g., calls to the OpenAI API) occurs only when the input source is changed.

Related work
------------

- https://github.com/bsilverthorn/vernac

FAQs
----

### It needs my OpenAI API key?

Maccarone prompts GPT-4 to write code. It will make OpenAI API calls using your key and you **will be charged** by OpenAI.

API calls are made every time Maccarone preprocesses a new version of a source file.

The number of tokens consumed is proportional to the size of your completed code. You cannot accurately predict that number in advance. A small source module might cost $0.01–0.10 to preprocess.

### What prevents my program from behaving differently after each preprocessing run?

The strength of your faith in GPT-4.

### What about non-English languages?

They are likely to work, but less likely than English.

### What does "maccarone" mean?

https://en.wikipedia.org/wiki/Macaronic_language
