# -*- coding: utf-8 -*-
"""
小章鱼主题 · 动画层优化器 (motion v2)

只改「动画」，不改「美术」：
  1. 用新的 keyframes 库替换每个 SVG 的 <style> 块
  2. 给身体主组写入以「底部坐姿点」为轴心的 transform-origin（官方约定用 px 值）
  3. 把成对的触手 ellipse 包成 <g>，各自带相位延迟 -> 波浪式蠕动
  4. 给睁眼状态叠加一片同色系「眼皮」，做自然眨眼
  5. 修正 idle 瞳孔：高光并入瞳孔组一起跟随光标

不引入 @import / url() / <script>，符合主题 SVG 净化规则。
"""
import re
import pathlib

ROOT = pathlib.Path(r"C:\Users\yinchangjing\clawd-octo-agent")
ASSETS = ROOT / "assets"

# ---------------------------------------------------------------- keyframes

STYLE = """<style>
@keyframes breathe{0%,100%{transform:translateY(0) scale(1,1)}50%{transform:translateY(-1.6px) scale(1.012,1.022)}}
@keyframes breatheSlow{0%,100%{transform:translateY(0) scale(1,1)}50%{transform:translateY(-1.1px) scale(1.008,1.016)}}
@keyframes breatheDeep{0%,100%{transform:translateY(0) scale(1,1)}48%{transform:translateY(-2.3px) scale(1.016,1.03)}}
@keyframes float{0%,100%{transform:translateY(0) rotate(0deg)}50%{transform:translateY(-3.4px) rotate(.8deg)}}
@keyframes wobble{0%,100%{transform:rotate(0deg)}30%{transform:rotate(-1.8deg)}70%{transform:rotate(1.8deg)}}
@keyframes sway{0%,100%{transform:rotate(-2.6deg)}50%{transform:rotate(2.6deg)}}
@keyframes shake{0%,100%{transform:translate(0,0) rotate(0deg)}20%{transform:translate(-1.8px,.4px) rotate(-.7deg)}45%{transform:translate(1.8px,-.4px) rotate(.7deg)}70%{transform:translate(-1px,.3px) rotate(-.4deg)}}
@keyframes shakeHard{0%,100%{transform:translate(0,0) rotate(0deg)}18%{transform:translate(-2.6px,.8px) rotate(-1.4deg)}42%{transform:translate(2.6px,-.8px) rotate(1.4deg)}66%{transform:translate(-1.6px,1px) rotate(-.9deg)}86%{transform:translate(1.6px,-1px) rotate(.9deg)}}
@keyframes bounce{0%,100%{transform:translateY(0) scale(1,1)}16%{transform:translateY(.8px) scale(1.035,.965)}44%{transform:translateY(-5.5px) scale(.98,1.035)}70%{transform:translateY(.5px) scale(1.028,.975)}88%{transform:translateY(-1.2px) scale(.995,1.005)}}
@keyframes wave{0%,100%{transform:rotate(0deg)}50%{transform:rotate(13deg)}}
@keyframes pulse{0%,100%{opacity:.45;transform:scale(.82)}50%{opacity:1;transform:scale(1.12)}}
@keyframes glow{0%,100%{filter:brightness(1) saturate(1)}50%{filter:brightness(1.09) saturate(1.05)}}
@keyframes typepress{0%,100%{transform:translateY(0)}50%{transform:translateY(1.6px)}}
@keyframes zz{0%{opacity:0;transform:translate(0,2px) scale(.55)}35%{opacity:.95;transform:translate(3px,-7px) scale(.9)}75%{opacity:.5;transform:translate(6px,-15px) scale(1)}100%{opacity:0;transform:translate(9px,-22px) scale(1.05)}}
@keyframes ink{0%{opacity:0;transform:scale(.25)}35%{opacity:.85;transform:scale(1)}100%{opacity:0;transform:scale(1.55)}}
@keyframes smoke{0%{opacity:.5;transform:translateY(0) scale(.75)}100%{opacity:0;transform:translateY(-18px) scale(1.5)}}
@keyframes look{0%,100%{transform:translateX(-1.4px)}50%{transform:translateX(1.4px)}}
@keyframes blink{0%,90%,100%{transform:scaleY(0)}91.5%{transform:scaleY(1)}93%{transform:scaleY(0)}94.2%{transform:scaleY(.5)}95.4%{transform:scaleY(0)}}
@keyframes tentacle{0%,100%{transform:rotate(-4.2deg) translateY(0)}50%{transform:rotate(4.2deg) translateY(1.1px)}}
@keyframes tentacleMini{0%,100%{transform:rotate(-8deg) translateY(0)}50%{transform:rotate(8deg) translateY(1px)}}
@keyframes swayTentacle{0%,100%{transform:rotate(-7deg)}50%{transform:rotate(7deg)}}
</style>"""

