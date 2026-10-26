# Mapping laser và HAND

## Laser

Người vận hành xác nhận mapping trên NX100: `20050 → IN#(1)`, Omron E3Z-LL61 digital. Driver dùng `IOREAD 20050,8`, lấy bit cấu hình (mặc định 0), sau đó áp dụng `active_high`. Phần hiển thị luôn thực hiện đọc kể cả `verified=false`; API trả thêm byte gốc, bit và trạng thái nghiệm thu mapping. Cờ verified vẫn được kiểm tra riêng khi nghiệm thu JOB/cycle, không dùng để chặn telemetry.

Thử đọc trực tiếp ngày 24/10/2026: REMOTE OFF → IOREAD bị controller từ chối với mã 2100; sau khi người vận hành bật REMOTE → đọc được byte 4, bit 0 OFF. Chưa xác nhận ON/OFF vật lý bằng cách che cảm biến trong lần thử này. Lỗi đọc trả UNKNOWN và hiện nguyên nhân; không làm mất các trường RSTATS/RPOSC còn đọc được. Polling telemetry chỉ đọc, tự phục hồi sau lỗi kết nối và không gửi lại lệnh điều khiển.

Tài liệu Yaskawa/Motoman Data Transmission, phần 5.2, mô tả interpreter code 2100 là chưa đặt command remote: https://www.manualslib.com/manual/1263633/Motoman-Nx-100.html (trang 73).

HW0483202 §3.2.3, trang in 3-29: IOREAD đọc theo nhóm bội số 8 điểm; một giá trị decimal cho mỗi byte. Phản hồi sai định dạng hoặc mất kết nối không được biến thành OFF. Không hiển thị khoảng cách mm.

Phải so sánh IN1 trên pendant với byte đọc được ở cả trạng thái có vật/không vật và khi rút nguồn cảm biến. Không suy ra bit từ tên IN#(1) mà chưa đo.

## HAND 1-1 và HAND 1-2

Hiện chưa có địa chỉ điều khiển HAND đã xác minh trong workspace. Hai control REAL bị khóa. Không suy ra HAND từ số thứ tự output hoặc ghi trực tiếp vào `20050`.

HW0483202 §3.2.3 giới hạn IOWRITE ở network input #22010..#23287. Driver chỉ cho phép một byte căn đầu bit 0, đã được khai báo thuộc quyền quản lý độc quyền của ứng dụng, với mapping ladder **đang tồn tại và đã được kiểm chứng** tới HAND. Không cài/sửa ladder trong dự án này. Nếu hệ thống chưa có mapping phù hợp thì backend này không thể điều khiển HAND bằng IOWRITE; giữ khóa và xác định phương thức được hỗ trợ tại máy.

Các trường cần xác minh trong `vacuum`: `verified`, `mode`, `start`, `bits`, `active_high`, `owned_byte`. `mode=independent` điều khiển độc lập. `mode=complementary` khi yêu cầu một HAND ON sẽ đặt HAND kia OFF trong cùng byte write; yêu cầu OFF sẽ bật HAND bổ sung. HMI hiển thị loại mapping để người vận hành hiểu hành vi.

Các bit có thể đảo cực tính độc lập. Driver đọc byte, bảo toàn bit khác, cập nhật cả hai bit trong một lệnh và đọc lại xác minh. Không retry nếu phản hồi mất. `owned_byte` chỉ hợp lệ khi không có host khác ghi byte đó; read-modify-write không bảo vệ trước host bên ngoài.

Trạng thái vacuum hiển thị kết quả command/readback cuối trong phiên. Khi mất kết nối hiển thị UNKNOWN; chưa gửi lệnh trong phiên cũng UNKNOWN. Không có pressure sensor và không xác nhận chất lượng bám vật.

MOCK dùng byte 22010, bits 0/1, độc lập, active high. Đây chỉ là địa chỉ mô phỏng, **không phải mapping được đề xuất cho robot thật**.
