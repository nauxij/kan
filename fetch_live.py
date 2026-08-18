import requests
from collections import defaultdict
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# ==========【配置区，新增URL只往这里列表里加即可】============
url_list = [
    "https://gh-proxy.org/https://raw.githubusercontent.com/nauxij/kan/refs/heads/main/qdyd.txt",
    "https://gh-proxy.org/https://raw.githubusercontent.com/fafa002/yf2025/refs/heads/main/yiyifafa.txt",
    "https://gh-proxy.org/https://raw.githubusercontent.com/807080747/zv/refs/heads/main/sese.txt",
    "http://tv123.vvvv.ee/tv.m3u",
    "http://rihou.cc:567/gggg.nzk"
]
# ==========================================================

# 1.精确别名【优先执行】：名字相近极易串台的频道全部放这里
alias_map = {
    "cctv-5":"CCTV5",
    "CCTV-03咪咕":"CCTV3",
    "CCTV-3HD":"CCTV3",
    "CCTV-3 综艺":"CCTV3",

    "凤凰(香港)":"凤凰香港",
    "凤凰卫视香港台":"凤凰香港",

    # 纬来系列
    "纬来电影台":"纬来电影",
    "緯來電影":"纬来电影",

    "纬来戏剧台":"纬来戏剧台",
    "纬来体育台":"纬来体育台",

    # 靖天、靖洋高危组，必须精确匹配，禁止模糊
    "靖天电影台":"靖天电影",
    "靖天戏剧台":"靖天戏剧",
    "靖天映画":"靖天映画",
    "靖洋戏剧台":"靖洋戏剧",
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
    "BRTV文艺":"北京文艺",

    "TVB星河频道":"TVB星河"
}

# 2.模糊关键词匹配：精确匹配没命中才跑这里；长关键词写上方，防止误匹配
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

def fix_url(link):
    """保留自定义协议：video://、rtmp://，仅处理//无协议链接"""
    lnk = link.strip()
    if lnk.startswith(("video://", "rtmp://")):
        return lnk
    if lnk.startswith("//"):
        lnk = "http:" + lnk
    return lnk

def get_std_name(raw_name):
    """优先精确别名，失败后执行关键词模糊匹配"""
    n = raw_name.strip()
    if n in alias_map:
        return alias_map[n]
    for keyword, std_name in fuzzy_rules:
        if keyword in n:
            return std_name
    return n

# 带重试+浏览器UA，解决超时、403防盗拦截
def get_req_session():
    sess = requests.Session()
    retry = Retry(total=3, backoff_factor=0.7, status_forcelist=[429,500,502,503,504])
    sess.mount("https://", HTTPAdapter(max_retries=retry))
    sess.mount("http://", HTTPAdapter(max_retries=retry))
    sess.headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    return sess

def load_txt(url):
    """自动兼容 UTF-8 / GBK / GB18030，后缀nzk/txt一律同等解析"""
    sess = get_req_session()
    try:
        resp = sess.get(url, timeout=25)
        resp.raise_for_status()
        # 多编码自动解码，解决GBK乱码
        content = None
        for code in ["utf-8", "gbk", "gb18030"]:
            try:
                content = resp.content.decode(code)
                break
            except UnicodeDecodeError:
                continue
        if not content:
            print(f"⚠️ {url} 编码无法识别，跳过")
            return []

        res = []
        for line in content.splitlines():
            ln = line.strip()
            if not ln or ln.startswith("#"):
                continue
            if "," in ln:
                name, raw_link = ln.split(",", maxsplit=1)
                std_name = get_std_name(name.strip())
                fixed_link = fix_url(raw_link)
                res.append((std_name, fixed_link))
        return res
    except Exception as e:
        print(f"⚠️ 请求 {url} 失败：{e}")
        return []

# 批量拉取所有源
all_source_data = []
for target_url in url_list:
    all_source_data.extend(load_txt(target_url))

# 台名归类 + 链接去重
channel = defaultdict(set)
all_got_names = set()
for name, link in all_source_data:
    channel[name].add(link)
    all_got_names.add(name)

# 白名单排序列表
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

# 打印不在白名单的台名，方便补充规则
unknown = all_got_names - std_set
if unknown:
    print("\n=========【陌生台名，可补充别名】=========")
    for u in sorted(unknown):
        print(f'"{u}":"填写标准台名",')
    print("===========================================\n")

# 按顺序导出结果
out_lines = []
for ch in order_list:
    for link in channel.get(ch, []):
        out_lines.append(f"{ch},{link}")

with open("qdyd.nzk", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines))

print("✅执行完成，已生成 qdyd.nzk")
print("已自动去重、台名标准化、仅保留白名单频道")
