# Askai

Askai is a really simple command line tool for using LLMs with openai API
from the shell.

## Usage

```
usage: askai.py [-h] [-i INSTRUCTION] [-t TEMPLATE] [-s] [-S] [-l] [-r] [input]

positional arguments:
  input                 input text or file

options:
  -h, --help            show this help message and exit
  -i INSTRUCTION, --instruction INSTRUCTION
                        prompt text or file
  -q QUESTION, --question QUESTION
                        prompt text or file
  -t TEMPLATE, --template TEMPLATE
                        Set the instruction template like Alpaca or ChatML
  -s, --short           Request a short answer
  -S, --shortest        Request a very short answer
  -l, --long            Request a long answer
  -r, --reason          Request a answer with reasoning
```

Input and instruction can be either a string or a filename. If no input is given
the script reads the input from stdin. The options for different types of answers
only add short prompts that ask for long or short answers to the instructions.

Other than the instruction that is used as system prompt, the optional question
is added on top of the user input in the form:

```
Question: QUESTION

Input:
INPUT
```

The script is tested with [Text generation web UI](https://github.com/oobabooga/text-generation-webui/)
but should work with any backend that provides chat completion via the openai API.

## License

The script is distributed under the MIT licence.
