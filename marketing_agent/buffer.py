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
from .social import (
    AudienceAngle,
    SOCIAL_SLOTS,
    audience_candidates,
    audience_for,
    caption_for_platform,
    deal_of_the_day,
    deals_for_slot,
)


API_URL = "https://api.buffer.com"
STATE_PATH = PROJECT_DIR / "marketing_agent" / "data" / "buffer-state.json"
CARD_DIR = PROJECT_DIR / "assets" / "social-deals"
PRODUCT_LOGO_DIR = PROJECT_DIR / "assets" / "product-logos"
REALISTIC_BACKGROUND = PROJECT_DIR / "assets" / "social-realistic-workspace-v1.png"
RAW_MEDIA_ROOT = "https://raw.githubusercontent.com/m-rehman55/ai-tool-gems/main/assets/social-deals"
TARGET_SERVICES = ("instagram", "facebook", "tiktok")
MEDIA_BY_SLOT = {"morning": "image", "evening": "video"}
VIDEO_SECONDS = 10
VIDEO_SPECS = {
    "tiktok": {"seconds": 10, "fps": 24, "cut": "fast"},
    "instagram": {"seconds": 12, "fps": 24, "cut": "polished"},
    "facebook": {"seconds": 14, "fps": 24, "cut": "clear"},
}
CREATIVE_CONCEPTS = (
    "orbit-drop",
    "creator-portal",
    "neon-price-radar",
    "glass-card-rush",
    "three-gem-reveal",
    "smart-stack",
    "deal-countdown",
)
PLATFORM_AUDIO_STYLES = {
    "tiktok": ("desi-pop-pulse", "future-bass-hook", "cinematic-trap"),
    "instagram": ("creator-pop", "glossy-house", "desi-electro"),
    "facebook": ("uplifting-desi", "clean-cinematic", "modern-business"),
}
PRODUCT_DOMAINS = {
    "chatgpt": "chatgpt.com", "gemini": "gemini.google.com", "veo": "deepmind.google",
    "leonardo": "leonardo.ai", "elevenlabs": "elevenlabs.io", "canva": "canva.com",
    "figma": "figma.com", "capcut": "capcut.com", "adobe": "adobe.com",
    "lovable": "lovable.dev", "gamma": "gamma.app", "replit": "replit.com",
    "n8n": "n8n.io", "notion": "notion.so", "nordvpn": "nordvpn.com",
    "surfshark": "surfshark.com", "youtube": "youtube.com", "netflix": "netflix.com",
    "linkedin": "linkedin.com", "windows": "microsoft.com",
}

CREATIVE_PALETTES = (
    {
        "gradient": ((247, 252, 255), (239, 247, 255)),
        "ink": (17, 50, 91), "muted": (76, 102, 132),
        "primary": (21, 93, 222), "cta": (255, 213, 48),
        "rows": ((241, 248, 255), (241, 255, 248), (255, 246, 248)),
        "accents": ((21, 93, 222), (20, 176, 105), (238, 66, 84)),
    },
    {
        "gradient": ((246, 255, 250), (255, 247, 241)),
        "ink": (17, 69, 57), "muted": (76, 111, 101),
        "primary": (16, 164, 115), "cta": (255, 190, 92),
        "rows": ((239, 255, 247), (244, 249, 255), (255, 244, 238)),
        "accents": ((16, 164, 115), (64, 133, 231), (239, 111, 73)),
    },
    {
        "gradient": ((252, 248, 255), (244, 250, 255)),
        "ink": (54, 37, 91), "muted": (100, 84, 126),
        "primary": (124, 79, 214), "cta": (255, 205, 78),
        "rows": ((249, 243, 255), (240, 250, 255), (255, 247, 236)),
        "accents": ((124, 79, 214), (30, 154, 205), (236, 139, 42)),
    },
    {
        "gradient": ((242, 255, 255), (246, 250, 255)),
        "ink": (12, 64, 74), "muted": (70, 108, 115),
        "primary": (0, 160, 189), "cta": (174, 235, 78),
        "rows": ((236, 253, 255), (243, 248, 255), (249, 243, 255)),
        "accents": ((0, 160, 189), (61, 112, 226), (148, 91, 208)),
    },
)


