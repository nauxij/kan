import requests
import re
from collections import defaultdict
import sys

def safe_print(txt):
    """Github Actions兼容，过滤ascii无法编码特殊字符"""
    if isinstance(txt, str):
        txt = txt.replace('\u2011', '-')
        txt = txt.replace('\u200b', '')
        txt = txt.encode("ascii", "replace").decode("ascii")
    print(txt)

# =========编码修复========
if sys.stdout.encoding.lower() != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ==========你的配置============
url1 = "https://gitee.com/x21y/yx/raw/main/qdyd.nzk"

# --------------------------
alias_map = {}

# 山东广电频道网页映射（保留，用于后续扩展）
sd_channel_web = {
    "山东文旅":"https://v.iqilu.com/live/yspd/",
}

def fetch_sdtv_live():
    """抓取山东广电实时有效m3u8直播流【直接调用jsonAPI】"""
    out = []
    headers = {
        "User-Agent":"Mozilla/5.0 (Android)",
        "Referer":"https://v.iqilu.com/live/yspd/"
    }
    api_url = "https://v.iqilu.com/api/getLiveInfo?channel=yspd"
    try:
        resp = requests.get(api_url,headers=headers,timeout=20)
        resp.raise_for_status()
        play_json = resp.json()
        real_m3u8 = play_json.get("data",{}).get("playUrl")

        try:
            safe_print(real_m3u8)
        except Exception:
            safe_print("打印出错，但直播源变量已经获取")

        if real_m3u8:
            out.append(("山东文旅", real_m3u8))
            safe_print("✅山东文旅 获取直播流成功")
        else:
            safe_print("⚠️山东文旅 api返回没有playUrl")

    except Exception as e:
        err_msg = f"❌山东文旅抓取异常: {str(e)}"
        safe_print(err_msg)
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
        safe_print(f"⚠️ 请求 {url} 异常：{str(e)}")
        return []


# ============ 主流程 =================
# 1.抓取山东文旅实时源
sd_result = fetch_sdtv_live()
# 2.加载外部源
src1 = load_txt(url1)
# 合并数据源，实时抓取的山东文旅优先
all_src = sd_result + src1

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
河北都市
长清新闻
济阳综合
济阳影视
平阴综合
平阴乡村
商河综合
商河影视
章丘综合
章丘公共
李沧
黄岛综合
黄岛生活
即墨综合
即墨生活
胶州综合
胶州生活
崂山
莱西综合
莱西生活
平度新闻
平度生活
莒县综合
岚山
五莲综合
五莲文化
长岛
福山综合
福山生活
海阳综合
海阳综艺
龙口综合
龙口生活
莱山综合
莱山影视
莱阳综合
莱阳民生
莱州综合
牟平综合
蓬莱综合
栖霞综合
栖霞苹果
招远综合
招远综艺
费县综合
费县生活
河东综合
河东影视
莒南综合
莒南影视
兰山综合
临沭综合
临沭生活
罗庄综合
罗庄影视
蒙阴1
蒙阴2
平邑综合
平阴生活
郯城1
郯城2
沂南综合
沂南红色影视
沂水综合
沂水生活
金乡综合
金乡生活
梁山综合
曲阜新闻
任城新闻
任城影视
泗水新闻
泗水文化
鱼台新闻
鱼台生活
兖州新闻
兖州生活
成武综合
成武综艺
曹县综合
东明
定陶1
定陶2
鄄城综合
巨野新闻
牡丹新闻
牡丹综艺
单县综合
郓城新闻
郓城综艺
山亭综合
市中综合
滕州综合
薛城新闻
峄城综合
台儿庄新闻
东营区新闻
东营区科教
广饶新闻
广饶科教
利津新闻
利津文化
潍坊滨海新闻
昌乐综合
昌邑综合
昌邑经济
坊子综合
高密综合
高密党建
潍坊高新区
寒亭综合
临朐综合
青州综合
青州文化
潍城
奎文
安丘综合
安丘民生
陵城综合
乐陵综合
乐陵综艺
临邑
宁津综合
平原综合
齐河综合
庆云综合
庆云生活
武城综合
武城综艺
夏津综合
夏津公共
禹城综合
禹城综艺
环翠TV
荣成综合
荣成生活
乳山综合
乳山生活
文登2
滨城TV
博兴综合
博兴生活
惠民综合
惠民影视
无棣综合
无棣综艺
阳信综合
邹平综合
邹平民生
沾化综合
沾化综艺
博山新闻
博山图文
高青综合
高青影视
桓台综合
桓台影视
临淄新闻
临淄生活
沂源综合
沂源生活
淄川新闻
淄川生活
张店综合
张店图文
茌平综合
茌平生活
东昌
东阿综合
东阿综艺
高唐综合
高唐综艺
冠县综合
临清综合
临清经济
莘县综合
莘县生活
阳谷综合
阳谷影视
东平综合
东平民生
岱岳
肥城生活
宁阳1
宁阳2
泰山
"""

order_list = [x.strip() for x in order_lines_raw.splitlines() if x.strip()]
std_set = set(order_list)

#打印陌生台名
unknown = all_got_names - std_set
if unknown:
    safe_print("\n=========【发现陌生台名】=========")
    for u in sorted(unknown):
        safe_print(f'"{u}":"填你的标准台名",')
    safe_print("================================================\n")

out = []
for ch in order_list:
    links = channel.get(ch, [])
    for l in links:
        out.append(f"{ch},{l}")

with open("qdyd.nzk","w",encoding="utf-8") as f:
    f.write("\n".join(out))

safe_print("✅执行完成，输出qdyd.nzk；山东文旅实时抓取源已合并，排在order第21位；仅输出order列表内频道")
