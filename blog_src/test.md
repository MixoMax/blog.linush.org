---
title: One Markdown to rule them all
author: Linus Horn
tags: [Markdown, Showcase]
description: A showcase of all Markdown features
created_date: 2023-10-01
---

# Markdown Feature Showcase

## Headings

# Heading 1
## Heading 2
### Heading 3
#### Heading 4
##### Heading 5
###### Heading 6

---

## Text Styles

**Bold text**

*Italic text*

~~Strikethrough~~

__Bold and _italic_ combined__

> Blockquote example

> ### Nested Blockquote
> - With a list inside

---

## Lists

### Unordered List

- Item 1
  - Subitem 1.1
  - Subitem 1.2
- Item 2

### Ordered List

1. First item
2. Second item
   1. Subitem 2.1
   2. Subitem 2.2

---

## Links

[Markdown Guide](https://www.markdownguide.org)

<https://www.example.com>

---

## Images

![Markdown Logo](https://markdown-here.com/img/icon256.png)

---

## Inline Code and Code Blocks

Inline code: `print("Hello, Markdown!")`

```python
def greet(name: str) -> None:
    print(f"Hello, {name}!")
```

```javascript
function greet(name) {
  console.log(`Hello, ${name}!`);
}
```

---

## Tables

| Syntax      | Description | Example           |
|-------------|-------------|-------------------|
| Header      | Title       | **Bold**          |
| Paragraph   | Text        | *Italic*          |
| Link        | URL         | [Link](#)         |

---

## Task Lists

- [x] Write Markdown file
- [ ] Use all features
- [x] Include code blocks

---

## Horizontal Rule

---

## Footnotes

Here is a footnote reference.[^1]

[^1]: This is the footnote content.

---

## Emoji

:smile: :rocket: :tada:

---

## Inline LaTeX

Inline math: $E = mc^2$

Display math:

$$
\int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
$$

---

## HTML

<div style="color: red; font-weight: bold;">This is HTML inside Markdown!</div>

---

## Escaping Characters

\*This text is not italicized\*

---

## Definition Lists

Term 1
: Definition 1

Term 2
: Definition 2

---

## Superscript and Subscript

H~2~O

X^2^

---

## Custom ID for Heading

### Heading with custom ID {#custom-id}