# 只有 sweeping / annoyed 用到的补充 keyframes，按需注入，避免污染其余 28 个文件
EXTRA_KEYFRAMES = """@keyframes tentacleTwitch{0%,100%{transform:rotate(-7deg) translateY(0)}50%{transform:rotate(7deg) translateY(1.6px)}}
@keyframes scrub{0%,100%{transform:rotate(3.5deg) translateY(.7px)}50%{transform:rotate(-2deg) translateY(0)}}
@keyframes sweep{0%,100%{transform:rotate(-7deg)}50%{transform:rotate(7deg)}}
@keyframes dust{0%{opacity:0;transform:translate(0,0) scale(.4)}25%{opacity:.55}100%{opacity:0;transform:translate(16px,-14px) scale(1.4)}}
@keyframes dart{0%,100%{transform:translateX(-1.7px) scale(1)}28%{transform:translateX(1.7px) scale(1.07)}52%{transform:translateX(-.8px) scale(1.01)}76%{transform:translateX(1.4px) scale(1.05)}}
@keyframes anger{0%,100%{opacity:.65;transform:translate(0,0) scale(.9)}50%{opacity:1;transform:translate(2px,-2px) scale(1.16)}}
"""

# 每个文件身体主组的新动画（含时长/缓动）
BODY = {
    "octo-idle-follow.svg": "breatheSlow 4.2s ease-in-out infinite",
    "octo-working-thinking.svg": "float 3.4s ease-in-out infinite",
    "octo-working-typing.svg": "breathe 2.6s ease-in-out infinite",
    "octo-working-juggling.svg": "bounce 1.7s ease-in-out infinite",
    "octo-working-building.svg": "glow 2.4s ease-in-out infinite",
    "octo-working-headphones-groove.svg": "sway 1.8s ease-in-out infinite",
    "octo-sleep-yawn.svg": "breatheSlow 3.6s ease-in-out infinite",
    "octo-sleep-doze.svg": "breatheDeep 5s ease-in-out infinite",
    "octo-sleep-collapse.svg": "breatheDeep 6.5s ease-in-out infinite",
    "octo-sleep-sleeping.svg": "breatheDeep 6s ease-in-out infinite",
    "octo-sleep-wake.svg": "bounce .95s cubic-bezier(.22,1.1,.36,1) 1 both",
    "octo-notif-notification.svg": "bounce 1.5s ease-in-out infinite",
    "octo-notif-error.svg": "shakeHard .72s ease-in-out infinite",
    "octo-notif-happy.svg": "float 2.1s ease-in-out infinite",
    "octo-notif-sweeping.svg": "scrub 1.5s ease-in-out infinite",
    "octo-notif-carrying.svg": "breathe 3.2s ease-in-out infinite",
    "octo-react-drag.svg": "sway 2.4s ease-in-out infinite",
    "octo-react-left.svg": "wobble 1.5s ease-in-out infinite",
    "octo-react-right.svg": "wobble 1.5s ease-in-out infinite",
    "octo-react-double.svg": "float 1.7s ease-in-out infinite",
    "octo-react-annoyed.svg": "shakeHard 0.48s ease-in-out infinite",
    "octo-mini-idle.svg": "sway 3.8s ease-in-out infinite",
    "octo-mini-alert.svg": "shake 0.62s ease-in-out infinite",
    "octo-mini-happy.svg": "float 2.2s ease-in-out infinite",
    "octo-mini-enter.svg": "bounce 1.05s cubic-bezier(.22,1.1,.36,1) 1 both",
    "octo-mini-peek.svg": "float 2.8s ease-in-out infinite",
    "octo-mini-crabwalk.svg": "wobble 1.15s ease-in-out infinite",
    "octo-mini-enter-sleep.svg": "breatheDeep 5.2s ease-in-out infinite",
    "octo-mini-sleep.svg": "breatheDeep 6.2s ease-in-out infinite",
    "octo-mini-typing.svg": "shake 0.72s ease-in-out infinite",
}

