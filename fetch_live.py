import requests
import re
from collections import defaultdict

# ==========你的配置============
url1 = "https://gitee.com/x21y/yx/raw/main/qdyd.nzk"

# --------------------------
# 【提前定义全局变量，放在所有函数前面！】
alias_map = {}

# 山东广电频道网页映射 台名:网页地址
sd_channel_web = {
    "山东文旅":"https://v.iqilu.com/live/yspd/",
}

def fetch_sdtv_live():
    """抓取山东广电实时有效m3u8直播流"""
    out = []
    headers = {
        "User‑Agent":"Mozilla/5.0 (Android)",
        "Referer":"https://v.iqilu.com/"
    }
    for ch_name,page_url in sd_channel_web.items():
        try:
            resp = requests.get(page_url,headers=headers,timeout=20)
            resp.raise_for_status()
            html = resp.text
            api_match = re.search(r'["\'](/api/getPlayUrl[^"\']+)["\']',html)
            if not api_match:
                print(f"⚠️{ch_name}：未找到播放api接口")
                continue
            api_path = api_match.group(1)
            api_full = "https://v.iqilu.com" + api_path
            r2 = requests.get(api_full,headers=headers,timeout=15)
            r2.raise_for_status()
            play_json = r2.json()
            real_m3u8 = play_json.get("data",{}).get("url")
            if real_m3u8:
                out.append((ch_name,real_m3u8))
                print(f"✅{ch_name} 获取直播流成功")
            else:
                print(f"⚠️{ch_name} api返回没有url")
        except Exception as e:
            print(f"❌{ch_name}抓取异常 {e}")
    return out


def fix_url(link):
    lnk = link.strip()
    if lnk.startswith(("video://", "rtmp://")):
        return lnk
    if lnk.startswith("//"):
        lnk = "http:" + lnk
    return lnk


def get_std_name(raw_name):
    n = raw_name.strip()
    if n in alias_map:
        return alias_map[n]
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


# ============ 主流程 =================
# 1.抓取山东文旅实时源
sd_result = fetch_sdtv_live()
# 2.加载外部源
src1 = load_txt(url1)
# 合并数据源，实时抓取的山东文旅优先
all_src = sd_result + src1

# ✅必须在这里提前初始化！！之前放后面就会报channel未定义
channel = defaultdict(list)
all_got_names = set()

for name, link in all_src:
    if link not in channel[name]:
        channel[name].append(link)
    all_got_names.add(name)


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
搜狐剧场
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
金光布袋戏
纬来电影台
纬来戏剧台
纬来体育台
龙祥时代
东森戏剧
"""

order_list = [x.strip() for x in order_lines_raw.splitlines() if x.strip()]
std_set = set(order_list)

#打印陌生台名
unknown = all_got_names - std_set
if unknown:
    print("\n=========【发现陌生台名】=========")
    for u in sorted(unknown):
        print(f'"{u}":"填你的标准台名",')
    print("================================================\n")

out = []
for ch in order_list:
    links = channel.get(ch, [])
    for l in links:
        out.append(f"{ch},{l}")

with open("qdyd.nzk","w",encoding="utf-8") as f:
    f.write("\n".join(out))

print("✅执行完成，输出qdyd.nzk；山东文旅实时抓取源已合并，排在order第21位；仅输出order列表内频道")
