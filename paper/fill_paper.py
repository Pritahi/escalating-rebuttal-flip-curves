#!/usr/bin/env python3
"""Fill the Apart sprint template.docx with final paper content.

Usage: python3 fill_paper.py   (reads CONTENT spec from paper_content.py)
Produces submission.docx
"""
import docx, copy
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

TEMPLATE = '/home/sandbox/apart/template.docx'
OUT = '/home/sandbox/apart/submission.docx'

def find_headings(doc):
    """map heading text -> paragraph index"""
    h = {}
    for i, p in enumerate(doc.paragraphs):
        if p.style.name.startswith('Heading') and p.text.strip():
            h[p.text.strip()] = i
    return h

def clear_between(doc, start_idx, end_idx):
    """delete paragraphs between two indices (exclusive)"""
    body = doc.element.body
    for p in doc.paragraphs[start_idx+1:end_idx]:
        p._element.getparent().remove(p._element)

def insert_para_before(anchor_para, text, style=None, bold=False, size=None, align=None, space_after=6):
    p = anchor_para.insert_paragraph_before('')
    r = p.add_run(text)
    r.bold = bold
    if size: r.font.size = Pt(size)
    if style: p.style = style
    if align is not None: p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    return p

def insert_bullet_before(anchor_para, text):
    p = anchor_para.insert_paragraph_before('', style='List Bullet')
    p.add_run(text)
    p.paragraph_format.space_after = Pt(3)
    return p

def insert_figure_before(doc, anchor_para, image_path, caption, width_in=6.3):
    p = anchor_para.insert_paragraph_before('')
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    r.add_picture(image_path, width=Inches(width_in))
    cap = anchor_para.insert_paragraph_before('')
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cr = cap.add_run(caption)
    cr.font.size = Pt(8); cr.italic = True
    cap.paragraph_format.space_after = Pt(8)
    return p

def insert_table_before(doc, anchor_para, headers, rows, caption=None, col_width=None):
    if caption:
        cap = anchor_para.insert_paragraph_before('')
        cr = cap.add_run(caption)
        cr.font.size = Pt(9); cr.bold = True
        cap.paragraph_format.space_after = Pt(2)
    t = doc.add_table(rows=1+len(rows), cols=len(headers))
    t.style = 'Table Grid'
    for j, h in enumerate(headers):
        cell = t.rows[0].cells[j]
        cell.text = h
        for para in cell.paragraphs:
            for r in para.runs: r.bold = True; r.font.size = Pt(8)
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            cell = t.rows[i+1].cells[j]
            cell.text = str(v)
            for para in cell.paragraphs:
                for r in para.runs: r.font.size = Pt(8)
    # move table xml before anchor
    anchor_para._p.addprevious(t._tbl)
    sp = anchor_para.insert_paragraph_before('')
    sp.paragraph_format.space_after = Pt(8)
    return t

def fill(spec):
    doc = docx.Document(TEMPLATE)

    # title + abstract table (table 0: row0 title, row1 abstract)
    t0 = doc.tables[0]
    t0.rows[0].cells[0].text = spec['title']
    for para in t0.rows[0].cells[0].paragraphs:
        for r in para.runs: r.font.size = Pt(16); r.bold = True
    t0.rows[1].cells[0].text = spec['abstract']
    for para in t0.rows[1].cells[0].paragraphs:
        for r in para.runs: r.font.size = Pt(9)

    # author line: insert after table
    h = find_headings(doc)

    # delete the "How to use this template" table if present
    if len(doc.tables) > 1:
        t1 = doc.tables[1]
        t1._tbl.getparent().remove(t1._tbl)

    h = find_headings(doc)
    sections = list(h.items())  # ordered by document position? find_headings iterates in order, yes
    names = [n for n, _ in sections]

    def anchor_for(section_name):
        """the paragraph before which content should go = next heading after section"""
        idx = h[section_name]
        following = [i for n, i in h.items() if i > idx]
        nxt = min(following) if following else len(doc.paragraphs)
        return idx, nxt

    # process sections from LAST to FIRST so indices stay valid
    order = ['1. Introduction', '2. Related Work', '3. Methods', '4. Results',
             '5. Discussion and Limitations', 'Limitations', 'Future Work', '6. Conclusion',
             'Code and Data', 'Author Contributions (optional)', 'References',
             'Appendix (optional)', 'LLM Usage Statement']
    content = spec['sections']
    for name in reversed(order):
        if name not in h: continue
        idx, nxt = anchor_for(name)
        anchor = doc.paragraphs[nxt] if nxt < len(doc.paragraphs) else None
        clear_between(doc, idx, nxt)
        items = content.get(name, [])
        if anchor is None:
            # append at end
            for it in items:
                add_item_end(doc, it)
        else:
            for it in items:
                add_item(doc, anchor, it)
        # refresh headings (paragraph list changed; heading objects persist via element refs)
        h = find_headings(doc)

    # remove empty optional sections
    for opt in ['Author Contributions (optional)']:
        h = find_headings(doc)
        if opt in h and opt not in content:
            idx, nxt = anchor_for(opt)
            clear_between(doc, idx-1 if False else idx, idx+1)  # remove the heading itself
            # also clear anything between it and next heading
            h2 = find_headings(doc)

    doc.save(OUT)
    print('saved', OUT)

def add_item(doc, anchor, it):
    kind = it[0]
    if kind == 'p': insert_para_before(anchor, it[1])
    elif kind == 'bullet': insert_bullet_before(anchor, it[1])
    elif kind == 'fig': insert_figure_before(doc, anchor, it[1], it[2])
    elif kind == 'table': insert_table_before(doc, anchor, it[1], it[2], caption=it[3] if len(it) > 3 else None)

def add_item_end(doc, it):
    kind = it[0]
    if kind == 'p':
        p = doc.add_paragraph(it[1]); return p
    elif kind == 'bullet': return doc.add_paragraph(it[1], style='List Bullet')

if __name__ == '__main__':
    import paper_content
    fill(paper_content.SPEC)
