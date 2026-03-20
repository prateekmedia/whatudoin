# whatudoin

A tiny static page for sharing what you're currently working on.

It reads tasks from `tasks.md` and renders them as a simple list or grouped categories.

## Run locally

Serve the project root with a small HTTP server:

```bash
python3 -m http.server
```

Then open `http://localhost:8000`.

## Edit tasks

Update `tasks.md`.

Supported formats:

```md
- One task
- [Linked task](https://example.com)

## Work
- Task in a category

## Deep Work
slug: focus
- Task in a category with an optional custom slug

## Personal
- Another task
```

If you use headings like `## Work`, the homepage shows categories first. Without headings, it shows a flat list.

If you add an optional `slug: ...` line directly under a heading, that value is used for `?cat=...`. If you omit it, the slug is generated from the heading text.
