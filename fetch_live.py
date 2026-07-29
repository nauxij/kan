import requests

# ==========你的配置============
url1 = "https://pan.vma.cc/pan/down.php/350735607a786faaaa69aa5bbe3a3078.txt"
url2 = "https://gitee.com/x21y/yx/raw/main/qdyd.txt"

# 排序模板
order_lines = """
CCTV1
山东卫视
凤凰香港
CHC动作电影
CCTV3
CCTV5
CCTV5+
央视台球
CCTV6
河南曲艺

CCTV8
兵器科技
梨园频道
CCTV11
CCTV12

星河
千禧经典
CCTV15
纬来音乐
CCTV17

山东文旅
纬来电影
天津文艺
北京文艺
淘电影

东森电影
美亚电影
天映频道
龙华偶像
山东教育卫视

湖南卫视
浙江卫视
东方卫视
江苏卫视
北京卫视

安徽卫视
天津卫视
辽宁卫视
深圳卫视
东南卫视

湖北卫视
广东卫视
黑龙江卫视
贵州卫视
河北卫视

重庆卫视
海南卫视
四川卫视
山西卫视
河南卫视

江西卫视
广西卫视
吉林卫视
云南卫视
陕西卫视

无线功夫

天津影视
精彩影视
西部电影
黑龙江影视

陕西都市青春
重温经典
天映经典
靖洋戏剧
龙华电影

龙华经典
龙华戏剧
峨眉电影
靖天电影
CHC影迷电影
CHC家庭影院

第一剧场
风云剧场
风云音乐

华数剧场
华数影院
云南都市
云南娱乐

龙祥电影
搜狐剧场
""".strip().splitlines()
# ==============================

resp1 = requests.get(url1, timeout=15)
resp2 = requests.get(url2, timeout=15)

raw_all = []
for text in [resp1.text, resp2.text]:
    for line in text.splitlines():
        ll = line.strip()
        if not ll or ll.startswith("#"):
            continue
        raw_all.append(ll)

# key:台名, value:链接列表，收集全部源
channel_links = {}
for line in raw_all:
    if ":" not in line:
        continue
    name_part, link = line.split(":",1)
    real_name = name_part.split(",")[0].strip()
    link = link.strip()
    if real_name not in channel_links:
        channel_links[real_name] = []
    # 去重，避免重复链接
    if link not in channel_links[real_name]:
        channel_links[real_name].append(link)

out = []
used_names = set()

# 按模板顺序输出，每个台最多输出2条源
for name in order_lines:
    n = name.strip()
    if n == "":
        out.append("")
        continue
    if n in channel_links:
        link_list = channel_links[n][:2]   # 只取前2个源
        for link in link_list:
            out.append(f"{n},{link}")
        used_names.add(n)

# 其它频道，同样每个台最多2个源
other_list = []
for ch_name, link_list in channel_links.items():
    if ch_name not in used_names:
        for link in link_list[:2]:
            other_list.append(f"{ch_name},{link}")

out.append("")
out.append("# 央卫港澳台")
out.extend(other_list)

with open("qdyd.nzk","w",encoding="utf-8") as f:
    f.write("\n".join(out))

print("✅完成，每个台最多保留2个直播源，格式：台名,链接")
