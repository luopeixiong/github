import xlrd

class xlwork(object):
    def __init__(self,xlname):
        self.xlname = xlname

    def read_xl(self):
        try:
            wb = xlrd.open_workbook(self.xlname)
            sh = wb.sheet_by_index(0)
            columnList = sh.col_values(0)
        except Exception as e:
            pass

        return columnList

    def xl_to_file(self,filename):
        columnList = self.read_xl()
        try:
            with open(filename,"w+",encoding="utf-8") as f:
                for line in columnList:
                    f.write(str(line)+"\n")
        except Exception as e:
            pass

        return filename

    def file_to_list(self,filename):
        data_list = []
        file = self.xl_to_file(filename)
        with open(file,"r",encoding="utf-8",errors="ignore") as f:
            for line in f.readlines():
                line = line.split()[0]
                data_list.append(line)

        return data_list

class txtwork(object):
    def __init__(self,filename):
        self.filename = filename

    def file_to_list(self):
        data_list = []
        with open(self.filename,"r",encoding="utf-8") as f:
            for line in f.readlines():
                line = line.split()[0]
                data_list.append(line)

        return data_list