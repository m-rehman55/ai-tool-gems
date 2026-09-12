"""Duplicate-safe publishing to owned social channels through Buffer's official API."""

from __future__ import annotations

import json
import math
import os
import shutil
import subprocess
import tempfile
import wave
from array import array
from io import BytesIO
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .catalog import Product
from .config import PROJECT_DIR, Settings
from .social import AudienceAngle, audience_candidates, audience_for, caption_for_platform, deal_of_the_day


API_URL = "https://api.buffer.com"
STATE_PATH = PROJECT_DIR / "marketing_agent" / "data" / "buffer-state.json"
CARD_DIR = PROJECT_DIR / "assets" / "social-deals"
RAW_MEDIA_ROOT = "https://raw.githubusercontent.com/m-rehman55/ai-tool-gems/main/assets/social-deals"
TARGET_SERVICES = ("instagram", "facebook", "tiktok")
VIDEO_SERVICES = ("instagram", "tiktok")
VIDEO_WEEKDAYS = (1, 3, 5)  # Tue, Thu, Sat: sustainable mix of Reels and static posts.
PRODUCT_DOMAINS = {
    "chatgpt": "chatgpt.com", "gemini": "gemini.google.com", "veo": "deepmind.google",
    "leonardo": "leonardo.ai", "elevenlabs": "elevenlabs.io", "canva": "canva.com",
    "figma": "figma.com", "capcut": "capcut.com", "adobe": "adobe.com",
    "lovable": "lovable.dev", "gamma": "gamma.app", "replit": "replit.com",
    "n8n": "n8n.io", "notion": "notion.so", "nordvpn": "nordvpn.com",
    "surfshark": "surfshark.com", "youtube": "youtube.com", "netflix": "netflix.com",
    "linkedin": "linkedin.com", "windows": "microsoft.com",
}


class BufferError(RuntimeError):
    """A safe, user-readable Buffer integration error."""


