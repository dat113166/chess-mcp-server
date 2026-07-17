"""
Server MCP cờ vua — cung cấp cho Claude các công cụ phân tích thế cờ.
Chạy: python chess_server.py
"""
import chess
import chess.engine
from mcp.server.fastmcp import FastMCP

# Tạo server, đặt tên để nhận diện trong Claude
mcp = FastMCP("co-vua")

# Đường dẫn tới Stockfish. SỬA lại cho đúng máy bạn:
#   Windows: r"C:\stockfish\stockfish.exe"
#   Linux/Mac đã cài qua apt/brew: "/usr/games/stockfish" hoặc "stockfish"
STOCKFISH_PATH = r"D:\mcp-server\chess-server\stockfish\stockfish-windows-x86-64-avx2.exe"


def _doc_diem(info) -> str:
    """Chuyển điểm số của engine thành lời giải thích dễ hiểu."""
    score = info["score"].white()
    if score.is_mate():
        n = score.mate()
        ai = "Trắng" if n > 0 else "Đen"
        return f"{ai} chiếu bí sau {abs(n)} nước"
    cp = score.score()  # centipawn: 100 = hơn 1 tốt
    loi = cp / 100
    if abs(loi) < 0.3:
        return f"Cân bằng ({loi:+.2f})"
    ai = "Trắng" if loi > 0 else "Đen"
    return f"{ai} lợi thế {abs(loi):.2f} tốt"


@mcp.tool()
def ve_ban_co(fen: str = chess.STARTING_FEN) -> str:
    """Vẽ bàn cờ ra dạng ký tự để xem trực quan.

    Args:
        fen: chuỗi FEN mô tả thế cờ. Bỏ trống = thế khai cuộc.
    """
    board = chess.Board(fen)
    luot = "Trắng đi" if board.turn == chess.WHITE else "Đen đi"
    return f"{board.unicode(empty_square='.')}\n\nLượt: {luot}"


@mcp.tool()
def nuoc_di_hop_le(fen: str) -> str:
    """Liệt kê tất cả nước đi hợp lệ trong một thế cờ.

    Args:
        fen: chuỗi FEN mô tả thế cờ hiện tại.
    """
    board = chess.Board(fen)
    if board.is_game_over():
        return f"Ván đã kết thúc: {board.result()}"
    moves = [board.san(m) for m in board.legal_moves]
    return f"Có {len(moves)} nước hợp lệ: " + ", ".join(moves)


@mcp.tool()
def kiem_tra_nuoc_di(fen: str, nuoc_di: str) -> str:
    """Kiểm tra một nước đi và cho biết chuyện gì xảy ra sau đó.

    Args:
        fen: thế cờ hiện tại (FEN).
        nuoc_di: nước đi dạng SAN, ví dụ "Nf3", "exd5", "Qh4".
    """
    board = chess.Board(fen)
    try:
        move = board.parse_san(nuoc_di)
    except ValueError:
        return f"'{nuoc_di}' không phải nước đi hợp lệ ở thế cờ này."

    ket_qua = []
    if board.is_capture(move):
        ket_qua.append("ăn quân")
    board.push(move)
    if board.is_checkmate():
        ket_qua.append("CHIẾU BÍ — thắng luôn")
    elif board.is_check():
        ket_qua.append("chiếu tướng")
    if board.is_stalemate():
        ket_qua.append("hết nước đi — hòa")

    mo_ta = ", ".join(ket_qua) if ket_qua else "nước đi bình thường"
    return f"Nước {nuoc_di} hợp lệ. Kết quả: {mo_ta}."


@mcp.tool()
def phan_tich_the_co(fen: str, do_sau: int = 15) -> str:
    """Dùng engine Stockfish phân tích thế cờ, trả về nước tốt nhất và đánh giá.

    Args:
        fen: thế cờ cần phân tích (FEN).
        do_sau: độ sâu tính toán (10-20). Càng cao càng chính xác nhưng chậm hơn.
    """
    board = chess.Board(fen)
    if board.is_game_over():
        return f"Ván đã kết thúc: {board.result()}"

    with chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH) as engine:
        info = engine.analyse(board, chess.engine.Limit(depth=do_sau))
        nuoc_tot = board.san(info["pv"][0])
        danh_gia = _doc_diem(info)
    return f"Nước tốt nhất: {nuoc_tot}. Đánh giá: {danh_gia}."


if __name__ == "__main__":
    mcp.run()