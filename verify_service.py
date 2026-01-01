import requests
import json

class KiminaVerifier:
    def __init__(self, host="http://localhost", port=8080):
        self.url = f"{host}:{port}/verify"

    def verify(self, custom_id, proof_code):
        payload = {
            "codes": [{"custom_id": custom_id, "proof": proof_code}],
            "infotree_type": "original"
        }
        
        try:
            response = requests.post(self.url, json=payload, timeout=10)
            data = response.json()
            res = data['results'][0]['response']
            
            # 1. Kiểm tra lỗi biên dịch nghiêm trọng (Errors luôn ưu tiên)
            errors = [m for m in res.get('messages', []) if m['severity'] == 'error']
            if errors:
                return f"❌ THẤT BẠI (Lỗi): {errors[0]['data']}"
            
            # 2. Kiểm tra lỗi sử dụng 'sorry'
            sorries = [m for m in res.get('messages', []) if "declaration uses 'sorry'" in m['data']]
            if sorries:
                return "⚠️ CHƯA HOÀN THÀNH: Bạn không được dùng 'sorry'!"

            # 3. LOGIC MỚI: Kiểm tra xem có bất kỳ thông báo lỗi nào không. 
            # Nếu không có error và không có sorry, thường là thành công.
            
            # Kiểm tra goals trong infotree (nếu dùng tactics 'by')
            if 'infotree' in res and res['infotree']:
                # Tìm node cao nhất có chứa thông tin mục tiêu
                main_node = res['infotree'][0]['node']
                goals_after = main_node.get('goalsAfter', [])
                if goals_after == []:
                    return "✅ THÀNH CÔNG: Chứng minh hợp lệ."
                else:
                    return "❓ CHƯA XONG: Vẫn còn mục tiêu chưa giải quyết."
            
            # 4. TRƯỜNG HỢP rfl: Nếu không có lỗi và không có infotree (hoặc infotree rỗng)
            # nhưng biên dịch thành công thì đó là chứng minh bằng Term (như rfl).
            return "✅ THÀNH CÔNG: Chứng minh hợp lệ (Term Mode)."

        except Exception as e:
            return f"❌ LỖI HỆ THỐNG: {str(e)}"

# Thử lại với Case_Dung của bạn
v = KiminaVerifier()
print(v.verify("Case_Dung", "theorem t1 (n : Nat) : n = n := rfl"))

test_cases = [
    ("Case_Dung", "theorem add_zero_test (n : Nat) : n + 0 = n := by induction n with | zero => rfl | succ n ih =>  rw [Nat.add_succ, ih]"),
    ("Case_Sai_Cu_Phap", "theorm t2 : 1 = 1 := rfl"),
    ("Case_Sai_Logic", "theorem t3 : 1 + 1 = 3 := rfl"),
    ("Case_Dung_Sorry", "theorem t4 : 2 + 2 = 4 := by sorry")
]

print("--- ĐANG CHẠY VERIFIER TEST ---")
for cid, code in test_cases:
    print(f"\n[{cid}]")
    print(f"Code: {code}")
    result = v.verify(cid, code)
    print(f"Kết quả -> {result}")