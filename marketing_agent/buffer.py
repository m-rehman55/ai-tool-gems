"""Duplicate-safe publishing to owned social channels through Buffer's official API."""

from __future__ import annotations

import json
import os
from io import BytesIO
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from typing import Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .catalog import Product
from .config import PROJECT_DIR, Settings
from .social import caption_for_platform, deal_of_the_day


API_URL = "https://api.buffer.com"
STATE_PATH = PROJECT_DIR / "marketing_agent" / "data" / "buffer-state.json"
CARD_DIR = PROJECT_DIR / "assets" / "social-deals"
RAW_MEDIA_ROOT = "https://raw.githubusercontent.com/m-rehman55/ai-tool-gems/main/assets/social-deals"
TARGET_SERVICES = ("instagram", "facebook", "tiktok")
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

    def create_image_post(
        self, channel_id: str, service: str, text: str, image_url: str, due_at: datetime, title: str
    ) -> dict:
        metadata_by_service = {
            "instagram": "metadata: { instagram: { type: post, shouldShareToFeed: true } }",
            "facebook": "metadata: { facebook: { type: post } }",
            "tiktok": f"metadata: {{ tiktok: {{ title: {json.dumps(title)} }} }}",
        }
        metadata = metadata_by_service.get(service, "")
        query = f"""
        mutation CreateDailyDeal {{
          createPost(input: {{
            text: {json.dumps(text, ensure_ascii=False)}
            channelId: {json.dumps(channel_id)}
            schedulingType: automatic
            mode: customScheduled
            dueAt: {json.dumps(due_at.isoformat().replace('+00:00', 'Z'))}
            assets: [{{ image: {{ url: {json.dumps(image_url)} }} }}]
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


def media_url_for(day: date) -> str:
    return f"{RAW_MEDIA_ROOT}/{deal_card_path(day).name}"


def scheduled_time(settings: Settings, day: date, now: datetime | None = None) -> datetime:
    target = datetime.combine(day, time(9, 0), settings.timezone).astimezone(timezone.utc)
    current = now or datetime.now(timezone.utc)
    if target <= current + timedelta(minutes=5):
        target = current + timedelta(minutes=10)
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
    due_at = scheduled_time(settings, day, now)
    image_url = media_url_for(day)
    results = {"scheduled": {}, "skipped": [], "errors": {}}
    for service in TARGET_SERVICES:
        if service in day_state:
            results["skipped"].append(service)
            continue
        channel = channels[service]
        caption = caption_for_platform(settings, day, service)
        try:
            post = client.create_image_post(channel["id"], service, caption, image_url, due_at, product.name)
            day_state[service] = {
                "post_id": post["id"],
                "channel_id": channel["id"],
                "scheduled_for": post.get("dueAt") or due_at.isoformat(),
                "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            results["scheduled"][service] = post["id"]
            _write_state(state_path, state)
        except BufferError as exc:
            results["errors"][service] = str(exc)
    if results["errors"]:
        raise BufferError(json.dumps(results, ensure_ascii=False))
    return results
