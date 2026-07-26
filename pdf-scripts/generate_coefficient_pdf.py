#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将晶振校准 Coefficient 研究报告 Markdown 转换为 PDF
使用 reportlab + Noto Sans CJK SC 字体
"""

import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily

# 注册中文字体
FONT_DIR = '/root/.codebuddy/artifact/5d808dc5-86f6-400c-8e9c-4969e8827f4c'
pdfmetrics.registerFont(TTFont('NotoSansCJK', f'{FONT_DIR}/NotoSansSC-Regular.ttf'))
pdfmetrics.registerFont(TTFont('NotoSansCJK-Bold', f'{FONT_DIR}/NotoSansSC-Bold.ttf'))
registerFontFamily('NotoSansCJK', normal='NotoSansCJK', bold='NotoSansCJK-Bold', italic='NotoSansCJK', boldItalic='NotoSansCJK-Bold')

# 颜色定义
COLOR_H2 = HexColor('#1565c0')
COLOR_H3 = HexColor('#1976d2')
COLOR_BODY = HexColor('#212121')
COLOR_LINK = HexColor('#1565c0')


def create_styles():
    styles = {}
    
    styles['H1'] = ParagraphStyle(
        name='H1',
        fontName='NotoSansCJK-Bold',
        fontSize=16,
        leading=24,
        textColor=HexColor('#283593'),
        spaceBefore=8*mm,
        spaceAfter=4*mm,
    )
    
    styles['H2'] = ParagraphStyle(
        name='H2',
        fontName='NotoSansCJK-Bold',
        fontSize=13,
        leading=20,
        textColor=COLOR_H2,
        spaceBefore=6*mm,
        spaceAfter=3*mm,
    )
    
    styles['H3'] = ParagraphStyle(
        name='H3',
        fontName='NotoSansCJK-Bold',
        fontSize=11.5,
        leading=18,
        textColor=COLOR_H3,
        spaceBefore=4*mm,
        spaceAfter=2*mm,
    )
    
    styles['BodyCN'] = ParagraphStyle(
        name='BodyCN',
        fontName='NotoSansCJK',
        fontSize=10,
        leading=17,
        alignment=TA_JUSTIFY,
        textColor=COLOR_BODY,
        spaceAfter=3*mm,
        firstLineIndent=20,
    )
    
    styles['Reference'] = ParagraphStyle(
        name='Reference',
        fontName='NotoSansCJK',
        fontSize=8.5,
        leading=14,
        alignment=TA_LEFT,
        textColor=HexColor('#424242'),
        spaceAfter=1.5*mm,
        leftIndent=8*mm,
        firstLineIndent=-8*mm,
    )
    
    return styles


def escape_xml(text):
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def convert_inline_formatting(text):
    text = escape_xml(text)
    text = re.sub(r'`([^`]+)`', r'<font face="NotoSansCJK" color="#c62828"><b>\1</b></font>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<font color="#1565c0">\1</font>', text)
    text = text.replace('ᵀ', '<super>T</super>')
    return text


def parse_markdown(md_text):
    styles = create_styles()
    story = []
    
    # 需要跳过的小标题（但不跳过其正文内容）
    skip_headings = {'执行摘要', '技术背景'}
    
    lines = md_text.split('\n')
    i = 0
    in_references = False
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        if not stripped:
            i += 1
            continue
        
        # 主标题（# 开头）- 跳过不显示
        if stripped.startswith('# ') and not stripped.startswith('## '):
            i += 1
            continue
        
        if stripped.startswith('### '):
            story.append(Paragraph(convert_inline_formatting(stripped[4:]), styles['H3']))
            i += 1
            continue
        
        if stripped.startswith('## '):
            heading_text = stripped[3:]
            # 跳过指定的小标题，但保留正文
            if heading_text in skip_headings:
                i += 1
                continue
            if '参考资料' in heading_text or 'References' in heading_text:
                in_references = True
            story.append(Paragraph(convert_inline_formatting(heading_text), styles['H2']))
            i += 1
            continue
        
        # 分隔线
        if stripped == '---':
            story.append(Spacer(1, 4*mm))
            i += 1
            continue
        
        # 参考资料列表项
        if in_references and re.match(r'^\d+\.\s+\[', stripped):
            match = re.match(r'^(\d+)\.\s+\[([^\]]+)\]\(([^\)]+)\)', stripped)
            if match:
                num = match.group(1)
                title = match.group(2)
                url = match.group(3)
                link_text = f'{num}. <a href="{url}"><font color="#1565c0">{escape_xml(title)}</font></a>'
                story.append(Paragraph(link_text, styles['Reference']))
            i += 1
            continue
        
        # 普通段落
        para_lines = [stripped]
        j = i + 1
        while j < len(lines):
            next_line = lines[j].strip()
            if not next_line:
                break
            if next_line.startswith('#') or next_line.startswith('---'):
                break
            para_lines.append(next_line)
            j += 1
        
        para_text = ' '.join(para_lines)
        para_text = convert_inline_formatting(para_text)
        
        if in_references:
            story.append(Paragraph(para_text, styles['Reference']))
        else:
            story.append(Paragraph(para_text, styles['BodyCN']))
        
        i = j
    
    return story


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont('NotoSansCJK', 8)
    canvas.setFillColor(HexColor('#9e9e9e'))
    page_num = canvas.getPageNumber()
    text = f"— {page_num} —"
    canvas.drawCentredString(A4[0] / 2, 1.2 * cm, text)
    canvas.restoreState()


def main():
    input_file = '/workspace/research_report_crystal_oscillator_coefficient.md'
    output_file = '/workspace/research_report_crystal_oscillator_coefficient.pdf'
    
    with open(input_file, 'r', encoding='utf-8') as f:
        md_text = f.read()
    
    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        rightMargin=2.2*cm,
        leftMargin=2.2*cm,
        topMargin=2.0*cm,
        bottomMargin=2.0*cm,
        title='晶振校准中的 Coefficient 研究报告',
        author='Research Agent',
    )
    
    story = parse_markdown(md_text)
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    
    print(f"PDF 已生成: {output_file}")


if __name__ == '__main__':
    main()
