#!/usr/bin/env python3
"""Storyboard of the Chinese example (labels are Chinese, comments English). python3 storyboard.py -> shots.json, then tools/resolve.py."""
import sys; sys.path.insert(0, "tools")
from sb import *

def LC(text, x, y, at="+0.4", size=52, rot=-2, **k): return L(text, x, y, at, size, rot, cn=True, **k)   # Chinese label (serif face); sb.LC does the same
DK = dict(blend="normal", color="#E4574B")   # stamps on dark boards
def HEAD(no, text):   # header of each habit: number + title
    return [L(f"NO.{no}", 250, 170, at="+0.15", size=58, rot=-4), LC(text, 250 + 150 + len(text) * 31, 175, at="+0.5", size=56, rot=1)]
def ROBOTS(x0, y, at, n=5, step=160, w=150):
    return [IM("robot", x0 + i * step, y, w, at=f"{at}+{0.1 + i * 0.16:.2f}", rot=(-4, 3, -2, 5, -3)[i % 5]) for i in range(n)]

shots = [
 # -- hook
 S("S01", "B01", "bg_office", [IM("chair", 600, 580, 430, at="+0.0", rot=-2), LC("没有升职", 1350, 320, at="+0.5", size=60), LC("没有加薪", 1380, 480, at="+1.5", size=60, rot=2),
    LC("也没人通知你", 1350, 640, at="+2.4", size=60)], push=(1.0, 1.06)),
 S("S02", "B01:agent", "bg_printout", [IM("robot_type", 640, 510, 580, at="+0.05"), L("CODING AGENT", 640, 905, at="+0.5", size=42),
    IM("nameplate", 1400, 520, 560, at="B01:boss", mode="drop"), LC("经 理", 1400, 500, at="B01:boss+0.35", size=62, rot=0), ST("已上任", 1430, 770, "B01:boss+0.7", size=96)]),
 S("S03", "B02", "bg_memo", [
    IM("clipboard", 400, 330, 170, at="B02:pick"), LC("挑任务", 400, 500, at="B02:pick+0.2", size=40),
    IM("typewriter", 960, 280, 250, at="B02:write"), LC("写说明", 960, 440, at="B02:write+0.2", size=40),
    IM("robot_run", 1520, 320, 210, at="B02:send"), LC("派活", 1520, 500, at="B02:send+0.2", size=40),
    IM("phone", 400, 745, 210, at="B02:follow"), LC("跟进", 400, 915, at="B02:follow+0.2", size=40),
    IM("magnifier", 960, 770, 105, at="B02:check"), LC("验收", 960, 915, at="B02:check+0.2", size=40),
    IM("stamp_tool", 1520, 755, 250, at="B02:ship"), LC("决定上线", 1520, 915, at="B02:ship+0.2", size=40),
    ST("管理", 960, 600, "B02:manage", size=150, rot=-8)]),
 S("S04", "B03", "bg_blueprint", [IM("typewriter", 500, 560, 460, at="B03:best"), LC("最会写提示词？", 500, 900, at="B03:best+0.4", size=50), ST("不一定", 540, 540, "B03:best+2.6", size=110),
    IM("necktie", 1250, 520, 150, at="B03:learn", rot=6), IM("nameplate", 1500, 640, 400, at="B03:learn+0.4"), LC("学会了当经理", 1420, 900, at="B03:learn+0.8", size=56)], push=(1.0, 1.05)),
 S("S05", "B04:addy", "bg_office", [PH("article_cover", 800, 390, 980, at="+0.0", rot=-2), TP(330, 230, "+0.3"), TP(1290, 200, "+0.35", rot=30),
    L("ADDY OSMANI", 470, 690, at="+0.3", size=50), L("CLAUDE CODE @ ANTHROPIC", 1150, 700, at="+1.6", size=36, rot=1),
    L("2026.11.08 · X", 1600, 180, at="B04:post", size=38, rot=3), LC("两天", 980, 870, at="B04:views", size=56), NUM(50, 1440, 860, "B04:views+0.5", unit="万+ 阅读", size=130)], flip=True),
 S("S06", "B05", "bg_dark", [Q("你对烂老板的每一句吐槽，都是一份怎么用 Agent 的缺陷报告。", "Addy Osmani · 2026.11", 960, 470, 1350, "B05:gripe"),
    ST("BUG REPORT", 1380, 860, "B05:bug+0.9", size=84, **DK)], push=(1.04, 1.0)),
 S("S07", "B06-3.0", "bg_office", [TITLE("你的 Agent，把你变成了经理", "+0.15", sub="十个管理习惯 · 改编自 Addy Osmani 长文", size=96)], push=(1.06, 1.0)),

 # -- 1 check its work
 S("S08", "B06", "bg_calendar", [NUM(10, 560, 470, "+0.5", unit="个习惯", size=200), LC("按影响力排序", 560, 740, at="+1.4", size=48),
    L("NO.1", 1400, 330, at="B06:n1", size=70, rot=-4), LC("给它一个能自查的办法", 1380, 500, at="B06:n1+0.5", size=52, rot=1), UL(1380, 570, 520, "B06:n1+1.6")], trans="push"),
 S("S09", "B07", "bg_printout", [IM("robot_paper", 600, 520, 520, at="B07:looks"), LC("「看起来做完了」", 600, 920, at="B07:looks+0.4", size=50),
    IM("magnifier", 1400, 430, 260, at="B07:suite", rot=-12), LC("你 = 它的测试", 1400, 740, at="B07:suite+0.5", size=56), NOTE("错了，等你碰巧看见", 1400, 900, "B07:suite+2.2", size=52)], flip=True),
 S("S10", "B08", "bg_office", [PH("foreman", 600, 520, 620, at="B08:newmgr", rot=-2), LC("新手经理：事事亲自验收", 600, 915, at="B08:newmgr+0.5", size=42),
    IM("bottle", 1420, 540, 170, at="B08:quarter"), L("1 QUARTER LATER", 1420, 180, at="B08:quarter+0.3", size=36, rot=2), ST("瓶颈", 1460, 520, "B08:quarter+1.4", size=130)], push=(1.0, 1.05)),
 S("S11", "B09", "bg_blueprint", [ST("通过", 640, 360, "B09:pass", size=150, rot=-8), ST("不通过", 1300, 380, "B09:pass+0.9", size=130, rot=6),
    LC("测试", 520, 720, at="B09:pass+2.7", size=56), LC("构建", 960, 740, at="B09:pass+3.3", size=56, rot=2), LC("截图", 1400, 720, at="B09:pass+3.9", size=56)]),
 S("S12", "B09:proof", "bg_memo", [IM("robot_paper", 620, 570, 560, at="+0.0"), LC("让它把结果拿给你看", 1370, 400, at="+0.4", size=48), ST("证据", 1400, 660, "+1.4", size=140)], flip=True),

 # -- 2 tell it what it cannot see
 S("S13", "B10", "bg_map", HEAD(2, "把它看不见的，告诉它") + [PH("briefing", 600, 590, 720, at="B10:intent", rot=-2), LC("指挥官意图", 600, 925, at="B10:intent+0.5", size=46),
    LC("给背景，不给控制", 1450, 540, at="B10:netflix", size=50, rot=2), L("NETFLIX: CONTEXT, NOT CONTROL", 1450, 680, at="B10:netflix+0.8", size=28)], trans="push"),
 S("S14", "B11", "bg_printout", [IM("printout", 300, 520, 230, at="B11:repo"), IM("robot_note", 640, 530, 260, at="B11:repo+0.3"), LC("代码里有的：不用说", 500, 930, at="B11:repo+0.8", size=42),
    IM("meeting", 1420, 380, 460, at="B11:meeting"), LC("会上的决定", 1420, 680, at="B11:meeting+1.3", size=46), LC("为什么重要", 1420, 810, at="B11:meeting+2.7", size=46, rot=2),
    LC("怎样才算做完", 1420, 925, at="B11:meeting+4.0", size=46)]),
 S("S15", "B12", "bg_memo", [LC("「让仪表盘快一点」", 500, 200, at="B12:vague", size=48), IM("gauge", 500, 580, 440, at="B12:vague+0.2"), ST("太模糊", 540, 620, "B12:vague+1.3", size=110),
    LC("目标：2 秒内打开", 1380, 300, at="B12:target", size=44), LC("原因：客户投诉最多", 1380, 450, at="B12:why", size=44, rot=1),
    LC("限制：不动数据库结构", 1380, 600, at="B12:limits", size=44), LC("验收：跑脚本，看前后数字", 1380, 750, at="B12:run", size=40, rot=1),
    NOTE("（数字只是举例）", 1380, 900, "B12:run+1.6", size=40)]),
 S("S16", "B13", "bg_blueprint", [IM("robot", 420, 600, 380, at="+0.1"), NOTE("你想要什么？", 880, 320, "B13:interview", size=56), NOTE("给谁用？", 900, 480, "B13:interview+1.0", size=56, rot=3),
    NOTE("怎样算完？", 880, 640, "B13:interview+2.0", size=56), IM("folder", 1480, 560, 400, at="B13:spec"), L("SPEC.MD", 1480, 880, at="B13:spec+0.4", size=46),
    LC("开新会话，照着做", 1480, 220, at="B13:spec+1.5", size=44, rot=2)], flip=True),

 # -- 3 compound corrections, hard limits
 S("S17", "B14", "bg_memo", HEAD(3, "让每次纠正都有复利") + [LC("同一个错", 480, 420, at="B14:twice", size=52), NUM(2, 480, 660, "B14:twice+0.6", unit="次", size=200),
    IM("notebook", 1340, 500, 600, at="B14:md", rot=3), L("CLAUDE.MD", 1340, 790, at="B14:md+0.4", size=50), NOTE("比换组的同事、换代的模型都活得久", 1100, 890, "B14:outlast", size=46), UL(1100, 935, 700, "B14:outlast+2.2")], trans="push", flip=True),
 S("S18", "B15", "bg_office", HEAD(4, "默认让它自己拿主意") + [PH("grove", 420, 560, 270, at="B15:grove"), L("ANDY GROVE · INTEL", 420, 885, at="B15:grove+0.5", size=30),
    L("PHOTO: INTEL FREE PRESS / CC BY 2.0", 420, 945, at="B15:grove+0.6", size=18, rot=0, type=False),
    IM("book", 860, 570, 250, at="B15:grove+1.2", rot=4), L("HIGH OUTPUT MANAGEMENT", 890, 885, at="B15:grove+1.6", size=26, rot=1),
    LC("管多紧？", 1480, 400, at="B15:grove+2.6", size=60), LC("看这件事上的表现", 1480, 560, at="B15:grove+4.4", size=44, rot=2), NOTE("不看整体多能干", 1480, 720, "B15:grove+6.6", size=54)]),
 S("S19", "B16", "bg_blueprint", [IM("typewriter", 480, 430, 330, at="B16:request"), LC("提示词 · 说明文件 = 请求", 500, 740, at="B16:request+0.5", size=40),
    IM("padlock", 1400, 420, 250, at="B16:hook"), LC("底线 = 强制规则", 1400, 740, at="B16:hook+0.5", size=48, rot=2)], flip=True),
 S("S20", "B16:caps", "bg_dark", [IM("megaphone", 520, 500, 500, at="+0.0", rot=-4), L("NEVER EVER DO THIS!!!", 1320, 300, at="+0.3", size=40), LC("「别偷懒」", 1320, 450, at="+1.6", size=56, rot=2),
    ST("可以停了", 1340, 640, "+3.0", size=100, **DK), LC("过度流程 = 新的微观管理", 960, 880, at="B16:micro", size=52, rot=-1)]),

 # -- 4 plan first, steer early
 S("S21", "B17", "bg_blueprint", HEAD(5, "先谈计划，再让它动手") + [IM("plans", 480, 620, 520, at="+0.9", rot=-3)] + ROBOTS(1000, 540, "B17:five") +
    [LC("5 个 Agent · 任务重叠", 1320, 780, at="B17:five+1.2", size=42), NOTE("≠ 5 倍产出", 1320, 900, "B17:five+2.6", size=60)], trans="push"),
 S("S22", "B17:conflict", "bg_dark", [IM("knot", 700, 540, 620, at="+0.0"), ST("合并冲突", 1400, 430, "+0.5", size=110, **DK), LC("作者：5 位", 1400, 680, at="+1.2", size=56, rot=2)]),
 S("S23", "B18", "bg_map", HEAD(6, "早点纠偏，果断重来") + [IM("wheel", 480, 590, 380, at="B18:esc"), L("ESC", 480, 890, at="B18:esc+0.3", size=64),
    NUM(2, 1120, 470, "B18:two", unit="次没纠正过来", size=130), IM("wastebasket", 1140, 800, 200, at="B18:two+1.6"), LC("清空会话 · 重写提示词", 1540, 800, at="B18:fresh", size=38, rot=2)], flip=True),
 S("S24", "B18:third", "bg_printout", [IM("printout", 520, 560, 300, at="+0.0"), LC("第 3 次纠正", 1300, 380, at="+0.2", size=64), NOTE("只是让它多背一段失败记录", 1300, 600, "+1.2", size=52)]),
 S("S25", "B19", "bg_calendar", [IM("tape_reel", 600, 540, 600, at="B19:rewind"), L("/REWIND", 600, 900, at="B19:rewind+0.3", size=54), LC("代码 + 对话，都能退回去", 1400, 330, at="B19:rewind+1.6", size=40, rot=2),
    LC("先试更大胆的方案", 1400, 600, at="B19:bold", size=52), UL(1400, 670, 460, "B19:bold+1.0")], flip=True),

 # -- 5 never delegate the judgment
 S("S26", "B20", "bg_dark", HEAD(7, "活可以交出去，判断不行") + [IM("printout", 420, 640, 270, at="B20:diff"), NUM(600, 960, 470, "B20:diff+0.2", unit="行改动", size=140),
    LC("命名合理 ✓", 1540, 380, at="B20:names", size=42, rot=2), LC("测试全绿 ✓", 1540, 540, at="B20:green", size=42), ST("批准", 1340, 760, "B20:approve+0.3", size=150, **DK)], trans="push"),
 S("S27", "B21", "bg_memo", [IM("stamp_tool", 520, 760, 330, at="+0.1"), LC("代码审查？", 520, 330, at="B21:ratify", size=64), ST("代码追认", 560, 480, "B21:ratify+2.2", size=110),
    IM("robot_run", 1400, 480, 330, at="B21:trap"), NOTE("差点就推上线了", 1400, 800, "B21:trap+1.6", size=56), LC("—— 艾迪自己", 1500, 930, at="B21:trap+2.6", size=36, rot=1)]),
 S("S28", "B21:paged", "bg_dark", [IM("phone", 560, 560, 480, at="+0.0"), IM("alarm", 1250, 400, 240, at="+0.5", rot=8), LC("半夜出事，找的是你", 1280, 760, at="+1.3", size=52)], flip=True),
 S("S29", "B22", "bg_calendar", HEAD(8, "设计不用你盯的流程") + [IM("bed", 700, 640, 760, at="B22:night"), IM("robot_type", 1500, 620, 330, at="B22:night+0.6"), LC("让它跑一整夜之前", 1100, 920, at="B22:night+1.0", size=44)]),
 S("S30", "B22:q1", "bg_blueprint", [IM("clipboard", 400, 560, 380, at="+0.0", rot=-3), LC("① 它知道什么叫做完吗", 1150, 200, at="+0.1", size=46), LC("② 能自己检查吗", 1080, 370, at="B22:q2", size=46, rot=1),
    LC("③ 边界在哪", 1040, 540, at="B22:q3", size=46), LC("④ 上限是多少", 1060, 710, at="B22:q4", size=46, rot=1), LC("⑤ 最后谁来批准", 1090, 880, at="B22:q5", size=46)]),
 S("S31", "B23", "bg_office", [IM("folder", 480, 580, 420, at="B23:pilot"), NUM(3, 1220, 400, "B23:pilot+0.6", unit="个文件先试", size=140), LC("试用期", 1220, 640, at="B23:pilot+0.2", size=60, rot=2),
    IM("robot_run", 1480, 860, 220, at="B23:rest", mode="slide", **{"from": [-700, 0]})], flip=True),
 S("S32", "B24", "bg_office", HEAD(9, "扩大验证，不是注意力") + [IM("coins", 500, 620, 480, at="B24:tax"), LC("编排税", 500, 900, at="B24:tax+0.4", size=60)] + ROBOTS(1040, 500, "B24:four", w=140) +
    [CI(500, 640, 300, 240, "B24:tax+2.2"), NOTE("每多一个，更贵", 500, 380, "B24:tax+3.6", size=50), LC("一天四五个后台 Agent", 1360, 730, at="B24:four+1.4", size=40), NOTE("有些日子，这都嫌多", 1360, 890, "B24:four+3.2", size=54)], trans="push"),
 S("S33", "B25", "bg_blueprint", [LC("AI 写了多少代码", 500, 430, at="B25:metric", size=48), ST("别量这个", 540, 600, "B25:metric+1.0", size=100),
    IM("stopwatch", 1150, 470, 230, at="B25:revert"), LC("合并速度", 1150, 760, at="B25:revert+0.2", size=44), IM("wastebasket", 1580, 480, 220, at="B25:revert+0.8"), LC("返工次数", 1580, 760, at="B25:revert+1.0", size=44, rot=2)], flip=True),
 S("S34", "B26", "bg_memo", HEAD(10, "决定不做什么") + [LC("开工几乎免费", 480, 400, at="B26:free", size=50), IM("lunchbox", 480, 660, 360, at="B26:lunch"), LC("午饭前就能交一份改动", 500, 900, at="B26:lunch+0.6", size=40),
    IM("magnifier", 1400, 470, 220, at="B26:scarce", rot=-10), LC("最稀缺：审查 + 验证", 1400, 760, at="B26:scarce+0.5", size=46, rot=2)]),
 S("S35", "B26:no", "bg_dark", [IM("hand_stop", 600, 560, 380, at="+0.0"), ST("不", 1300, 520, "+0.9", size=300, **DK)]),

 # -- 6 where the analogy breaks
 S("S36", "B27", "bg_lab", [LC("这个比喻，也有不成立的地方", 960, 220, at="B27:break", size=52), IM("robot", 620, 640, 360, at="B27:junior"), IM("badge", 1300, 590, 240, at="B27:junior+0.3", rot=5),
    LC("初级工程师", 1300, 900, at="B27:junior+0.5", size=48), ST("不是", 1330, 620, "B27:junior+1.3", size=120)], trans="push"),
 S("S37", "B28", "bg_office", [PH("card_puncher", 500, 620, 500, at="B28:pushback", rot=-2), NOTE("「这样不对。」", 560, 200, "B28:pushback+1.6", size=64),
    IM("robot_paper", 1400, 640, 440, at="B28:obey"), NOTE("「好的！」", 1420, 220, "B28:obey+0.4", size=70, rot=3), ST("很有把握", 1640, 420, "B28:sure+0.4", size=84)], flip=True),
 S("S38", "B29", "bg_lab", [L("WHARTON · SHAW & NAVE · 2026", 960, 180, at="B29:wharton", size=40), IM("brain", 440, 580, 420, at="B29:wharton+0.3"), LC("3 组实验", 440, 900, at="B29:wharton+1.0", size=50),
    NUM(1372, 1280, 470, "B29:n1372", unit="人", size=170), LC("参与者", 1280, 720, at="B29:n1372+1.2", size=46), NOTE("AI 一半的答案是故意给错的", 1280, 880, "B29:n1372+2.6", size=44)], flip=True),
 S("S39", "B29:p73", "bg_dark", [NUM(73, 660, 440, "+0.0", unit="%", size=280), LC("AI 答错时，照单全收", 660, 740, at="+1.0", size=48),
    L("SOURCE: ADDY OSMANI, COGNITIVE SURRENDER (2026.05)", 700, 920, at="+1.6", size=22, type=False), ST("更自信了", 1420, 480, "B29:conf+0.5", size=110, **DK)]),
 S("S40", "B30", "bg_dark", [IM("flag", 520, 560, 290, at="B30:surrender"), L("COGNITIVE SURRENDER", 1260, 200, at="B30:surrender+0.2", size=40), LC("认知投降", 1260, 360, at="B30:surrender+0.5", size=72),
    IM("robot", 1120, 680, 220, at="B30:argue"), IM("robot_note", 1480, 680, 175, at="B30:argue+0.4"), LC("让它反驳自己的答案", 1300, 930, at="B30:argue+1.2", size=40), ST("对策", 1640, 420, "B30:argue+2.4", size=80, **DK)], flip=True),
 S("S41", "B31", "bg_memo", [IM("robot_note", 420, 540, 250, at="B31:notebook"), LC("没有经验，只有笔记", 440, 890, at="B31:notebook+0.5", size=42),
    PH("typing_pool", 1340, 450, 620, at="B31:people", rot=2), NOTE("管好 5 个 Agent ≠ 管好 5 个人", 1300, 790, "B31:people+1.4", size=48), LC("激励", 1000, 900, at="B31:none", size=44), LC("冲突", 1210, 915, at="B31:none+0.7", size=44, rot=2), LC("成长", 1420, 900, at="B31:none+1.4", size=44), LC("信任", 1630, 915, at="B31:none+2.1", size=44, rot=2), ST("练不到", 1320, 480, "B31:none+4.6", size=120, **DK)]),

 # -- ending
 S("S42", "B32", "bg_office", [IM("nameplate", 560, 500, 620, at="B32:title2"), L("MANAGER", 560, 480, at="B32:title2+0.3", size=48, rot=0), ST("不需要", 700, 690, "B32:title2+1.2", size=120),
    LC("写清背景", 1420, 320, at="B32:staff+2.6", size=56), LC("定义完成", 1440, 500, at="B32:staff+3.5", size=56, rot=2), LC("认真审查", 1420, 680, at="B32:staff+4.4", size=56)], trans="push"),
 S("S43", "B33", "bg_calendar", [IM("hourglass", 520, 540, 250, at="B33:minutes"), LC("过去：几个季度", 520, 900, at="B33:minutes+0.6", size=46), IM("stopwatch", 1200, 540, 260, at="B33:minutes+2.6"),
    LC("现在：几分钟", 1200, 900, at="B33:minutes+2.9", size=46, rot=2), NOTE("错了，可以撤回", 1580, 520, "B33:undo", size=54)], flip=True),
 S("S44", "B34", "bg_dark", [Q("这份工作，正在从「写代码」，变成「让好代码被写出来的那个原因」。", "Addy Osmani", 960, 440, 1350, "+0.1"), IM("typewriter", 430, 800, 230, at="+1.6", rot=-5), AR([600, 800], [1250, 800], "+2.6"), IM("robot_paper", 1450, 780, 230, at="+3.4")], push=(1.0, 1.05)),
 S("S45", "B35", "bg_office", [IM("chair", 520, 590, 420, at="B35:born"), IM("robot", 860, 720, 220, at="B35:born+0.7"), LC("练习，变得很便宜", 1400, 450, at="B35:cheap", size=64), UL(1400, 530, 520, "B35:cheap+1.2"),
    L("ORIGINAL: ADDY OSMANI · X · 2026.11.08", 1400, 900, at="B35:cheap+2.2", size=24, type=False), IM("nameplate", 1400, 700, 360, at="B35:cheap+3.0", mode="drop")], flip=True, push=(1.0, 1.06)),
]

