# Freepik MCP

MCP Server for seamless Freepik API integration with AI assistants.

## What is this?

A **Model Context Protocol (MCP) server** that connects AI assistants (Claude, Cursor, etc.) with Freepik APIs. Generate images, search resources and icons, detect AI content — all from your AI workflow.

> **This fork** includes an optimized OpenAPI spec loader that reduces tool context from ~26K to ~4K tokens (~85% reduction), making it practical for daily use without blowing up your context window.

## Available Tools

| Tool | Description |
|------|-------------|
| `text_to_image_mystic_sync` | Generate images from text prompts (Mystic AI with auto-polling) |
| `detect_ai_image` | Detect if an image is AI-generated (confidence score) |
| `search_resources` | Search photos, vectors, PSDs, AI-generated content |
| `get_resource_detail_by_id` | Get resource metadata by ID |
| `download_resource_by_id` | Download a resource by ID |
| `get_resource_download_formats` | Get available download formats for a resource |
| `search_icons` | Search icons by term, slug, family |
| `get_icon_detail_by_id` | Get icon metadata by ID |
| `download_icon_by_id` | Download icon (SVG, PNG, GIF, MP4, PSD, EPS, JSON, AEP) |

## Prerequisites

- **Python 3.12+**
- **uv** package manager ([install](https://docs.astral.sh/uv/getting-started/installation/))
- **Freepik API Key** ([get one here](https://freepik.com/api))

## Installation

```bash
git clone https://github.com/sh4d0w/freepik-mcp.git
cd freepik-mcp
uv sync
```

Create your `.env` file:

```bash
echo "FREEPIK_API_KEY=your_api_key_here" > .env
```

## Setup for AI Assistants

Replace `/FULL/PATH/TO/freepik-mcp` with the actual path (run `pwd` in the repo directory) and `your_key` with your Freepik API key.

### Claude Code (CLI)

```bash
claude mcp add -e FREEPIK_API_KEY=your_key -s user freepik -- \
  uv run --directory /FULL/PATH/TO/freepik-mcp main.py
```

To toggle on/off (add to `~/.zshrc` or `~/.bashrc`):

```bash
alias freepik-on='claude mcp add -e FREEPIK_API_KEY=your_key -s user freepik -- uv run --directory /FULL/PATH/TO/freepik-mcp main.py'
alias freepik-off='claude mcp remove -s user freepik'
```

Restart your Claude Code session after toggling.

### Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows/WSL):

```json
{
  "mcpServers": {
    "freepik": {
      "command": "uv",
      "args": ["run", "--directory", "/FULL/PATH/TO/freepik-mcp", "main.py"],
      "env": { "FREEPIK_API_KEY": "your_key" }
    }
  }
}
```

### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "freepik": {
      "command": "uv",
      "args": ["run", "--directory", "/FULL/PATH/TO/freepik-mcp", "main.py"],
      "env": { "FREEPIK_API_KEY": "your_key" }
    }
  }
}
```

## Usage Examples

### Image Generation

Generate a photorealistic image:

```
Generate a cozy coffee shop with warm lighting, indoor view.
Use realism model, 2k resolution, widescreen_16_9 aspect ratio.
```

Generate for social media:

```
Create an Instagram Story image (social_story_9_16, fluid model):
minimalist gradient from purple to pink with cloud texture
```

Generate with style reference:

```
Generate an image in the style of the attached picture [attach file]:
urban cityscape at sunset
```

#### Mystic AI Parameters

| Parameter | Values | Notes |
|-----------|--------|-------|
| `model` | `realism`, `fluid`, `zen`, `flexible`, `super_real`, `editorial_portraits` | `realism` for photos, `zen` for clean/minimal, `fluid` for artistic |
| `resolution` | `1k`, `2k`, `4k` | Default to `2k` for good quality/speed balance |
| `aspect_ratio` | `square_1_1`, `classic_4_3`, `traditional_3_4`, `widescreen_16_9`, `social_story_9_16`, `portrait_2_3`, `standard_3_2`, `horizontal_2_1`, `vertical_1_2`, `social_5_4`, `social_post_4_5`, `smartphone_horizontal_20_9`, `smartphone_vertical_9_20` | Match to your use case |
| `engine` | `automatic`, `magnific_illusio`, `magnific_sharpy`, `magnific_sparkle` | `automatic` is recommended |
| `structure_reference` | Base64 image | Preserves composition from reference |
| `style_reference` | Base64 image | Transfers style from reference |
| `creative_detailing` | integer | Higher = more detail per pixel at high resolutions |
| `fixed_generation` | `true` / `false` | Same settings produce same result |
| `filter_nsfw` | `true` / `false` | NSFW content filter |

### Resource Search

Search for photos:

```
Find landscape photos of mountains in winter, premium only
```

Search for vectors:

```
Find vector illustrations about online education, portrait orientation
```

Search with filters:

```
Find blue abstract backgrounds added in the last month, AI-generated
```

Download a resource:

```
Download resource 30955 in maximum quality
```

#### Search Filters

| Filter | Values |
|--------|--------|
| `filters.orientation` | `landscape`, `portrait`, `square`, `panoramic` |
| `filters.content_type` | `photo`, `psd`, `vector`, `ai-generated` |
| `filters.license` | `free`, `premium` |
| `filters.color` | `black`, `blue`, `gray`, `green`, `orange`, `red`, `white`, `yellow`, `purple`, `cyan`, `pink` |
| `filters.period` | `last-month`, `last-quarter`, `last-semester`, `last-year` |
| `order` | `relevance`, `recent` |

### Icon Search

Search icons:

```
Find outline-style settings icons
```

Download in specific format:

```
Download icon 5563984 as SVG
Download icon 5563984 as PNG 256px
```

#### Icon Download Formats

| Format | Sizes | Best for |
|--------|-------|----------|
| SVG | vector | Web, scalable graphics |
| PNG | 16, 24, 32, 64, 128, 256, 512px | UI mockups, apps |
| EPS | vector | Print |
| GIF / MP4 | animated | Animated icons |
| JSON | Lottie | Web animations |
| PSD / AEP | layered | Editing in Photoshop/After Effects |

### AI Image Detection

```
Check if this image is AI-generated [attach file]
```

Returns a confidence score indicating the probability the image was created by AI.

## CLAUDE.md Snippet

Add this to your project's `CLAUDE.md` to get optimal behavior when Freepik MCP is enabled:

```markdown
## Freepik MCP (if enabled)

When the `freepik` MCP server is active, use it for image generation, resource/icon search, and AI detection.

### Image Generation (`text_to_image_mystic_sync`)
- Always set `aspect_ratio` to match context: `widescreen_16_9` (banners), `social_story_9_16` (stories), `square_1_1` (avatars/icons), `portrait_2_3` (cards)
- Choose `model` by style: `realism` (photos), `zen` (clean/minimal), `fluid` (artistic), `super_real` (hyper-real), `editorial_portraits` (people)
- Default `resolution` to `2k`. Use `4k` only when explicitly needed
- Prompts should be detailed and in English for best results — translate user's intent
- Generation takes 30-120s — warn the user before starting
- For reproducible results use `fixed_generation: true`
- If user provides a reference image, read it as base64 and pass via `structure_reference` (composition) or `style_reference` (style transfer)

### Resource Search (`search_resources`)
- Use English `term` for best results
- Apply `filters.content_type` (photo/vector/psd/ai-generated) and `filters.orientation` (landscape/portrait/square) to narrow results
- After search, show resource IDs and thumbnails, then download with `download_resource_by_id`

### Icon Search (`search_icons`)
- Search by `term`, download with `download_icon_by_id`
- Prefer SVG format for web, PNG 256px for UI mockups

### AI Detection (`detect_ai_image`)
- Accepts image file, returns AI-generation probability score
```

## Development

| Command | Description |
|---------|-------------|
| `make install` | Install dependencies |
| `make dev` | Development mode with auto-reload |
| `make run` | Production mode |
| `make lint` | Code quality check |
| `make format` | Auto-format code |
| `make clean` | Remove temp files |
| `make version` | Check FastMCP version |

## Token Optimization

This fork optimizes the OpenAPI specification before registering MCP tools:

- Strips response schemas (not needed for tool invocation)
- Truncates verbose parameter descriptions
- Removes examples and unused component schemas
- Removes disabled duplicate tools

Result: **9 tools at ~4K tokens** instead of the original ~26K.

## Security

- **Never commit your API key** — use `.env` files only
- The `.env` file is in `.gitignore`
- API key can also be passed via the `env` field in MCP config

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `command not found: uv` | Install uv: `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Invalid API key | Verify at [freepik.com/api](https://freepik.com/api) |
| Path not found | Run `pwd` in repo directory and use that full path |
| Connection refused | Ensure server is running (`make dev`) |
| High token usage warning | Make sure you're using this optimized fork |

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feat/my-feature`
3. Commit using [Conventional Commits](https://www.conventionalcommits.org/): `git commit -m "feat: add my feature"`
4. Push and open a Pull Request

## Links

- [Freepik API Documentation](https://freepik.com/api)
- [Original Repository](https://github.com/freepik-company/freepik-mcp)
- [MCP Protocol Spec](https://modelcontextprotocol.io)