def _creative_palette(day: date, slot: str) -> dict:
    return CREATIVE_PALETTES[(day.toordinal() * 2 + SOCIAL_SLOTS.index(slot)) % len(CREATIVE_PALETTES)]


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

    def post_status(self, post_id: str) -> dict:
        """Read delivery state without requiring Buffer's optional insights scope."""
        query = f"""
        query DailyPostStatus {{
          post(input: {{ id: {json.dumps(post_id)} }}) {{
            id
            status
            dueAt
            channelId
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
        metadata = self._metadata_for(service, media_type, title)
        asset = f"{{ {media_type}: {{ url: {json.dumps(media_url)} }} }}"
        query = f"""
        mutation CreateDailyDeal {{
          createPost(input: {{
            text: {json.dumps(text, ensure_ascii=False)}
            channelId: {json.dumps(channel_id)}
            schedulingType: automatic
            mode: customScheduled
            aiAssisted: true
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

    @staticmethod
    def _metadata_for(service: str, media_type: str, title: str) -> str:
        metadata_by_service = {
            "instagram": (
                "metadata: { instagram: { type: reel, shouldShareToFeed: true, isAiGenerated: true } }"
                if media_type == "video"
                else "metadata: { instagram: { type: post, shouldShareToFeed: true } }"
            ),
            "facebook": (
                "metadata: { facebook: { type: reel } }"
                if media_type == "video"
                else "metadata: { facebook: { type: post } }"
            ),
            "tiktok": (
                "metadata: { tiktok: { isAiGenerated: true } }"
                if media_type == "video"
                else f"metadata: {{ tiktok: {{ title: {json.dumps(title)} }} }}"
            ),
        }
        return metadata_by_service.get(service, "")

    def edit_media_post(
        self,
        post_id: str,
        service: str,
        text: str,
        media_url: str,
        title: str,
        media_type: str,
    ) -> dict:
        """Replace a still-scheduled post in place so repairs never create duplicates."""
        if media_type not in {"image", "video"}:
            raise BufferError(f"Unsupported media type: {media_type}")
        metadata = self._metadata_for(service, media_type, title)
        asset = f"{{ {media_type}: {{ url: {json.dumps(media_url)} }} }}"
        query = f"""
        mutation RepairScheduledPost {{
          editPost(input: {{
            id: {json.dumps(post_id)}
            text: {json.dumps(text, ensure_ascii=False)}
            aiAssisted: true
            assets: [{asset}]
            {metadata}
          }}) {{
            ... on PostActionSuccess {{ post {{ id text dueAt channelId }} }}
            ... on MutationError {{ message }}
          }}
        }}
        """
        data = self.graphql(query)
        result = data.get("editPost", {})
        if result.get("message"):
            raise BufferError(f"{service}: {result['message']}")
        post = result.get("post")
        if not post:
            raise BufferError(f"{service}: Buffer returned no post after repair")
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


def _product_logo(product: Product, max_size: int = 92):
    """Load a locally cached official-site favicon, fetching it once when needed."""
    from PIL import Image

    PRODUCT_LOGO_DIR.mkdir(parents=True, exist_ok=True)
    cached = PRODUCT_LOGO_DIR / f"{product.id}.png"
    if cached.exists():
        logo = Image.open(cached).convert("RGBA")
    else:
        request = Request(
            f"https://www.google.com/s2/favicons?domain={PRODUCT_DOMAINS[product.id]}&sz=256",
            headers={"User-Agent": "AI-Tool-Gems-Marketing-Agent/2.0"},
        )
        with urlopen(request, timeout=20) as response:
            logo = Image.open(BytesIO(response.read())).convert("RGBA")
        logo.save(cached, format="PNG", optimize=True)
    logo.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    return logo


def deal_card_path(day: date, product: Product | None = None, slot: str = "morning") -> Path:
    product = product or deal_of_the_day(day)
    return CARD_DIR / f"{day.isoformat()}-{slot}-{product.id}.jpg"


def deal_video_path(
    day: date,
    product: Product | None = None,
    slot: str = "morning",
    service: str | None = None,
) -> Path:
    product = product or deal_of_the_day(day)
    suffix = f"-{service}" if service else ""
    return CARD_DIR / f"{day.isoformat()}-{slot}-{product.id}{suffix}.mp4"


def creative_concept_for(day: date, slot: str = "evening") -> str:
    """Rotate the visual story daily while keeping the core brand recognizable."""
    return CREATIVE_CONCEPTS[(day.toordinal() + SOCIAL_SLOTS.index(slot)) % len(CREATIVE_CONCEPTS)]


def platform_audio_style(day: date, service: str) -> str:
    """Choose a platform-shaped original music style; never copy a protected melody."""
    styles = PLATFORM_AUDIO_STYLES.get(service)
    if not styles:
        raise ValueError(f"Unsupported social service: {service}")
    return styles[(day.toordinal() + TARGET_SERVICES.index(service)) % len(styles)]


def is_video_day(day: date) -> bool:
    """Backwards-compatible helper: every day includes one evening video."""
    return True


def media_type_for_slot(slot: str) -> str:
    """Keep the daily cadence predictable: morning photo, evening Reel/video."""
    try:
        return MEDIA_BY_SLOT[slot]
    except KeyError as exc:
        raise ValueError(f"Unsupported social slot: {slot}") from exc


def _render_single_deal_card_legacy(day: date, output: Path | None = None) -> Path:
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
    cta = "ORDER ON WHATSAPP  +92 323 6715731"
    cta_box = draw.textbbox((0, 0), cta, font=_font(30, True))
    draw.text(((width - (cta_box[2] - cta_box[0])) / 2, cta_top + 27), cta, font=_font(30, True), fill=ink)

    draw.text((72, 1175), "Check current availability and exact terms before payment.", font=_font(25), fill=muted)
    draw.text((72, 1220), "aitoolgems.tech", font=_font(34, True), fill=ink)
    draw.text((72, 1280), "Independent reseller. Brand names belong to their owners.", font=_font(20), fill=muted)
    ImageOps.exif_transpose(image).save(output, format="JPEG", quality=91, optimize=True, progressive=True)
    return output


def render_deal_card(day: date, output: Path | None = None, slot: str = "morning") -> Path:
    """Create a clean 4:5 card with Gemini plus two rotating catalog deals."""
    from PIL import Image, ImageDraw, ImageOps

    products = deals_for_slot(day, slot)
    focus = products[1]
    output = output or deal_card_path(day, focus, slot)
    output.parent.mkdir(parents=True, exist_ok=True)
    width, height = 1080, 1350
    palette = _creative_palette(day, slot)
    layout_variant = day.toordinal() % 3
    concept = creative_concept_for(day, slot)
    image = Image.new("RGB", (width, height))
    pixels = image.load()
    for y in range(height):
        mix = y / (height - 1)
        start, end = palette["gradient"]
        colour = tuple(round(start[i] * (1 - mix) + end[i] * mix) for i in range(3))
        for x in range(width):
            pixels[x, y] = colour
    draw = ImageDraw.Draw(image)
    ink = palette["ink"]
    muted = palette["muted"]
    green = palette["primary"]
    lime = palette["cta"]
    white = (255, 255, 255)

    if layout_variant == 0:
        draw.ellipse((-120, 140, 360, 620), fill=palette["rows"][0])
        draw.ellipse((760, 820, 1210, 1270), fill=palette["rows"][2])
    elif layout_variant == 1:
        for offset, accent in enumerate(palette["accents"]):
            draw.rounded_rectangle((760 + offset * 55, -90, 850 + offset * 55, 420), radius=40, fill=accent)
    else:
        for radius, accent in ((260, palette["accents"][0]), (190, palette["accents"][1]), (120, palette["accents"][2])):
            draw.ellipse((940 - radius, 190 - radius, 940 + radius, 190 + radius), outline=accent, width=8)

    draw.rounded_rectangle((60, 48, 1020, 205), radius=42, fill=white, outline=(206, 230, 220), width=3)
    logo_path = PROJECT_DIR / "assets" / "brand-logo-light.png"
    logo = Image.open(logo_path).convert("RGBA")
    logo.thumbnail((118, 118))
    logo_box = Image.new("RGBA", (124, 124), (255, 255, 255, 0))
    logo_box.alpha_composite(logo, ((124 - logo.width) // 2, (124 - logo.height) // 2))
    image.paste(logo_box, (80, 64), logo_box)
    draw.text((225, 80), "AI TOOL GEMS", font=_font(40, True), fill=ink)
    draw.text((227, 134), "PAKISTAN", font=_font(21, True), fill=green)
    draw.rounded_rectangle((762, 91, 976, 157), radius=33, fill=lime)
    draw.text((812, 110), "3 DEALS", font=_font(25, True), fill=ink)

    ribbon_labels = ("GOOD NEWS", "SMART STACK", "PRICE DROP")
    draw.rounded_rectangle((70, 232, 306, 272), radius=20, fill=green)
    draw.text((94, 240), ribbon_labels[layout_variant], font=_font(19, True), fill=white)
    draw.text((70, 283), f"{slot.upper()} — 3 DEALS", font=_font(46, True), fill=ink)
    draw.text((72, 338), f"{concept.replace('-', ' ').title()} | Gemini + two fresh picks", font=_font(23), fill=muted)

    row_colours = palette["rows"]
    accent_colours = palette["accents"]
    for index, product in enumerate(products):
        top = 378 + index * 210
        bottom = top + 192
        accent = accent_colours[index]
        draw.rounded_rectangle((68, top, 1012, bottom), radius=38, fill=row_colours[index], outline=(208, 228, 220), width=2)
        draw.rounded_rectangle((68, top, 82, bottom), radius=7, fill=accent)
        mirror = layout_variant == 1 or (layout_variant == 2 and index % 2 == 1)
        logo_left = 853 if mirror else 105
        logo_center = logo_left + 61
        draw.rounded_rectangle((logo_left, top + 35, logo_left + 122, top + 157), radius=30, fill=white, outline=(205, 226, 218), width=2)
        try:
            product_logo = _product_logo(product, 84)
            logo_position = (logo_center - product_logo.width // 2, top + 96 - product_logo.height // 2)
            image.paste(product_logo, logo_position, product_logo)
        except Exception:
            initials = "".join(word[0] for word in product.name.split()[:2]).upper()
            initials_box = draw.textbbox((0, 0), initials, font=_font(34, True))
            draw.text((logo_center - (initials_box[2] - initials_box[0]) / 2, top + 76), initials, font=_font(34, True), fill=ink)

        text_x = 105 if mirror else 260
        price_x = 520 if mirror else 747
        name_lines = _wrapped_lines(draw, product.name, _font(37, True), 390 if mirror else 430)
        name_y = top + 26
        for line in name_lines[:2]:
            draw.text((text_x, name_y), line, font=_font(37, True), fill=ink)
            name_y += 43
        draw.text((text_x, top + 113), f"{product.duration}  |  {product.access} access", font=_font(20, True), fill=muted)
        draw.text((text_x, top + 146), f"Delivery {product.delivery}  |  Warranty {product.warranty}", font=_font(18), fill=muted)

        if index == 0:
            badge_left = 520 if mirror else 778
            draw.rounded_rectangle((badge_left, top + 18, badge_left + 191, top + 50), radius=16, fill=(220, 250, 230))
            draw.text((badge_left + 26, top + 25), "ALWAYS FEATURED", font=_font(14, True), fill=ink)
        draw.text((price_x, top + 65), f"Rs. {product.price:,}", font=_font(44, True), fill=ink)
        if product.saving:
            draw.text((price_x + 22, top + 122), f"SAVE Rs. {product.saving:,}", font=_font(19, True), fill=accent)

    cta_top = 1034
    draw.rounded_rectangle((70, cta_top, 1010, cta_top + 104), radius=48, fill=lime)
    cta = "ORDER ON WHATSAPP  +92 323 6715731"
    cta_box = draw.textbbox((0, 0), cta, font=_font(30, True))
    draw.text(((width - (cta_box[2] - cta_box[0])) / 2, cta_top + 33), cta, font=_font(30, True), fill=ink)

    draw.text((72, 1182), "Compare prices, plans and access details before payment.", font=_font(24), fill=muted)
    draw.text((72, 1225), "aitoolgems.tech/deals", font=_font(33, True), fill=ink)
    draw.text((72, 1283), "Availability is confirmed on WhatsApp. Independent reseller.", font=_font(19), fill=muted)
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
    seconds: int = VIDEO_SECONDS,
    sample_rate: int = 44_100,
) -> None:
    """Create a layered, trend-inspired original soundbed safe for automatic commercial posts."""
    themes = {
        "focus-tech": ((261.63, 329.63, 392.00, 523.25, 392.00, 329.63, 293.66, 392.00), 112),
        "creator-pulse": ((329.63, 392.00, 493.88, 659.25, 493.88, 587.33, 523.25, 659.25), 124),
        "clean-business": ((220.00, 277.18, 329.63, 440.00, 329.63, 369.99, 277.18, 329.63), 104),
        # Platform-shaped, fully original arrangements. These follow current short-form
        # pacing conventions without reproducing any copyrighted melody or recording.
        "desi-pop-pulse": ((293.66, 349.23, 440.00, 523.25, 440.00, 392.00, 349.23, 440.00), 126),
        "future-bass-hook": ((246.94, 369.99, 415.30, 554.37, 415.30, 493.88, 369.99, 554.37), 132),
        "cinematic-trap": ((220.00, 261.63, 329.63, 392.00, 329.63, 293.66, 246.94, 329.63), 140),
        "creator-pop": ((329.63, 415.30, 493.88, 659.25, 554.37, 493.88, 415.30, 493.88), 120),
        "glossy-house": ((261.63, 329.63, 392.00, 523.25, 659.25, 523.25, 392.00, 329.63), 124),
        "desi-electro": ((293.66, 392.00, 440.00, 587.33, 523.25, 440.00, 392.00, 523.25), 128),
        "uplifting-desi": ((261.63, 329.63, 392.00, 440.00, 523.25, 440.00, 392.00, 329.63), 112),
        "clean-cinematic": ((220.00, 277.18, 329.63, 415.30, 493.88, 415.30, 329.63, 277.18), 108),
        "modern-business": ((246.94, 311.13, 369.99, 493.88, 369.99, 415.30, 311.13, 369.99), 116),
    }
    notes, bpm = themes.get(theme, themes["focus-tech"])
    beat_seconds = 60 / bpm
    samples = array("h")
    total = seconds * sample_rate
    for index in range(total):
        elapsed = index / sample_rate
        beat_index = int(elapsed / beat_seconds)
        within_beat = elapsed % beat_seconds
        half_beat = elapsed % (beat_seconds / 2)
        note = notes[beat_index % len(notes)]

        # Bright pluck, warm bass and dance-style drums create energy without copying a song.
        pluck_env = math.exp(-7.5 * within_beat)
        pluck = (
            math.sin(2 * math.pi * note * elapsed)
            + 0.35 * math.sin(2 * math.pi * note * 2 * elapsed)
        ) * pluck_env
        bass = math.sin(2 * math.pi * (note / 4) * elapsed) * math.exp(-3.2 * within_beat)
        kick = math.sin(2 * math.pi * (62 - min(36, within_beat * 180)) * elapsed) * math.exp(-18 * within_beat)
        clap_phase = (elapsed + beat_seconds / 2) % beat_seconds
        clap_noise = math.sin(index * 12.9898) * math.sin(index * 0.173)
        clap = clap_noise * math.exp(-34 * clap_phase)
        hat_noise = math.sin(index * 78.233) * math.sin(index * 0.711)
        hat = hat_noise * math.exp(-55 * half_beat)
        riser = math.sin(2 * math.pi * (520 + elapsed * 42) * elapsed) * max(0, elapsed - (seconds - 1.0)) * 0.08
        master_fade = min(1.0, elapsed / 0.12, max(0.0, (seconds - elapsed) / 0.35))
        # A short dhol-like transient adds a South-Asian commercial feel without
        # sampling a song. The syncopation changes with the selected BPM/style.
        dhol_phase = (elapsed + beat_seconds / 4) % (beat_seconds / 2)
        dhol = math.sin(2 * math.pi * (135 - min(58, dhol_phase * 250)) * elapsed) * math.exp(-22 * dhol_phase)
        mono = master_fade * (
            0.15 * pluck + 0.10 * bass + 0.16 * kick + 0.042 * clap + 0.024 * hat + 0.07 * dhol + riser
        )
        shimmer = 0.025 * math.sin(2 * math.pi * note * 1.5 * elapsed) * pluck_env
        left = int(32767 * max(-0.92, min(0.92, mono + shimmer)))
        right = int(32767 * max(-0.92, min(0.92, mono - shimmer)))
        samples.extend((left, right))
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(2)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        audio.writeframes(samples.tobytes())


def _render_single_deal_video_legacy(day: date, output: Path | None = None) -> Path | None:
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


def render_deal_video(day: date, output: Path | None = None, slot: str = "morning") -> Path | None:
    """Render an 8-second 9:16 creative showing all three deals and prices."""
    from PIL import Image, ImageDraw

    executable = _ffmpeg_executable()
    if not executable:
        return None
    products = deals_for_slot(day, slot)
    focus = products[1]
    audience = audience_for(focus, day)
    output = output or deal_video_path(day, focus, slot)
    output.parent.mkdir(parents=True, exist_ok=True)
    card = Image.open(render_deal_card(day, slot=slot)).convert("RGB")
    palette = _creative_palette(day, slot)

    width, height = 720, 1280
    frame = Image.new("RGB", (width, height))
    pixels = frame.load()
    for y in range(height):
        mix = y / (height - 1)
        start, end = palette["gradient"]
        colour = tuple(round(start[i] * (1 - mix) + end[i] * mix) for i in range(3))
        for x in range(width):
            pixels[x, y] = colour
    draw = ImageDraw.Draw(frame)
    ink, muted, green, lime = palette["ink"], palette["muted"], palette["primary"], palette["cta"]
    draw.text((38, 35), f"{slot.upper()} — 3 CLEAR DEALS", font=_font(34, True), fill=ink)
    draw.text((40, 84), audience.label.upper()[:48], font=_font(18, True), fill=green)
    card.thumbnail((660, 825))
    frame.paste(card, ((width - card.width) // 2, 130))
    draw.rounded_rectangle((36, 990, 684, 1128), radius=42, fill=lime)
    cta = "WHATSAPP  +92 323 6715731"
    cta_box = draw.textbbox((0, 0), cta, font=_font(35, True))
    draw.text(((width - cta_box[2]) / 2, 1018), cta, font=_font(35, True), fill=ink)
    draw.text((133, 1075), "GEMINI + 2 ROTATING DAILY DEALS", font=_font(21, True), fill=ink)
    draw.text((153, 1160), "aitoolgems.tech/deals", font=_font(32, True), fill=ink)
    draw.text((74, 1218), "Promotional listing | Independent reseller", font=_font(18), fill=muted)

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


def render_realistic_deal_video(day: date, output: Path | None = None, slot: str = "evening") -> Path | None:
    """Render a photorealistic 10-second, five-scene 9:16 deal Reel."""
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

    executable = _ffmpeg_executable()
    if not executable:
        return None
    products = deals_for_slot(day, slot)
    focus = products[1]
    audience = audience_for(focus, day)
    output = output or deal_video_path(day, focus, slot)
    output.parent.mkdir(parents=True, exist_ok=True)
    width, height = 720, 1280
    palette = _creative_palette(day, slot)
    ink, primary, cta = palette["ink"], palette["primary"], palette["cta"]

    if REALISTIC_BACKGROUND.exists():
        source = Image.open(REALISTIC_BACKGROUND).convert("RGB")
        background = ImageOps.fit(source, (width, height), method=Image.Resampling.LANCZOS)
        background = ImageEnhance.Color(background).enhance(0.92)
        background = ImageEnhance.Contrast(background).enhance(0.94)
    else:
        background = Image.new("RGB", (width, height), palette["gradient"][0])

    logos: dict[str, Image.Image | None] = {}
    for product in products:
        try:
            request = Request(
                f"https://www.google.com/s2/favicons?domain={PRODUCT_DOMAINS[product.id]}&sz=256",
                headers={"User-Agent": "AI-Tool-Gems-Marketing-Agent/1.0"},
            )
            with urlopen(request, timeout=12) as response:
                logo = Image.open(BytesIO(response.read())).convert("RGBA")
            logo.thumbnail((92, 92), Image.Resampling.LANCZOS)
            logos[product.id] = logo
        except Exception:
            logos[product.id] = None

    brand_logo = Image.open(PROJECT_DIR / "assets" / "brand-logo-light.png").convert("RGBA")
    brand_logo.thumbnail((76, 76), Image.Resampling.LANCZOS)

    def scene_base(strength: int = 70) -> Image.Image:
        scene = background.copy().convert("RGBA")
        scene.alpha_composite(Image.new("RGBA", scene.size, (8, 31, 38, strength)))
        draw = ImageDraw.Draw(scene, "RGBA")
        draw.rounded_rectangle((28, 24, 692, 116), radius=34, fill=(255, 255, 255, 230))
        scene.alpha_composite(brand_logo, (44, 32))
        draw.text((132, 45), "AI TOOL GEMS", font=_font(29, True), fill=ink)
        draw.text((133, 80), "PAKISTAN", font=_font(15, True), fill=primary)
        draw.rounded_rectangle((542, 48, 665, 93), radius=22, fill=cta)
        draw.text((568, 60), "DEALS", font=_font(18, True), fill=ink)
        return scene

    def paste_logo(scene: Image.Image, product: Product, box: tuple[int, int, int, int]) -> None:
        draw = ImageDraw.Draw(scene, "RGBA")
        draw.rounded_rectangle(box, radius=28, fill=(255, 255, 255, 245), outline=(210, 232, 226, 255), width=2)
        logo = logos.get(product.id)
        center_x = (box[0] + box[2]) // 2
        center_y = (box[1] + box[3]) // 2
        if logo:
            scene.alpha_composite(logo, (center_x - logo.width // 2, center_y - logo.height // 2))
        else:
            initials = "".join(word[0] for word in product.name.split()[:2]).upper()
            bounds = draw.textbbox((0, 0), initials, font=_font(36, True))
            draw.text((center_x - (bounds[2] - bounds[0]) / 2, center_y - 24), initials, font=_font(36, True), fill=ink)

    frames: list[Image.Image] = []
    intro = scene_base(42)
    draw = ImageDraw.Draw(intro, "RGBA")
    draw.rounded_rectangle((36, 650, 684, 1105), radius=46, fill=(255, 255, 255, 232))
    draw.text((72, 700), "YOUR AI STACK", font=_font(53, True), fill=ink)
    draw.text((72, 765), "JUST GOT SMARTER.", font=_font(48, True), fill=primary)
    draw.rounded_rectangle((72, 856, 482, 921), radius=30, fill=cta)
    draw.text((103, 873), "3 VERIFIED DEALS", font=_font(27, True), fill=ink)
    draw.text((72, 958), "For students, creators and teams", font=_font(26, True), fill=ink)
    draw.text((72, 1002), "Clear PKR prices. Fast WhatsApp ordering.", font=_font(21), fill=palette["muted"])
    draw.text((46, 1215), "AI-generated promotional visual", font=_font(16), fill=(255, 255, 255, 235))
    frames.append(intro.convert("RGB"))

    for index, product in enumerate(products, 1):
        scene = scene_base(86)
        draw = ImageDraw.Draw(scene, "RGBA")
        draw.rounded_rectangle((38, 510, 682, 1120), radius=50, fill=(255, 255, 255, 240))
        draw.rounded_rectangle((62, 544, 190, 586), radius=20, fill=primary)
        draw.text((83, 554), f"DEAL {index}/3", font=_font(17, True), fill=(255, 255, 255))
        paste_logo(scene, product, (62, 620, 202, 760))
        name_y = 624
        for line in _wrapped_lines(draw, product.name, _font(43, True), 410)[:2]:
            draw.text((232, name_y), line, font=_font(43, True), fill=ink)
            name_y += 51
        draw.text((66, 806), "TODAY'S PRICE", font=_font(20, True), fill=palette["muted"])
        draw.text((64, 840), f"Rs. {product.price:,}", font=_font(72, True), fill=ink)
        if product.saving:
            draw.rounded_rectangle((400, 858, 644, 910), radius=26, fill=cta)
            draw.text((424, 872), f"SAVE Rs. {product.saving:,}", font=_font(20, True), fill=ink)
        draw.text((68, 950), f"{product.duration}  |  {product.access} access", font=_font(23, True), fill=ink)
        draw.text((68, 994), f"Delivery {product.delivery}  |  Warranty {product.warranty}", font=_font(20), fill=palette["muted"])
        draw.text((68, 1054), "Availability confirmed before payment", font=_font(18), fill=palette["muted"])
        draw.text((46, 1215), "AI-generated promotional visual", font=_font(16), fill=(255, 255, 255, 235))
        frames.append(scene.convert("RGB"))

    outro = scene_base(92).filter(ImageFilter.GaussianBlur(radius=0.35))
    draw = ImageDraw.Draw(outro, "RGBA")
    draw.rounded_rectangle((38, 450, 682, 1130), radius=54, fill=(255, 255, 255, 244))
    draw.text((75, 500), "PICK YOUR DEAL", font=_font(50, True), fill=ink)
    for index, product in enumerate(products):
        row_y = 600 + index * 116
        draw.rounded_rectangle((72, row_y, 650, row_y + 92), radius=27, fill=palette["rows"][index])
        draw.text((96, row_y + 18), product.name[:24], font=_font(26, True), fill=ink)
        price = f"Rs. {product.price:,}"
        bounds = draw.textbbox((0, 0), price, font=_font(27, True))
        draw.text((620 - (bounds[2] - bounds[0]), row_y + 47), price, font=_font(27, True), fill=palette["accents"][index])
    draw.rounded_rectangle((72, 970, 650, 1062), radius=43, fill=cta)
    draw.text((119, 992), "WHATSAPP +92 323 6715731", font=_font(27, True), fill=ink)
    draw.text((190, 1082), "aitoolgems.tech/deals", font=_font(25, True), fill=ink)
    draw.text((46, 1215), "AI-generated promotional visual", font=_font(16), fill=(255, 255, 255, 235))
    frames.append(outro.convert("RGB"))

    with tempfile.TemporaryDirectory(prefix="atg-video-") as temporary:
        temporary_dir = Path(temporary)
        frame_paths: list[Path] = []
        for index, frame in enumerate(frames):
            frame_path = temporary_dir / f"scene-{index}.jpg"
            frame.save(frame_path, format="JPEG", quality=93, optimize=True)
            frame_paths.append(frame_path)
        audio_path = temporary_dir / "trend-inspired-original.wav"
        _write_original_audio(audio_path, audio_theme_for(audience), VIDEO_SECONDS)
        command = [executable, "-y"]
        for frame_path in frame_paths:
            command.extend(("-loop", "1", "-t", "2", "-i", str(frame_path)))
        command.extend(("-i", str(audio_path)))
        filters = []
        for index in range(len(frame_paths)):
            filters.append(
                f"[{index}:v]scale=720:1280,setsar=1,fps=25,"
                "fade=t=in:st=0:d=0.12,fade=t=out:st=1.88:d=0.12"
                f"[v{index}]"
            )
        filters.append("".join(f"[v{index}]" for index in range(len(frame_paths))) + f"concat=n={len(frame_paths)}:v=1:a=0[v]")
        command.extend((
            "-filter_complex", ";".join(filters), "-map", "[v]", "-map", f"{len(frame_paths)}:a",
            "-t", str(VIDEO_SECONDS), "-c:v", "libx264", "-preset", "medium", "-crf", "25",
            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
            "-movflags", "+faststart", "-shortest", str(output),
        ))
        completed = subprocess.run(command, capture_output=True, text=True, timeout=180)
        if completed.returncode != 0:
            output.unlink(missing_ok=True)
            raise BufferError(f"Video render failed: {completed.stderr[-700:]}")
    return output


def render_orbit_campaign_video(
    day: date,
    service: str,
    output: Path | None = None,
    slot: str = "evening",
) -> Path | None:
    """Render a kinetic, platform-paced 9:16 campaign with real orbit motion."""
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

    executable = _ffmpeg_executable()
    if not executable:
        return None
    if service not in VIDEO_SPECS:
        raise ValueError(f"Unsupported social service: {service}")

    products = deals_for_slot(day, slot)
    focus = products[1]
    spec = VIDEO_SPECS[service]
    seconds, fps = int(spec["seconds"]), int(spec["fps"])
    concept = creative_concept_for(day, slot)
    audio_style = platform_audio_style(day, service)
    output = output or deal_video_path(day, focus, slot, service)
    output.parent.mkdir(parents=True, exist_ok=True)
    width, height = 720, 1280
    palette = _creative_palette(day, slot)
    ink, muted = palette["ink"], palette["muted"]
    primary, cta = palette["primary"], palette["cta"]

    if REALISTIC_BACKGROUND.exists():
        source = Image.open(REALISTIC_BACKGROUND).convert("RGB")
        source = ImageOps.fit(source, (820, 1420), method=Image.Resampling.LANCZOS)
        source = ImageEnhance.Color(source).enhance(1.04)
        source = ImageEnhance.Contrast(source).enhance(0.96)
    else:
        source = Image.new("RGB", (820, 1420), palette["gradient"][0])

    brand_logo = Image.open(PROJECT_DIR / "assets" / "brand-logo-light.png").convert("RGBA")
    brand_logo.thumbnail((102, 102), Image.Resampling.LANCZOS)
    product_logos: dict[str, Image.Image | None] = {}
    for product in products:
        try:
            product_logos[product.id] = _product_logo(product, 92)
        except Exception:
            product_logos[product.id] = None

    hooks = {
        "tiktok": "STOP OVERPAYING FOR AI",
        "instagram": "YOUR CREATOR STACK, UPGRADED",
        "facebook": "3 AI DEALS. CLEAR PKR PRICES.",
    }
    concept_labels = {
        "orbit-drop": "TODAY'S AI ORBIT",
        "creator-portal": "OPEN YOUR CREATOR PORTAL",
        "neon-price-radar": "PRICE DROP DETECTED",
        "glass-card-rush": "3 GEMS. ONE SMART STACK.",
        "three-gem-reveal": "YOUR 3-GEM REVEAL",
        "smart-stack": "BUILD A SMARTER STACK",
        "deal-countdown": "DON'T MISS TODAY'S DROP",
    }

    def ease_out(value: float) -> float:
        value = max(0.0, min(1.0, value))
        return 1 - (1 - value) ** 3

    def centered(draw, text_value: str, y: int, font, fill) -> None:
        bounds = draw.textbbox((0, 0), text_value, font=font)
        draw.text(((width - (bounds[2] - bounds[0])) / 2, y), text_value, font=font, fill=fill)

    def logo_tile(frame, logo, center: tuple[int, int], size: int, glow, pulse: float = 1.0, fallback: str = "AI") -> None:
        layer = Image.new("RGBA", frame.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer, "RGBA")
        actual = max(54, int(size * pulse))
        x, y = center
        draw.ellipse((x - actual // 2 - 13, y - actual // 2 - 13, x + actual // 2 + 13, y + actual // 2 + 13), fill=(*glow, 46))
        draw.rounded_rectangle(
            (x - actual // 2, y - actual // 2, x + actual // 2, y + actual // 2),
            radius=max(18, actual // 4), fill=(255, 255, 255, 244), outline=(*glow, 210), width=3,
        )
        frame.alpha_composite(layer)
        if logo:
            copy = logo.copy()
            copy.thumbnail((int(actual * 0.66), int(actual * 0.66)), Image.Resampling.LANCZOS)
            frame.alpha_composite(copy, (x - copy.width // 2, y - copy.height // 2))
        else:
            initials = "".join(word[0] for word in fallback.split()[:2]).upper()
            bounds = draw.textbbox((0, 0), initials, font=_font(max(18, actual // 3), True))
            draw.text((x - (bounds[2] - bounds[0]) / 2, y - actual // 6), initials, font=_font(max(18, actual // 3), True), fill=ink)

    total_frames = seconds * fps
    hook_end = 2.05 if service == "tiktok" else 2.4
    outro_start = seconds - (2.15 if service == "tiktok" else 2.7)
    reveal_span = (outro_start - hook_end) / 3

    with tempfile.TemporaryDirectory(prefix=f"atg-{service}-orbit-") as temporary:
        temporary_dir = Path(temporary)
        for frame_index in range(total_frames):
            elapsed = frame_index / fps
            # Slow parallax makes the photoreal workspace feel filmed rather than static.
            crop_x = int(50 + 22 * math.sin(elapsed * 0.55 + day.day))
            crop_y = int(58 + 16 * math.cos(elapsed * 0.42 + day.month))
            frame = source.crop((crop_x, crop_y, crop_x + width, crop_y + height)).convert("RGBA")
            tint = Image.new("RGBA", frame.size, (*palette["gradient"][0], 30))
            frame.alpha_composite(tint)
            shade = Image.new("RGBA", frame.size, (7, 24, 36, 68 if elapsed < hook_end else 86))
            frame.alpha_composite(shade)
            draw = ImageDraw.Draw(frame, "RGBA")

            # Moving ambient orbs and orbit paths reinforce the gem/technology identity.
            for orbit_index, accent in enumerate(palette["accents"]):
                phase = elapsed * (0.8 + orbit_index * 0.17) + orbit_index * 2.1
                ox = int(360 + math.cos(phase) * (280 - orbit_index * 44))
                oy = int(410 + math.sin(phase * 0.76) * (240 - orbit_index * 28))
                radius = 34 + orbit_index * 8
                draw.ellipse((ox - radius, oy - radius, ox + radius, oy + radius), fill=(*accent, 40))
            ring_shift = int(10 * math.sin(elapsed * 1.6))
            draw.ellipse((95, 170 + ring_shift, 625, 680 - ring_shift), outline=(*primary, 125), width=3)
            draw.ellipse((150, 222 - ring_shift, 570, 635 + ring_shift), outline=(*cta, 105), width=2)

            # Consistent brand bar; campaign layout and motion change daily.
            draw.rounded_rectangle((24, 22, 696, 112), radius=34, fill=(255, 255, 255, 236))
            frame.alpha_composite(brand_logo, (38, 29))
            draw.text((132, 42), "AI TOOL GEMS", font=_font(29, True), fill=ink)
            draw.text((133, 77), "PAKISTAN", font=_font(15, True), fill=primary)
            draw.rounded_rectangle((526, 43, 674, 91), radius=23, fill=cta)
            draw.text((548, 56), "3 DEALS", font=_font(19, True), fill=ink)

            if elapsed < hook_end:
                progress = ease_out(elapsed / hook_end)
                pulse = 1 + 0.06 * math.sin(elapsed * math.pi * 3)
                logo_tile(frame, brand_logo, (360, 390), 176, primary, pulse)
                for index, product in enumerate(products):
                    angle = elapsed * (1.65 if concept in {"orbit-drop", "creator-portal"} else 1.2) + index * math.tau / 3
                    center = (int(360 + math.cos(angle) * 218), int(415 + math.sin(angle) * 155))
                    logo_tile(frame, product_logos[product.id], center, 94, palette["accents"][index], 1.0, product.name)
                panel_y = int(790 + (1 - progress) * 120)
                draw.rounded_rectangle((34, panel_y, 686, 1118), radius=48, fill=(255, 255, 255, 239))
                centered(draw, hooks[service], panel_y + 46, _font(42 if service != "facebook" else 36, True), ink)
                centered(draw, concept_labels[concept], panel_y + 111, _font(25, True), primary)
                centered(draw, "Gemini + 2 fresh picks • clear PKR prices", panel_y + 177, _font(22, True), muted)
                centered(draw, "WAIT FOR DEAL #3", panel_y + 229, _font(27, True), ink)
            elif elapsed < outro_start:
                product_index = min(2, int((elapsed - hook_end) / reveal_span))
                product = products[product_index]
                local = (elapsed - hook_end - product_index * reveal_span) / reveal_span
                enter = ease_out(min(1.0, local / 0.28))
                exit_value = ease_out(max(0.0, (local - 0.82) / 0.18))
                slide = int((1 - enter) * (160 if product_index % 2 == 0 else -160) + exit_value * -90)
                panel_left = 38 + slide
                draw.rounded_rectangle((panel_left, 455, panel_left + 644, 1125), radius=52, fill=(255, 255, 255, 242))
                draw.rounded_rectangle((panel_left + 32, 493, panel_left + 188, 541), radius=22, fill=primary)
                draw.text((panel_left + 56, 505), f"DEAL {product_index + 1}/3", font=_font(19, True), fill=(255, 255, 255))
                orbit_angle = elapsed * 2.2 + product_index
                logo_center = (panel_left + 322 + int(math.cos(orbit_angle) * 36), 658 + int(math.sin(orbit_angle) * 20))
                logo_tile(frame, product_logos[product.id], logo_center, 154, palette["accents"][product_index], 1 + 0.04 * math.sin(elapsed * 5), product.name)
                centered(draw, product.name.upper(), 770, _font(43 if len(product.name) < 17 else 36, True), ink)
                centered(draw, "TODAY'S PRICE", 839, _font(20, True), muted)
                price_scale = 1 + 0.05 * math.sin(min(1, local * 4) * math.pi)
                centered(draw, f"Rs. {product.price:,}", 878, _font(int(70 * price_scale), True), palette["accents"][product_index])
                if product.saving:
                    centered(draw, f"SAVE Rs. {product.saving:,}", 970, _font(24, True), primary)
                centered(draw, f"{product.duration} • {product.access} access", 1020, _font(22, True), ink)
                centered(draw, "Availability checked before payment", 1066, _font(18, False), muted)
            else:
                local = (elapsed - outro_start) / (seconds - outro_start)
                pulse = 1 + 0.025 * math.sin(local * math.pi * 7)
                draw.rounded_rectangle((34, 400, 686, 1135), radius=54, fill=(255, 255, 255, 245))
                centered(draw, "PICK YOUR AI STACK", 446, _font(46, True), ink)
                for index, product in enumerate(products):
                    row_y = 548 + index * 114
                    draw.rounded_rectangle((62, row_y, 658, row_y + 91), radius=29, fill=palette["rows"][index])
                    logo_tile(frame, product_logos[product.id], (112, row_y + 45), 64, palette["accents"][index], fallback=product.name)
                    draw.text((158, row_y + 18), product.name[:25], font=_font(24, True), fill=ink)
                    draw.text((158, row_y + 52), f"Rs. {product.price:,}", font=_font(23, True), fill=palette["accents"][index])
                button_width = int(574 * pulse)
                left = (width - button_width) // 2
                draw.rounded_rectangle((left, 920, left + button_width, 1018), radius=48, fill=(27, 186, 103, 255))
                centered(draw, "WHATSAPP +92 323 6715731", 948, _font(28, True), (255, 255, 255))
                centered(draw, "aitoolgems.tech/deals", 1045, _font(26, True), ink)
                centered(draw, "Message now • availability confirmed first", 1087, _font(18, False), muted)

            draw.text((28, 1238), f"AI-assisted creative • {concept} • independent reseller", font=_font(15), fill=(255, 255, 255, 225))
            frame_path = temporary_dir / f"frame-{frame_index:04d}.jpg"
            frame.convert("RGB").save(frame_path, format="JPEG", quality=88, optimize=True)

        audio_path = temporary_dir / f"{audio_style}.wav"
        _write_original_audio(audio_path, audio_style, seconds)
        command = [
            executable, "-y", "-framerate", str(fps), "-i", str(temporary_dir / "frame-%04d.jpg"),
            "-i", str(audio_path), "-t", str(seconds), "-c:v", "libx264", "-preset", "medium", "-crf", "24",
            "-pix_fmt", "yuv420p", "-r", str(fps), "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
            "-movflags", "+faststart", "-shortest", str(output),
        ]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=300)
        if completed.returncode != 0:
            output.unlink(missing_ok=True)
            raise BufferError(f"Advanced video render failed: {completed.stderr[-700:]}")
    return output


def render_daily_media(day: date) -> list[Path]:
    """Build one photo plus a native-paced video for each destination platform."""
    assets = [render_deal_card(day, slot="morning")]
    for service in TARGET_SERVICES:
        video = render_orbit_campaign_video(day, service, slot="evening")
        if video:
            assets.append(video)
    return assets


def render_platform_media(day: date, service: str, slot: str) -> Path:
    """Render exactly one destination asset for fast, targeted queue repairs."""
    if service not in TARGET_SERVICES:
        raise ValueError(f"Unsupported social service: {service}")
    if slot not in SOCIAL_SLOTS:
        raise ValueError(f"Unsupported social slot: {slot}")
    if media_type_for_slot(slot) == "image":
        return render_deal_card(day, slot=slot)
    return render_orbit_campaign_video(day, service, slot=slot)


def media_url_for(day: date, service: str = "facebook", slot: str = "morning") -> tuple[str, str]:
    products = deals_for_slot(day, slot)
    media_type = media_type_for_slot(slot)
    if media_type == "video":
        asset = deal_video_path(day, products[1], slot, service)
    else:
        asset = deal_card_path(day, products[1], slot)
    return f"{RAW_MEDIA_ROOT}/{asset.name}", media_type


def scheduled_time(
    settings: Settings,
    day: date,
    now: datetime | None = None,
    service: str = "instagram",
    audience: AudienceAngle | None = None,
    slot: str = "morning",
) -> datetime:
    """Use researched, platform-specific morning/evening windows in Pakistan local time."""
    if service not in TARGET_SERVICES:
        raise ValueError(f"Unsupported social service: {service}")
    if slot not in SOCIAL_SLOTS:
        raise ValueError(f"Unsupported social slot: {slot}")
    # Monday=0. Initial benchmarks come from Buffer's 2026 analyses of
    # 14M Facebook, 9.6M Instagram and 7.1M TikTok posts. Real account
    # metrics are still collected so these can be tuned as the audience grows.
    pakistan_windows = {
        "facebook": {
            "morning": ((9, 0), (8, 0), (8, 0), (9, 0), (8, 0), (10, 0), (10, 0)),
            "evening": ((21, 0), (19, 0), (18, 0), (19, 0), (20, 0), (22, 0), (20, 0)),
        },
        "instagram": {
            "morning": ((10, 0), (10, 0), (8, 0), (9, 0), (9, 0), (10, 0), (10, 0)),
            "evening": ((19, 0), (19, 0), (18, 0), (19, 0), (22, 0), (21, 0), (21, 0)),
        },
        "tiktok": {
            "morning": ((11, 0), (7, 0), (6, 0), (6, 0), (10, 0), (10, 0), (9, 0)),
            "evening": ((20, 0), (22, 0), (22, 0), (22, 0), (18, 0), (17, 0), (20, 0)),
        },
    }
    hour, minute = pakistan_windows[service][slot][day.weekday()]
    local_target = datetime.combine(day, time(hour, minute), settings.timezone)
    target = local_target.astimezone(timezone.utc)
    current = now or datetime.now(timezone.utc)
    if target <= current + timedelta(minutes=5):
        # A late hosted run must never burst multiple networks together.
        service_delay = {"facebook": 15, "instagram": 30, "tiktok": 45}[service]
        slot_delay = 0 if slot == "morning" else 75
        target = current + timedelta(minutes=service_delay + slot_delay)
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


def _caption_issues(
    settings: Settings,
    day: date,
    service: str,
    slot: str,
    caption: str,
) -> list[str]:
    products = deals_for_slot(day, slot)
    issues: list[str] = []
    compact_caption = "".join(character for character in caption if character.isdigit())
    expected_number = "".join(character for character in settings.whatsapp_number if character.isdigit())
    if expected_number not in compact_caption:
        issues.append("current WhatsApp number is missing")
    if "Gemini" not in caption:
        issues.append("Gemini is missing")
    if caption.count("PRICE: Rs.") != 3:
        issues.append("three clear PKR price lines are required")
    for product in products:
        if product.name.upper() not in caption:
            issues.append(f"{product.name} is missing")
    if f"utm_source={service}" not in caption or f"utm_term={slot}" not in caption:
        issues.append("platform tracking is incomplete")
    if settings.site_url.rstrip("/") not in caption:
        issues.append("website CTA is missing")
    if any(marker in caption.lower() for marker in ("todo", "example.com", "923476242709")):
        issues.append("placeholder or legacy contact content detected")
    hashtag_limit = {"facebook": 3, "instagram": 6, "tiktok": 6}[service]
    if len([word for word in caption.split() if word.startswith("#")]) > hashtag_limit:
        issues.append("hashtag count exceeds the platform limit")
    character_limit = {"facebook": 5000, "instagram": 2200, "tiktok": 2200}[service]
    if len(caption) > character_limit:
        issues.append(f"caption exceeds {character_limit} characters")
    return issues


def campaign_preflight(
    settings: Settings,
    day: date,
    state_path: Path = STATE_PATH,
    client: BufferClient | None = None,
    now: datetime | None = None,
) -> dict:
    """Block unsafe inputs, while reporting past delivery failures without stopping a new day."""
    client = client or BufferClient(settings.buffer_api_key)
    current = now or datetime.now(timezone.utc)
    status = connection_status(settings, client)
    errors: list[str] = []
    warnings: list[str] = []
    for service, channel in status["channels"].items():
        if channel["queue_paused"]:
            errors.append(f"{service} queue is paused in Buffer")

    checked_assets: list[str] = []
    for slot in SOCIAL_SLOTS:
        for service in TARGET_SERVICES:
            caption = caption_for_platform(settings, day, service, slot=slot)
            for issue in _caption_issues(settings, day, service, slot, caption):
                errors.append(f"{slot}:{service}: {issue}")
            media_url, _ = media_url_for(day, service, slot)
            asset = CARD_DIR / media_url.rsplit("/", 1)[-1]
            if not asset.exists() or asset.stat().st_size < 5_000:
                errors.append(f"{slot}:{service}: media asset is missing or incomplete")
            else:
                checked_assets.append(asset.name)

    state = _read_state(state_path)
    recent: list[tuple[datetime, str, dict]] = []
    for day_key, records in state.get("published_dates", {}).items():
        for state_key, record in records.items():
            try:
                due_at = datetime.fromisoformat(str(record.get("scheduled_for", "")).replace("Z", "+00:00"))
            except ValueError:
                continue
            if due_at <= current - timedelta(minutes=30):
                recent.append((due_at, f"{day_key}:{state_key}", record))
    delivery_checks = 0
    for _, label, record in sorted(recent, reverse=True)[:6]:
        try:
            snapshot = client.post_status(record["post_id"])
            delivery_checks += 1
            delivery = str(snapshot.get("status", "unknown")).lower()
            if delivery in {"error", "failed", "publishing_error"}:
                warnings.append(f"previous delivery failed: {label}")
        except BufferError as exc:
            warnings.append(f"could not recheck {label}: {str(exc)[:160]}")

    result = {
        "ready": not errors,
        "date": day.isoformat(),
        "channels": status["channels"],
        "captions_checked": len(SOCIAL_SLOTS) * len(TARGET_SERVICES),
        "assets_checked": len(checked_assets),
        "delivery_checks": delivery_checks,
        "warnings": warnings,
        "errors": errors,
    }
    if errors:
        raise BufferError(json.dumps(result, ensure_ascii=False))
    return result


def repair_future_posts(
    settings: Settings,
    day: date,
    state_path: Path = STATE_PATH,
    client: BufferClient | None = None,
    now: datetime | None = None,
) -> dict:
    """Update future queued posts in place with current captions, media and contact details."""
    queue_edit_safety_window = timedelta(minutes=15)
    client = client or BufferClient(settings.buffer_api_key)
    current = now or datetime.now(timezone.utc)
    state = _read_state(state_path)
    records = state.get("published_dates", {}).get(day.isoformat(), {})
    repaired: dict[str, str] = {}
    skipped: dict[str, str] = {}
    for state_key, record in records.items():
        slot = record.get("slot") or (state_key.split(":", 1)[0] if ":" in state_key else "morning")
        service = record.get("service") or (state_key.split(":", 1)[-1] if ":" in state_key else state_key)
        if slot not in SOCIAL_SLOTS or service not in TARGET_SERVICES:
            skipped[state_key] = "unsupported legacy record"
            continue
        try:
            due_at = datetime.fromisoformat(str(record.get("scheduled_for", "")).replace("Z", "+00:00"))
        except ValueError:
            skipped[state_key] = "invalid schedule"
            continue
        if due_at <= current + queue_edit_safety_window:
            skipped[state_key] = "already due or too close to publishing"
            continue
        snapshot = client.post_status(record["post_id"])
        if str(snapshot.get("status", "")).lower() in {"sent", "published"}:
            skipped[state_key] = "already published"
            continue
        products = deals_for_slot(day, slot)
        audience, learning_mode = learned_audience_for(products[1], day, state)
        caption = caption_for_platform(settings, day, service, audience, slot)
        media_url, media_type = media_url_for(day, service, slot)
        post = client.edit_media_post(
            record["post_id"],
            service,
            caption,
            media_url,
            f"{slot.title()} — 3 AI Tool Deals",
            media_type,
        )
        record.update({
            "post_id": post.get("id", record["post_id"]),
            "audience": audience.id,
            "learning_mode": learning_mode,
            "deal_ids": [product.id for product in products],
            "media_type": media_type,
            "contact_number": settings.whatsapp_number,
            "caption_version": 2,
            "repaired_at": current.isoformat(timespec="seconds"),
        })
        repaired[state_key] = record["post_id"]
        _write_state(state_path, state)
    return {"date": day.isoformat(), "repaired": repaired, "skipped": skipped}


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
    results = {
        "date": day.isoformat(),
        "campaigns": {},
        "scheduled": {},
        "skipped": [],
        "errors": {},
    }
    for slot in SOCIAL_SLOTS:
        products = deals_for_slot(day, slot)
        focus = products[1]
        audience, learning_mode = learned_audience_for(focus, day, state)
        results["campaigns"][slot] = {
            "products": [product.name for product in products],
            "audience": audience.label,
            "learning_mode": learning_mode,
            "creative_concept": creative_concept_for(day, slot),
        }
        for service in TARGET_SERVICES:
            state_key = f"{slot}:{service}"
            if state_key in day_state:
                results["skipped"].append(state_key)
                continue
            channel = channels[service]
            caption = caption_for_platform(settings, day, service, audience, slot)
            due_at = scheduled_time(settings, day, now, service, audience, slot)
            media_url, media_type = media_url_for(day, service, slot)
            try:
                create_post = client.create_video_post if media_type == "video" else client.create_image_post
                post = create_post(
                    channel["id"], service, caption, media_url, due_at, f"{slot.title()} — 3 AI Tool Deals"
                )
                day_state[state_key] = {
                    "post_id": post["id"],
                    "channel_id": channel["id"],
                    "scheduled_for": post.get("dueAt") or due_at.isoformat(),
                    "slot": slot,
                    "service": service,
                    "audience": audience.id,
                    "learning_mode": learning_mode,
                    "deal_ids": [product.id for product in products],
                    "media_type": media_type,
                    "creative_concept": creative_concept_for(day, slot),
                    "audio_theme": platform_audio_style(day, service) if media_type == "video" else None,
                    "audio_strategy": "platform-shaped-original-commercial-safe" if media_type == "video" else None,
                    "video_seconds": VIDEO_SPECS[service]["seconds"] if media_type == "video" else None,
                    "ai_disclosed": media_type == "video",
                    "contact_number": settings.whatsapp_number,
                    "caption_version": 2,
                    "recorded_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }
                results["scheduled"][state_key] = post["id"]
                _write_state(state_path, state)
            except BufferError as exc:
                results["errors"][state_key] = str(exc)
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
        "✅ Morning + evening social campaigns scheduled",
        "",
    ]
    labels = {"facebook": "Facebook", "instagram": "Instagram", "tiktok": "TikTok"}
    current_slot = ""
    for state_key in result["scheduled"]:
        slot, service = state_key.split(":", 1)
        if slot != current_slot:
            campaign = result.get("campaigns", {}).get(slot, {})
            products = campaign.get("products", [product.name for product in deals_for_slot(day, slot)])
            lines.extend([
                f"{slot.upper()}: {' + '.join(products)}",
                f"Audience: {campaign.get('audience', 'relevant Pakistan buyers')}",
                f"Creative: {campaign.get('creative_concept', creative_concept_for(day, slot))}",
            ])
            current_slot = slot
        record = day_state.get(state_key, {})
        scheduled = record.get("scheduled_for", "")
        try:
            local_time = datetime.fromisoformat(scheduled.replace("Z", "+00:00")).astimezone(settings.timezone)
            time_label = local_time.strftime("%I:%M %p PKT")
        except (TypeError, ValueError):
            time_label = "scheduled"
        media = "Reel/video" if record.get("media_type") == "video" else "photo post"
        audio = record.get("audio_theme")
        extra = f" • audio: {audio}" if audio else ""
        lines.append(f"• {labels[service]}: {media} • {time_label}{extra}")
        if service == TARGET_SERVICES[-1]:
            lines.append("")
    lines.extend([
        "",
        "Tracked product links and duplicate protection are active.",
        "Automatic-safe original audio is embedded; no manual posting is required.",
        "Native library trend songs remain platform-only and cannot be attached by Buffer automatic publishing.",
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
    checked, updated, errors, analytics_warnings = 0, 0, {}, {}
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
                delivery = client.post_status(record["post_id"])
                record["delivery_status"] = delivery.get("status", "unknown")
                record["delivery_checked_at"] = current.isoformat(timespec="seconds")
            except (BufferError, AttributeError) as exc:
                errors[f"{day_key}:{service}"] = str(exc)
            try:
                snapshot = client.post_metrics(record["post_id"])
                metrics = {
                    metric.get("type", metric.get("name", "unknown")): metric.get("value", 0)
                    for metric in snapshot.get("metrics", [])
                }
                record.update({
                    "delivery_status": snapshot.get("status", record.get("delivery_status", "unknown")),
                    "metrics": metrics,
                    "metrics_updated_at": snapshot.get("metricsUpdatedAt"),
                    "metrics_checked_on": current.date().isoformat(),
                })
                record.pop("metrics_error", None)
                updated += 1
            except BufferError as exc:
                record["metrics_error"] = str(exc)[:300]
                record["metrics_checked_on"] = current.date().isoformat()
                analytics_warnings[f"{day_key}:{service}"] = str(exc)
    _write_state(state_path, state)
    return {
        "checked": checked,
        "updated": updated,
        "delivery_errors": errors,
        "analytics_warnings": analytics_warnings,
    }


def delivery_audit(
    settings: Settings,
    day: date,
    state_path: Path = STATE_PATH,
    client: BufferClient | None = None,
    now: datetime | None = None,
    strict: bool = False,
) -> dict:
    """Verify that every daily post reached a terminal sent state after its due time."""
    client = client or BufferClient(settings.buffer_api_key)
    current = now or datetime.now(timezone.utc)
    state = _read_state(state_path)
    records = state.get("published_dates", {}).get(day.isoformat(), {})
    expected = {f"{slot}:{service}" for slot in SOCIAL_SLOTS for service in TARGET_SERVICES}
    missing = sorted(expected - set(records))
    sent: dict[str, str] = {}
    pending: dict[str, str] = {}
    failed: dict[str, str] = {}

    for state_key in sorted(expected & set(records)):
        record = records[state_key]
        try:
            snapshot = client.post_status(record["post_id"])
            status = str(snapshot.get("status", "unknown")).lower()
        except (BufferError, KeyError) as exc:
            failed[state_key] = f"status check failed: {str(exc)[:180]}"
            continue
        record["delivery_status"] = status
        record["delivery_checked_at"] = current.isoformat(timespec="seconds")
        if status in {"sent", "published"}:
            sent[state_key] = status
            continue
        if status in {"error", "failed", "publishing_error"}:
            failed[state_key] = status
            continue
        try:
            due_at = datetime.fromisoformat(str(record.get("scheduled_for", "")).replace("Z", "+00:00"))
        except ValueError:
            failed[state_key] = "invalid scheduled time"
            continue
        if due_at <= current - timedelta(minutes=45):
            failed[state_key] = f"stuck after due time ({status})"
        else:
            pending[state_key] = status

    _write_state(state_path, state)
    result = {
        "ok": not missing and not failed,
        "date": day.isoformat(),
        "expected": len(expected),
        "sent": sent,
        "pending": pending,
        "missing": missing,
        "failed": failed,
    }
    if strict and not result["ok"]:
        raise BufferError(json.dumps(result, ensure_ascii=False))
    return result
