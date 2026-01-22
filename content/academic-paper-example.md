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

# Code Example

```python
def hello():
    print("Hello, World!")
```

# References

[^note]: This is a footnote example.
