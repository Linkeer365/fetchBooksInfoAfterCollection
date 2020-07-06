import os

with open("./【长期更新】每日传书计划.md","r",encoding="utf-8") as f:
	lines=f.readlines()

for each_idx,each in enumerate(lines):
	if len(each.split("|"))>=5:
		new_line="|".join([each2 for each2_idx, each2 in enumerate(each.split("|")) if each2_idx!=4])
		lines[each_idx]=new_line

lines_str="".join(lines)

with open("./【长期更新】每日传书计划.md","w",encoding="utf-8") as f:
	f.write(lines_str)

print("done.")