# 局部微调：一次性动画改成可循环、给游离元素补轴心、统一刺眼的红色
SMALL_FIXES = {
    "octo-idle-follow.svg": [
        ('<g style="animation:swayTentacle 4s ease-in-out infinite">',
         '<g style="transform-origin:64px 145px;animation:swayTentacle 4s ease-in-out infinite">'),
    ],
    "octo-react-left.svg": [
        ('animation:wave 0.5s ease-in-out"', 'animation:wave 1.05s ease-in-out infinite"'),
    ],
    "octo-react-right.svg": [
        ('animation:wave 0.5s ease-in-out"', 'animation:wave 1.05s ease-in-out infinite"'),
    ],
    "octo-react-double.svg": [
        ('animation:float 0.6s ease-in-out infinite"', 'animation:float 1.6s ease-in-out infinite"'),
        ('animation:float 0.6s ease-in-out infinite .3s"', 'animation:float 1.6s ease-in-out infinite .3s"'),
        ('animation:float 0.6s ease-in-out infinite .6s"', 'animation:float 1.6s ease-in-out infinite .6s"'),
    ],
    "octo-notif-notification.svg": [
        ('fill="#FF4444"', 'fill="#F2788C"'),
    ],
    "octo-notif-error.svg": [
        ('fill="#E88080"', 'fill="#E39AA6"'),
        ('fill="#F09090"', 'fill="#EDAAB4"'),
        ('fill="#FF9999"', 'fill="#F4A0B0"'),
        ('stroke="#FF6B6B"', 'stroke="#D9737F"'),
    ],
    "octo-react-annoyed.svg": [
        ('stroke="#FF6B6B"', 'stroke="#D9737F"'),
    ],
    "octo-mini-alert.svg": [
        ('fill="#FF6B6B"', 'fill="#F2788C"'),
    ],
}

# ------------------------------------------- 二次打磨：把「看得出在做什么」做扎实
# sweeping：扫帚原本完全静止，只有一颗灰尘在飘，读不出「在扫地」。
#   -> 扫帚以握把为轴心左右扫，身体同频小幅晃动，灰尘改成 3 颗错开相位地扬起来。
SWEEP_BROOM_OLD = (
    '<line x1="145" y1="68" x2="165" y2="138" stroke="#8B6914" stroke-width="3" stroke-linecap="round"/>'
    '<rect x="158" y="133" width="16" height="8" rx="2" fill="#D4A574"/>'
    '<circle cx="170" cy="143" r="2" fill="#D4C7E0" opacity="0.5" style="animation:float 1.2s ease-in-out infinite"/>'
)
SWEEP_BROOM_NEW = (
    '<g style="transform-origin:156px 102px;animation:sweep 1.5s ease-in-out infinite">'
    '<line x1="156" y1="100" x2="178" y2="168" stroke="#8B6914" stroke-width="3" stroke-linecap="round"/>'
    '<rect x="171" y="163" width="16" height="8" rx="2" fill="#D4A574"/></g>'
    '<circle cx="177" cy="173" r="2.1" fill="#D4C7E0" opacity="0" '
    'style="transform-origin:177px 173px;animation:dust 1.5s ease-out infinite"/>'
    '<circle cx="182" cy="169" r="1.6" fill="#E2D8EC" opacity="0" '
    'style="transform-origin:182px 169px;animation:dust 1.5s ease-out infinite;animation-delay:-.5s"/>'
    '<circle cx="173" cy="176" r="1.3" fill="#D4C7E0" opacity="0" '
    'style="transform-origin:173px 176px;animation:dust 1.5s ease-out infinite;animation-delay:-1s"/>'
)

