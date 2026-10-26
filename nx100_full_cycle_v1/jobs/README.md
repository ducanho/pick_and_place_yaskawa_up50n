# JOB MOVEUNTI hiện có trên NX100

Tên gọi Ethernet: `MOVEUNTI`, không có phần mở rộng. Người vận hành đã test JOB trên pendant ngày 23/10/2026 theo yêu cầu cung cấp.

Không tìm thấy export `moveunti.jbi` trong workspace lúc audit. Không tạo bản giả, không upload, không sửa/ghi đè JOB. Cần export bản đang chạy từ pendant để đối chiếu trước nghiệm thu REAL.

HW0483202 §3.2.2, trang in 3-18: START có operand tên JOB sẽ chạy JOB đó từ đầu. Gửi:

```text
CONNECT Robot_access<CR><LF>
HOSTCTRL_REQUEST START 9<CR><LF>
MOVEUNTI<CR>
```

Mỗi dòng sau phải chờ ACK đúng của controller. `0000<CR><LF>` chỉ xác nhận nhận lệnh. Driver không dùng START rỗng, SETMJ hoặc JSEQ, không đổi master JOB. Trước START đọc `RJDIR *` để tìm đúng tên; trong quá trình chạy đọc `RJSEQ`, RSTATS, RPOSC và IOREAD.

Framing RJDIR và khả năng lệnh trên NX100 cụ thể vẫn cần xác minh tại máy. Danh sách JOB không hợp lệ bị chặn thay vì đoán parser. RUNNING phải được quan sát ON, sau đó OFF. Nếu JOB quá nhanh không bắt được cạnh ON, hệ thống không tự suy đoán đã hoàn tất.

REAL chưa có tín hiệu chứng minh nguyên nhân JOB dừng do laser. IN1 ON và RUNNING OFF chỉ là quan sát tương quan; khóa vacuum tự động. Không thay IMOV UNTIL bằng TCP IMOV và không tự thêm logic trong JOB/ladder.
