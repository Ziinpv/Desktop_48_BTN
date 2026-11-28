# -*- coding: utf-8 -*-
"""Vẽ Hình 2.1 — sơ đồ ca sử dụng LUXE Wedding Studio."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "hinh-2-1-use-case.png"

NAVY = "#1F4E79"
INK = "#1A1A1A"
MUTED = "#4A5568"
LINE = "#5C6B7A"
WHITE = "#FFFFFF"
BUS = {
    "QT": "#1F4E79",
    "NV": "#795290",
    "TN": "#B8860B",
    "K": "#0F766E",
}

W, H = 1680, 2800


def font(size, bold=False):
    name = "timesbd.ttf" if bold else "times.ttf"
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)


def text_size(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def center_text(draw, cx, cy, text, fnt, fill):
    tw, th = text_size(draw, text, fnt)
    draw.text((cx - tw / 2, cy - th / 2), text, font=fnt, fill=fill)


def draw_actor(draw, cx, head_y, label, fnt):
    r = 22
    draw.ellipse((cx - r, head_y, cx + r, head_y + 2 * r), outline=NAVY, width=3)
    neck = head_y + 2 * r
    hip = neck + 52
    draw.line((cx, neck, cx, hip), fill=NAVY, width=3)
    draw.line((cx - 32, neck + 18, cx + 32, neck + 18), fill=NAVY, width=3)
    draw.line((cx, hip, cx - 26, hip + 40), fill=NAVY, width=3)
    draw.line((cx, hip, cx + 26, hip + 40), fill=NAVY, width=3)
    lines = label.split("\n")
    y = hip + 52
    for line in lines:
        tw, th = text_size(draw, line, fnt)
        draw.text((cx - tw / 2, y), line, font=fnt, fill=NAVY)
        y += th + 2
    return neck + 18


def hollow_triangle(draw, tip, base_mid, size=14):
    """Tam giác rỗng tại đầu mũi tên tổng quát hóa, tip hướng về tác nhân tổng quát."""
    dx = tip[0] - base_mid[0]
    dy = tip[1] - base_mid[1]
    length = max((dx * dx + dy * dy) ** 0.5, 1)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    p1 = tip
    p2 = (tip[0] - ux * size + px * size * 0.55, tip[1] - uy * size + py * size * 0.55)
    p3 = (tip[0] - ux * size - px * size * 0.55, tip[1] - uy * size - py * size * 0.55)
    draw.polygon([p1, p2, p3], fill=WHITE, outline=NAVY)
    draw.line([p1, p2, p3, p1], fill=NAVY, width=2)


PACKAGES = [
    (
        "Nền tảng",
        "#E8F0F8",
        [
            ("UC-01", "Đăng nhập, giữ phiên, đổi mật khẩu", "QT  NV  TN  K"),
            ("UC-02", "Quản lý tài khoản", "QT"),
            ("UC-13", "Sao lưu và phục hồi", "QT  NV"),
            ("UC-14", "Xem nhật ký thao tác", "QT  NV"),
        ],
    ),
    (
        "Danh mục",
        "#F4EEF6",
        [
            ("UC-03", "Quản lý loại dịch vụ", "QT  NV"),
            ("UC-04", "Quản lý dịch vụ và danh mục", "QT  NV"),
            ("UC-06", "Quản lý khách hàng", "QT  NV  TN"),
            ("UC-15", "Quản lý kho áo cưới", "QT  NV  K"),
        ],
    ),
    (
        "Thuê và trả",
        "#FBF6EA",
        [
            ("UC-05", "Lập và sửa phiếu thuê áo", "QT  NV"),
            ("UC-12", "Đặt lịch hẹn chụp", "QT  NV"),
            ("UC-08", "Quá hạn, thu phí, nhận trả", "QT  NV  TN  K"),
            ("UC-16", "Ghi thanh toán và in biên lai", "QT  NV  TN"),
        ],
    ),
    (
        "Tra cứu và báo cáo",
        "#E7F4F1",
        [
            ("UC-07", "Theo dõi hợp đồng chưa trả", "QT  NV  K"),
            ("UC-09", "Tra cứu áo và in mã QR", "QT  NV  K"),
            ("UC-10", "Tra cứu khách và xuất hóa đơn", "QT  NV  TN"),
            ("UC-11", "Xem bảng điều khiển và biểu đồ", "QT  NV  TN  K"),
        ],
    ),
]

ACTORS = {
    "QT": {"UC-01", "UC-02", "UC-03", "UC-04", "UC-05", "UC-06", "UC-07", "UC-08", "UC-09", "UC-10", "UC-11", "UC-12", "UC-13", "UC-14", "UC-15", "UC-16"},
    "NV": {"UC-01", "UC-03", "UC-04", "UC-05", "UC-06", "UC-07", "UC-08", "UC-09", "UC-10", "UC-11", "UC-12", "UC-13", "UC-14", "UC-15", "UC-16"},
    "TN": {"UC-01", "UC-06", "UC-08", "UC-10", "UC-11", "UC-16"},
    "K": {"UC-01", "UC-07", "UC-08", "UC-09", "UC-11", "UC-15"},
}


def main():
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    f_title = font(28, True)
    f_pkg = font(22, True)
    f_code = font(22, True)
    f_name = font(26, True)
    f_actor = font(20)
    f_small = font(18)
    f_legend = font(20)

    actor_x = 108
    qt_y, nv_y, tn_y, k_y = 150, 620, 1180, 1680
    labels = [
        ("QT", "Quản trị\nviên", qt_y),
        ("NV", "Nhân viên\nstudio", nv_y),
        ("TN", "Thu ngân", tn_y),
        ("K", "Nhân viên\nkho", k_y),
    ]
    hands = {}
    for key, label, ay in labels:
        hands[key] = (actor_x + 32, draw_actor(draw, actor_x, ay, label, f_small))

    # Khoảng giữa hai nhân vật: bắt đầu dưới nhãn Quản trị, kết thúc trước đầu Nhân viên
    gen_top = qt_y + 44 + 52 + 40 + 52 + 50
    gen_bot = nv_y - 20
    note = "kế thừa quyền"
    tw, th = text_size(draw, note, f_legend)
    mid = (gen_top + gen_bot) / 2
    draw.line((actor_x, gen_top, actor_x, mid - th / 2 - 6), fill=NAVY, width=2)
    draw.line((actor_x, mid + th / 2 + 6, actor_x, gen_bot), fill=NAVY, width=2)
    hollow_triangle(draw, (actor_x, gen_bot), (actor_x, mid))
    draw.text((actor_x - tw / 2, mid - th / 2), note, font=f_legend, fill=NAVY)

    oval_left = 520
    oval_right = 1620
    pitch = 116
    oval_h = 104
    y = 100
    bus_y = {k: [] for k in ACTORS}
    pkg_boxes = []

    for title, fill, cases in PACKAGES:
        block_h = 42 + len(cases) * pitch + 8
        box = (480, y, 1640, y + block_h)
        pkg_boxes.append((box, fill))
        draw.rounded_rectangle(box, radius=10, fill=fill, outline="#C5D0DC", width=2)
        draw.text((oval_left, y + 8), title, font=f_pkg, fill=NAVY)
        oy = y + 40
        for code, name, who in cases:
            draw.ellipse((oval_left, oy, oval_right, oy + oval_h), fill=WHITE, outline=NAVY, width=3)
            cx = (oval_left + oval_right) / 2
            center_text(draw, cx, oy + 28, code, f_code, NAVY)
            center_text(draw, cx, oy + 56, name, f_name, INK)
            center_text(draw, cx, oy + 84, who, f_actor, MUTED)
            mid = oy + oval_h / 2
            for key, codes in ACTORS.items():
                if code in codes:
                    bus_y[key].append(mid)
            oy += pitch
        y = box[3] + 14

    boundary = (450, 28, 1660, y + 8)
    draw.rounded_rectangle(boundary, radius=12, outline=NAVY, width=4)
    title = "LUXE Wedding Studio"
    tw, th = text_size(draw, title, f_title)
    tx = (boundary[0] + boundary[2]) / 2 - tw / 2
    draw.rectangle((tx - 12, 36, tx + tw + 12, 36 + th + 6), fill=WHITE)
    draw.text((tx, 38), title, font=f_title, fill=NAVY)

    bus_x = {"QT": 300, "NV": 332, "TN": 364, "K": 396}
    for key, ys in bus_y.items():
        color = BUS[key]
        x = bus_x[key]
        hand_y = hands[key][1]
        top = min(min(ys), hand_y)
        bot = max(max(ys), hand_y)
        draw.line((hands[key][0], hand_y, x, hand_y), fill=color, width=3)
        draw.line((x, top, x, bot), fill=color, width=3)
        for mid in ys:
            draw.line((x, mid, oval_left - 2, mid), fill=color, width=2)

    legend_y = boundary[3] + 28
    draw.text((48, legend_y), "Đường màu là liên kết tác nhân — ca sử dụng. Chữ dưới mỗi ellipse là vai trò được vào ca đó.", font=f_legend, fill=INK)
    lx = 48
    ly = legend_y + 34
    for key, label in (("QT", "Quản trị"), ("NV", "Nhân viên"), ("TN", "Thu ngân"), ("K", "Kho")):
        draw.line((lx, ly + 10, lx + 42, ly + 10), fill=BUS[key], width=5)
        draw.text((lx + 50, ly), label, font=f_legend, fill=INK)
        lx += 280
    draw.text((48, ly + 36), "Mũi tên tam giác rỗng: Quản trị kế thừa mọi ca của Nhân viên, và thêm UC-02.", font=f_legend, fill=INK)

    img = img.crop((0, 0, W, ly + 80))
    img.save(OUT, "PNG")
    print(OUT, img.size)


if __name__ == "__main__":
    main()