save(shots,
    pauses={"B06": 3.0}, tail=3.0,
    score=[dict(src="music/hook.mp3", at="0", to="B06", start=0.0),
           dict(src="music/chA.mp3", at="B06", to="B14", start=0.0),
           dict(src="music/chB.mp3", at="B14", to="B20", start=0.0),
           dict(src="music/chC.mp3", at="B20", to="B27", start=0.0),
           dict(src="music/chD.mp3", at="B27", to="B32", start=0.0),
           dict(src="music/end.mp3", at="B32", to=None, start=0.0)],
    musicHi=0.26, musicLo=0.11, teaserVol=0.45,
    cover="cover.jpg", coverFrames=15, motif="img/robot", subtitles=True,
    teaser=[dict(at="B08:quarter+1.3", len=1.3), dict(at="B26:no+1.0", len=1.3), dict(at="B29:p73+1.6", len=1.4),
            dict(at="B17:conflict+1.2", len=1.3), dict(at="B28:obey+0.6", len=1.4)],
    teaserMusic="music/hook.mp3", teaserStart=38*30,
    cover_shot=dict(bg="img/bg_dark.png", els=[
        dict(t="piece", src="img/robot_type.png", x=520, y=560, w=720, rot=-3),
        dict(t="piece", src="img/nameplate.png", x=1380, y=300, w=640, rot=3),
        dict(t="label", text="MANAGER", x=1380, y=280, size=52, rot=3),
        dict(t="tape", x=1100, y=170, rot=-30, w=180),
        dict(t="title", text="你的 Agent 把你变成了经理", x=1260, y=640, size=78),
        dict(t="label", text="没升职，没加薪，但你已经在带团队了", x=1260, y=820, size=40, rot=1, cn=True),
        dict(t="stamp", text="十个习惯", x=330, y=140, size=64, rot=-8, blend="normal", color="#E4574B")]),
)
