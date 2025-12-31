from kimina_client import KiminaClient

def verify(proof_string: str) -> (bool, str):
    """
    Xác nhận chứng minh (Formal Proof) Lean 4 là ĐÚNG hay SAI.
    - Trả về (True, "") nếu chứng minh hoàn toàn hợp lệ.
    - Trả về (False, "lỗi...") nếu có lỗi logic hoặc cú pháp.
    """
    try:
        client = KiminaClient(api_url="http://localhost:8080")
        
        # Gửi chứng minh đến server
        raw_results = client.check(proof_string)
        
        # Bóc tách dữ liệu theo cấu trúc SDK thực tế
        results = raw_results if isinstance(raw_results, list) else [raw_results]
        
        for item in results:
            # Truy cập vào phần response (chứa kết quả từ Lean REPL)
            response = getattr(item, "response", item)
            
            # Lấy danh sách messages (nơi chứa thông báo lỗi logic)
            messages = getattr(response, "messages", [])
            
            for m in messages:
                # Chuyển đổi message object sang dict để kiểm tra
                m_data = m if isinstance(m, dict) else getattr(m, "__dict__", {})
                
                # Nếu có bất kỳ message nào mức độ 'error', chứng minh đó SAI
                if m_data.get("severity") == "error":
                    error_msg = m_data.get("data", "Logic error")
                    line = m_data.get("pos", {}).get("line", "?")
                    return (False, f"Lỗi logic tại dòng {line}: {error_msg}")

        # Nếu duyệt hết mà không thấy 'error' nào, chứng minh được chấp nhận
        return (True, "Chứng minh hợp lệ.")

    except Exception as e:
        return (False, f"Lỗi hệ thống: {str(e)}")

# --- KIỂM TRA THỰC TẾ ---
if __name__ == "__main__":
    # 1. Một chứng minh ĐÚNG (Định lý giao hoán số tự nhiên)
    valid_proof = """
theorem add_comm (n m : Nat) : n + m = m + n := by
  induction n with
  | zero => simp
  | succ n ih => simp [ih, Nat.add_succ, Nat.succ_add]
"""

    # 2. Một chứng minh SAI (Cố tình chứng minh 2+2=5)
    invalid_proof = """
theorem wrong_math : 2 + 2 = 5 := rfl
"""

    print("--- Đang xác thực chứng minh ĐÚNG ---")
    ok1, msg1 = verify(valid_proof)
    print(f"Kết quả: {'✅ PASS' if ok1 else '❌ FAIL'}")

    print("\n--- Đang xác thực chứng minh SAI ---")
    ok2, msg2 = verify(invalid_proof)
    print(f"Kết quả: {'✅ PASS' if ok2 else '❌ FAIL'}")
    if not ok2:
        print(f"Thông báo: {msg2}")