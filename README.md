# Reel to Recipe - Simple API

Extract recipes from Instagram Reels, TikToks, and other short-form cooking videos using AI vision.

## Quick Start (5 minutes)

### 1. Clone and Setup
```bash
git clone https://github.com/vixomaix/reel-to-recipe-simple.git
cd reel-to-recipe-simple
```

### 2. Set OpenAI API Key
```bash
export OPENAI_API_KEY="sk-..."
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

## API

### POST /extract

Extract recipe from a video URL.

**Headers:**
- `Authorization: Bearer demo-api-key` (default API key)

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

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | OpenAI API key |
| `API_KEY` | `demo-api-key` | API authentication key |
| `PORT` | `8000` | Server port |

## Supported Platforms

- Instagram Reels
- TikTok
- YouTube Shorts
- Twitter/X Videos
- Any video URL supported by yt-dlp

## License

MIT
