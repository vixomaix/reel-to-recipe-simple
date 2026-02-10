# Reel to Recipe - Simple API

Extract recipes from Instagram Reels, TikToks, and other short-form cooking videos using AI vision.

**Now supports OpenAI GPT-4o and Kimi (Moonshot AI)!**

## Quick Start (5 minutes)

### 1. Clone and Setup
```bash
git clone https://github.com/vixomaix/reel-to-recipe-simple.git
cd reel-to-recipe-simple
```

### 2. Set API Key

**Option A: OpenAI (Default)**
```bash
export OPENAI_API_KEY="sk-..."
export AI_PROVIDER="openai"
```

**Option B: Kimi (Moonshot AI)**
```bash
export KIMI_API_KEY="your-kimi-api-key"
export AI_PROVIDER="kimi"
```

### 3. Run with Docker
```bash
docker-compose up --build
```

### 4. Test It
```bash
curl -X POST http://localhost:8000/extract \
  -H "Authorization: Bearer demo-api-key" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://instagram.com/reel/..."}'
```

## AI Providers

### OpenAI GPT-4o (Default)
- Best overall performance
- Model: `gpt-4o`
- Fast and accurate recipe extraction

### Kimi / Moonshot AI
- Great for Chinese recipes
- Model: `moonshot-v1-8k-vision-preview`
- Get API key at: https://platform.moonshot.cn/

Switch between providers by setting `AI_PROVIDER` env variable.

## API

### POST /extract

Extract recipe from a video URL.

**Headers:**
- `Authorization: Bearer demo-api-key` (default API key)
- `Content-Type: application/json`

**Request:**
```json
{
  "url": "https://instagram.com/reel/ABC123"
}
```

**Response:**
```json
{
  "title": "Creamy Garlic Pasta",
  "description": "Quick 15-minute pasta recipe",
  "ingredients": ["200g pasta", "3 cloves garlic", "1/2 cup cream"],
  "instructions": ["Boil pasta", "Sauté garlic", "Mix with cream"],
  "prep_time": "5 minutes",
  "cook_time": "10 minutes",
  "servings": 2,
  "tags": ["pasta", "quick", "vegetarian"]
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "version": "1.1.0",
  "provider": "openai"
}
```

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `AI_PROVIDER` | `openai` | AI provider: `openai` or `kimi` |
| `OPENAI_API_KEY` | - | OpenAI API key (if using OpenAI) |
| `KIMI_API_KEY` | - | Kimi API key (if using Kimi) |
| `API_KEY` | `demo-api-key` | API authentication key |
| `PORT` | `8000` | Server port |

## Supported Platforms

- Instagram Reels
- TikTok
- YouTube Shorts
- Twitter/X Videos
- Facebook Videos
- Any video URL supported by yt-dlp

## Architecture

```
POST /extract
    │
    ├── Download video (yt-dlp)
    ├── Extract 8 frames (FFmpeg)
    ├── Send to AI Vision (4 frames)
    └── Return structured recipe
```

Single synchronous request, ~15-30 seconds response time.

## License

MIT
