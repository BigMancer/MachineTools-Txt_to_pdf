import re

from PyPDF2 import PdfFileReader as pdfr
from PyPDF2 import PdfFileWriter as pdfw
from reportlab.lib.styles import ParagraphStyle as PS
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak
from reportlab.platypus.doctemplate import BaseDocTemplate, PageTemplate
from reportlab.platypus.frames import Frame
from reportlab.platypus.paragraph import Paragraph
from reportlab.platypus.tableofcontents import TableOfContents

pattern =  re.compile(r'(第[0-9]{1,3}章：.*)|(续[0-9]{1,2})')
# 目录的正则表达式
txt_path = "我家老婆来自一千年前.txt"
# 源文件路径
aim_pdf_path='我家老婆来自一千年前.pdf'
# 目的PDF路径
function_switch = {
    "add_big_toc":0,
    "build_toc":0,
    # 生成页面目录
    "build_left_bookmark":1
    # 生成左边栏书签
}
# 三个功能的开关




pdfmetrics.registerFont(TTFont('FS_GB2312', 'FS_GB2312.ttf'))  # register Font
# 注册字体

class MyDocTemplate(BaseDocTemplate):

    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        self._Machine_bookmark_list=[]
        BaseDocTemplate.__init__(self, filename, **kw)

        template = PageTemplate(
            'normal', [Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')])
        self.addPageTemplates(template)
    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'Heading1':
                key = 'h2-%s' % self.seq.nextf('heading2')
                self.canv.bookmarkPage(key)
                self.notify('TOCEntry', (1, text, self.page, key))
                self._Machine_bookmark_list.append({
                    'title':text,
                    'page_num':self.page
                })



def loading_txt(txt_path:str)->list:
    with open(txt_path, 'r') as f:
        txt_datas = f.readlines()
    return txt_datas

def build_pdf_file(txt_datas:list,aim_pdf_path:str)->None:
    if function_switch["add_big_toc"]:
        h1 =   PS(name='Heading1', fontName="FS_GB2312",fontSize=14,leading=16)
    else:
        h1 =   PS(name='Heading1', fontName="FS_GB2312",leading=16)
    body = PS(name='body', leading=12, fontName="FS_GB2312")
    # Build story.
    story = []
    # For conciseness we use the same styles for headings and TOC entries
    toc = TableOfContents()
    toc.levelStyles = [h1]
    if function_switch["build_toc"]==1:
        story.append(toc)
        story.append(PageBreak())
    for txt_data in txt_datas:

        if re.search(pattern, txt_data):
            story.append(Paragraph(txt_data, h1))
            # 标题页面使用h1段落样式
        else:
            story.append(Paragraph(txt_data,body ))
            # 正文段落使用正常body样式
    doc = MyDocTemplate(aim_pdf_path)
    doc.multiBuild(story)

    bookmark_list = doc._Machine_bookmark_list
    if function_switch["build_left_bookmark"]:
        build_left_bookmark_for_pdf(aim_pdf_path,bookmark_list)




def build_left_bookmark_for_pdf(aim_pdf_path:str,bookmark_list:list)->None:
    pdf_reader=pdfr(aim_pdf_path)
    pdf_writer=pdfw()
    pdfpage_num = pdf_reader.getNumPages()
    for page_num in range(pdfpage_num):
        the_page = pdf_reader.getPage(page_num)
        pdf_writer.addPage(the_page)
    for bookmark in bookmark_list:
        pdf_writer.addBookmark(bookmark['title'],bookmark['page_num']-1)
    with open(aim_pdf_path,'wb')as fp:
        pdf_writer.write(fp)
    pass




if __name__ =="__main__":
    txt_datas = loading_txt(txt_path)
    build_pdf_file(txt_datas, aim_pdf_path)
    pass
