import tkinter as tk
from tkinter import filedialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from difflib import SequenceMatcher
import threading
import time


# Hàm kiểm tra địa chỉ trên Google Maps
def check_address(driver, address):
    try:
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'searchboxinput'))
        )
        search_box.clear()
        search_box.send_keys(address)
        search_box.send_keys(Keys.RETURN)
        time.sleep(0.5)

        # Chờ kết quả hiển thị
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'DkEaL'))
        )
        result_elements = driver.find_element(By.CLASS_NAME, 'DkEaL').text

        similarity = SequenceMatcher(None, address.lower(), result_elements.lower()).ratio()
        return similarity > 0.5

    except Exception as e:
        print(f"Lỗi khi kiểm tra địa chỉ '{address}': {e}")
        return False


# Hàm kiểm tra danh sách địa chỉ trong nhiều tab
def check_addresses_in_tabs():
    start_time = time.time()  # Lưu thời gian bắt đầu

    # Đọc danh sách địa chỉ từ hộp nhập liệu
    addresses = text_input.get("1.0", "end-1c").splitlines()
    if not addresses:
        result_label.config(text="Vui lòng nhập địa chỉ.", fg="red")
        return

    # Lấy số lượng tab từ hộp nhập liệu
    try:
        num_tabs = int(tab_count_entry.get())  # Sử dụng số lượng tab từ Entry
        if num_tabs < 1:
            result_label.config(text="Số lượng tab phải lớn hơn hoặc bằng 1.", fg="red")
            return
    except ValueError:
        result_label.config(text="Vui lòng nhập một số hợp lệ cho số lượng tab.", fg="red")
        return

    chunk_size = len(addresses) // num_tabs + (1 if len(addresses) % num_tabs else 0)
    address_chunks = [addresses[i:i + chunk_size] for i in range(0, len(addresses), chunk_size)]

    # Khởi tạo trình duyệt với options ẩn
    options = Options()
    options.add_argument('--headless')  # Chạy trình duyệt ở chế độ ẩn
    options.add_argument('--disable-gpu')  # Tắt GPU (cần thiết cho chế độ ẩn trên một số hệ thống)
    options.add_argument('--no-sandbox')  # Bỏ qua sandbox (cần thiết trên một số hệ thống)
    
    driver = webdriver.Chrome(options=options)

    try:
        # Mở Google Maps
        driver.get('https://www.google.com/maps')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'searchboxinput'))
        )

        filtered_addresses = []
        invalid_addresses = []  # Danh sách địa chỉ không hợp lệ
        total_addresses = 0  # Số địa chỉ đã kiểm tra
        valid_addresses = 0  # Số địa chỉ hợp lệ
        
        # Duyệt qua từng nhóm và mở tab mới cho mỗi nhóm
        for i, chunk in enumerate(address_chunks):
            if i > 0:  # Mở tab mới nếu không phải tab đầu tiên
                driver.execute_script("window.open('');")
                driver.switch_to.window(driver.window_handles[i])

            driver.get('https://www.google.com/maps')
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'searchboxinput'))
            )

            # Hiển thị thông báo đang thực thi công việc
            result_label.config(text="Đang kiểm tra...", fg="blue")
            root.update()  # Cập nhật giao diện trong lúc xử lý

            # Kiểm tra từng địa chỉ trong nhóm
            for address in chunk:
                total_addresses += 1  # Tăng số địa chỉ đã kiểm tra

                if check_address(driver, address):
                    valid_addresses += 1  # Tăng số địa chỉ hợp lệ
                    filtered_addresses.append(address)
                else:
                    invalid_addresses.append(address)  # Thêm địa chỉ không hợp lệ vào danh sách

        # Tính toán thời gian đã trôi qua
        end_time = time.time()
        elapsed_time = end_time - start_time

        # Hiển thị kết quả
        result_label.config(text=f"Kiểm tra hoàn tất! {valid_addresses}/{total_addresses} địa chỉ hợp lệ. Thời gian: {elapsed_time:.2f} giây.", fg="green")
        output_text.delete(1.0, "end")
        for addr in filtered_addresses:
            output_text.insert("end", f"{addr}\n")

        # Hiển thị địa chỉ không hợp lệ
        invalid_output_text.delete(1.0, "end")
        for addr in invalid_addresses:
            invalid_output_text.insert("end", f"{addr}\n")

    finally:
        driver.quit()


# Hàm khởi chạy kiểm tra địa chỉ trong luồng riêng
def start_check():
    threading.Thread(target=check_addresses_in_tabs).start()


# Tạo giao diện với Tkinter
root = tk.Tk()
root.title("Kiểm tra địa chỉ với Selenium")

# Nhập địa chỉ từ người dùng
label_input = tk.Label(root, text="Nhập địa chỉ (mỗi địa chỉ một dòng):")
label_input.pack(pady=10)

text_input = tk.Text(root, height=10, width=50)
text_input.pack(pady=5)

# Thêm Entry để người dùng nhập số lượng tab
label_tab_count = tk.Label(root, text="Nhập số lượng tab muốn mở:")
label_tab_count.pack(pady=5)

tab_count_entry = tk.Entry(root, width=10)
tab_count_entry.pack(pady=5)
tab_count_entry.insert(0, "3")  # Mặc định số tab là 3

# Nút kiểm tra
button_check = tk.Button(root, text="Kiểm tra", command=start_check)
button_check.pack(pady=10)

# Nhãn hiển thị trạng thái kết quả
result_label = tk.Label(root, text="", font=("Arial", 10))
result_label.pack(pady=5)

# Hiển thị kết quả kiểm tra
label_output = tk.Label(root, text="Kết quả hợp lệ:")
label_output.pack(pady=10)

output_text = tk.Text(root, height=10, width=50)
output_text.pack(pady=5)

# Hiển thị kết quả không hợp lệ
label_invalid_output = tk.Label(root, text="Địa chỉ không hợp lệ:")
label_invalid_output.pack(pady=10)

invalid_output_text = tk.Text(root, height=10, width=50)
invalid_output_text.pack(pady=5)

# Chạy giao diện
root.mainloop()
