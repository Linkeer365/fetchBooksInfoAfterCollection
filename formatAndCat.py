import os
import re
assert os.path.exists("./cc.md")

def main():
    new_str=""
    with open("./cc.md","r",encoding="utf-8") as f:
        lines_str=f.read()
        str1=re.sub("\|  ","| ",lines_str)
        new_str=re.sub("  \|"," |",str1)
        with open("./ff.md","w",encoding="utf-8") as g:
            g.write(new_str)

    print("Format file written.")

    with open("./【长期更新】每日传书计划.md","a",encoding="utf-8") as f:
        f.write("\n## 传书\n\n")
        f.write("| 书名 | 作者 | ISBN号 | md5值 |\n")
        f.write("| ---- | ---- | ---- | ---- |\n")
        f.write(new_str)
	os.remove("./cc.md")
	os.remove("./ff.md")
    print("done.")

if __name__=="__main__":
    main()


# print("hello.")