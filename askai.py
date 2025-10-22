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
import json

try:
    import sseclient
    HAS_SSECLIENT = True
except ImportError:
    HAS_SSECLIENT = False

URL = (
    os.environ.get("LLM_API_BASEURL", "http://localhost:5000") + "/v1/chat/completions"
)


def askai(text, system_prompt, template=None, stream=True, hide_reasoning=False, prefix=""):
    if not HAS_SSECLIENT:
        stream = False

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": text},
    ]
    if prefix:
        messages.append({"role": "assistant", "content": prefix})
        print(prefix, end="")

    request = {
        "messages": messages,
        "mode": "instruct",
        "user_bio": "",
        "max_tokens": 4096,
        "temperature": 1.0,
        "top_p": 0.9,
        "stream": stream,
    }
    if template:
        request["instruction_template"] = template

    response = requests.post(URL, json=request, stream=stream)
    if response.status_code == 200:
        if stream:
            import sseclient
            client = sseclient.SSEClient(response)
            in_reasoning = False
            try:
                for event in client.events():
                    try:
                        payload = json.loads(event.data)
                    except json.decoder.JSONDecodeError:
                        break
                    chunk = payload['choices'][0]['delta']
                    if payload["choices"] and "reasoning_content" in payload['choices'][0]['delta']:
                        if hide_reasoning:
                            continue
                        if not in_reasoning:
                            in_reasoning = True
                            print("Thinking:")
                            print("---------\n")
                        if chunk["reasoning_content"]:
                            print(chunk["reasoning_content"], end='', flush=True)
                    if payload["choices"] and "content" in payload['choices'][0]['delta']:
                        if in_reasoning:
                            in_reasoning = False
                            print("\n\nAnswer:")
                            print("-------\n")
                        if chunk["content"]:
                            print(chunk["content"], end='', flush=True)
                print()
            except requests.exceptions.ChunkedEncodingError:
                print("Error streaming the response.")
        else:
            result = response.json()["choices"][0]["message"]
            if not hide_reasoning and "reasoning_content" in result:
                print("Thinking:")
                print("---------\n")
                print(result["reasoning_content"].strip())
                print("\n\nAnswer:")
                print("-------\n")
            print(result["content"].strip())
    else:
        print("Error while asking the AI.")


def main():
    description = "Simple cmdline tool for asking an AI."
    epilog = ""
    if not HAS_SSECLIENT:
        epilog = "Hint: To enable streaming output install the python sseclient module."

    parser = argparse.ArgumentParser(description=description, epilog=epilog)
    parser.add_argument("input", type=str, help="filename or input text", nargs="*")
    parser.add_argument(
        "-i",
        "--instruction",
        type=str,
        help="prompt text or file",
        default="You are a helpful AI assistant.",
    )
    parser.add_argument(
        "-q",
        "--question",
        type=str,
        help="prompt text or file",
        default="",
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
    parser.add_argument(
        "-p", "--prefix", help="Start the answer with this prefix", default=""
    )
    if HAS_SSECLIENT:
        parser.add_argument(
            "-n", "--no-streaming", help="Disable streaming", action="store_true"
        )
    parser.add_argument(
        "--hide-reasoning", help="Hide reasoning", action="store_true"
    )
    args = parser.parse_args()
    inpt = " ".join(args.input)
    instruction = args.instruction
    question = args.question

    if inpt and os.path.isfile(inpt):
        with open(inpt, "r") as file:
            inpt = file.read()
    elif not inpt or inpt == "-":
        inpt = sys.stdin.read()

    if os.path.isfile(instruction):
        with open(instruction, "r") as file:
            instruction = file.read()

    if os.path.isfile(question):
        with open(question, "r") as file:
            question = file.read()

    if question:
        inpt = "Question: " + question + "\n\nInput:\n" + inpt

    if args.short:
        instruction += "\nGive a short reply only answering the question."
    elif args.shortest:
        instruction += "\nGive a single word answer to the question."
    elif args.long:
        instruction += "\nGive a detailed reply."
    if args.reason:
        instruction += "\nInclude your reasoning in the answer."

    stream = HAS_SSECLIENT and not args.no_streaming
    askai(text=inpt, system_prompt=instruction, template=args.template, stream=stream, hide_reasoning=args.hide_reasoning, prefix=args.prefix)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
