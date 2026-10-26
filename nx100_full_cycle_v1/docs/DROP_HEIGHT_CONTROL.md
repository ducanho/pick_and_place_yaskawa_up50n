# DROP HEIGHT CONTROL

## Luồng P010 hiện tại

Theo yêu cầu mới, người vận hành tự sửa JOB DROP và xác nhận MOVEUNTI không còn
dùng P010. P009 là DROP SAFE. Sau H2ON, trước START DROP, PC đọc SAVEV 4,9,
lấy XY/RX/RY/RZ, posture và tool từ P009, thay Z bằng 330 + count * chiều dày,
ghi LOADV vào P010 rồi đọc lại SAVEV 4,10 đối chiếu toàn bộ. P009 không bị ghi đổi.
P009 dùng Cartesian BASE; pulse hoặc hệ tọa độ khác bị từ chối.
Không gửi MOVL từ PC để hạ Z. JOB DROP cần di chuyển và kết thúc tại P010;
backend chờ đúng JOB DROP, RUNNING OFF, RPOSC đạt đích nhiều mẫu rồi mới gọi H2OFF.
H2OFF, đếm, nâng Z+200 và tự gắp tiếp giữ nguyên. Không tạo/upload/sửa JBI.
LOADV mất phản hồi không retry, readback sai không START DROP. Ghi và kiểm tra
trước START giúp JOB không đọc giá trị cũ, không cần thêm tín hiệu chờ vào JBI.

Phần dưới mô tả đường cũ dùng MOVL từ PC, chỉ giữ cho kiểm thử hồi quy.

Phần mới chỉ chạy sau lệnh START DROP đã có. Camera, YOLO, calibration, chọn target,
MOVE XY, MOVEUNTI, laser, H2ON, nâng ván và nội dung JOB DROP không thay đổi.

Người vận hành xác nhận DROP kết thúc tại Z safe = 600 mm. Backend chờ đúng JOB DROP,
RUNNING OFF, Z trong dung sai của 600 và RPOSC ổn định nhiều mẫu. Sau đó lấy nguyên
X/Y/RX/RY/RZ tại điểm cuối JOB làm DROP POSITION; không thay các giá trị này bằng tư
thế gắp hay tọa độ tự đặt. Trước khi hạ, kiểm tra lại pose safe chưa đổi.

## Trình tự

1. Đọc bộ đếm và chiều dày, tính `Z_drop = 330 + stacked_count * board_thickness_mm`.
2. Kiểm tra workspace, Z_drop không cao hơn điểm safe; gửi MOVL chỉ đổi Z.
3. Chờ RUNNING OFF và RPOSC đạt đích đủ số mẫu, ghi `DROP_Z_REACHED`.
4. `_finish_drop()` gọi `_execute_hand_job(2, False, cfg['vacuum'], required_pose=target)`.
   Hàm này kiểm tra lại robot dừng đúng pose, rồi qua `Controller.start_hand_job()`
   thực sự gửi `client.execute('START', 'H2OFF')` tới NX100. Không ghi I/O thay JOB,
   không tạo hay sửa JOB và không retry START.
5. Chờ RJSEQ đúng H2OFF và RUNNING OFF hai mẫu, kiểm tra các cờ remote/teach/alarm/
   error/hold, đọc lại telemetry. Chỉ khi đó mới ghi `H2OFF_COMPLETE` và lưu receipt.
6. Tự lưu tăng bộ đếm một lần theo cycle ID khi H2OFF hoàn thành, ghi
   `STACK_COUNT_UPDATED`. Không cần nút xác nhận nhả. Receipt ghi
   `count_basis=h2off_completed`, không khẳng định có cảm biến xác nhận nhả ván.
7. Gửi một MOVL tới Z_drop + 200 mm, giữ nguyên X/Y/RX/RY/RZ, ghi
   `POST_H2OFF_MOVE`. Chờ robot dừng đúng đích rồi kết thúc lượt gắp.
