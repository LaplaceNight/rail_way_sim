import networkx as nx
import csv

from collections import deque

# 定义地铁线路信息
line2_up = ["yuzui", "tianbaojie", "qinglianjie", "luotanglu", "youfangqiao", "yurundajie", "yuantong",
            "aotidong", "xinglongdajie", "jiqingmen", "yunjinlu", "mochouhu", "hanzhongmen", "shanghailu",
            "xinjiekou", "daxinggong", "xianmen", "minggugong", "muxuyuan", "xiamafang", "xiaolingwei",
            "zhonglingjie", "maqun", "jinmalu", "xianhemen", "xuezelu", "xianlinzhongxin", "yangshangongyuan",
            "nanda", "jingtianlu"]

line2_down = ["jingtianlu", "nanda", "yangshangongyuan", "xianlinzhongxin", "xuezelu", "xianhemen", "jinmalu",
              "maqun", "zhonglingjie", "xiaolingwei", "xiamafang", "muxuyuan", "minggugong", "xianmen", "daxinggong",
              "xinjiekou", "shanghailu", "hanzhongmen", "mochouhu", "yunjinlu", "jiqingmen", "xinglongdajie",
              "aotidong", "yuantong", "yurundajie", "youfangqiao", "luotanglu", "qinglianjie", "tianbaojie", "yuzui"]

line3_up = ["linchang", "xinghuolu", "dongdachengxianxueyuan", "taifenglu", "tianruncheng", "liuzhoudonglu",
            "shangyuanmen", "wutangguangchang", "xiaoshizhan", "nanjingzhan", "xinzhuang", "jimingsi",
            "fuqiaozhan", "daxinggong", "changfujie", "fuzimiao", "wudingmen", "yuhuamen", "kazimen",
            "daminglu", "mingfaguangchang", "nanjingnanzhan", "hongyundadao", "shengtaixilu", "tianyuanxilu","jiulonghu",
            "chengxindadao", "dongdajiulonghuxiaoqu", "mozhoudonglu"]

line3_down = ["mozhoudonglu", "dongdajiulonghuxiaoqu", "chengxindadao", "jiulonghu","tianyuanxilu", "shengtaixilu",
              "hongyundadao", "nanjingnanzhan", "mingfaguangchang", "daminglu", "kazimen", "yuhuamen",
              "wudingmen", "fuzimiao", "changfujie", "daxinggong", "fuqiaozhan", "jimingsi", "xinzhuang",
              "nanjingzhan", "xiaoshizhan", "wutangguangchang", "shangyuanmen", "liuzhoudonglu",
              "tianruncheng", "taifenglu", "dongdachengxianxueyuan", "xinghuolu", "linchang"]
line4_up = ["longjiangzhan", "caochangmen", "yunnanlu", "gulouzhan", "jimingsi", "jiuhuashan", "gangzicun",
            "jiangwangmiao", "wangjiawan", "jubaoshan", "xuzhuangzhan", "jinmalu", "huitonglu", "lingshanzhan",
            "dongliuzhan", "mengbeizhan", "huashuzhan", "xianlinhu"]

line4_down = ["xianlinhu", "huashuzhan", "mengbeizhan", "dongliuzhan", "lingshanzhan", "huitonglu", "jinmalu",
              "xuzhuangzhan", "jubaoshan", "wangjiawan", "jiangwangmiao", "gangzicun", "jiuhuashan", "jimingsi",
              "gulouzhan", "yunnanlu", "caochangmen", "longjiangzhan"]

line1_up = ["yaokedaxue", "nanjingjiaoyuan", "nanyida", "longmiandadao", "tianyindadao", "zhushanlu", "xiaolongwan", "baijiahu", "shengtailu", "hedingqiao", "shuanglongdadao", "nanjingnanzhan",
            "huashenmiao", "ruanjiandadao", "tianlongsi", "andemen", "zhonghuamen", "sanshanjie", "zhangfuyuan", "xinjiekou", "zhujianglu", "gulouzhan", "xuanwumen", "xinmofan", "nanjingzhan", "hongshan", "maigaoqiao"]

line1_down = ["maigaoqiao", "hongshan", "nanjingzhan", "xinmofan", "xuanwumen", "gulouzhan", "zhujianglu", "xinjiekou", "zhangfuyuan", "sanshanjie", "zhonghuamen", "andemen", "tianlongsi", "ruanjiandadao",
              "huashenmiao", "nanjingnanzhan", "shuanglongdadao", "hedingqiao", "shengtailu", "baijiahu", "xiaolongwan", "zhushanlu", "tianyindadao", "longmiandadao", "nanyida", "nanjingjiaoyuan", "yaokedaxue"]









