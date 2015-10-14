# -*-coding:UTF-8 -*-

__author__ = 'junho'

"""
########################################################
purpose    : mysql测试
date       : 2015/10/14
author     : junho
--------------------------------------------------------
########################################################
"""

import MySQLdb

def executeMysql(sql):
    try:
        conn = MySQLdb.connect(host="localhost", user="root", passwd="544989", db="test_mysql", charset="utf8")
        cursor = conn.cursor()
        cursor.execute(sql)
        ret = cursor.fetchall()
        cursor.close()
        conn.commit()
        conn.close()
        return ret
    except MySQLdb.Error,e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

# insert into tmp_testPython(acc_nbr,cust_name) values('18922189820','黄俊浩');
sql = """
select * from tmp_testPython;
"""
rets = executeMysql(sql)
for r in rets:
    print r

# test
s = 'abc,aa,568,'
print s.rstrip(',')