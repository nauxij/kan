import requests
from collections import defaultdict

# ==========你的配置============
url1 = "https://gh-proxy.org/https://raw.githubusercontent.com/fafa002/yf2025/refs/heads/main/yiyifafa.txt"
url2 = "https://www.985pan.com/down.php/bf5e9607ff407fcdd71f63928ea5bc79.txt"
url3 = "http://wangziduoqing.com/yuan/zb.txt"
url4 = "https://gh-proxy.org/https://raw.githubusercontent.com/807080747/zv/refs/heads/main/sese.txt"
url5 = "http://rihou.cc:567/gggg.nzk"
# ==============================

# --------------------------
# 1.精确别名【优先执行】：名字相近极易串台的频道全部放这里
alias_map = {
    "cctv‑5":"CCTV5",
    "凤凰(香港)":"凤凰香港",
    "凤凰卫视香港台":"凤凰香港",

    # 纬来系列
    "纬来电影台":"纬来电影",
    "纬来戏剧台":"纬来戏剧台",
    "纬来体育台":"纬来体育台",

    # 靖天、靖洋高危组，必须精确匹配，禁止模糊
    "靖天电影台":"靖天电影",
    "靖天戏剧台":"靖天戏剧台",
    "靖天映画":"靖天映画",
    "靖洋戏剧台":"靖洋戏剧台",
    "靖洋戏剧":"靖洋戏剧",

    # 民视 / 公视 / 采昌 高危组
    "民视影剧台":"民视影剧台",
    "公视戏剧":"公视戏剧",
    "采昌影剧台":"采昌影剧台",

    # CHC系列
    "CHC动作电影":"CHC动作电影",
    "CHC影迷电影":"CHC影迷电影",
    "CHC家庭影院":"CHC家庭影院",

    # 天映系列
    "天映频道":"天映频道",
    "天映经典":"天映经典",

    "TVB星河频道":"TVB星河"
}

# 2.模糊关键词匹配：精确匹配没命中才跑这里；长关键词写上方，防止误匹配
# CCTV、凤凰这类特征独立，不会和别的台撞字，放这里
fuzzy_rules = [
    ("CCTV5+", "CCTV5+"),
    ("cctv5+", "CCTV5+"),
    ("CCTV5", "CCTV5"),
    ("cctv5", "CCTV5"),
    ("中央5", "CCTV5"),

    ("CCTV3", "CCTV3"),
    ("cctv3", "CCTV3"),

    ("CCTV6", "CCTV6"),
    ("cctv6", "CCTV6"),

    ("凤凰香港", "凤凰香港"),
    ("凤凰卫视香港", "凤凰香港"),

    ("纬来电影", "纬来电影"),
    ("TVB星河", "TVB星河"),
]
# --------------------------

def fix_url(link):
    """
    保留自定义协议：video://、rtmp://，仅处理//无协议链接
    """
    lnk = link.strip()
    if lnk.startswith(("video://", "rtmp://")):
        return lnk
    if lnk.startswith("//"):
        lnk = "http:" + lnk
    return lnk


def get_std_name(raw_name):
    """优先精确别名，失败后执行关键词模糊匹配"""
    n = raw_name.strip()
    #第一步：精确完整台名匹配
    if n in alias_map:
        return alias_map[n]
    #第二步：关键词模糊包含匹配
    for keyword, std_name in fuzzy_rules:
        if keyword in n:
            return std_name
    #都没匹配上，返回原始台名
    return n


def load_txt(url):
    try:
        resp = requests.get(url, timeout=25)
        resp.encoding = "utf-8"
        text = resp.text
        res = []
        for line in text.splitlines():
            ln = line.strip()
            if not ln or ln.startswith("#"):
                continue
            if "," in ln:
                name, raw_link = ln.split(",", maxsplit=1)
                ch_name = name.strip()
                std_name = get_std_name(ch_name)
                fixed_link = fix_url(raw_link)
                res.append((std_name, fixed_link))
        return res
    except Exception as e:
        print(f"⚠️ 请求 {url} 异常：{e}")
        return []


#抓取全部5条数据源
src1 = load_txt(url1)
src2 = load_txt(url2)
src3 = load_txt(url3)
src4 = load_txt(url4)
src5 = load_txt(url5)

channel = defaultdict(list)
all_got_names = set() #收集所有经过别名/模糊转换后的台名

for name, link in src1 + src2 + src3 + src4 + src5:
    if link not in channel[name]:
        channel[name].append(link)
    all_got_names.add(name)


order_lines_raw = """
凤凰香港
CHC动作电影
CCTV3
CCTV5
CCTV5+
央视台球
CCTV6
河南曲艺
兵器科技
梨园频道

星河
纬来育乐
五星体育
纬来电影
天津文艺
北京文艺
淘电影
东森电影
美亚电影
天映频道
龙华偶像
Popc
1905电影
无线功夫
天津影视
精彩影视
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
龙祥电影
淘剧场
now星影
黄金华剧台
ELTA影剧
广西影视
都市剧场
湖南电影
湖南电视剧
龙华洋片
华丽翡翠台
TVB星河
千禧经典台
民视影剧台
公视戏剧
采昌影剧台
靖天映画
靖天戏剧台
靖天电影台
靖洋戏剧台
东方影视
纬来电影台
纬来戏剧台
纬来体育台
"""

order_list = [x.strip() for x in order_lines_raw.splitlines() if x.strip()]
std_set = set(order_list)

#打印陌生台名，方便补充规则
unknown = all_got_names - std_set
if unknown:
    print("\n=========【发现陌生台名，可以拿来补别名/模糊规则】=========")
    for u in sorted(unknown):
        print(f'"{u}":"填你的标准台名",')
    print("================================================\n")

out = []
for ch in order_list:
    links = channel.get(ch, [])
    for l in links:
        out.append(f"{ch},{l}")

with open("qdyd.txt","w",encoding="utf-8") as f:
    f.write("\n".join(out))

print("✅执行完成，输出qdyd.nzk，共5条数据源，优先精确别名+关键词模糊匹配，仅保留配置列表中的频道，外部多余台全部舍弃")
