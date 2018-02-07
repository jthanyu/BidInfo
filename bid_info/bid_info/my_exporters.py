# _*_ coding:utf-8 _*_
from scrapy.exporters import BaseItemExporter
import xlwt


class ExcelItemExporter(BaseItemExporter):
    def __init__(self, file, **kwargs):
        self._configure(kwargs)
        self.file = file
        self.wbook = xlwt.Workbook()
        self.wsheet = self.wbook.add_sheet('招标信息')
        self.row = 0

    def finish_exporting(self):
        self.wbook.save(self.file)

    # 调用基类的_get_serialized_fields方法,获得item所有字段的迭代器,然后将各字段写入Excel表
    def export_item(self, item):
        fields = self._get_serialized_fields(item)
        for col, v in enumerate(x for _, x in fields):
            self.wsheet.write(self.row, col, v)
        self.row += 1