class BufferClient:
    def __init__(self, api_key: str, transport: Callable[[str], dict] | None = None):
        if not api_key:
            raise BufferError("BUFFER_API_KEY is missing")
        self.api_key = api_key
        self._transport = transport

    def graphql(self, query: str) -> dict:
        if self._transport:
            payload = self._transport(query)
        else:
            request = Request(
                API_URL,
                data=json.dumps({"query": query}).encode("utf-8"),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "AI-Tool-Gems-Marketing-Agent/1.0",
                },
                method="POST",
            )
            try:
                with urlopen(request, timeout=30) as response:
                    payload = json.loads(response.read().decode("utf-8"))
            except HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")
                raise BufferError(f"Buffer API HTTP {exc.code}: {detail[:300]}") from exc
            except (URLError, TimeoutError) as exc:
                raise BufferError(f"Buffer API connection failed: {exc}") from exc
        if payload.get("errors"):
            message = "; ".join(error.get("message", "Unknown GraphQL error") for error in payload["errors"])
            raise BufferError(message)
        return payload.get("data", {})

    def organizations(self) -> list[dict]:
        data = self.graphql("query AccountOrganizations { account { organizations { id name } } }")
        return data.get("account", {}).get("organizations", [])

    def channels(self, organization_id: str) -> list[dict]:
        organization = json.dumps(organization_id)
        data = self.graphql(
            "query OwnedChannels { channels(input: { organizationId: " + organization + " }) "
            "{ id name displayName service isQueuePaused } }"
        )
        return data.get("channels", [])

    def owned_channels(self) -> dict[str, dict]:
        discovered: dict[str, list[dict]] = {service: [] for service in TARGET_SERVICES}
        organizations = self.organizations()
        if not organizations:
            raise BufferError("No Buffer organization was found for this API key")
        for organization in organizations:
            for channel in self.channels(organization["id"]):
                service = str(channel.get("service", "")).lower()
                if service in discovered:
                    discovered[service].append(channel)
        selected: dict[str, dict] = {}
        for service, choices in discovered.items():
            override = os.getenv(f"BUFFER_{service.upper()}_CHANNEL_ID", "").strip()
            if override:
                choices = [channel for channel in choices if channel.get("id") == override]
            if not choices:
                raise BufferError(f"No connected {service} channel was found in Buffer")
            if len(choices) > 1:
                names = ", ".join(channel.get("displayName") or channel.get("name") or channel["id"] for channel in choices)
                raise BufferError(
                    f"Multiple {service} channels found ({names}). Set BUFFER_{service.upper()}_CHANNEL_ID."
                )
            selected[service] = choices[0]
        return selected

    def post_metrics(self, post_id: str) -> dict:
        """Read delivery status and normalized metrics for one owned post."""
        query = f"""
        query DailyPostMetrics {{
          post(input: {{ id: {json.dumps(post_id)} }}) {{
            id
            status
            metrics {{ type name value unit }}
            metricsUpdatedAt
          }}
        }}
        """
        return self.graphql(query).get("post", {})

    def create_image_post(
        self, channel_id: str, service: str, text: str, image_url: str, due_at: datetime, title: str
    ) -> dict:
        return self.create_media_post(channel_id, service, text, image_url, due_at, title, "image")

    def create_video_post(
        self, channel_id: str, service: str, text: str, video_url: str, due_at: datetime, title: str
    ) -> dict:
        return self.create_media_post(channel_id, service, text, video_url, due_at, title, "video")

    def create_media_post(
        self,
        channel_id: str,
        service: str,
        text: str,
        media_url: str,
        due_at: datetime,
        title: str,
        media_type: str,
    ) -> dict:
        if media_type not in {"image", "video"}:
            raise BufferError(f"Unsupported media type: {media_type}")
        metadata_by_service = {
            "instagram": (
                "metadata: { instagram: { type: reel, shouldShareToFeed: true } }"
                if media_type == "video"
                else "metadata: { instagram: { type: post, shouldShareToFeed: true } }"
            ),
            "facebook": (
                "metadata: { facebook: { type: reel } }"
                if media_type == "video"
                else "metadata: { facebook: { type: post } }"
            ),
            "tiktok": (
                "metadata: { tiktok: { isAiGenerated: false } }"
                if media_type == "video"
                else f"metadata: {{ tiktok: {{ title: {json.dumps(title)} }} }}"
            ),
        }
        metadata = metadata_by_service.get(service, "")
        asset = f"{{ {media_type}: {{ url: {json.dumps(media_url)} }} }}"
        query = f"""
        mutation CreateDailyDeal {{
          createPost(input: {{
            text: {json.dumps(text, ensure_ascii=False)}
            channelId: {json.dumps(channel_id)}
            schedulingType: automatic
            mode: customScheduled
            dueAt: {json.dumps(due_at.isoformat().replace('+00:00', 'Z'))}
            assets: [{asset}]
            {metadata}
          }}) {{
            ... on PostActionSuccess {{ post {{ id text dueAt channelId }} }}
            ... on MutationError {{ message }}
          }}
        }}
        """
        data = self.graphql(query)
        result = data.get("createPost", {})
        if result.get("message"):
            raise BufferError(f"{service}: {result['message']}")
        post = result.get("post")
        if not post:
            raise BufferError(f"{service}: Buffer returned no post after scheduling")
        return post


