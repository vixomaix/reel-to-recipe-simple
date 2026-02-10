import os
import base64
import tempfile
import shutil
from pathlib import Path
from typing import List, Optional
from openai import OpenAI
import yt_dlp


class VideoExtractor:
    def __init__(self, api_key: str, provider: str = "openai"):
        """
        Initialize extractor with AI provider.
        
        Args:
            api_key: API key for the provider
            provider: "openai" or "kimi" (Moonshot AI)
        """
        self.provider = provider.lower()
        self.temp_dir = None
        
        if self.provider == "openai":
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4o"
        elif self.provider == "kimi":
            # Moonshot AI (Kimi) uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.moonshot.cn/v1"
            )
            self.model = "moonshot-v1-8k-vision-preview"
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'openai' or 'kimi'")

    def extract(self, url: str) -> dict:
        """Extract recipe from video URL."""
        self.temp_dir = tempfile.mkdtemp()
        try:
            video_path = self._download_video(url)
            frames = self._extract_frames(video_path)
            recipe = self._analyze_frames(frames)
            return recipe
        finally:
            self._cleanup()

    def _download_video(self, url: str) -> str:
        """Download video using yt-dlp."""
        output_path = Path(self.temp_dir) / "video.mp4"
        ydl_opts = {
            "format": "best[filesize<50M]",
            "outtmpl": str(output_path),
            "quiet": True,
            "no_warnings": True,
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            raise ValueError(f"Failed to download video: {str(e)}")
        
        if not output_path.exists():
            raise ValueError("Video download failed - no file created")
        
        return str(output_path)

    def _extract_frames(self, video_path: str, num_frames: int = 8) -> List[str]:
        """Extract frames using FFmpeg."""
        import subprocess
        
        # Get video duration
        probe_cmd = [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", video_path
        ]
        result = subprocess.run(probe_cmd, capture_output=True, text=True)
        duration = float(result.stdout.strip())
        
        # Extract frames at evenly spaced intervals
        frames = []
        for i in range(num_frames):
            timestamp = (duration / num_frames) * i + (duration / num_frames / 2)
            frame_path = Path(self.temp_dir) / f"frame_{i:03d}.jpg"
            
            cmd = [
                "ffmpeg", "-ss", str(timestamp), "-i", video_path,
                "-vframes", "1", "-q:v", "2", str(frame_path),
                "-y", "-loglevel", "error"
            ]
            subprocess.run(cmd, check=True)
            
            if frame_path.exists():
                frames.append(str(frame_path))
        
        if not frames:
            raise ValueError("Failed to extract any frames from video")
        
        return frames

    def _analyze_frames(self, frame_paths: List[str]) -> dict:
        """Send frames to AI Vision for recipe extraction."""
        # Encode frames to base64
        images = []
        for path in frame_paths:
            with open(path, "rb") as f:
                encoded = base64.b64encode(f.read()).decode("utf-8")
                images.append(f"data:image/jpeg;base64,{encoded}")
        
        # Build message content with images
        content = [
            {
                "type": "text",
                "text": (
                    "Analyze these frames from a cooking video and extract the recipe. "
                    "Return ONLY a JSON object with this structure:\n"
                    "{\n"
                    '  "title": "Recipe name",\n'
                    '  "description": "Brief description",\n'
                    '  "ingredients": ["ingredient 1", "ingredient 2"],\n'
                    '  "instructions": ["step 1", "step 2"],\n'
                    '  "prep_time": "e.g., 10 minutes",\n'
                    '  "cook_time": "e.g., 20 minutes",\n'
                    '  "servings": number,\n'
                    '  "tags": ["tag1", "tag2"]\n'
                    "}\n"
                    "If you cannot identify a cooking recipe, return an error field."
                )
            }
        ]
        
        # Add up to 4 frames (to save tokens)
        for img_url in images[:4]:
            content.append({
                "type": "image_url",
                "image_url": {"url": img_url}
            })
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": content}],
                max_tokens=2000,
                temperature=0.3
            )
            
            import json
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            if "```json" in result_text:
                result_text = result_text.split("```json")[1].split("```")[0]
            elif "```" in result_text:
                result_text = result_text.split("```")[1].split("```")[0]
            
            result = json.loads(result_text.strip())
            
            if "error" in result:
                raise ValueError(result["error"])
            
            return result
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse recipe: {str(e)}")
        except Exception as e:
            raise ValueError(f"AI analysis failed: {str(e)}")

    def _cleanup(self):
        """Remove temporary files."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir = None
