import requests
from collections import defaultdict

# ==========你的配置============
url1 = "https://gh-proxy.org/https://raw.githubusercontent.com/fafa002/yf2025/refs/heads/main/yiyifafa.txt"
url2 = "https://www.985pan.com/down.php/bf5e9607ff407fcdd71f63928ea5bc79.txt"
url3 = "http://wangziduoqing.com/yuan/zb.txt"
url4 = "https://gh-proxy.org/https://raw.githubusercontent.com/807080747/zv/refs/heads/main/sese.txt"
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


# 抓取全部5个数据源
src1 = load_txt(url1)
src2 = load_txt(url2)
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

    f.write("\n".join(out))

print("✅执行完成，输出qdyd.nzk，共4条数据源，已删除原第二条线路url2，仅保留配置列表中的频道，外部多余台全部舍弃")
