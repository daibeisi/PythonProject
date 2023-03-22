import xmlrpc.client
import time
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm, Inches, Pt
from pyecharts import options
from pyecharts.charts import Bar
from snapshot_selenium import snapshot
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
from pyecharts.render import make_snapshot

url = ""
db = ""
user, pwd = "", ""
uid = 1


def draw_bar(data, tag, main_title, image_name):
    bar = (
        Bar(init_opts=options.InitOpts(theme=ThemeType.MACARONS))
        .add_xaxis(data.get('x_list'))
        .add_yaxis(tag, data.get('y_list'), category_gap="60%", markline_opts=options.MarkLineOpts(
            data=[options.MarkLineItem(type_='average', name='平均值')],
            precision=0
        ), label_opts=options.LabelOpts(
            is_show=True,
            position='top'
        ))
        .set_series_opts(itemstyle_opts={  # set_series_opts设置系列配置
            "normal": {  # normal代表一般、正常情况
                # LinearGradient 设置线性渐变，offset为0是柱子0%处颜色，为1是100%处颜色
                "color": JsCode("""new echarts.graphic.LinearGradient(0, 0, 0, 1, [{
                    offset: 0, 
                    color: 'rgba(0, 233, 245, 1)'
                }, {
                    offset: 1, 
                    color: 'rgba(0, 45, 187, 1)'
                }], false)"""),
                "barBorderRadius": [10, 10, 0, 0],  # 设置柱子4个角为30变成圆柱
                "shadowColor": 'red',  # 阴影颜色
                "position": 'top'
            }})
        .set_global_opts(
            title_opts=options.TitleOpts(
                title=main_title,
                pos_left='center',  # 标题的位置 距离左边20%距离。
                item_gap=10,  # 主副标题之间的距离
                title_textstyle_opts=options.TextStyleOpts(
                    color='black',
                    font_size=28
                )
            ),
            xaxis_opts=options.AxisOpts(
                axistick_opts=options.AxisTickOpts(
                    is_inside=False,  # 刻度线是否在内侧
                ),
                axisline_opts=options.AxisLineOpts(
                    linestyle_opts=options.LineStyleOpts(width=3,  # 设置宽度
                                                         opacity=0,  # 设置透明度
                                                         type_='dashed',  # 'solid', 'dashed', 'dotted'
                                                         color='black')
                ),  # 坐标轴线的配置项
                axislabel_opts=options.LabelOpts(
                    interval=0,
                    font_size=14,  # 字的大小
                    formatter=JsCode(
                        """function(params) {
                            var newParamsName = '';
                            var paramsNameNumber = params.length;
                            var provideNumber = 4;
                            var rowNumber = Math.ceil(paramsNameNumber / provideNumber);
                            if (paramsNameNumber > provideNumber) {
                                for (var p = 0; p < rowNumber; p++) {
                                     var tempStr = '';
                                     var start = p * provideNumber;
                                     var end = start + provideNumber;
                                     if (p == rowNumber - 1) {
                                          tempStr = params.substring(start, paramsNameNumber);
                                     } else {
                                          tempStr = params.substring(start, end) + '\\n';
                                     }
                                     newParamsName += tempStr;
                                }
                            } else {
                                newParamsName = params;
                            }
                            return newParamsName
                        }"""
                    )
                    # ,rotate=15
                )
            ),
            yaxis_opts=options.AxisOpts(
                axislabel_opts=options.LabelOpts(
                    font_size=14,
                )
            ),
            legend_opts=options.LegendOpts(
                type_=None,  # 'plain'：普通图例。缺省就是普通图例。
                pos_left='left',  # 图例横向的位置,right表示在右侧，也可以为百分比
                orient='vertical'  # horizontal #图例方式的方式
            ),
            toolbox_opts=options.ToolboxOpts(
                feature={
                    'dataZoom': {},
                    'dataView': {},
                    'saveAsImage': {},
                    'restore': {}
                }
            )

        )
    )
    make_snapshot(snapshot, bar.render(), image_name)


models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

main_company_list = models.execute_kw(db, uid, pwd, 'tyibs.base.maintenance.company', 'search_read',
                                      [[
                                          ["sl_state", "=", "yes"]
                                      ]], {'fields': ['id', 'name']})

main_company_info_list = []

for main_company in main_company_list:
    main_company_id = main_company['id']
    main_company_name = main_company['name']
    company_all_lift = models.execute_kw(db, uid, pwd, 'tyibs.base.lift', 'search_count',
                                         [[
                                             ['maintenance_company_id', '=', main_company_id],
                                             ['is_zb_get_data', '=', 'yes'],
                                             ['lift_status', '=', 'using']
                                         ]])
    company_online_lift = models.execute_kw(db, uid, pwd, 'tyibs.base.lift', 'search_count',
                                            [[
                                                ['maintenance_company_id', '=', main_company_id],
                                                ['is_zb_get_data', '=', 'yes'],
                                                ['lift_status', '=', 'using'],
                                                ['tt_online_lift', '=', 'yes']
                                            ]])
    company_overdue_lift = models.execute_kw(db, uid, pwd, 'tyibs.base.lift', 'search_count',
                                             [[
                                                 ['maintenance_company_id', '=', main_company_id],
                                                 ['is_zb_get_data', '=', 'yes'],
                                                 ['tt_online_lift', '=', 'yes'],
                                                 ['main_status', '=', 'over_no_main']
                                             ]])
    company_rescue = models.execute_kw(db, uid, pwd, 'tyibs.er.work.order.save', 'search_count',
                                       [[
                                           ['lift_maintenance_company_id', '=', main_company_id],
                                           ['save_result', 'in', ['save_success', 'get_out_yourself']]
                                       ]])

    main_company_info_list.append({
        'name': main_company_name,
        'company_all_lift': company_all_lift,
        'company_online_lift': company_online_lift,
        'company_overdue_lift': company_overdue_lift,
        'company_rescue': company_rescue,
        'company_complaint': 0,
        'company_inspection': 0,
        'company_insurance': 0,
        'company_risk_level': "二级"
    })
    time.sleep(1)

main_company_info_list = sorted(main_company_info_list, key=lambda x: x['company_online_lift'], reverse=True)

x_list = []
y_list = []

for index, main_company_info in enumerate(main_company_info_list):
    if index >= 10:
        break
    x_list.append(main_company_info['name'])
    y_list.append(main_company_info['company_online_lift'])

data = {
    'x_list': x_list,
    'y_list': y_list
}

doc = DocxTemplate('C:\\Users\\daibeisi\\Desktop\\test.docx')

draw_bar(data, '数量', '维保单位电梯上线前十统计', '维保单位电梯上线前十统计.png')
# 载入维保单位电梯上线前十统计柱状图
main_company_online_lift_top10 = InlineImage(doc, image_descriptor=r"维保单位电梯上线前十统计.png", width=Mm(160), height=Mm(90))

context = {
    'main_company_online_lift_top10': main_company_online_lift_top10,
    'main_company_info_list': main_company_info_list
}
doc.render(context)
doc.save('C:\\Users\\daibeisi\\Desktop\\test1.docx')
