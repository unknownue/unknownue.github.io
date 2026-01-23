+++
title = "Example Page"
[extra]
authors = [
    {name = "Your Name"},
]
venue = {name = "Publication Venue", date = 2025-01-01}
buttons = [
    {name = "Paper", url = "#"},
    {name = "Code", url = "#"},
]
katex = true
+++

This is an example page demonstrating the website features.

# Features

This template supports:

* A header with title, author, publication venue, year, and optional buttons
* Syntax highlighting with a dark theme
* Math rendering via KaTeX
* Figures via Zola shortcodes
* Markdown footnotes
* Twitter Summary Card, OpenGraph, and JSON-LD metadata

Let's demonstrate math rendering: writing
```tex
$$
\int_{\mathbb{R}} \frac{1}{\sqrt{2\pi\sigma^2}} \exp\left(\frac{(x-\mu)^2}{-2\sigma^2}\right) \mathrm{d} x = 1.
$$
```
in the Markdown file produces the output
$$
\int_{\mathbb{R}} \frac{1}{\sqrt{2\pi\sigma^2}} \exp\left(\frac{(x-\mu)^2}{-2\sigma^2}\right) \mathrm{d} x = 1.
$$

This theme also supports footnotes.[^note]

# Long Text Testing

This section tests how the theme handles various types of long content that might overflow or require special handling.

## Long URL Example

Here's a very long URL that might break layout: https://example.com/very/long/path/that/keeps/going/on/and/on/without/any/breaks/whatsoever/and/contains/many/segments

## Long Technical Term

Incomprehensibilities is one of the longest words in common usage, but antidisestablishmentarianism is even longer and pneumonoultramicroscopicsilicovolcanoconiosis is the longest word in major dictionaries.

## Inline Code with Long Path

When working with files located at `/usr/local/very/long/directory/path/that/goes/on/and/on/final/destination/file.txt`, you may encounter issues.

## Long Sentence Without Spaces

Thisisaverylongsentencewithoutanyspacesatallthatjustkeepsgoingandgoingandgoingandgoingandgoingandgoingandgoingandgoingandgoingandgoingandgoingandgoingandgoingandgoing.

## Long Sentence with Spaces

This is a more normal long sentence that contains many words but still uses proper spacing between each word and continues to describe various things without taking a breath or pause for punctuation of any kind and just keeps going on and on.

# Code Example

```python
def hello():
    print("Hello, World!")
```

# References

[^note]: This is a footnote example.