# sweeping：光让扫帚摆还不够 —— 身体和扫帚必须「同向同步」，读起来才是章鱼在推扫帚。
#   身体常态朝扫帚方向（右）倾着，最右倾时扫帚头刚好扫到最右；触手也提速跟上扫地节奏。
SWEEP_FIXES = [
    ("animation:tentacle 3.4s", "animation:tentacle 1.5s"),
    ("animation-delay:-0.32s", "animation-delay:-0.3s"),
    ("animation-delay:-0.64s", "animation-delay:-0.6s"),
    ("animation-delay:-0.96s", "animation-delay:-0.9s"),
    ("animation-delay:-1.28s", "animation-delay:-1.2s"),
]

# annoyed：身体 0.55s 急促抖，触手却还挂在 3.4s 慢波上，节奏割裂。
#   眼睛是重灾区：半眯（squint）读成「困」，改成急促眨眼后在缩略图上又被看成「闭眼」。
#   -> 干脆拿掉眼皮，让眼睛始终完全睁开，用「瞪眼 + 眼珠乱转」表达烦躁。
_EYE_L = (
    '<ellipse cx="85" cy="96" rx="11" ry="13" fill="#2D2D2D"/>'
    '<ellipse cx="84" cy="92" rx="5" ry="5" fill="#FFFFFF"/>'
    '<ellipse cx="89" cy="99" rx="2" ry="2" fill="#FFFFFF" opacity="0.5"/>'
)
_EYE_R = (
    '<ellipse cx="115" cy="96" rx="11" ry="13" fill="#2D2D2D"/>'
    '<ellipse cx="114" cy="92" rx="5" ry="5" fill="#FFFFFF"/>'
    '<ellipse cx="119" cy="99" rx="2" ry="2" fill="#FFFFFF" opacity="0.5"/>'
)
# add_lids 生成的两片眼皮（在 second_pass 之前插入），这里直接删掉
_LID_L = (
    '<ellipse cx="85" cy="96" rx="13.00" ry="15.00" fill="#BA97C9" '
    'style="transform-origin:85px 81.00px;animation:blink 5.8s ease-in-out infinite"/>'
)
_LID_R = (
    '<ellipse cx="115" cy="96" rx="13.00" ry="15.00" fill="#BA97C9" '
    'style="transform-origin:115px 81.00px;animation:blink 5.8s ease-in-out infinite"/>'
)
ANNOYED_FIXES = [
    ("animation:tentacle 3.4s", "animation:tentacleTwitch 1.7s"),
    (_LID_L, ""),
    (_LID_R, ""),
    (
        _EYE_L,
        '<g style="transform-origin:85px 96px;animation:dart 1.05s ease-in-out infinite">'
        + _EYE_L + "</g>",
    ),
    (
        _EYE_R,
        '<g style="transform-origin:115px 96px;animation:dart 1.05s ease-in-out infinite">'
        + _EYE_R + "</g>",
    ),
    (
        '<path d="M130,60 L135,55 L140,60 L145,53" stroke="#D9737F" stroke-width="2" '
        'fill="none" stroke-linecap="round"/>',
        '<path d="M130,60 L135,55 L140,60 L145,53" stroke="#D9737F" stroke-width="2" '
        'fill="none" stroke-linecap="round" '
        'style="transform-origin:137.5px 57.5px;animation:anger .62s ease-in-out infinite"/>',
    ),
]

