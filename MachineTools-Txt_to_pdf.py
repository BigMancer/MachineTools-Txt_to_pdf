# coding: utf-8

# setting sts font utf-8
from hashlib import sha1
from reportlab.lib.pagesizes import A4
from reportlab.platypus import PageBreak
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.platypus import BaseDocTemplate, Frame, PageTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
import sys
import re

pdfmetrics.registerFont(TTFont('STSONG', 'FS_GB2312.ttf'))  # register Font
pdfmetrics.registerFont(TTFont('simhei', 'FS_GB2312.ttf'))  # register Font
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(fontName='STSONG', name='STSONG',
                          leading=20, fontSize=12, firstLineIndent=22, wordWrap='CJK'))
styles.add(ParagraphStyle(fontName='simhei', name='simhei',
                          leading=25, fontSize=14, wordWrap='CJK'))  # content Font


class MyDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        super().__init__(filename,**kw)

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if isinstance(flowable, Paragraph):
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                level = 0
            elif style == 'simhei':
                level = 1
            else:
                return
            E = [level, text, self.page]
            #if we have a bookmark name append that to our notify data
            bn = getattr(flowable,'_bookmarkName',None)
            if bn is not None: E.append(bn)
            self.notify('TOCEntry', tuple(E))


# # this function makes our headings
def doHeading(data, text, sty):
    # create bookmarkname
    bn = sha1(text.encode('utf-8')).hexdigest()
    # modify paragraph text to include an anchor point with name bn
    h = Paragraph(text + '<a name="%s"/>' % bn, sty)
    # store the bookmark name on the flowable so afterFlowable can see this
    h._bookmarkName = bn
    data.append(h)
    # Page Number


def footer(canvas, doc):
    page_num = canvas.getPageNumber()
    canvas.saveState()
    P = Paragraph("%d" % page_num,styles['Normal'])
    w, h = P.wrap(doc.width, doc.bottomMargin)
    P.drawOn(canvas, doc.leftMargin + w/2, h)
    canvas.restoreState()

    # load txt file


def loadTxt(txt_path):
    with open(txt_path, 'r') as f:
        txt_datas = f.readlines()
    return txt_datas


def toPDF(txt_datas, pdf_path):
    PDF = MyDocTemplate(pdf_path, pagesize=A4)
    frame = Frame(PDF.leftMargin, PDF.bottomMargin, PDF.width, PDF.height,id='normal')
    template = PageTemplate(frames=frame,onPage=footer)
    PDF.addPageTemplates([template])

    data = []
    NUM = 0
    # add txt
    for txt_data in txt_datas:
        txt_data = txt_data.lstrip()  # remove left space
        if len(txt_data) == 0:  # no text
            continue
        txt_data = txt_data
        a = re.findall(r'(第[0-9]{1,3}章：.*)|(续[0-9]{1,2})',txt_data)
    
        if len(a)!=0:
            doHeading(data, txt_data, styles['simhei'])
        else:
            data.append(Paragraph(txt_data, styles['STSONG']))
        NUM = NUM + 1
    PDF.multiBuild(data)

if __name__ == "__main__":
    txt_path = "我家老婆来自一千年前.txt"
    pdf_path = "我家老婆来自一千年前.pdf"
    txt_datas = loadTxt(txt_path)
    toPDF(txt_datas, pdf_path)
