# coding: utf-8
# Author：boxker
# Mail：icjb@foxmail.com

import sqlite3


class simpleToolSql:
    """
    simpleToolSql for sqlite3
    简单数据库工具类
    编写这个类主要是为了封装sqlite，继承此类复用方法
    """

    def __init__(self, filename="taobaokesql", result_dict=True):
        """
        初始化数据库
        filename：文件名
        """
        self.filename = filename + ".db"
        self.db = sqlite3.connect(self.filename)
        if result_dict:
            self.db.row_factory = self._dict_factory  # must before cursor set.
        self.c = self.db.cursor()

    def _dict_factory(self, cursor, row):
        d = {}

        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def close(self):
        """
        关闭数据库
        """
        self.c.close()
        self.db.close()

    def execute(self, sql, param=None):
        """
        执行数据库的增、删、改
        sql：sql语句
        param：数据，可以是list或tuple，亦可是None
        retutn：成功返回True
        """
        try:
            if param is None:
                self.c.execute(sql)
            else:
                if type(param) is list:
                    self.c.executemany(sql, param)
                else:
                    self.c.execute(sql, param)
            count = self.db.total_changes
            self.db.commit()
        except Exception as e:
            print(e)
            return False, e
        if count > 0:
            return True
        else:
            return False

    def query(self, sql, param=None):
        """
        查询语句
        sql：sql语句
        param：参数,可为None
        retutn：成功返回True
        """
        if param is None:
            self.c.execute(sql)
        else:
            self.c.execute(sql, param)
        return self.c.fetchall()


if __name__ == "__main__":
    """
    测试代码
    """
    pass