# 身体主组默认轴心（px，用户坐标系）；mini 用较小的基准
ORIGIN_BIG_FALLBACK = (100, 140)
ORIGIN_MINI = (100, 146)

TENT_RE = re.compile(
    r'(<ellipse\b[^>]*fill="#9B6BB0"[^>]*/>)\s*(<ellipse\b[^>]*fill="#B08ACC"[^>]*/>)'
)
EYE_RE = re.compile(
    r'<ellipse\b[^>]*cx="(-?[\d.]+)"[^>]*cy="(-?[\d.]+)"[^>]*rx="([\d.]+)"[^>]*ry="([\d.]+)"[^>]*fill="#2D2D2D"'
)
WHITE_RE = re.compile(
    r'<ellipse\b[^>]*cx="(-?[\d.]+)"[^>]*cy="(-?[\d.]+)"[^>]*rx="([\d.]+)"[^>]*ry="([\d.]+)"[^>]*fill="#FFFFFF"'
)
HEAD_RE = re.compile(r'<ellipse\b[^>]*rx="(?:50|25)"[^>]*ry="(?:47|23)"[^>]*fill="(#[0-9A-Fa-f]{6})"')
TAIL_RE = re.compile(
    r'(?:\s+|'
    r'<ellipse\b[^>]*fill="#FFFFFF"[^>]*/>|'
    r'<g\b[^>]*>\s*<ellipse\b[^>]*fill="#FFFFFF"[^>]*/>\s*</g>'
    r')'
)


def shade(hex_color, factor=0.93):
    """把颜色按比例压暗，用于生成眼皮色。"""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02X%02X%02X" % (
        max(0, min(255, round(r * factor))),
        max(0, min(255, round(g * factor))),
        max(0, min(255, round(b * factor))),
    )


def body_origin(text, is_mini):
    if is_mini:
        return ORIGIN_MINI
    m = re.search(r'<g transform="translate\(100,(\d+)\)">', text)
    if m:
        return (100, int(m.group(1)))
    return ORIGIN_BIG_FALLBACK


def tentacle_span(text, is_mini):
    """返回只包含触手的那段文本区间；big 主题里触手都在 translate(100,Y) 组内。"""
    if is_mini:
        return (0, len(text))
    m = re.search(r'<g transform="translate\(100,\d+\)">', text)
    if not m:
        return None
    start = m.end()
    depth = 1
    for tok in re.finditer(r'</?g\b[^>]*>', text[start:]):
        depth += -1 if tok.group(0).startswith("</") else 1
        if depth == 0:
            return (start, start + tok.start())
    return None


def wrap_tentacles(text, is_mini):
    span = tentacle_span(text, is_mini)
    if span is None:
        return text, 0
    i, j = span
    seg = text[i:j]
    kf = "tentacleMini" if is_mini else "tentacle"
    dur = "2.4s" if is_mini else "3.4s"
    n = [0]

    def repl(mo):
        idx = n[0]
        n[0] += 1
        shaft = mo.group(1)
        attrs = dict(re.findall(r'(\w[\w-]*)="([^"]*)"', shaft))
        cx = float(attrs.get("cx", 0))
        cy = float(attrs.get("cy", 0))
        ry = float(attrs.get("ry", 0))
        ox, oy = cx, cy - ry + 2
        delay = -0.32 * idx
        delay_css = "0s" if delay == 0 else "%.2fs" % delay
        style = (
            "transform-origin:%.2fpx %.2fpx;"
            "animation:%s %s ease-in-out infinite;animation-delay:%s"
            % (ox, oy, kf, dur, delay_css)
        )
        return '<g style="%s">%s%s</g>' % (style, mo.group(1), mo.group(2))

    return text[:i] + TENT_RE.sub(repl, seg) + text[j:], n[0]


