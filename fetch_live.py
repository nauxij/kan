import requests
from collections import defaultdict

# ==========你的配置============
url2 = "https://gitee.com/x21y/yx/raw/main/qdyd.txt"
# ==============================

def fix_url(link):
    """修复//无协议链接，补全http://"""
    lnk = link.strip()
    if lnk.startswith("//"):
        lnk = "http:" + lnk
    return lnk


def load_txt(url):
    try:
        resp = requests.get(url, timeout=25)
        resp.encoding = "utf-8"
        text = resp.text
        # 识别Cloudflare HTML拦截页面，直接丢弃该源
        if "<!DOCTYPE html>" in text or "<html" in text:
            print(f"⚠️ {url} 返回HTML人机验证页面，跳过此源")
            return []
        res = []
        for line in text.splitlines():
            ln = line.strip()
            if not ln or ln.startswith("#"):
                continue
            if "," not in ln:
                continue
            name, raw_link = ln.split(",", maxsplit=1)
            ch_name = name.strip()
            fixed_link = fix_url(raw_link)
            res.append((ch_name, fixed_link))
        return res
    except Exception as e:
        print(f"⚠️ 请求 {url} 异常：{e}")
        return []


# 只读取 url2 数据源
src2 = load_txt(url2)

channel = defaultdict(list)

# 源2每个台最多1个源，单台总数不超过2
s2_dict = {}
for name, url in src2:
    if name not in s2_dict:
        s2_dict[name] = url
for n, u in s2_dict.items():
    if len(channel[n]) < 2 and u not in channel[n]:
        channel[n].append(u)


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


out = []
out.append("央卫港澳台,#genre#")
used = set()

# 按模板顺序输出频道
for item in order_lines:
    ch = item.strip()
    if ch == "":
        out.append("")
        continue
    if ch in channel:
        for one_url in channel[ch]:
            out.append(f"{ch},{one_url}")
        used.add(ch)

# 其余未在模板的频道
out.append("")
out.append("# 其它频道")
for ch_name, url_list in channel.items():
    if ch_name not in used:
        for u in url_list:
            out.append(f"{ch_name},{u}")


with open("qdyd.nzk", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("✅执行完成，输出qdyd.nzk")