# 创建有向图
G = nx.DiGraph()
linename=["line2_up","line2_down","line3_up","line3_down","line4_up","line4_down","line1_up","line1_down"]
# 添加节点和边
for line, stations in zip(linename,[line2_up, line2_down, line3_up, line3_down,line4_up,line4_down,line1_up,line1_down]):
    for i in range(len(stations) - 1):
        G.add_edge(stations[i], stations[i + 1], line=f"{line}")


station_name={"89":"linchang","90":"xinghuolu","91":"dongdachengxianxueyuan","73":"taifenglu","92":"tianruncheng",
              "93":"liuzhoudonglu","94":"shangyuanmen","95":"wutangguangchang","96":"xiaoshizhan",
              "14":"nanjingzhan","97":"xinzhuang","98":"jimingsi","99":"fuqiaozhan","26":"daxinggong",
              "100":"changfujie","101":"fuzimiao","102":"wudingmen","103":"yuhuamen","104":"kazimen",
              "105":"daminglu","106":"mingfaguangchang","44":"nanjingnanzhan","107":"hongyundadao",
              "108":"shengtaixilu","109":"tianyuanxilu","110":"jiulonghu","111":"chengxindadao",
              "112":"dongdajiulonghuxiaoqu","113":"mozhoudonglu",
              "40":"jingtianlu", "39":"nanda", "38":"yangshangongyuan","37": "xianlinzhongxin", "36":"xuezelu", "35":"xianhemen", "34":"jinmalu",
              "33":"maqun","32":"zhonglingjie", "31":"xiaolingwei", "30":"xiamafang", "29":"muxuyuan", "28":"minggugong", "27":"xianmen", "26":"daxinggong",
              "9":"xinjiekou", "25":"shanghailu", "24":"hanzhongmen", "23":"mochouhu", "22":"yunjinlu", "21":"jiqingmen", "20":"xinglongdajie",
              "19":"aotidong", "2":"yuantong", "18":"yurundajie", "17":"youfangqiao", "163":"luotanglu", "162":"qinglianjie", "161":"tianbaojie", "160":"yuzui",
              "114":"longjiangzhan", "115":"caochangmen", "116":"yunnanlu", "11":"gulouzhan", "98":"jimingsi","117": "jiuhuashan", "118":"gangzicun",
              "119":"jiangwangmiao", "120":"wangjiawan", "121":"jubaoshan", "122":"xuzhuangzhan", "34":"jinmalu", "123":"huitonglu", "124":"lingshanzhan",
              "125":"dongliuzhan", "126":"mengbeizhan", "127":"huashuzhan", "128":"xianlinhu",
              "16":"maigaoqiao","15":"hongshan","14":"nanjingzhan","13":"xinmofan","12":"xuanwumen","11":"gulouzhan","10":"zhujianglu","9":"xinjiekou","8":"zhangfuyuan","7":"sanshanjie","6":"zhonghuamen","5":"andemen","41":"tianlongsi","42":"ruanjiandadao","43":"huashenmiao","44":"nanjingnanzhan","45":"shuanglongdadao","46":"hedingqiao","47":"shengtailu","48":"baijiahu","49":"xiaolongwan","50":"zhushanlu","51":"tianyindadao","52":"longmiandadao","53":"nanyida","54":"nanjingjiaoyuan","55":"yaokedaxue"}



def bfs(graph, start, end):
    queue = deque([(start, [start])])
    visited = set([start])

    while queue:
        current, path = queue.popleft()

        for neighbor in graph.successors(current):
            if neighbor == end:
                return path + [neighbor]

            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))


def get_station_line(path):
    lines=[]
    for i in range(len(path) - 1):
        current_line = G[path[i]][path[i + 1]]['line']
        lines.append(current_line)
    lines
    route=[]
    change_station=[]
    route.append(lines[0])
    a=lines[0]
    for count,items in enumerate(lines):
        b=items
        if a==b:
            continue
        else:
            change_station.append(path[count])
            route.append(items)
            a=b
    if len(route)==1:
        return route[0],route[-1],None,None
    else: 
        return route[0],route[-1],route[1:],change_station
    

# start_station = "yuzui"
# end_station = "longjiangzhan"
# path = bfs(G, start_station, end_station)
# line_on,line_off,line_change,station_change=get_station_line(path)
in_channel=1
out_channel=1
with open("od_96_93.csv","r") as od,open("od_xiaoshi_liuzhou.csv","w",newline="") as out:
    original=csv.reader(od)
    writer = csv.writer(out)
    for row in original:
        if len(row)!=0:
            origin=station_name[row[5]]
            destination=station_name[row[7]]
            start_station = origin
            end_station = destination
            path = bfs(G, start_station, end_station)
            line_on,line_off,line_change,station_change=get_station_line(path)
                        


            
            writer.writerow([row[0],row[1],row[2],origin,in_channel, destination,out_channel,line_on,line_off,line_change,station_change])       
