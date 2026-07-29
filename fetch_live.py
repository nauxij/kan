import requests

url1 = "https://pan.vma.cc/pan/down.php/350735607a786faaaa69aa5bbe3a3078.txt"
url2 = "https://gitee.com/x21y/yx/raw/main/qdyd.txt"
out_file = "qdyd.nzk"

# ========== 你的自定义排序顺序（原样复制，包含分组空行） ==========
order_lines = """央卫港澳台,#genre#
CCTV1：CCTV1#CCTV1综合#CCTV-1综合#CCTV-01#CCTV1HD
山东卫视：山东卫视#山东卫视4K
凤凰香港：凤凰香港
CHC动作电影：CHC动作电影
CCTV3：CCTV3#CCTV3综艺#CCTV-3综艺#CCTV-03

CCTV5：CCTV5#CCTV5体育#CCTV-5 体育#CCTV-05
CCTV5+：CCTV5+#CCTV5+体育#CCTV-5+ 体育赛事
央视台球：央视台球#CCTV央视台球
CCTV6：CCTV6#CCTV6电影#CCTV-6 电影#CCTV-06
河南曲艺：河南曲艺

CCTV8：CCTV8#CCTV8电视剧#CCTV-8 电视剧#CCTV-08
兵器科技：兵器科技
梨园频道：梨园#梨园频道#犁园频道
CCTV11：CCTV11#CCTV11戏曲#CCTV-11 戏曲#CCTV-11
CCTV12：CCTV12#CCTV12法制#CCTV12社会与法#CCTV-12 社会与法#CCTV-12

星河：星河
千禧经典：千禧经典
CCTV15：CCTV15#CCTV15音乐#CCTV-15 音乐#CCTV-15
纬来育乐：纬来育乐
CCTV17：CCTV17#CCTV17农业#CCTV17农村#CCTV-17 农业农村#CCTV-17

山东文旅：山东文旅
纬来电影：纬来电影
天津文艺：天津文艺
北京文艺：北京文艺#BTV2
淘电影：淘电影


东森电影：东森电影
Popc：Popc
天映频道：天映频道#天映电影
龙华偶像：龙华偶像
山东教育卫视：山东教育卫视#山东教育

湖南卫视：湖南卫视#湖南卫视4K
浙江卫视：浙江卫视#浙江卫视4K
东方卫视：东方卫视#上海卫视#东方卫视4K
江苏卫视：江苏卫视#江苏卫视4K
北京卫视：北京卫视#北京卫视4K

安徽卫视：安徽卫视
天津卫视：天津卫视
辽宁卫视：辽宁卫视
深圳卫视：深圳卫视#深圳卫视4K
东南卫视：东南卫视

湖北卫视：湖北卫视
广东卫视：广东卫视#广东卫视4K
黑龙江卫视：黑龙江卫视
贵州卫视：贵州卫视
河北卫视：河北卫视

重庆卫视：重庆卫视
海南卫视：海南卫视
四川卫视：四川卫视#四川卫视4K
山西卫视：山西卫视
河南卫视：河南卫视

江西卫视：江西卫视
广西卫视：广西卫视
吉林卫视：吉林卫视
云南卫视：云南卫视
陕西卫视：陕西卫视

无线功夫：无线功夫

天津影视：天津影视
精彩影视：精彩影视
西部电影：西部电影
黑龙江影视：黑龙江影视

陕西都市青春：都市青春
重温经典：重温经典
天映经典：天映经典
靖洋戏剧：靖洋戏剧
龙华电影：龙华电影

龙华经典：龙华经典
龙华戏剧：龙华戏剧
峨眉电影：峨眉电影
靖天电影：靖天电影
CHC影迷电影：CHC影迷电影
CHC家庭影院：CHC家庭影院#CHC家庭电影


黑龙江影视：黑龙江影视
第一剧场：第一剧场#CCTV第一剧场
风云剧场：风云剧场#CCTV风云剧场
风云音乐：风云音乐#CCTV风云音乐

华数剧场：华数剧场
华数影院：华数影院
云南都市：云南都市
云南娱乐：云南娱乐

龙祥电影：龙祥电影
搜狐剧场：搜狐剧场"""

# 解析排序表，生成 {频道名称:完整行内容}
order_list_raw = order_lines.splitlines()
# key取冒号前面作为频道名
order_map = {}
order_index = []
for line in order_list_raw:
    line_strip = line.strip()
    if not line_strip:
        order_index.append("")
        continue
    if "：" in line:
        name = line.split("：",1)[0].strip()
        order_map[name] = line
        order_index.append(name)
    else:
        order_index.append(line)


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
    all_text = t1 + "\n" + t2
    #源数据去重
    source_lines = list(dict.fromkeys(all_text.splitlines()))
    #源数据字典 key=频道名，value=完整行
    source_dict = {}
    for l in source_lines:
        ll = l.strip()
        if not ll:
            continue
        if "：" in ll:
            cname = ll.split("：",1)[0].strip()
            source_dict[cname] = ll

    output = []
    unknown = []
    #按预设顺序输出
    for item in order_index:
        if item == "":
            output.append("")
            continue
        if item in source_dict:
            output.append(source_dict[item])
        else:
            #预设里有，但源没这个频道，就写排序模板里原始行
            if item in order_map:
                output.append(order_map[item])

    #收集不在排序列表里的频道，追加到末尾
    for cname,full_line in source_dict.items():
        if cname not in order_map:
            unknown.append(full_line)

    if unknown:
        output.append("")
        output.append("# 其它频道")
        output.extend(unknown)

    final_text = "\n".join(output)
    with open(out_file,"w",encoding="utf-8") as f:
        f.write(final_text)
    print("完成写入qdyd.nzk，已按自定义顺序排列")