def add_lids(text, is_mini):
    """给睁眼状态插入眨眼眼皮。"""
    head_m = HEAD_RE.search(text)
    head = head_m.group(1) if head_m else "#C8A2D8"
    lid_color = shade(head)

    whites = [
        (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)))
        for m in WHITE_RE.finditer(text)
    ]
    eyes = [
        (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)))
        for m in EYE_RE.finditer(text)
    ]
    eyes = [e for e in eyes if e[3] >= 4]
    if not eyes:
        return text, 0

    dur = "4.6s" if is_mini else "5.8s"
    lids = []
    for cx, cy, rx, ry in eyes:
        rx_u, ry_u = rx + 2, ry + 2
        for wx, wy, wrx, wry in whites:
            if abs(wx - cx) < 4 and abs(wy - cy) < 4 and wrx >= 9:
                rx_u, ry_u = max(rx_u, wrx + 1.7), max(ry_u, wry + 1.7)
        lids.append(
            '<ellipse cx="%g" cy="%g" rx="%.2f" ry="%.2f" fill="%s" '
            'style="transform-origin:%gpx %.2fpx;animation:blink %s ease-in-out infinite"/>'
            % (cx, cy, rx_u, ry_u, lid_color, cx, cy - ry_u, dur)
        )
    if not lids:
        return text, 0

    matches = list(EYE_RE.finditer(text))
    pos = matches[-1].end()
    # 正则停在 fill="#2D2D2D" 的引号处，必须先跨过这个标签的结尾
    gt = text.find(">", pos)
    if gt == -1:
        raise SystemExit("cannot find end of eye tag")
    pos = gt + 1
    while True:
        tm = TAIL_RE.match(text, pos)
        if not tm or tm.end() == pos:
            break
        pos = tm.end()
    return text[:pos] + "".join(lids) + text[pos:], len(lids)


def fix_idle_pupils(text):
    """把瞳孔与高光包进同一个组，让高光跟着瞳孔一起跟随光标。"""
    for side, cx in (("left", 85), ("right", 115)):
        old = (
            '<circle id="pupil-%s" cx="%d" cy="96" r="7.5" fill="#2D2D2D"/>'
            '<ellipse cx="%d" cy="92" rx="4" ry="3.5" fill="#FFFFFF" opacity="0.9"/>'
            '<ellipse cx="%d" cy="98" rx="2" ry="2" fill="#FFFFFF" opacity="0.4"/>'
            % (side, cx, cx - 2, cx + 3)
        )
        new = (
            '<g id="pupil-%s"><circle cx="%d" cy="96" r="7.5" fill="#2D2D2D"/>'
            '<ellipse cx="%d" cy="92" rx="4" ry="3.5" fill="#FFFFFF" opacity="0.9"/>'
            '<ellipse cx="%d" cy="98" rx="2" ry="2" fill="#FFFFFF" opacity="0.4"/></g>'
            % (side, cx, cx - 2, cx + 3)
        )
        if old not in text:
            raise SystemExit("idle pupil markup changed, aborting: %s" % side)
        text = text.replace(old, new)
    return text


def idle_lids(text):
    """idle 状态的两片眼皮（眼睛带眼白，需要按眼白尺寸取眼皮）。"""
    lids = []
    for cx, cy, rx, ry in ((85, 96, 13, 15), (115, 96, 13, 15)):
        rx_u, ry_u = rx + 1.7, ry + 1.7
        lids.append(
            '<ellipse cx="%g" cy="%g" rx="%.2f" ry="%.2f" fill="%s" '
            'style="transform-origin:%gpx %.2fpx;animation:blink 5.8s ease-in-out infinite"/>'
            % (cx, cy, rx_u, ry_u, shade("#C8A2D8"), cx, cy - ry_u)
        )
    anchor = '<path d="M96,116 Q100,119 104,116"'
    if anchor not in text:
        raise SystemExit("idle mouth anchor missing")
    return text.replace(anchor, "".join(lids) + anchor)


