Maccarone: AI-managed code blocks in Python ⏪⏩
===============================================

[![PyPI version](https://badge.fury.io/py/maccarone.svg)](https://badge.fury.io/py/maccarone)

Maccarone lets you [_delegate_](https://silverthorn.blog/posts/2023-08-llm-assisted-programming-maccarone/) sections of your Python program to AI ownership.

Here's what it looks like in [the VS Code extension](https://marketplace.visualstudio.com/items?itemName=maccarone.maccarone):

![screencap-20230629](https://github.com/bsilverthorn/maccarone/assets/92956/c1549168-28ad-49ef-bcff-dd232838220c)

Example
-------

You might write some code like this:

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

Quickstart
----------

### Prerequisites

- Python 3.8+
- OpenAI API key with GPT-4 (`export OPENAI_API_KEY`)

### Easy Mode - VS Code Extension

Easy mode is the free extension from [the VS Code marketplace](https://marketplace.visualstudio.com/items?itemName=maccarone.maccarone).

Install it in VS Code and you're done (if you have the prerequisites above).

### Other Option - Command Line

If you don't use VS Code, you can still install Maccarone directly from PyPI:

- `pip install maccarone`

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

### Is this project active?

Yes and no. It was created to evaluate a specific flavor of LLM-assisted programming. It feels feature-complete for that purpose.

PRs and bug reports are welcome, however, and there may be future maintenance releases.
