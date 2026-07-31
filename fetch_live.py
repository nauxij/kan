import requests
from collections import defaultdict

# ==========你的配置============
url1 = "https://gh-proxy.org/https://raw.githubusercontent.com/fafa002/yf2025/refs/heads/main/yiyifafa.txt"
# url2 已移除
url3 = "https://gh-proxy.org/https://raw.githubusercontent.com/alantang1977/JunTV/refs/heads/main/output/result.m3u"
url4 = "https://gh-proxy.org/https://raw.githubusercontent.com/swhtv/1/refs/heads/main/swtvlive"
url5 = "http://rihou.cc:567/gggg.nzk"
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
            #兼容m3u格式，跳过#EXTM3U,#EXT‑INF开头行
            if ln.startswith("#"):
                continue
            if "," in ln:
                name, raw_link = ln.split(",", maxsplit=1)
                ch_name = name.strip()
                fixed_link = fix_url(raw_link)
                res.append((ch_name, fixed_link))
        return res
    except Exception as e:
        print(f"⚠️ 请求 {url} 异常：{e}")
        return []


# 抓取剩余4个数据源（去掉原来url2）
src1 = load_txt(url1)
src3 = load_txt(url3)
src4 = load_txt(url4)
src5 = load_txt(url5)

channel = defaultdict(list)
#合并全部源，相同链接自动去重
for name, link in src1 + src3 + src4 + src5:
    if link not in channel[name]:
        channel[name].append(link)


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

# 只输出列表内存在的台，不在order_lines里的台全部丢弃
for ch in order_lines:
    if ch in channel:
        for one_url in channel[ch]:
            out.append(f"{ch},{one_url}")


with open("qdyd.nzk", "w", encoding="utf-8") as f:
    f.write("\n".join(out))

print("✅执行完成，输出qdyd.nzk，共4条数据源，已删除原第二条线路url2，仅保留配置列表中的频道，外部多余台全部舍弃")
