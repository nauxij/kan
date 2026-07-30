import requests
from collections import defaultdict

# ==========你的配置============
url1 = "https://gh-proxy.org/https://raw.githubusercontent.com/fafa002/yf2025/refs/heads/main/yiyifafa.txt"
url2 = "https://gitee.com/x21y/yx/raw/main/qdyd.txt"
# ==============================

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


# 同时抓取两个地址
src1 = load_txt(url1)
src2 = load_txt(url2)

channel = defaultdict(list)
# 用来去重同一个频道的重复链接
for name, link in src1 + src2:
    if link not in channel[name]:
        channel[name].append(link)


order_lines_raw = """
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
纬来育乐
CCTV15
五星体育
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
农林卫视
陕西新闻
淘剧场
动作影院
喜剧影院
星影
黄金华剧台
ELTA综合
河南电视剧
广西影视
经典电影台
都市剧场
湖南电影
湖南电视剧
龙华洋片
华丽翡翠台
天映新加坡
吉林都市
爱奇艺
TVB星河
千禧经典台
民视影剧台
公视戏剧
采昌影剧台
靖天映画
靖天戏剧台
靖天电影台
靖洋戏剧台
精选动漫台
东方影视
金光布袋戏
纬来电影台
纬来戏剧台
纬来体育台
龙祥时代
东森戏剧
""".strip().splitlines()

# 台名去重，保留顺序
seen = set()
order_lines = []
for item in order_lines_raw:
    it = item.strip()
    if it == "":
        continue
    if it not in seen:
        seen.add(it)
        order_lines.append(it)


out = []
out.append("央卫港澳台,#genre#")

# 只输出列表内存在的台，**删掉【其它频道】，不在order_lines里的台全部丢弃**
for ch in order_lines:
    if ch in channel:
        for one_url in channel[ch]:
            out.append(f"{ch},{one_url}")


with open("qdyd.nzk", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("✅执行完成，输出qdyd.nzk，仅保留配置列表中的频道，外部多余台全部舍弃")
