"""Test các tool cờ vua trong chess-server.py (không cần Stockfish).

Tên file có dấu gạch ngang nên không dùng `import` thường được,
phải nạp bằng importlib.
"""
import importlib.util
from pathlib import Path

import chess
import pytest

SERVER_PATH = Path(__file__).resolve().parent.parent / "chess-server.py"


def _load_server():
    spec = importlib.util.spec_from_file_location("chess_server", SERVER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


server = _load_server()

# --- Các thế cờ dùng chung ---
START = chess.STARTING_FEN
INVALID_FENS = ["", "không phải fen", "8/8/8/8/8/8/8 w - - 0 1"]
# Sau 1.e4 f6: Trắng đi Qh5 sẽ chiếu
FEN_QH5 = "rnbqkbnr/ppppp1pp/5p2/8/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2"
# Sau 1.f3 e5 2.g4: Đen đi Qh4 là chiếu bí (fool's mate)
FEN_BEFORE_MATE = "rnbqkbnr/pppp1ppp/8/4p3/6P1/5P2/PPPPP2P/RNBQKBNR b KQkq g3 0 2"
# Đã bị chiếu bí: Trắng thua
FEN_CHECKMATED = "rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3"
# Tốt Trắng a7 sắp phong cấp
FEN_PROMOTE = "8/P7/8/8/8/8/k6K/8 w - - 0 1"
# Cả hai bên còn quyền nhập thành
FEN_CASTLE = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"
# Xe đen ở f8 khống chế f1: nhập thành cánh vua bị cấm, cánh hậu vẫn được
FEN_CASTLE_BLOCKED = "5rk1/8/8/8/8/8/8/R3K2R w KQ - 0 1"
# Qf7 sẽ làm Đen hết nước đi mà không bị chiếu (hòa)
FEN_STALEMATE = "7k/8/5Q2/8/8/8/8/K7 w - - 0 1"


# ---------- ve_ban_co ----------
def test_ve_ban_co_mac_dinh_la_the_khai_cuoc():
    out = server.ve_ban_co()
    assert "Lượt: Trắng đi" in out
    assert "♔" in out and "♚" in out


def test_ve_ban_co_luot_den():
    assert "Lượt: Đen đi" in server.ve_ban_co(FEN_BEFORE_MATE)


@pytest.mark.parametrize("fen", INVALID_FENS)
def test_ve_ban_co_fen_sai(fen):
    with pytest.raises(ValueError):
        server.ve_ban_co(fen)


# ---------- nuoc_di_hop_le ----------
def test_nuoc_di_hop_le_khai_cuoc_co_20_nuoc():
    out = server.nuoc_di_hop_le(START)
    assert out.startswith("Có 20 nước hợp lệ")
    assert "e4" in out and "Nf3" in out


def test_nuoc_di_hop_le_van_da_ket_thuc():
    assert server.nuoc_di_hop_le(FEN_CHECKMATED) == "Ván đã kết thúc: 0-1"


@pytest.mark.parametrize("fen", INVALID_FENS)
def test_nuoc_di_hop_le_fen_sai(fen):
    with pytest.raises(ValueError):
        server.nuoc_di_hop_le(fen)


def test_nuoc_di_hop_le_phong_cap():
    out = server.nuoc_di_hop_le(FEN_PROMOTE)
    for quan in ("a8=Q", "a8=R", "a8=B", "a8=N"):
        assert quan in out


def test_nuoc_di_hop_le_nhap_thanh():
    out = server.nuoc_di_hop_le(FEN_CASTLE)
    assert "O-O" in out and "O-O-O" in out


def test_nuoc_di_hop_le_khong_nhap_thanh_qua_o_bi_chieu():
    moves = server.nuoc_di_hop_le(FEN_CASTLE_BLOCKED).split(": ", 1)[1].split(", ")
    assert "O-O" not in moves
    assert "O-O-O" in moves


# ---------- kiem_tra_nuoc_di ----------
def test_kiem_tra_nuoc_di_binh_thuong():
    out = server.kiem_tra_nuoc_di(START, "e4")
    assert out == "Nước e4 hợp lệ. Kết quả: nước đi bình thường."


def test_kiem_tra_nuoc_di_khong_hop_le():
    out = server.kiem_tra_nuoc_di(START, "e5")
    assert "không phải nước đi hợp lệ" in out


def test_kiem_tra_nuoc_di_rac():
    assert "không phải nước đi hợp lệ" in server.kiem_tra_nuoc_di(START, "abc")


@pytest.mark.parametrize("fen", INVALID_FENS)
def test_kiem_tra_nuoc_di_fen_sai(fen):
    with pytest.raises(ValueError):
        server.kiem_tra_nuoc_di(fen, "e4")


def test_kiem_tra_nuoc_di_an_quan():
    # 1.e4 d5 -> exd5 ăn tốt
    fen = "rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq d6 0 2"
    assert "ăn quân" in server.kiem_tra_nuoc_di(fen, "exd5")


def test_kiem_tra_nuoc_di_chieu():
    out = server.kiem_tra_nuoc_di(FEN_QH5, "Qh5+")
    assert "chiếu tướng" in out
    assert "CHIẾU BÍ" not in out


def test_kiem_tra_nuoc_di_chieu_bi():
    out = server.kiem_tra_nuoc_di(FEN_BEFORE_MATE, "Qh4#")
    assert "CHIẾU BÍ" in out


def test_kiem_tra_nuoc_di_phong_cap():
    out = server.kiem_tra_nuoc_di(FEN_PROMOTE, "a8=Q")
    assert "hợp lệ" in out
    assert "chiếu tướng" in out  # hậu mới ở a8 chiếu vua đen ở a2


def test_kiem_tra_nuoc_di_phong_cap_thieu_quan_la_khong_hop_le():
    # Tốt đi tới hàng cuối bắt buộc phải chọn quân phong
    assert "không phải nước đi hợp lệ" in server.kiem_tra_nuoc_di(FEN_PROMOTE, "a8")


def test_kiem_tra_nuoc_di_nhap_thanh():
    assert "Nước O-O hợp lệ" in server.kiem_tra_nuoc_di(FEN_CASTLE, "O-O")
    assert "Nước O-O-O hợp lệ" in server.kiem_tra_nuoc_di(FEN_CASTLE, "O-O-O")


def test_kiem_tra_nuoc_di_nhap_thanh_bi_cam():
    out = server.kiem_tra_nuoc_di(FEN_CASTLE_BLOCKED, "O-O")
    assert "không phải nước đi hợp lệ" in out


def test_kiem_tra_nuoc_di_hoa_het_nuoc():
    out = server.kiem_tra_nuoc_di(FEN_STALEMATE, "Qf7")
    assert "hết nước đi — hòa" in out


# ---------- phan_tich_the_co (chỉ nhánh không có Stockfish) ----------
def test_phan_tich_the_co_thieu_stockfish(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "STOCKFISH_PATH", str(tmp_path / "khong-co-stockfish"))
    with pytest.raises(FileNotFoundError):
        server.phan_tich_the_co(START)


def test_phan_tich_the_co_van_ket_thuc_khong_can_stockfish(monkeypatch, tmp_path):
    monkeypatch.setattr(server, "STOCKFISH_PATH", str(tmp_path / "khong-co-stockfish"))
    assert server.phan_tich_the_co(FEN_CHECKMATED) == "Ván đã kết thúc: 0-1"