8. FULL CYCLE tự bắt đầu lượt mới với cycle ID riêng, ảnh mới và XY tính lại.
   Không phát hiện ván liên tục 2 giây trên frame mới thì dừng bình thường tại
   COMPLETE, `stop_reason=no_boards`. Lỗi camera hoặc HOLD dừng vòng lặp;
   không tự tiếp tục sau restart. Các chế độ chạy từng giai đoạn không lặp.

Phản hồi START 0000 không được dùng làm bằng chứng H2OFF đã hoàn thành. Trạng thái
OUTPUT hiện có chỉ được lưu trong receipt để đối chiếu; không coi là cảm biến nhả
ván hoặc bằng chứng áp suất. Lỗi H2OFF, timeout, mất phản hồi hoặc sai pose/JOB
không tăng đếm và không tự gọi lại H2OFF. Nếu lệnh nâng sau H2OFF thất bại, giữ
bộ đếm đã lưu, không tăng trùng hoặc tự phát lại lệnh. Mỗi cycle chỉ vào DROP một lần.

## Lưu trữ và RESET

`data/real/drop_stack.json` (MOCK dùng thư mục riêng) lưu first_drop_z_mm=330,
board_thickness_mm=12 mặc định, stacked_count, last_completed_drop_cycle_id và danh
sách cycle đã ghi nhận để chống tăng trùng. Ghi qua file tạm, flush/fsync và atomic
replace. Bộ đếm chỉ được đổi trong bộ nhớ sau khi lưu thành công.

HMI cho sửa chiều dày khi cycle không hoạt động. RESET STACK cần xác nhận, chỉ cho
phép tại IDLE/COMPLETE, không có worker và robot đã dừng nếu đang kết nối. RESET đưa
count về 0, next Z về 330, giữ chiều dày và lịch sử chống trùng. Không gửi MOVL/JOB.

Khởi động lại giữa DROP/H2OFF/nâng sau thả chuyển journal sang FAULT, không tự chạy
lại lệnh hay tăng đếm. Nếu bộ đếm đã ghi trước khi journal hoàn tất thì cycle ID cũ
không tăng thêm lần nữa. File bộ đếm hỏng không tự được thay bằng count=0.

## Kiểm thử

MOCK kiểm tra 330/342/354, chỉ START H2OFF sau hạ Z và dừng đúng đích, H2OFF lỗi/
timeout/sai JOB không tăng đếm, chống gọi lại và tăng trùng, RESET, lỗi lưu file,
khôi phục sau restart. Kiểm tra lưu count trước lệnh nâng, nâng chỉ đổi Z thêm 200,
lỗi nâng giữ nguyên count. API kiểm tra lease, cycle ID và RESET không gửi lệnh robot.
Browser smoke kiểm tra không còn nút xác nhận nhả, count=1, Z cuối=530,
next Z=342 và desktop/tablet.

Không tự thử MOVL, DROP hoặc H2OFF trên robot REAL trong lần triển khai này.

## File triển khai

- Mới: workflow/drop.py, tests/test_drop.py, docs/DROP_HEIGHT_CONTROL.md.
- Backend: workflow/cycle.py, workflow/state_machine.py, app.py, config.json.
- HMI: templates/index.html, static/app.js, static/style.css.
- MOCK/hồi quy: robot/mock.py, tests/test_cycle.py, tests/test_laser_h2_cycle.py,
  tests/test_api.py, tests/test_independence.py, tools/browser_smoke.py.
- Tài liệu: README.md, docs/TEST_REPORT.md và kết quả test/browser.

Kết quả: 128/128 unittest đạt; browser smoke đạt, gồm hủy/chấp nhận RESET STACK,
count trở về 0, next Z=330 và chiều dày giữ 12. Server REAL đã cập nhật,
không tự thực hiện chu trình robot. Các lần bàn giao DROP cũ không tự nối lại;
ACK về IDLE để bắt đầu chu trình mới.