def _font(size: int, bold: bool = False):
    from PIL import ImageFont

    filename = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    candidates = [
        Path("/usr/share/fonts/truetype/dejavu") / filename,
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / ("arialbd.ttf" if bold else "arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size=size)
    return ImageFont.load_default(size=size)


def _wrapped_lines(draw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        proposed = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), proposed, font=font)[2] > max_width:
            lines.append(current)
            current = word
        else:
            current = proposed
    if current:
        lines.append(current)
    return lines


def deal_card_path(day: date, product: Product | None = None) -> Path:
    product = product or deal_of_the_day(day)
    return CARD_DIR / f"{day.isoformat()}-{product.id}.jpg"


def deal_video_path(day: date, product: Product | None = None) -> Path:
    product = product or deal_of_the_day(day)
    return CARD_DIR / f"{day.isoformat()}-{product.id}.mp4"


def is_video_day(day: date) -> bool:
    return day.weekday() in VIDEO_WEEKDAYS


def render_deal_card(day: date, output: Path | None = None) -> Path:
    """Create a platform-safe 4:5 deal card from verified catalog data."""
    from PIL import Image, ImageDraw, ImageOps

    product = deal_of_the_day(day)
    output = output or deal_card_path(day, product)
    output.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1080, 1350
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y in range(height):
        mix = y / (height - 1)
        start, end = (243, 255, 248), (235, 246, 255)
        colour = tuple(round(start[i] * (1 - mix) + end[i] * mix) for i in range(3))
        for x in range(width):
            pixels[x, y] = colour
    draw = ImageDraw.Draw(image)
    ink = (18, 64, 57)
    muted = (78, 112, 106)
    green = (73, 196, 121)
    lime = (166, 232, 84)
    white = (255, 255, 255)

    draw.rounded_rectangle((60, 55, 1020, 215), radius=42, fill=white, outline=(206, 230, 220), width=3)
    logo_path = PROJECT_DIR / "assets" / "brand-logo-light.png"
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((125, 125))
    logo_box = Image.new("RGBA", (130, 130), (255, 255, 255, 0))
    logo_box.alpha_composite(logo, ((130 - logo.width) // 2, (130 - logo.height) // 2))
    image.paste(logo_box, (78, 70), logo_box)
    draw.text((230, 88), "AI TOOL GEMS", font=_font(42, True), fill=ink)
    draw.text((232, 143), "PAKISTAN", font=_font(22, True), fill=green)
    draw.rounded_rectangle((755, 100, 980, 168), radius=34, fill=(229, 255, 207))
    draw.text((793, 119), "DAILY DEAL", font=_font(25, True), fill=ink)

    draw.rounded_rectangle((60, 255, 1020, 1125), radius=58, fill=white, outline=(211, 229, 222), width=3)
    draw.ellipse((742, 285, 968, 511), fill=(229, 252, 241))
    draw.rounded_rectangle((785, 328, 925, 468), radius=35, fill=white, outline=(204, 230, 218), width=3)
    try:
        domain = PRODUCT_DOMAINS[product.id]
        logo_request = Request(
            f"https://www.google.com/s2/favicons?domain={domain}&sz=256",
            headers={"User-Agent": "AI-Tool-Gems-Marketing-Agent/1.0"},
        )
        with urlopen(logo_request, timeout=12) as logo_response:
            product_logo = Image.open(BytesIO(logo_response.read())).convert("RGBA")
        product_logo.thumbnail((104, 104))
        logo_position = (855 - product_logo.width // 2, 398 - product_logo.height // 2)
        image.paste(product_logo, logo_position, product_logo)
    except Exception:
        initials = "".join(word[0] for word in product.name.split()[:2]).upper()
        initials_box = draw.textbbox((0, 0), initials, font=_font(42, True))
        draw.text((855 - (initials_box[2] - initials_box[0]) / 2, 372), initials, font=_font(42, True), fill=ink)
    draw.text((100, 315), product.category.upper(), font=_font(25, True), fill=green)
    name_font = _font(66, True)
    name_lines = _wrapped_lines(draw, product.name, name_font, 790)
    y = 365
    for line in name_lines[:3]:
        draw.text((100, y), line, font=name_font, fill=ink)
        y += 82
    y = max(y + 25, 575)
    draw.text((100, y), "TODAY'S LISTED PRICE", font=_font(23, True), fill=muted)
    draw.text((100, y + 42), f"Rs. {product.price:,}", font=_font(92, True), fill=ink)
    draw.text((640, y + 82), f"was Rs. {product.old_price:,}", font=_font(28), fill=muted)
    draw.line((637, y + 102, 895, y + 102), fill=(216, 91, 91), width=5)
    if product.saving:
        draw.rounded_rectangle((635, y + 122, 915, y + 168), radius=23, fill=(229, 255, 207))
        draw.text(
            (665, y + 131),
            f"SAVE Rs. {product.saving:,} • {product.discount_percent}%",
            font=_font(21, True),
            fill=ink,
        )

    pills = [product.duration, f"{product.access} access", f"Delivery {product.delivery}"]
    pill_y = y + 190
    for index, label in enumerate(pills):
        top = pill_y + index * 78
        draw.rounded_rectangle((100, top, 865, top + 58), radius=29, fill=(241, 249, 245))
        draw.ellipse((122, top + 18, 144, top + 40), fill=green)
        draw.text((165, top + 13), label, font=_font(28, index == 0), fill=ink)

    cta_top = 995
    draw.rounded_rectangle((100, cta_top, 980, cta_top + 92), radius=44, fill=lime)
    cta = "ORDER ON WHATSAPP  +92 347 6242709"
    cta_box = draw.textbbox((0, 0), cta, font=_font(30, True))
    draw.text(((width - (cta_box[2] - cta_box[0])) / 2, cta_top + 27), cta, font=_font(30, True), fill=ink)

    draw.text((72, 1175), "Check current availability and exact terms before payment.", font=_font(25), fill=muted)
    draw.text((72, 1220), "aitoolgems.tech", font=_font(34, True), fill=ink)
    draw.text((72, 1280), "Independent reseller. Brand names belong to their owners.", font=_font(20), fill=muted)
    ImageOps.exif_transpose(image).save(output, format="JPEG", quality=91, optimize=True, progressive=True)
    return output


def _ffmpeg_executable() -> str | None:
    executable = shutil.which("ffmpeg")
    if executable:
        return executable
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except (ImportError, RuntimeError):
        return None


def audio_theme_for(audience: AudienceAngle) -> str:
    if audience.id in {"creators", "entertainment"}:
        return "creator-pulse"
    if audience.id in {"students", "developers"}:
        return "focus-tech"
    return "clean-business"


def _write_original_audio(
    path: Path,
    theme: str = "focus-tech",
    seconds: int = 8,
    sample_rate: int = 44_100,
) -> None:
    """Create a short original brand jingle without copyrighted or platform-library audio."""
    themes = {
        "focus-tech": ((261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 293.66, 392.00), 0.13, 92),
        "creator-pulse": ((329.63, 392.00, 493.88, 659.25, 493.88, 587.33, 523.25, 659.25), 0.15, 110),
        "clean-business": ((220.00, 277.18, 329.63, 440.00, 329.63, 369.99, 277.18, 329.63), 0.11, 78),
    }
    notes, volume, bass_note = themes.get(theme, themes["focus-tech"])
    samples = array("h")
    total = seconds * sample_rate
    for index in range(total):
        elapsed = index / sample_rate
        note = notes[min(int(elapsed), len(notes) - 1)]
        within_beat = elapsed % 1.0
        envelope = min(1.0, within_beat / 0.04) * max(0.0, 1.0 - within_beat * 0.72)
        chord = math.sin(2 * math.pi * note * elapsed)
        harmony = 0.42 * math.sin(2 * math.pi * note * 1.5 * elapsed)
        pulse = 0.24 * math.sin(2 * math.pi * bass_note * elapsed) * max(0.0, 1 - within_beat * 5)
        sparkle = 0.10 * math.sin(2 * math.pi * note * 2 * elapsed) * max(0.0, 1 - within_beat * 3)
        value = int(32767 * volume * envelope * (chord + harmony + pulse + sparkle))
        samples.append(max(-32768, min(32767, value)))
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(samples.tobytes())


def render_deal_video(day: date, output: Path | None = None) -> Path | None:
    """Render an 8-second 9:16 Reel/TikTok creative with original audio."""
    from PIL import Image, ImageDraw

    executable = _ffmpeg_executable()
    if not executable:
        return None
    product = deal_of_the_day(day)
    audience = audience_for(product, day)
    output = output or deal_video_path(day, product)
    output.parent.mkdir(parents=True, exist_ok=True)
    card = Image.open(render_deal_card(day)).convert("RGB")

    width, height = 720, 1280
    frame = Image.new("RGB", (width, height))
    pixels = frame.load()
    for y in range(height):
        mix = y / (height - 1)
        start, end = (239, 255, 246), (232, 244, 255)
        colour = tuple(round(start[i] * (1 - mix) + end[i] * mix) for i in range(3))
        for x in range(width):
            pixels[x, y] = colour
    draw = ImageDraw.Draw(frame)
    ink, muted, green, lime = (18, 64, 57), (78, 112, 106), (73, 196, 121), (166, 232, 84)
    draw.text((38, 35), "PAKISTAN'S AI TOOL DEAL", font=_font(34, True), fill=ink)
    audience_label = audience.label.upper()
    draw.text((40, 84), audience_label[:48], font=_font(18, True), fill=green)
    card.thumbnail((660, 825))
    frame.paste(card, ((width - card.width) // 2, 130))
    draw.rounded_rectangle((36, 990, 684, 1128), radius=42, fill=lime)
    price = f"PRICE  Rs. {product.price:,}"
    price_box = draw.textbbox((0, 0), price, font=_font(49, True))
    draw.text(((width - price_box[2]) / 2, 1012), price, font=_font(49, True), fill=ink)
    draw.text((130, 1074), "VIEW DETAILS • ORDER ON WHATSAPP", font=_font(22, True), fill=ink)
    draw.text((189, 1160), "aitoolgems.tech", font=_font(32, True), fill=ink)
    draw.text((74, 1218), "Promotional listing • Independent reseller", font=_font(18), fill=muted)

    with tempfile.TemporaryDirectory(prefix="atg-video-") as temporary:
        temporary_dir = Path(temporary)
        frame_path = temporary_dir / "frame.png"
        audio_path = temporary_dir / "original-brand-audio.wav"
        frame.save(frame_path, format="PNG", optimize=True)
        _write_original_audio(audio_path, audio_theme_for(audience))
        command = [
            executable,
            "-y",
            "-loop", "1",
            "-i", str(frame_path),
            "-i", str(audio_path),
            "-t", "8",
            "-vf", "zoompan=z='min(zoom+0.00015,1.03)':d=200:s=720x1280:fps=25,fade=t=in:st=0:d=0.25,fade=t=out:st=7.5:d=0.5",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "29",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "96k",
            "-movflags", "+faststart",
            "-shortest",
            str(output),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=120)
        if completed.returncode != 0:
            output.unlink(missing_ok=True)
            raise BufferError(f"Video render failed: {completed.stderr[-500:]}")
    return output


def render_daily_media(day: date) -> list[Path]:
    assets = [render_deal_card(day)]
    if is_video_day(day):
        video = render_deal_video(day)
        if video:
            assets.append(video)
    return assets


def media_url_for(day: date, service: str = "facebook") -> tuple[str, str]:
    video = deal_video_path(day)
    if service in VIDEO_SERVICES and is_video_day(day) and video.exists():
        return f"{RAW_MEDIA_ROOT}/{video.name}", "video"
    card = deal_card_path(day)
    return f"{RAW_MEDIA_ROOT}/{card.name}", "image"


def scheduled_time(
    settings: Settings,
    day: date,
    now: datetime | None = None,
    service: str = "instagram",
    audience: AudienceAngle | None = None,
) -> datetime:
    """Schedule in a relevant Pakistan window and stagger networks to avoid burst-like behavior."""
    product = deal_of_the_day(day)
    audience = audience or audience_for(product, day)
    offsets = {"facebook": -30, "instagram": 0, "tiktok": 30}
    local_target = datetime.combine(day, audience.pakistan_time, settings.timezone)
    target = (local_target + timedelta(minutes=offsets.get(service, 0))).astimezone(timezone.utc)
    current = now or datetime.now(timezone.utc)
    if target <= current + timedelta(minutes=5):
        fallback_offsets = {"facebook": 10, "instagram": 14, "tiktok": 18}
        target = current + timedelta(minutes=fallback_offsets.get(service, 10))
    return target.replace(microsecond=0)


def _read_state(path: Path) -> dict:
    if not path.exists():
        return {"published_dates": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def _write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def connection_status(settings: Settings, client: BufferClient | None = None) -> dict:
    client = client or BufferClient(settings.buffer_api_key)
    channels = client.owned_channels()
    return {
        "connected": True,
        "channels": {
            service: {
                "id": channel["id"],
                "name": channel.get("displayName") or channel.get("name"),
                "queue_paused": bool(channel.get("isQueuePaused")),
            }
            for service, channel in channels.items()
        },
    }


def _metric_value(metrics: dict, *names: str) -> float:
    normalized = {str(key).lower(): value for key, value in metrics.items()}
    for name in names:
        try:
            return float(normalized.get(name.lower(), 0) or 0)
        except (TypeError, ValueError):
            continue
    return 0.0


def _engagement_score(metrics: dict) -> float:
    """Normalize meaningful interactions while giving buying signals extra weight."""
    reactions = _metric_value(metrics, "reactions", "likes")
    comments = _metric_value(metrics, "comments")
    shares = _metric_value(metrics, "shares", "reposts")
    saves = _metric_value(metrics, "saves")
    clicks = _metric_value(metrics, "clicks", "linkClicks")
    views = _metric_value(metrics, "impressions", "reach", "views", "videoViews")
    weighted = reactions + comments * 4 + shares * 5 + saves * 4 + clicks * 6
    return round((weighted / views * 1000) if views > 0 else weighted, 4)


def learned_audience_for(product: Product, day: date, state: dict) -> tuple[AudienceAngle, str]:
    """Apply a winner only after every eligible angle has enough real observations."""
    default = audience_for(product, day)
    candidates = audience_candidates(product)
    if len(candidates) == 1:
        return default, "single-relevant-audience"
    scores: dict[str, list[float]] = {candidate.id: [] for candidate in candidates}
    for services in state.get("published_dates", {}).values():
        for record in services.values():
            audience_id = record.get("audience")
            metrics = record.get("metrics")
            if audience_id in scores and isinstance(metrics, dict) and metrics:
                scores[audience_id].append(_engagement_score(metrics))
    if not scores or any(len(values) < 2 for values in scores.values()):
        return default, "exploration"
    averages = {key: sum(values) / len(values) for key, values in scores.items()}
    winner = max(candidates, key=lambda candidate: averages[candidate.id])
    return winner, "metrics-winner"


def publish_daily_deal(
    settings: Settings,
    day: date,
    state_path: Path = STATE_PATH,
    client: BufferClient | None = None,
    now: datetime | None = None,
) -> dict:
    client = client or BufferClient(settings.buffer_api_key)
    channels = client.owned_channels()
    state = _read_state(state_path)
    day_state = state.setdefault("published_dates", {}).setdefault(day.isoformat(), {})
    product = deal_of_the_day(day)
    audience, learning_mode = learned_audience_for(product, day, state)
    results = {
        "date": day.isoformat(),
        "product": product.name,
        "audience": audience.label,
        "learning_mode": learning_mode,
        "scheduled": {},
        "skipped": [],
        "errors": {},
    }
    for service in TARGET_SERVICES:
        if service in day_state:
            results["skipped"].append(service)
            continue
        channel = channels[service]
        caption = caption_for_platform(settings, day, service, audience)
        due_at = scheduled_time(settings, day, now, service, audience)
        media_url, media_type = media_url_for(day, service)
        try:
            if media_type == "video":
                post = client.create_video_post(
                    channel["id"], service, caption, media_url, due_at, product.name
                )
            else:
                post = client.create_image_post(
                    channel["id"], service, caption, media_url, due_at, product.name
                )
            day_state[service] = {
                "post_id": post["id"],
                "channel_id": channel["id"],
                "scheduled_for": post.get("dueAt") or due_at.isoformat(),
                "audience": audience.id,
                "learning_mode": learning_mode,
                "media_type": media_type,
                "audio_theme": audio_theme_for(audience) if media_type == "video" else None,
                "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            results["scheduled"][service] = post["id"]
            _write_state(state_path, state)
        except BufferError as exc:
            results["errors"][service] = str(exc)
    if results["errors"]:
        raise BufferError(json.dumps(results, ensure_ascii=False))
    return results


def format_publish_confirmation(
    settings: Settings,
    day: date,
    result: dict,
    state_path: Path = STATE_PATH,
) -> str:
    """Create a concise owner-safe Telegram receipt only when new posts were scheduled."""
    if not result.get("scheduled"):
        return ""
    day_state = _read_state(state_path).get("published_dates", {}).get(day.isoformat(), {})
    lines = [
        "✅ Daily social campaign scheduled",
        "",
        f"Product: {result.get('product', deal_of_the_day(day).name)}",
        f"Audience: {result.get('audience', 'relevant Pakistan buyers')}",
        f"Learning: {result.get('learning_mode', 'exploration')}",
        "",
    ]
    labels = {"facebook": "Facebook", "instagram": "Instagram", "tiktok": "TikTok"}
    for service in TARGET_SERVICES:
        if service not in result["scheduled"]:
            continue
        record = day_state.get(service, {})
        scheduled = record.get("scheduled_for", "")
        try:
            local_time = datetime.fromisoformat(scheduled.replace("Z", "+00:00")).astimezone(settings.timezone)
            time_label = local_time.strftime("%I:%M %p PKT")
        except (TypeError, ValueError):
            time_label = "scheduled"
        media = str(record.get("media_type", "post")).title()
        audio = record.get("audio_theme")
        extra = f" • audio: {audio}" if audio else ""
        lines.append(f"• {labels[service]}: {media} • {time_label}{extra}")
    lines.extend([
        "",
        "Tracked product links and duplicate protection are active.",
        "You do not need to post manually.",
    ])
    return "\n".join(lines)


def refresh_performance(
    settings: Settings,
    state_path: Path = STATE_PATH,
    client: BufferClient | None = None,
    now: datetime | None = None,
) -> dict:
    """Refresh real post results without allowing analytics failures to stop future posts."""
    client = client or BufferClient(settings.buffer_api_key)
    state = _read_state(state_path)
    current = now or datetime.now(timezone.utc)
    checked, updated, errors = 0, 0, {}
    for day_key, services in state.get("published_dates", {}).items():
        for service, record in services.items():
            scheduled = record.get("scheduled_for", "")
            try:
                due_at = datetime.fromisoformat(scheduled.replace("Z", "+00:00"))
            except (TypeError, ValueError):
                continue
            if due_at > current - timedelta(hours=6):
                continue
            if record.get("metrics_checked_on") == current.date().isoformat():
                continue
            checked += 1
            try:
                snapshot = client.post_metrics(record["post_id"])
                metrics = {
                    metric.get("type", metric.get("name", "unknown")): metric.get("value", 0)
                    for metric in snapshot.get("metrics", [])
                }
                record.update({
                    "delivery_status": snapshot.get("status", "unknown"),
                    "metrics": metrics,
                    "metrics_updated_at": snapshot.get("metricsUpdatedAt"),
                    "metrics_checked_on": current.date().isoformat(),
                })
                record.pop("metrics_error", None)
                updated += 1
            except BufferError as exc:
                record["metrics_error"] = str(exc)[:300]
                record["metrics_checked_on"] = current.date().isoformat()
                errors[f"{day_key}:{service}"] = str(exc)
    _write_state(state_path, state)
    return {"checked": checked, "updated": updated, "errors": errors}
