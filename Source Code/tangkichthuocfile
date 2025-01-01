def increase_file_size(file_name, size_in_mb):
    try:
        with open(file_name, 'ab') as f:
         
            f.write(b'\0' * size_in_mb * 1024 * 1024)
        print(f"Tập tin '{file_name}' đã được tăng thêm {size_in_mb} MB.")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")


increase_file_size("Noidung.docx.exe", 660)
