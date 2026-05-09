# youtube-seo

Mine YouTube autocomplete + top-N video metadata for a topic into a structured SEO research artifact at `<video-dir>/seo/research.json`. No API key, anonymous, ~25s per run.

Consumed by the `youtube-seo-research` skill (and downstream consumer skills `script-writer` and `thumbnail-creator`).

## Usage

```bash
# From inside a video folder (reads outline.md H1 for the topic):
uv run --project ../../tools/youtube-seo seo-research

# Or with an explicit topic:
uv run --project ../../tools/youtube-seo seo-research --topic "text rendering"
```

(Detailed flag reference, output schema, troubleshooting — added in Task 11.)
