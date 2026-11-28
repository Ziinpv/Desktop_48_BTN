# -*- coding: utf-8 -*-
"""Xuất báo cáo Markdown của đồ án môn học ra file Word."""

import re
from pathlib import Path

from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Mm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "BaoCaoTongKet_DoAnMonHoc_PhatTrienUngDungDesktop.md"
OUT = ROOT / "BaoCaoTongKet_DoAnMonHoc_PhatTrienUngDungDesktop.docx"

NAVY = RGBColor(0x1F, 0x4E, 0x79)
BODY = RGBColor(0x1A, 0x1A, 0x1A)
MUTED = RGBColor(0x55, 0x55, 0x55)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
HEADER_FILL = "1F4E79"
PLACEHOLDER_FILL = "FFF6E0"
CODE_FILL = "F4F6F8"
ZEBRA = "F7F9FB"

TOKEN = re.compile(r"(`[^`]+`|\*\*[^*]+?\*\*|\*[^*]+?\*)")


def set_run_font(run, name, size, bold=False, italic=False, color=None):
    run.font.name = name
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    if color is not None:
        run.font.color.rgb = color
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), name)


def paragraph_border_bottom(paragraph, color="1F4E79"):
    pPr = paragraph._p.get_or_add_pPr()
    pBdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), color)
    pBdr.append(bottom)
    pPr.append(pBdr)


def keep_with_next(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    el = OxmlElement("w:keepNext")
    pPr.append(el)


def outline_level(paragraph, level):
    pPr = paragraph._p.get_or_add_pPr()
    el = OxmlElement("w:outlineLvl")
    el.set(qn("w:val"), str(level))
    pPr.append(el)


def shade_cell(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def set_cell_borders(cell, color="BFBFBF", sz="4"):
    tcPr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    for edge in ("top", "left", "bottom", "right"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), sz)
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tcPr.append(borders)


def set_table_full_width(table):
    tbl = table._tbl
    tblPr = tbl.tblPr
    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.append(tblW)
    tblW.set(qn("w:w"), "5000")
    tblW.set(qn("w:type"), "pct")
    tblLayout = tblPr.find(qn("w:tblLayout"))
    if tblLayout is None:
        tblLayout = OxmlElement("w:tblLayout")
        tblPr.append(tblLayout)
    tblLayout.set(qn("w:type"), "fixed")


def prevent_row_split(row):
    trPr = row._tr.get_or_add_trPr()
    cant = OxmlElement("w:cantSplit")
    trPr.append(cant)


def mark_header_row(row):
    trPr = row._tr.get_or_add_trPr()
    hdr = OxmlElement("w:tblHeader")
    trPr.append(hdr)


def add_page_field(paragraph):
    run1 = paragraph.add_run()
    set_run_font(run1, "Times New Roman", 10, color=MUTED)
    fld_begin = OxmlElement("w:fldChar")
    fld_begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    fld_end = OxmlElement("w:fldChar")
    fld_end.set(qn("w:fldCharType"), "end")
    run1._r.append(fld_begin)
    run1._r.append(instr)
    run1._r.append(fld_end)


def add_inline(paragraph, text, size, color, font="Times New Roman", force_bold=False, force_italic=False):
    if text is None:
        return
    parts = TOKEN.split(text)
    for part in parts:
        if not part:
            continue
        bold = force_bold
        italic = force_italic
        use_font = font
        content = part
        if part.startswith("`") and part.endswith("`"):
            content = part[1:-1]
            use_font = "Consolas"
            size_here = max(9, size - 1)
        elif part.startswith("**") and part.endswith("**"):
            content = part[2:-2]
            bold = True
            size_here = size
        elif part.startswith("*") and part.endswith("*") and not part.startswith("**"):
            content = part[1:-1]
            italic = True
            size_here = size
        else:
            size_here = size
        run = paragraph.add_run(content)
        set_run_font(run, use_font, size_here, bold=bold, italic=italic, color=color)


def is_caption(text):
    plain = re.sub(r"[*`]", "", text).strip()
    if plain.startswith("Bảng "):
        return "table"
    if plain.startswith("Hình "):
        return "figure"
    return None


def split_row(line):
    raw = line.strip()
    if raw.startswith("|"):
        raw = raw[1:]
    if raw.endswith("|"):
        raw = raw[:-1]
    return [cell.strip() for cell in raw.split("|")]


def is_separator(cells):
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in cells)


