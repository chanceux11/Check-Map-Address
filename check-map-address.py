import tkinter as tk
from tkinter import messagebox
from geopy.geocoders import Nominatim
from concurrent.futures import ThreadPoolExecutor
from difflib import SequenceMatcher
import time

# Cấu hình geolocator với timeout
geolocator = Nominatim(user_agent="address_checker", timeout=10)

# Hàm tính tỷ lệ tương đồng
def similarity_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()

# Hàm xử lý geocode từng địa chỉ
def geocode_address(address):
    try:
        location = geolocator.geocode(address)
        if location:
            # So sánh tỷ lệ tương đồng giữa address và name trong location.raw
            name = location.raw.get("name", "")
            print(name)
            # Tính độ tương đồng
            similarity = SequenceMatcher(None, address.lower(), name.lower()).ratio()

            # In ra nếu độ tương đồng vượt ngưỡng (ví dụ 0.5)
            if similarity > 0.5:
                return address
    except Exception as e:
        print(f"Địa chỉ: {address} --> Lỗi: {e}")
        return None
    return None

# Hàm xử lý khi người dùng bấm nút "Kiểm tra"
def check_addresses():
    # Đọc danh sách địa chỉ từ text box
    addresses = text_input.get("1.0", "end-1c").splitlines()

    # Nếu không có địa chỉ nào
    if not addresses:
        messagebox.showwarning("Cảnh báo", "Vui lòng nhập địa chỉ.")
        return

    # Sử dụng đa luồng để tăng tốc
    start_time = time.time()
    valid_addresses = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(geocode_address, addresses))

    # Lọc ra các địa chỉ hợp lệ
    valid_addresses = [address for address in results if address is not None]

    # Hiển thị kết quả trong text box kết quả
    output_text.delete(1.0, "end")
    if valid_addresses:
        for address in valid_addresses:
            output_text.insert("end", f"{address}\n")
    else:
        output_text.insert("end", "Không có địa chỉ hợp lệ nào.")

    elapsed_time = time.time() - start_time
    messagebox.showinfo("Hoàn thành", f"Đã kiểm tra xong!\nThời gian thực thi: {elapsed_time:.2f} giây")

# Tạo cửa sổ giao diện
root = tk.Tk()
root.title("Kiểm tra địa chỉ")

# Nhập địa chỉ từ người dùng
label_input = tk.Label(root, text="Nhập địa chỉ (mỗi địa chỉ một dòng):")
label_input.pack(pady=10)

text_input = tk.Text(root, height=10, width=50)
text_input.pack(pady=5)

# Nút kiểm tra
button_check = tk.Button(root, text="Kiểm tra", command=check_addresses)
button_check.pack(pady=10)

# Hiển thị kết quả kiểm tra
label_output = tk.Label(root, text="Kết quả:")
label_output.pack(pady=10)

output_text = tk.Text(root, height=10, width=50)
output_text.pack(pady=5)

# Chạy giao diện
root.mainloop()
 
