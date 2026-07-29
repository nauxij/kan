import requests

url1 = "https://pan.vma.cc/pan/down.php/350735607a786faaaa69aa5bbe3a3078.txt"
url2 = "https://gitee.com/x21y/yx/raw/main/qdyd.txt"
out_file = "qdyd.nzk"

def get_txt(url):
    try:
        h = {"User-Agent":"Mozilla/5.0"}
        r = requests.get(url,headers=h,timeout=15)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"获取失败 {url} : {e}")
        return ""

if __name__ == "__main__":
    t1 = get_txt(url1)
    t2 = get_txt(url2)
    #合并两份源
    all_text = t1 + "\n" + t2
    #简单去重行
    lines = list(dict.fromkeys(all_text.splitlines()))
    final = "\n".join(lines)
    with open(out_file,"w",encoding="utf-8") as f:
        f.write(final)
    print("完成写入qdyd.nzk")
