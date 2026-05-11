from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.ttLib.tables import _c_m_a_p
import copy
import os


# ── Config ────────────────────────────────────────────────
COMIC  = "fonts/ComicNeue/ComicNeue-BoldItalic.ttf"
NOTO   = "fonts/NotoSans/NotoSansSymbols2-Regular.ttf"
OUTPUT = "fonts/Merge/ComicNeueSymbols-BoldItalic.ttf"
# ──────────────────────────────────────────────────────────

print("Loading fonts...")
comic = TTFont(COMIC)
noto  = TTFont(NOTO)

# Find missing codepoints
comic_cmap = comic.getBestCmap()
noto_cmap  = noto.getBestCmap()
missing    = set(noto_cmap.keys()) - set(comic_cmap.keys())
print(f"Glyphs to import: {len(missing)}")

# Subset Noto to only missing glyphs
print("Subsetting Noto...")
opts = subset.Options()
opts.layout_features = []
opts.name_IDs        = []
opts.notdef_outline  = True
ss = subset.Subsetter(options=opts)
ss.populate(unicodes=missing)
ss.subset(noto)

noto_cmap_after  = noto.getBestCmap()
noto_glyph_order = [g for g in noto.getGlyphOrder() if g != ".notdef"]

# 1. Copy glyph outlines (glyf table)
print("Copying glyph outlines...")
for gname in noto_glyph_order:
    if gname not in comic['glyf'].keys():
        comic['glyf'][gname] = copy.deepcopy(noto['glyf'][gname])

# 2. Copy horizontal metrics (hmtx table)
print("Copying metrics...")
for gname in noto_glyph_order:
    if gname not in comic['hmtx'].metrics:
        comic['hmtx'].metrics[gname] = noto['hmtx'].metrics[gname]

# 3. Update glyph order
existing   = set(comic.getGlyphOrder())
new_glyphs = [g for g in noto_glyph_order if g not in existing]
comic.setGlyphOrder(comic.getGlyphOrder() + new_glyphs)

# 4. Update cmap — respect each subtable's codepoint range
print("Updating cmap...")

bmp     = {cp: g for cp, g in noto_cmap_after.items() if cp <= 0xFFFF and cp not in comic_cmap}
non_bmp = {cp: g for cp, g in noto_cmap_after.items() if cp >  0xFFFF and cp not in comic_cmap}

# Add BMP symbols to existing subtables (format 4 supports up to 0xFFFF)
for table in comic['cmap'].tables:
    if table.format == 4:
        table.cmap.update(bmp)

# For non-BMP (> 0xFFFF), we need a format 12 subtable
# Check if one already exists, otherwise create it
fmt12 = next((t for t in comic['cmap'].tables if t.format == 12), None)

if fmt12 is None and non_bmp:
    print("Creating format 12 cmap subtable for non-BMP symbols...")
    fmt12 = _c_m_a_p.cmap_format_12(12)
    fmt12.platEncID = 3
    fmt12.platformID = 3
    fmt12.language = 0
    fmt12.cmap = {}
    comic['cmap'].tables.append(fmt12)

if fmt12 is not None:
    fmt12.cmap.update(non_bmp)
    # Also add BMP glyphs to fmt12 so it's a complete map
    fmt12.cmap.update(bmp)

print(f"  BMP symbols added:     {len(bmp)}")
print(f"  Non-BMP symbols added: {len(non_bmp)}")

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)  # ← add this
comic.save(OUTPUT)
print(f"Done! Saved as: {OUTPUT}")