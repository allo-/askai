#!/usr/bin/env python3

# Copyright (c) 2024 Alexander Schier
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import requests
import os
import sys
import argparse

URL = (
    os.environ.get("LLM_API_BASEURL", "http://localhost:5000") + "/v1/chat/completions"
)


def askai(text, system_prompt, template=None):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    request = {
        "messages": messages,
        "mode": "instruct",
        "user_bio": "",
        "max_new_tokens": 4096,
        "max_tokens": 4096,
    }
    if template:
        request["instruction_template"] = template
    response = requests.post(URL, json=request)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        print("Error while asking the AI.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=str, help="input text or file", nargs="?")
    parser.add_argument(
        "-i",
        "--instruction",
        type=str,
        help="prompt text or file",
        default="You are a helpful AI assistant.",
    )
    parser.add_argument(
        "-t",
        "--template",
        help="Set the instruction template like Alpaca or ChatML",
        default="",
    )
    parser.add_argument(
        "-s", "--short", help="Request a short answer", action="store_true"
    )
    parser.add_argument(
        "-S", "--shortest", help="Request a very short answer", action="store_true"
    )
    parser.add_argument(
        "-l", "--long", help="Request a long answer", action="store_true"
    )
    parser.add_argument(
        "-r", "--reason", help="Request a answer with reasoning", action="store_true"
    )
    args = parser.parse_args()
    inpt = args.input
    instruction = args.instruction

    if inpt and os.path.isfile(inpt):
        with open(inpt, "r") as file:
            inpt = file.read()
    elif not inpt or inpt == "-":
        inpt = sys.stdin.read()

    if os.path.isfile(instruction):
        with open(instruction, "r") as file:
            instruction = file.read()

    if args.short:
        instruction += "\nGive a short reply only answering the question."
    elif args.shortest:
        instruction += "\nGive a single word answer to the question."
    elif args.long:
        instruction += "\nGive a detailed reply."
    if args.reason:
        instruction += "\nInclude your reasoning in the answer."

    print(askai(text=inpt, system_prompt=instruction, template=args.template))


if __name__ == "__main__":
    main()
