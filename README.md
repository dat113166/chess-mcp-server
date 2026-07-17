# Chess MCP Server

MCP server cung cấp cho Claude các công cụ phân tích cờ vua, dùng thư viện
`python-chess` và engine Stockfish. Viết như một bài thực hành để hiểu cách
Model Context Protocol hoạt động.

## Tính năng

Bốn tool, chia hai nhóm:

**Không cần engine:**
- `ve_ban_co(fen)` — vẽ bàn cờ ra dạng ký tự
- `nuoc_di_hop_le(fen)` — liệt kê mọi nước đi hợp lệ
- `kiem_tra_nuoc_di(fen, nuoc_di)` — kiểm tra một nước có hợp lệ không, có ăn quân / chiếu / chiếu bí không

**Cần Stockfish:**
- `phan_tich_the_co(fen, do_sau)` — trả về nước tốt nhất và đánh giá thế cờ

## Cài đặt

```bash
pip install "mcp[cli]" python-chess
```

Tải Stockfish ở [stockfishchess.org/download](https://stockfishchess.org/download/),
giải nén vào thư mục `stockfish/`, rồi sửa dòng `STOCKFISH_PATH` trong file
server cho đúng đường dẫn `.exe`.

## Chạy thử

```bash
mcp dev chess-server.py
```

Mở link Inspector hiện ra để test từng tool.

## Cắm vào Claude Desktop

Sửa file config (Settings → Developer → Edit Config):

```json
{
  "mcpServers": {
    "co-vua": {
      "command": "python",
      "args": ["D:/mcp-server/chess-server/chess-server.py"]
    }
  }
}
```