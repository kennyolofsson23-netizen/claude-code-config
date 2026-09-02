---
name: feedback_favicon_rgba_nextjs
description: Next.js 16 Turbopack requires RGBA format PNGs inside .ico files — non-RGBA causes build failure
type: feedback
---

When generating favicon.ico for Next.js 16+ (Turbopack), all embedded PNGs must be in RGBA format.

**Why:** Turbopack's image processing rejects non-RGBA PNGs with: "Format error decoding Ico: The PNG is not in RGBA format!" — build fails completely.

**How to apply:** When using Pillow to create .ico files, always call `.convert('RGBA')` on both the source image and each resized icon before saving. Place favicon.ico in `src/app/` for App Router convention.
