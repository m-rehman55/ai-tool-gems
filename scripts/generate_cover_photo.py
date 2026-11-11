import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent

def generate_cover_photo():
    width, height = 1920, 1080
    cover = Image.new('RGB', (width, height), (11, 15, 25))
    draw = ImageDraw.Draw(cover)
    
    # 1. Subtle premium gradient background
    for y in range(height):
        ratio = y / height
        # Gradient from deep dark navy (11, 15, 25) to slate indigo (26, 36, 60)
        r = int(11 * (1 - ratio) + 24 * ratio)
        g = int(15 * (1 - ratio) + 32 * ratio)
        b = int(25 * (1 - ratio) + 54 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))
        
    # 2. Add subtle ambient glow orbs
    glow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    # Cyan glow on top-right
    glow_draw.ellipse([width - 500, -100, width + 300, 600], fill=(56, 189, 248, 45))
    # Purple/violet glow on bottom-left
    glow_draw.ellipse([-200, height - 500, 600, height + 300], fill=(168, 85, 247, 45))
    glow = glow.filter(ImageFilter.GaussianBlur(80))
    cover.paste(glow, (0, 0), glow)
    
    # 3. Add brand logo on the left/center
    logo_path = BASE / "assets" / "brand-logo-light.png"
    if logo_path.exists():
        logo_im = Image.open(logo_path).convert("RGBA")
        logo_w = 420
        ratio = logo_w / logo_im.width
        logo_h = int(logo_im.height * ratio)
        logo_resized = logo_im.resize((logo_w, logo_h), Image.Resampling.LANCZOS)
        # Position logo
        cover.paste(logo_resized, (140, 120), logo_resized)
        
    # Draw texts using default / system fonts
    draw = ImageDraw.Draw(cover)
    
    # Try loading clean Windows TrueType fonts
    font_paths = [
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]
    
    title_font = None
    sub_font = None
    badge_font = None
    
    for fp in font_paths:
        if os.path.exists(fp):
            try:
                title_font = ImageFont.truetype(fp, 72)
                sub_font = ImageFont.truetype(fp, 36)
                badge_font = ImageFont.truetype(fp, 26)
                break
            except Exception:
                pass
                
    if not title_font:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()
        badge_font = ImageFont.load_default()
        
    # Headline text
    text_x = 140
    text_y = 500
    draw.text((text_x, text_y), "PAKISTAN'S #1 AI TOOLS HUB", fill=(56, 189, 248), font=badge_font)
    draw.text((text_x, text_y + 40), "Official & Private AI Subscriptions", fill=(255, 255, 255), font=title_font)
    draw.text((text_x, text_y + 130), "ChatGPT Plus • Midjourney • Canva Pro • Claude • CapCut • Adobe", fill=(203, 213, 225), font=sub_font)
    draw.text((text_x, text_y + 185), "Instant 10-Min Delivery  |  100% Replacement Warranty  |  Best PKR Rates", fill=(148, 163, 184), font=badge_font)

    # 4. Draw Badges for Payment & Trust
    pill_y = 780
    pills = [
        ("⚡ Instant Activation (5-15 Mins)", (34, 197, 94)),
        ("🇵🇰 EasyPaisa / JazzCash / SadaPay / Bank", (59, 130, 246)),
        ("🔐 100% Private & Dedicated Accounts", (168, 85, 247)),
        ("🌐 aitoolgems.tech", (234, 179, 8))
    ]
    
    curr_x = text_x
    for text, border_col in pills:
        # Approximate width
        pill_w = len(text) * 15 + 40
        pill_h = 56
        # Draw pill box
        draw.rounded_rectangle([curr_x, pill_y, curr_x + pill_w, pill_y + pill_h], radius=28, fill=(15, 23, 42), outline=border_col, width=2)
        draw.text((curr_x + 20, pill_y + 14), text, fill=(241, 245, 249), font=badge_font)
        curr_x += pill_w + 24
        if curr_x > 1800:
            break

    # 5. Place Showcase Tool Logos in an aesthetic grid on the right side
    showcase_slugs = [
        "chatgpt", "canva", "midjourney",
        "claude", "capcut", "adobe",
        "elevenlabs", "leonardo", "cursor"
    ]
    
    grid_start_x = 1260
    grid_start_y = 140
    box_size = 140
    gap = 36
    
    for i, slug in enumerate(showcase_slugs):
        row = i // 3
        col = i % 3
        bx = grid_start_x + col * (box_size + gap)
        by = grid_start_y + row * (box_size + gap)
        
        # Draw glassy container
        draw.rounded_rectangle([bx, by, bx + box_size, by + box_size], radius=24, fill=(15, 23, 42), outline=(51, 65, 85), width=2)
        
        png_p = BASE / "assets" / "product-logos" / f"{slug}.png"
        if png_p.exists():
            t_im = Image.open(png_p).convert("RGBA")
            # Fit inside box
            pad = 32
            max_inner = box_size - pad
            r = min(max_inner / t_im.width, max_inner / t_im.height)
            tw, th = int(t_im.width * r), int(t_im.height * r)
            t_resized = t_im.resize((tw, th), Image.Resampling.LANCZOS)
            
            px = bx + (box_size - tw) // 2
            py = by + (box_size - th) // 2
            cover.paste(t_resized, (px, py), t_resized)

    # Save cover photo
    out_path = BASE / "assets" / "whatsapp_business_cover_photo.jpg"
    cover.save(out_path, quality=95)
    print(f"Generated WhatsApp Cover Photo at: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    generate_cover_photo()

