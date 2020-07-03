import sqlite3
import os
history_dir=r"C:\Users\linsi\AppData\Local\CentBrowser\User Data\Default"
history_path=os.path.join(history_dir,"History")

c=sqlite3.connect(history_path)
cursor=c.cursor()


sql_select = """ SELECT datetime(last_visit_time/1000000-11644473600,'unixepoch','localtime')
                 FROM urls
                 ORDER BY last_visit_time DESC
             """
hist = list(cursor.execute (sql_select))
cnt=0
for each in hist:
	print(each)
	if cnt>10:
		break
