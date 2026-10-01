"""Generate the Project 02 Midterm presentation as a landscape PDF."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyBboxPatch
from matplotlib.table import Table

PROJECT_DIR = Path(__file__).resolve().parents[1]
EXPERIMENTS_DIR = PROJECT_DIR / "experiments"
OUTPUT = PROJECT_DIR / "presentation.pdf"

NAVY = "#12355B"
BLUE = "#1F77B4"
AMBER = "#D97706"
LIGHT = "#F3F7FB"
TEXT = "#1F2937"
GREEN = "#16803C"
RED = "#B42318"


def load_summary(name: str) -> dict[str, str]:
    with (EXPERIMENTS_DIR / name).open(encoding="utf-8", newline="") as handle:
        return next(csv.DictReader(handle))


def setup_slide(title: str, subtitle: str | None = None):
    fig = plt.figure(figsize=(13.333, 7.5), facecolor="white")
    fig.text(0.055, 0.91, title, fontsize=25, fontweight="bold", color=NAVY)
    fig.add_artist(
        plt.Line2D([0.055, 0.945], [0.885, 0.885], color=AMBER, linewidth=2)
    )
    if subtitle:
        fig.text(0.055, 0.855, subtitle, fontsize=12, color="#52606D")
    return fig


def add_footer(fig, page: int):
    fig.text(
        0.055,
        0.035,
        "Project 02 — AI Board Game Arena | Midterm",
        fontsize=8.5,
        color="#6B7280",
    )
    fig.text(0.945, 0.035, str(page), ha="right", fontsize=8.5, color="#6B7280")


def add_bullets(fig, items, x=0.09, y=0.78, line=0.075, size=17, color=TEXT):
    for index, item in enumerate(items):
        fig.text(x, y - index * line, f"• {item}", fontsize=size, color=color)


def add_table(fig, rows, columns, bbox, fontsize=11, header_color=NAVY):
    axis = fig.add_axes(bbox)
    axis.axis("off")
    table = Table(axis, bbox=[0, 0, 1, 1])
    widths = [1 / columns] * columns
    height = 1 / len(rows)
    for row_index, row in enumerate(rows):
        for column_index, value in enumerate(row):
            face = header_color if row_index == 0 else (
                "#EAF2F8" if row_index % 2 == 0 else "white"
            )
            cell = table.add_cell(
                row_index,
                column_index,
                widths[column_index],
                height,
                text=str(value),
                loc="center",
                facecolor=face,
                edgecolor="white",
            )
            cell.get_text().set_fontsize(fontsize)
            cell.get_text().set_color("white" if row_index == 0 else TEXT)
            if row_index == 0:
                cell.get_text().set_weight("bold")
    axis.add_table(table)


def create_pdf() -> None:
    e1 = load_summary("e1_random_minimax_d2_summary.csv")
    e2 = load_summary("e2_minimax_alphabeta_d3_summary.csv")
    d2 = load_summary("e3_alphabeta_d2_summary.csv")
    d4 = load_summary("e3_alphabeta_d4_summary.csv")
    d6 = load_summary("e3_alphabeta_d6_summary.csv")

    with PdfPages(OUTPUT) as pdf:
        page = 1

        fig = plt.figure(figsize=(13.333, 7.5), facecolor=NAVY)
        fig.text(
            0.08, 0.66, "AI BOARD GAME ARENA", fontsize=34,
            fontweight="bold", color="white"
        )
        fig.text(
            0.08, 0.55, "Connect Four — Minimax và Alpha-Beta Pruning",
            fontsize=25, color="#FDE68A"
        )
        fig.text(
            0.08, 0.40,
            "Midterm Milestone | Nhóm 3 thành viên",
            fontsize=18, color="white"
        )
        fig.text(
            0.08, 0.29,
            "Project 02 — Artificial Intelligence",
            fontsize=15, color="#CBD5E1"
        )
        fig.text(0.92, 0.08, str(page), ha="right", fontsize=10, color="#CBD5E1")
        pdf.savefig(fig, facecolor=fig.get_facecolor())
        plt.close(fig)
        page += 1

        fig = setup_slide("1. Bài toán và mục tiêu")
        add_bullets(fig, [
            "Connect Four là game hai người, zero-sum, perfect information.",
            "Bàn cờ 6 × 7; quân rơi xuống ô trống thấp nhất.",
            "Người chơi thắng khi tạo bốn quân liên tiếp: ngang, dọc hoặc chéo.",
            "Mục tiêu: xây dựng AI chọn nước đi tốt bằng tìm kiếm đối kháng.",
            "So sánh plain Minimax với Alpha-Beta pruning về chất lượng và chi phí.",
        ], y=0.78, line=0.095, size=18)
        fig.text(0.10, 0.18, "Ràng buộc: triển khai từ đầu, chạy offline, không dùng hosted LLM API.",
                 fontsize=14, color=RED, fontweight="bold")
        add_footer(fig, page); pdf.savefig(fig); plt.close(fig); page += 1

        fig = setup_slide("2. Biểu diễn trạng thái và giao diện engine")
        add_table(fig, [
            ["Thành phần", "Đặc tả"],
            ["Board", "Tuple 6 × 7, row 0 ở trên, row 5 ở dưới"],
            ["Ô trống / quân", '".", "X", "O"'],
            ["Nước đi", "Chỉ là column 0–6; engine tự tính landing row"],
            ["legal_moves", "Trả các cột chưa đầy"],
            ["apply_move", "Tạo board mới, không mutate board cũ"],
            ["terminal", "Có winner hoặc board đầy"],
        ], 2, [0.07, 0.07, 0.86, 0.28], fontsize=12)
        fig.text(0.10, 0.18, "AI core giữ trong starter/student_core.py; engine chỉ xử lý luật game.",
                 fontsize=15, color=GREEN, fontweight="bold")
        add_footer(fig, page); pdf.savefig(fig); plt.close(fig); page += 1

        fig = setup_slide("3. Hàm đánh giá heuristic")
        add_bullets(fig, [
            "Điểm terminal: thắng +1,000,000; thua −1,000,000; hòa 0.",
            "Kiểm soát cột giữa: ưu tiên vị trí có nhiều đường thắng hơn.",
            "Duyệt mọi cửa sổ 4 ô theo ngang, dọc và hai hướng chéo.",
            "Ba quân + một ô trống: +100; hai quân + hai ô trống: +10.",
            "Mối đe dọa tương ứng của đối thủ nhận điểm âm.",
        ], y=0.78, line=0.09, size=17)
        fig.text(0.12, 0.17, "evaluate(board, player) → float", fontsize=21,
                 color=BLUE, fontweight="bold")
        add_footer(fig, page); pdf.savefig(fig); plt.close(fig); page += 1

        fig = setup_slide("4. Minimax")
        add_bullets(fig, [
            "Max node: tối đa hóa điểm của maximizing_player.",
            "Min node: giả định đối thủ chọn phản hồi bất lợi nhất.",
            "Mỗi cạnh của cây là một cột hợp lệ được apply_move.",
            "Dừng tại terminal state hoặc depth = 0 rồi gọi evaluate.",
            "Độ phức tạp xấp xỉ O(b^d), với branching factor tối đa khoảng 7.",
        ], y=0.78, line=0.09, size=17)
        box = FancyBboxPatch((0.18, 0.14), 0.64, 0.14, boxstyle="round,pad=0.02",
                             facecolor=LIGHT, edgecolor=BLUE, linewidth=2,
                             transform=fig.transFigure)
        fig.add_artist(box)
        fig.text(0.50, 0.205, "MINIMAX → (best_column, value)", ha="center",
                 fontsize=20, color=NAVY, fontweight="bold")
        add_footer(fig, page); pdf.savefig(fig); plt.close(fig); page += 1

        fig = setup_slide("5. Alpha-Beta pruning")
        add_bullets(fig, [
            "Giữ nguyên kết quả tối ưu của Minimax ở cùng depth.",
            "Alpha: giá trị tốt nhất Max đã chắc chắn đạt được.",
            "Beta: giá trị tốt nhất Min đã chắc chắn đạt được.",
            "Khi alpha ≥ beta, phần còn lại của nhánh không cần duyệt.",
            "Đếm node để định lượng hiệu quả pruning.",
        ], y=0.78, line=0.09, size=17)
        fig.text(0.14, 0.18, "alpha = −∞     |     beta = +∞     |     cắt khi alpha ≥ beta",
                 fontsize=19, color=AMBER, fontweight="bold")
        add_footer(fig, page); pdf.savefig(fig); plt.close(fig); page += 1

        fig = setup_slide("6. Thiết kế thí nghiệm")
        add_table(fig, [
            ["Experiment", "Matchup", "Games", "Mục đích"],
            ["E1", "Random vs Minimax d=2", "50", "So với baseline"],
            ["E2", "Minimax d=3 vs Alpha-Beta d=3", "50", "Đo pruning"],
            ["E3-D2", "Alpha-Beta d=2 self-play", "50", "Chi phí depth 2"],
            ["E3-D4", "Alpha-Beta d=4 self-play", "50", "Chi phí depth 4"],
            ["E3-D6", "Alpha-Beta d=6 self-play", "50", "Chi phí depth 6"],
        ], 4, [0.07, 0.07, 0.86, 0.30], fontsize=12)
        fig.text(0.10, 0.15, "Seed = 42 | đổi X/O xen kẽ | tổng cộng 250 ván | lưu CSV raw + summary",
                 fontsize=15, color=GREEN, fontweight="bold")
        add_footer(fig, page); pdf.savefig(fig); plt.close(fig); page += 1

        fig = setup_slide("7. Kết quả: chất lượng chơi")
        add_table(fig, [
            ["Matchup", "Win", "Draw", "Loss", "Avg turns"],
            ["Random vs Minimax d=2", "0", "0", "50", "11.26"],
            ["Minimax d=3 vs Alpha-Beta d=3", "25", "0", "25", "39.00"],
            ["Alpha-Beta d=2 self-play", "25", "0", "25", "34.00"],
            ["Alpha-Beta d=4 self-play", "25", "0", "25", "37.00"],
            ["Alpha-Beta d=6 self-play", "25", "0", "25", "35.00"],
        ], 5, [0.07, 0.07, 0.86, 0.30], fontsize=12)
        fig.text(0.10, 0.15, "E1: Minimax thắng Random trong cả 50 ván. E2/E3 được cân bằng X/O.",
                 fontsize=15, color=GREEN, fontweight="bold")
        add_footer(fig, page); pdf.savefig(fig); plt.close(fig); page += 1

        fig = setup_slide("8. Kết quả: Alpha-Beta hiệu quả hơn")
        add_table(fig, [
            ["Chỉ số — depth 3", "Minimax", "Alpha-Beta", "Kết luận"],
            ["Nodes / move", "247.28", "101.72", "−58.87% node"],
            ["Time / move", "36.107 ms", "13.454 ms", "−62.74% thời gian"],
            ["Node ratio", "2.431×", "—", "Minimax / Alpha-Beta"],
            ["Win/Draw/Loss", "25/0/25", "25/0/25", "Cùng chất lượng"],
        ], 4, [0.07, 0.07, 0.86, 0.28], fontsize=12)
        fig.text(0.11, 0.14, "Kết luận: pruning giảm chi phí mà không làm thay đổi kết quả tìm kiếm.",
                 fontsize=16, color=GREEN, fontweight="bold")
        add_footer(fig, page); pdf.savefig(fig); plt.close(fig); page += 1

        fig = setup_slide("9. Ảnh hưởng của search depth")
        node_image = plt.imread(EXPERIMENTS_DIR / "t09_alphabeta_nodes_by_depth.png")
        time_image = plt.imread(EXPERIMENTS_DIR / "t09_alphabeta_time_by_depth.png")
        ax1 = fig.add_axes([0.07, 0.15, 0.41, 0.62]); ax1.imshow(node_image); ax1.axis("off")
        ax2 = fig.add_axes([0.53, 0.15, 0.41, 0.62]); ax2.imshow(time_image); ax2.axis("off")
        fig.text(0.10, 0.11, "Depth 2: 28.53 nodes/move | 3.982 ms", fontsize=13, color=TEXT)
        fig.text(0.55, 0.11, "Depth 6: 7,063.14 nodes/move | 640.57 ms", fontsize=13, color=TEXT)
        add_footer(fig, page); pdf.savefig(fig); plt.close(fig); page += 1

        fig = setup_slide("10. Kết luận và phân công")
        add_bullets(fig, [
            "Đã triển khai evaluate, Minimax và Alpha-Beta từ first principles.",
            "Alpha-Beta giảm 58.87% node và 62.74% thời gian ở depth 3.",
            "Tăng depth cải thiện khả năng nhìn trước nhưng chi phí tăng mạnh.",
            "Bộ test AI core: 14/14 passed; thí nghiệm: 250 ván hợp lệ.",
            "Bước tiếp theo: hoàn thiện report, rehearsal và demo benchmark states.",
        ], y=0.78, line=0.075, size=15)
        add_table(fig, [
            ["Thành viên", "Phụ trách"],
            ["Member 1", "AI core: evaluate, Minimax, Alpha-Beta"],
            ["Member 2", "Testing, measurement, tournament"],
            ["Member 3", "Analysis, charts, presentation"],
        ], 2, [0.09, 0.16, 0.82, 0.23], fontsize=12)
        add_footer(fig, page); pdf.savefig(fig); plt.close(fig)


if __name__ == "__main__":
    create_pdf()
    print(OUTPUT)
