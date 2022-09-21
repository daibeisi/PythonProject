from reportlab.pdfbase import pdfmetrics  # 注册字体
from reportlab.pdfbase.ttfonts import TTFont  # 字体类
from reportlab.platypus import Table, SimpleDocTemplate, Paragraph, Image  # 报告内容相关类
from reportlab.lib.pagesizes import letter  # 页面的标志尺寸(8.5*inch, 11*inch)
from reportlab.lib.styles import getSampleStyleSheet  # 文本样式
from reportlab.lib import colors  # 颜色模块
from reportlab.graphics.charts.barcharts import VerticalBarChart  # 图表类
from reportlab.graphics.charts.legends import Legend  # 图例类
from reportlab.graphics.shapes import Drawing  # 绘图工具
from reportlab.lib.units import cm  # 单位：cm

# 注册字体(提前准备好字体文件, 如果同一个文件需要多种字体可以注册多个)
pdfmetrics.registerFont(TTFont('MSYH', 'C:\\Windows\\Fonts\\msyh.ttc'))


class GeneratePDF:
    def __init__(self):
        self._style = getSampleStyleSheet()  # 获取所有样式表
        self._context = list()

    def draw_title(self, title: str):
        """绘制标题"""
        ct = self._style['Title']  # 拿到标题样式
        ct.fontName = 'MSYH'  # 字体名
        # ct.textColor = colors.green  # 字体颜色
        # ct.bold = True
        self._context.append(Paragraph(title, ct))

    def draw_heading1(self, heading1: str):
        """绘制标题1"""
        ct = self._style['Heading1']
        ct.fontName = 'MSYH'  # 字体名
        self._context.append(Paragraph(heading1, ct))

    def draw_heading2(self, heading2: str):
        """绘制标题2"""
        ct = self._style['Heading2']
        ct.fontName = 'MSYH'  # 字体名
        self._context.append(Paragraph(heading2, ct))

    def draw_heading3(self, heading3: str):
        """绘制标题3"""
        ct = self._style['Heading3']
        ct.fontName = 'MSYH'  # 字体名
        self._context.append(Paragraph(heading3, ct))

    def draw_text(self, text: str):
        """绘制正文"""
        ct = self._style['BodyText']
        ct.fontName = 'MSYH'  # 字体名
        ct.firstLineIndent = 20  # 第一行开头空格
        ct.wordWrap = 'CJK'  # 设置自动换行
        ct.alignment = 0  # 左对齐
        self._context.append(Paragraph(text, ct))

    def draw_table(self, *args):
        """绘制表格"""
        # 列宽度
        col_width = 120
        style = [
            ('FONTNAME', (0, 0), (-1, -1), 'MSYH'),  # 字体
            ('FONTSIZE', (0, 0), (-1, 0), 12),  # 第一行的字体大小
            ('FONTSIZE', (0, 1), (-1, -1), 10),  # 第二行到最后一行的字体大小
            ('BACKGROUND', (0, 0), (-1, 0), '#d5dae6'),  # 设置第一行背景颜色
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # 第一行水平居中
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),  # 第二行到最后一行左右左对齐
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # 所有表格上下居中对齐
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.darkslategray),  # 设置表格内文字颜色
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),  # 设置表格框线为grey色，线宽为0.5
            # ('SPAN', (0, 1), (0, 2)),  # 合并第一列二三行
            # ('SPAN', (0, 3), (0, 4)),  # 合并第一列三四行
            # ('SPAN', (0, 5), (0, 6)),  # 合并第一列五六行
            # ('SPAN', (0, 7), (0, 8)),  # 合并第一列五六行
        ]
        table = Table(args, colWidths=col_width, style=style)
        self._context.append(table)

    def draw_bar(self, bar_data: list, ax: list, items: list):
        """创建图表"""
        drawing = Drawing(500, 250)
        bc = VerticalBarChart()
        bc.x = 45  # 整个图表的x坐标
        bc.y = 45  # 整个图表的y坐标
        bc.height = 200  # 图表的高度
        bc.width = 350  # 图表的宽度
        bc.data = bar_data
        bc.strokeColor = colors.black  # 顶部和右边轴线的颜色
        bc.valueAxis.valueMin = 5000  # 设置y坐标的最小值
        bc.valueAxis.valueMax = 26000  # 设置y坐标的最大值
        bc.valueAxis.valueStep = 2000  # 设置y坐标的步长
        bc.categoryAxis.labels.dx = 2
        bc.categoryAxis.labels.dy = -8
        bc.categoryAxis.labels.angle = 20
        bc.categoryAxis.categoryNames = ax
        # 图示
        leg = Legend()
        leg.fontName = 'MSYH'
        leg.alignment = 'right'
        leg.boxAnchor = 'ne'
        leg.x = 475  # 图例的x坐标
        leg.y = 240
        leg.dxTextSpace = 10
        leg.columnMaximum = 3
        leg.colorNamePairs = items
        drawing.add(leg)
        drawing.add(bc)
        self._context.append(drawing)

    def draw_img(self, path):
        """绘制图片"""
        img = Image(path)  # 读取指定路径下的图片
        img.drawWidth = 5 * cm  # 设置图片的宽度
        img.drawHeight = 8 * cm  # 设置图片的高度
        self._context.append(img)

    def build(self, filename):
        """创建pdf文件"""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        doc.build(self._context)


if __name__ == '__main__':
    pdf = GeneratePDF()
    # 添加标题
    pdf.draw_title('数据分析就业薪资')
    # 添加图片
    # pdf.draw_img('抗疫必胜.png')
    # 添加标题一
    pdf.draw_heading1('一、大数据岗位现状介绍')
    # 添加段落文字
    pdf.draw_text('众所周知，大数据分析师岗位是香饽饽，'
                  '近几年数据分析热席卷了整个互联网行业，'
                  '与数据分析的相关的岗位招聘、培训数不胜数。'
                  '很多人前赴后继，想要参与到这波红利当中。'
                  '那么数据分析师就业前景到底怎么样呢？')
    # 添加标题一
    pdf.draw_heading1('二、不同级别的平均薪资')
    # 添加表格
    data = [
        ('职位名称', '平均薪资', '较上年增长率'),
        ('数据分析师', '18.5K', '25%'),
        ('高级数据分析师', '25.5K', '14%'),
        ('资深数据分析师', '29.3K', '10%')
    ]
    pdf.draw_table(*data)
    # 添加标题一
    pdf.draw_heading1('三、热门城市的就业情况')
    # 生成图表
    b_data = [(25400, 12900, 20100, 20300, 20300, 17400), (15800, 9700, 12982, 9283, 13900, 7623)]
    ax_data = ['BeiJing', 'ChengDu', 'ShenZhen', 'ShangHai', 'HangZhou', 'NanJing']
    leg_items = [(colors.red, '平均薪资'), (colors.green, '招聘量')]
    pdf.draw_bar(b_data, ax_data, leg_items)
    # 生成pdf
    pdf.build('report.pdf')