class Builder:
    def __init__(self):
        self.doc = Document()
        self.cover = True
        self._setup()

    def _setup(self):
        section = self.doc.sections[0]
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.left_margin = Cm(3)
        section.right_margin = Cm(2)
        section.top_margin = Cm(2)
        section.bottom_margin = Cm(1.8)
        section.header_distance = Cm(0.6)
        section.footer_distance = Cm(0.6)
        section.different_first_page_header_footer = True

        sectPr = section._sectPr
        pgNumType = sectPr.find(qn("w:pgNumType"))
        if pgNumType is None:
            pgNumType = OxmlElement("w:pgNumType")
            sectPr.append(pgNumType)
        pgNumType.set(qn("w:start"), "0")

        normal = self.doc.styles["Normal"]
        normal.font.name = "Times New Roman"
        normal.font.size = Pt(13)
        normal.font.color.rgb = BODY
        rPr = normal.element.get_or_add_rPr()
        rFonts = rPr.find(qn("w:rFonts"))
        if rFonts is None:
            rFonts = OxmlElement("w:rFonts")
            rPr.append(rFonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
            rFonts.set(qn(attr), "Times New Roman")

        header = section.header
        header.is_linked_to_previous = False
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        run = hp.add_run("Báo cáo tổng kết đồ án môn học  ·  Phát triển Ứng dụng Desktop")
        set_run_font(run, "Times New Roman", 9, italic=True, color=MUTED)
        paragraph_border_bottom(hp)

        footer = section.footer
        footer.is_linked_to_previous = False
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        label = fp.add_run("Trang ")
        set_run_font(label, "Times New Roman", 10, color=MUTED)
        add_page_field(fp)

        # Trang bìa không hiện header/footer
        section.first_page_header.paragraphs[0].text = ""
        section.first_page_footer.paragraphs[0].text = ""

        core = self.doc.core_properties
        core.title = "Báo cáo tổng kết đồ án môn học Phát triển Ứng dụng Desktop"
        core.subject = "LUXE Wedding Studio — Nhóm 24"
        core.author = "Hoàng Long — 2212407"
        core.category = "Báo cáo đồ án môn học"
        core.language = "vi-VN"

    def _base_format(self, paragraph, align, before=0, after=6, line=1.15, size_line=None):
        fmt = paragraph.paragraph_format
        fmt.alignment = align
        fmt.space_before = Pt(before)
        fmt.space_after = Pt(after)
        fmt.line_spacing = line
        fmt.line_spacing_rule = WD_LINE_SPACING.MULTIPLE

    def add_picture(self, rel):
        path = (ROOT / rel).resolve()
        p = self.doc.add_paragraph()
        self._base_format(p, WD_ALIGN_PARAGRAPH.CENTER, 8, 2, 1.0)
        if not path.exists():
            add_inline(p, f"[Không thấy ảnh {rel}]", 12, RGBColor(0x8A, 0x5A, 0x00), force_italic=True)
            return p
        try:
            from PIL import Image as PILImage

            with PILImage.open(path) as im:
                pw, ph = im.size
        except Exception:
            pw, ph = 1600, 2200
        max_w, max_h = 15.6, 22.5
        width = max_w
        height = width * ph / pw
        if height > max_h:
            height = max_h
            width = height * pw / ph
        run = p.add_run()
        run.add_picture(str(path), width=Cm(width))
        return p

    def add_heading_text(self, text, level):
        p = self.doc.add_paragraph()
        if level == 1 and not self.cover:
            p.paragraph_format.page_break_before = True
        if self.cover:
            align = WD_ALIGN_PARAGRAPH.CENTER
            size = 18 if level == 1 else 16
            before, after = (0, 6) if level > 1 else (18, 8)
            color = NAVY
        elif level == 1:
            align = WD_ALIGN_PARAGRAPH.CENTER
            size, before, after, color = 16, 0, 12, NAVY
        elif level == 2:
            align = WD_ALIGN_PARAGRAPH.LEFT
            size, before, after, color = 14, 14, 6, NAVY
        else:
            align = WD_ALIGN_PARAGRAPH.LEFT
            size, before, after, color = 13, 10, 4, RGBColor(0x2E, 0x50, 0x90)
        self._base_format(p, align, before, after, 1.08)
        add_inline(p, text, size, color, force_bold=True)
        outline_level(p, level - 1)
        keep_with_next(p)
        return p

    def add_body(self, text, kind="body", level=0):
        p = self.doc.add_paragraph()
        caption = is_caption(text)
        if self.cover and kind == "body":
            self._base_format(p, WD_ALIGN_PARAGRAPH.CENTER, 2, 4, 1.15)
            add_inline(p, text, 13, BODY)
            return p
        if caption == "table":
            self._base_format(p, WD_ALIGN_PARAGRAPH.CENTER, 12, 4, 1.08)
            add_inline(p, text, 12, NAVY, force_bold=True)
            keep_with_next(p)
            return p
        if caption == "figure":
            self._base_format(p, WD_ALIGN_PARAGRAPH.CENTER, 4, 12, 1.08)
            add_inline(p, text, 12, NAVY, force_bold=True, force_italic=True)
            return p
        if kind == "quote":
            self._base_format(p, WD_ALIGN_PARAGRAPH.LEFT, 6, 6, 1.15)
            p.paragraph_format.left_indent = Cm(1)
            p.paragraph_format.right_indent = Cm(0.5)
            add_inline(p, text, 12, MUTED, force_italic=True)
            return p
        if kind == "bullet":
            self._base_format(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 1, 2, 1.15)
            extra = 0.75 * max(level, 0)
            p.paragraph_format.left_indent = Cm(1.0 + extra)
            p.paragraph_format.first_line_indent = Cm(-0.4)
            add_inline(p, "•  " + text, 13, BODY)
            return p
        if kind == "number":
            self._base_format(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 1, 3, 1.15)
            p.paragraph_format.left_indent = Cm(1.0)
            p.paragraph_format.first_line_indent = Cm(-0.45)
            add_inline(p, text, 13, BODY)
            return p
        if kind == "ref":
            self._base_format(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 0, 4, 1.15)
            p.paragraph_format.left_indent = Cm(0.75)
            p.paragraph_format.first_line_indent = Cm(-0.75)
            add_inline(p, text, 12, BODY)
            return p
        if "[Chèn ảnh" in text or text.strip().startswith("[Chèn"):
            self._base_format(p, WD_ALIGN_PARAGRAPH.CENTER, 8, 2, 1.15)
            add_inline(p, text, 12, RGBColor(0x8A, 0x5A, 0x00), force_italic=True)
            keep_with_next(p)
            # nền nhạt để thấy vùng cần dán ảnh
            pPr = p._p.get_or_add_pPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:color"), "auto")
            shd.set(qn("w:fill"), PLACEHOLDER_FILL)
            pPr.append(shd)
            return p
        self._base_format(p, WD_ALIGN_PARAGRAPH.JUSTIFY, 0, 6, 1.15)
        add_inline(p, text, 13, BODY)
        return p

    def add_code(self, lines):
        text = "\n".join(lines)
        p = self.doc.add_paragraph()
        self._base_format(p, WD_ALIGN_PARAGRAPH.LEFT, 6, 4, 1.0)
        p.paragraph_format.left_indent = Cm(0.2)
        run = p.add_run(text)
        set_run_font(run, "Consolas", 9, color=RGBColor(0x1E, 0x29, 0x3B))
        pPr = p._p.get_or_add_pPr()
        shd = OxmlElement("w:shd")
        shd.set(qn("w:val"), "clear")
        shd.set(qn("w:color"), "auto")
        shd.set(qn("w:fill"), CODE_FILL)
        pPr.append(shd)
        keep_with_next(p)

    def add_table(self, rows):
        if len(rows) < 2:
            return
        header = rows[0]
        body = [r for r in rows[1:] if not is_separator(r)]
        cols = max(len(header), max((len(r) for r in body), default=0))
        table = self.doc.add_table(rows=1 + len(body), cols=cols)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = True
        set_table_full_width(table)

        def norm(row):
            row = list(row) + [""] * (cols - len(row))
            return row[:cols]

        header = norm(header)
        for c, value in enumerate(header):
            cell = table.rows[0].cells[c]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            shade_cell(cell, HEADER_FILL)
            set_cell_borders(cell, "1F4E79", "4")
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.05
            add_inline(p, value, 10, WHITE, force_bold=True)
        mark_header_row(table.rows[0])
        prevent_row_split(table.rows[0])

        for r_idx, row in enumerate(body):
            values = norm(row)
            for c, value in enumerate(values):
                cell = table.rows[r_idx + 1].cells[c]
                cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.TOP
                if r_idx % 2 == 1:
                    shade_cell(cell, ZEBRA)
                set_cell_borders(cell)
                p = cell.paragraphs[0]
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.05
                add_inline(p, value, 10.5, BODY)
            prevent_row_split(table.rows[r_idx + 1])

        # khoảng trống sau bảng
        spacer = self.doc.add_paragraph()
        spacer.paragraph_format.space_before = Pt(0)
        spacer.paragraph_format.space_after = Pt(6)

    def render_cover(self, lines):
        """Trang bìa: tên trường ở trên, tên báo cáo ở giữa, đúng thứ tự nộp bài."""
        blocks = []
        i = 0
        n = len(lines)
        while i < n:
            stripped = lines[i].strip()
            if not stripped:
                i += 1
                continue
            if stripped.startswith("|"):
                rows = []
                while i < n and lines[i].strip().startswith("|"):
                    rows.append(split_row(lines[i]))
                    i += 1
                blocks.append(("table", rows))
                continue
            if stripped.startswith("#"):
                level = len(stripped) - len(stripped.lstrip("#"))
                text = stripped[level:].strip()
                blocks.append(("h", level, text))
                i += 1
                continue
            if stripped.startswith("> "):
                blocks.append(("quote", stripped[2:].strip()))
                i += 1
                continue
            blocks.append(("p", stripped))
            i += 1

        def is_school(block):
            if block[0] != "p":
                return False
            plain = re.sub(r"[*`]", "", block[1])
            return "TRƯỜNG ĐẠI HỌC" in plain or "KHOA CÔNG NGHỆ" in plain

        school = [b for b in blocks if is_school(b)]
        titles = [b for b in blocks if b[0] == "h"]
        h2_text = {b[2] for b in titles if b[1] == 2}
        titles = [b for b in titles if not (b[1] == 1 and b[2] in h2_text)]
        rest = [b for b in blocks if b not in school and b not in titles and not (b[0] == "h" and b[1] == 1 and b[2] in h2_text)]

        for _ in range(2):
            sp = self.doc.add_paragraph()
            sp.paragraph_format.space_after = Pt(0)

        for block in school:
            plain = re.sub(r"[*`]", "", block[1]).strip()
            p = self.doc.add_paragraph()
            self._base_format(p, WD_ALIGN_PARAGRAPH.CENTER, 0, 2, 1.0)
            size = 14 if "TRƯỜNG" in plain else 13
            add_inline(p, plain, size, NAVY, force_bold=True)

        rule = self.doc.add_paragraph()
        self._base_format(rule, WD_ALIGN_PARAGRAPH.CENTER, 2, 10, 1.0)
        paragraph_border_bottom(rule, "1F4E79")

        for _ in range(1):
            sp = self.doc.add_paragraph()
            sp.paragraph_format.space_after = Pt(0)

        for block in titles:
            level = block[1]
            p = self.doc.add_paragraph()
            self._base_format(p, WD_ALIGN_PARAGRAPH.CENTER, 4, 2, 1.05)
            size = 20 if level >= 2 and "PHÁT TRIỂN" in block[2] else 16
            add_inline(p, block[2], size, NAVY, force_bold=True)

        gap = self.doc.add_paragraph()
        gap.paragraph_format.space_after = Pt(8)

        for block in rest:
            if block[0] == "table":
                self.add_table(block[1])
            elif block[0] == "quote":
                self.add_body(block[1], "quote")
            else:
                self.add_body(block[1], "body")

    def build(self, lines):
        cover_end = next((idx for idx, line in enumerate(lines) if line.strip() == "---"), None)
        if cover_end is not None:
            self.render_cover(lines[:cover_end])
            self.cover = False
            lines = lines[cover_end:]

        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]
            stripped = line.strip()

            if stripped == "---":
                j = i + 1
                while j < n and not lines[j].strip():
                    j += 1
                nxt = lines[j].strip() if j < n else ""
                self.cover = False
                if not nxt.startswith("# "):
                    self.doc.add_page_break()
                i += 1
                continue

            img_m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", stripped)
            if img_m:
                self.add_picture(img_m.group(2))
                i += 1
                continue

            if stripped.startswith("```"):
                i += 1
                buf = []
                while i < n and not lines[i].strip().startswith("```"):
                    buf.append(lines[i].rstrip())
                    i += 1
                if i < n:
                    i += 1
                self.add_code(buf)
                continue

            if stripped.startswith("|"):
                buf = []
                while i < n and lines[i].strip().startswith("|"):
                    buf.append(split_row(lines[i]))
                    i += 1
                self.add_table(buf)
                continue

            if stripped.startswith("### "):
                self.add_heading_text(stripped[4:].strip(), 3)
                i += 1
                continue
            if stripped.startswith("## "):
                self.add_heading_text(stripped[3:].strip(), 2)
                i += 1
                continue
            if stripped.startswith("# "):
                self.add_heading_text(stripped[2:].strip(), 1)
                i += 1
                continue

            if not stripped:
                i += 1
                continue

            if stripped.startswith("> "):
                self.add_body(stripped[2:].strip(), "quote")
                i += 1
                continue

            m_num = re.match(r"^(\d+)\.\s+(.*)$", stripped)
            if m_num and not self.cover:
                self.add_body(f"{m_num.group(1)}.  {m_num.group(2)}", "number")
                i += 1
                continue

            if stripped.startswith("- "):
                level = (len(line) - len(line.lstrip(" "))) // 2
                self.add_body(stripped[2:].strip(), "bullet", level=level)
                i += 1
                continue

            if re.match(r"^\[\d+\]", stripped):
                self.add_body(stripped, "ref")
                i += 1
                continue

            self.add_body(stripped, "body")
            i += 1

        self.doc.save(OUT)


def main():
    text = SRC.read_text(encoding="utf-8")
    Builder().build(text.splitlines())
    print(OUT)


if __name__ == "__main__":
    main()