def second_pass(name, text):
    """逐状态手工打磨。必须跑在触手/眨眼之后，因为它要改这两者的 animation 值。"""
    if name == "octo-notif-sweeping.svg":
        if SWEEP_BROOM_OLD not in text:
            raise SystemExit("sweeping broom anchor missing")
        text = text.replace(SWEEP_BROOM_OLD, SWEEP_BROOM_NEW, 1)
        fixes = SWEEP_FIXES
    elif name == "octo-react-annoyed.svg":
        fixes = ANNOYED_FIXES
    else:
        return text
    for old, new in fixes:
        if old not in text:
            raise SystemExit("anchor missing in %s: %r" % (name, old))
        text = text.replace(old, new)
    # 只给这两个状态注入专属 keyframes，其余 28 个文件不受影响
    if "</style>" not in text:
        raise SystemExit("no <style> block in %s" % name)
    return text.replace("</style>", EXTRA_KEYFRAMES + "</style>", 1)


def process(path):
    name = path.name
    is_mini = name.startswith("octo-mini")
    text = path.read_text(encoding="utf-8")
    report = []

    # 1) 新样式表
    text, n = re.subn(r"<style>.*?</style>", STYLE, text, count=1, flags=re.DOTALL)
    assert n == 1, name

    # 2) 身体主组：轴心 + 新动画
    ox, oy = body_origin(text, is_mini)
    anim = BODY[name]
    new_body = '<g style="transform-origin:%dpx %dpx;animation:%s"' % (ox, oy, anim)
    text, n = re.subn(r'<g style="animation:[^"]*"', new_body, text, count=1)
    if n == 0:
        # 没有动画属性的裸 <g>（drag / collapse）
        text, n = re.subn(
            r'<g><g transform="translate\(100,\d+\)">',
            lambda mo: new_body + ">" + mo.group(0)[3:],
            text,
            count=1,
        )
    report.append("body=%s@(%d,%d)" % (anim.split()[0], ox, oy))

    # 2b) 局部微调
    for old, new in SMALL_FIXES.get(name, []):
        if old not in text:
            raise SystemExit("missing fix anchor in %s: %r" % (name, old))
        text = text.replace(old, new, 1)

    # 3) 触手波浪
    text, nt = wrap_tentacles(text, is_mini)
    report.append("tent=%d" % nt)

    # 4) 眨眼
    if not is_mini and name in ("octo-idle-follow.svg",):
        text = fix_idle_pupils(text)
        text = idle_lids(text)
        report.append("lid=2(pupil-grouped)")
    elif "sleep" not in name and "error" not in name:
        text, nl = add_lids(text, is_mini)
        report.append("lid=%d" % nl)

    # 5) 逐状态二次打磨
    text2 = second_pass(name, text)
    if text2 != text:
        report.append("pass2")

    path.write_text(text2, encoding="utf-8")
    return "  ".join(report)


def main():
    files = sorted(ASSETS.glob("*.svg"))
    print("optimizing %d svg files\n" % len(files))
    for p in files:
        print("%-38s %s" % (p.name, process(p)))

    # 收尾自校验：XML 合法 + 动画引用的 keyframe 都有定义
    import xml.etree.ElementTree as ET

    problems = 0
    for p in files:
        text = p.read_text(encoding="utf-8")
        try:
            ET.fromstring(text)
        except ET.ParseError as e:
            problems += 1
            print("XML FAIL %s: %s" % (p.name, e))
        used = set(re.findall(r"animation:\s*([A-Za-z][\w-]*)", text))
        defined = set(re.findall(r"@keyframes\s+([\w-]+)", text))
        if used - defined:
            problems += 1
            print("MISSING KEYFRAMES %s: %s" % (p.name, used - defined))
    print("\nvalidation problems = %d" % problems)
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
