from kimina_client import KiminaClient

def verify(code_string: str) -> (bool, str):
    """
    Xác thực code Lean 4 và trả về vị trí lỗi chi tiết.
    """
    try:
        # Sử dụng api_url như đã kiểm tra ở bước trước
        client = KiminaClient(api_url="http://localhost:8080")
        
        # Gửi code. Kimina sẽ biên dịch và trả về các thông báo (messages)
        results = client.check(code_string)
        
        is_valid = True
        error_details = []

        if not isinstance(results, list):
            results = [results]

        for res in results:
            messages = getattr(res, "messages", [])
            for m in messages:
                # Chỉ xử lý nếu mức độ là 'error'
                if getattr(m, "severity", "") == "error":
                    is_valid = False
                    
                    # Lấy nội dung lỗi
                    msg_text = getattr(m, "data", "Unknown error")
                    
                    # Trích xuất vị trí (Dòng và Cột)
                    pos = getattr(m, "pos", None)
                    if pos:
                        line = getattr(pos, "line", "?")
                        col = getattr(pos, "column", "?")
                        # Format: [Dòng:Cột] Nội dung lỗi
                        error_details.append(f"❌ Lỗi tại [Dòng {line}, Cột {col}]: {msg_text}")
                    else:
                        error_details.append(f"❌ Lỗi: {msg_text}")

        if is_valid:
            return (True, "✅ Code hợp lệ!")
        else:
            # Gộp các lỗi lại thành một chuỗi xuống dòng
            full_error_msg = "\n".join(error_details)
            return (False, full_error_msg)

    except Exception as e:
        return (False, f"⚠️ Lỗi hệ thống (Connection/SDK): {str(e)}")

# --- CHƯƠNG TRÌNH CHẠY THỬ ---
if __name__ == "__main__":
    # Ví dụ code sai: cộng một số với một chuỗi ký tự
    code_with_error = """def addition (n : Nat) : Nat := n + 1
def wrong_example := addition "Hello"
"""
    
    print("--- Đang thực thi kiểm tra Lean 4 ---")
    success, message = verify(code_with_error)
    
    print(f"Trạng thái: {'SUCCESS' if success else 'FAILURE'}")
    print(f"Thông báo:\n{message}")