# Kết quả kiểm thử — 24/10/2026

## Chuẩn bị pick tiếp theo trong lúc DROP / nâng

151/151 kiểm thử đạt, 0 failure/error/skip, 90,17 giây. Sau tính Z thả, tạo
StableTarget cho thứ tự ID sau ID đang gắp; worker camera cập nhật bằng các
frame vốn đã chạy, không tạo thêm lượt YOLO hay lệnh robot. Sau nâng Z+200,
chuyển lịch sử ổn định sang lượt kế, bắt buộc frame có timestamp sau bước nâng
và xác minh lại ID/instance/độ tin cậy/XY. Dùng XY của frame mới nhất.
Giữ 5 frame/1 giây; mất ổn định, đổi ID/instance/vị trí, ảnh gián đoạn hoặc
uncertain sẽ phải tích lũy lại. HOLD/lỗi/kết thúc batch/restart xóa phần chuẩn bị.
Không dùng lịch sử ảnh che để kết luận hết ván; empty check vẫn bắt đầu sau nâng.
Unit kiểm tra dùng một frame mới khi đã đủ lịch sử, từ chối frame cũ/che/đổi
vị trí/instance/camera lỗi/thứ tự không khớp. MOCK full cycle xác nhận lượt hai
nhận được lịch sử tích lũy trong DROP; các lượt 1/2/3/4/1 vẫn đúng. Browser smoke
đạt desktop/tablet, không lỗi JS. Không thử chuyển động trên robot REAL.

## Sửa trực tiếp số tấm đã xếp

Thêm POST /api/drop/count và ô ĐÃ XẾP + LƯU. Chỉ sửa khi IDLE/COMPLETE,
không worker, robot đã dừng nếu kết nối; giữ lease/revision/request guard.
Nhận số nguyên không âm, lưu atomic, giữ lịch sử chống đếm trùng và last_picked_id.
Tính lại next Z theo count mới, không gửi lệnh chuyển động hoặc ghi P010 khi sửa.
13 kiểm thử API đạt: quyền, giá trị sai, robot chạy, lưu qua restart, tăng/giảm,
bảo toàn lịch sử/thứ tự và không phát lệnh robot. Browser smoke đạt: nhập 7,
poll không ghi đè bản nháp, LƯU cập nhật next Z=414; RESET vẫn hoạt động,
desktop/tablet đạt, không lỗi JS. Kiểm thử dùng MOCK, không thử gắp REAL.

## Chọn ID theo vòng tăng dần

144/144 kiểm thử đạt, 0 failure/error/skip, 89,86 giây. Chọn ID đang thấy lớn hơn
ID gắp cuối trước, hết ID lớn hơn mới quay về ID nhỏ nhất. ID nhỏ tái xuất hiện
với instance mới không chen trước ID lớn hơn. ID không thấy/uncertain bị bỏ qua;
chỉ một ID vẫn tiếp tục gắp được. Giữ kiểm tra ảnh mới và 5 frame/1 giây ổn định.
last_picked_id lưu atomic cùng tăng count sau H2OFF; lỗi lưu không tiến thứ tự,
duplicate cycle không đổi thứ tự, restart giữ ID cuối và không tự chạy robot.
MOCK chạy đủ 5 chu trình xác nhận 1/2/3/4/1; unit kiểm tra hai vòng 1/2/3/4.
Browser smoke đạt desktop/tablet và không lỗi JS. Không thử gắp trên robot REAL.

## Hiển thị cảm biến áp suất IN2 / IN3

Mapping theo sơ đồ người vận hành: 20051=IN2 (bit1), 20052=IN3 (bit2), cùng byte
IOREAD 20050,8 với laser IN1 (bit0). HMI hiển thị riêng ON/OFF/UNKNOWN, địa chỉ
và byte hiện tại; không suy diễn áp suất từ OUTPUT relay và không hiển thị kPa.
Không thay điều kiện chạy cycle. Lỗi/stale/mất kết nối hiển thị UNKNOWN.
Giao diện cũng giải mã trực tiếp byte đang có để dùng ngay với server hiện tại,
không restart hoặc ngắt chu trình đang chạy. Config backend lưu input_contacts
[20051,20052] cho lần khởi động sau. Kiểm tra read-only hiện tại thấy byte=5,
IN2 OFF / IN3 ON; đây là ảnh chụp trạng thái tại thời điểm đọc.
17 kiểm thử sensor/API đạt; browser smoke xác nhận IN2 ON/IN3 OFF trên MOCK,
desktop vừa viewport, tablet không tràn ngang, không lỗi JavaScript.

## P010 lấy DROP SAFE từ P009, mốc Z +300

139/139 kiểm thử đạt, 0 failure/error/skip, 81,47 giây. Người vận hành xác nhận
P009 là DROP SAFE. PC đọc SAVEV 4,9, sao chép XY/RX/RY/RZ/posture/tool sang P010,
chỉ thay Z=300+count*chiều dày, ghi LOADV rồi đọc lại P010 trước START DROP.
Không lấy XY từ vị trí gắp hoặc P010 cũ; P009 không bị ghi đổi. JBI do người vận
hành xử lý với MOVL P010. Bộ đếm/lịch sử được giữ, mốc lưu REAL cập nhật +300.
Kiểm tra 300/312/324, nâng sau thả tới 500/512/524, nguồn P009 khác P010 cũ và
vị trí gắp. Browser smoke đạt, reset về next Z=300, không lỗi JS. Không ghi biến
hoặc thử chuyển động robot REAL trong lần cập nhật này.

## Ghi Z thả vào P010 trước DROP

138/138 kiểm thử đạt, 0 failure/error/skip, 80,75 giây. PC đọc SAVEV 4,10,
chỉ thay Z, ghi LOADV và xác minh SAVEV trước START DROP. Không gửi MOVL hạ Z;
người vận hành tự sửa JBI. P010 phải Cartesian BASE, giữ nguyên XY/tư thế/tool.
JOB DROP dừng tại P010 mới gọi H2OFF; đếm/nâng Z+200/lặp gắp giữ nguyên.
Kiểm tra 330/342/354, trường khác giữ nguyên, readback sai chặn DROP/H2OFF,
DROP không đến P010 chặn H2OFF, LOADV mất phản hồi là UNKNOWN và không retry.
Browser smoke đạt, không lỗi JS. Không ghi biến hay thử chuyển động REAL.
Thử đọc SAVEV read-only trên controller trả ERROR 2100; chưa xác minh đọc/ghi
P010 trên phần cứng khi controller cho phép lệnh. Các kết quả chức năng dùng MOCK.

## Gắp liên tục đến khi hết ván

132/132 kiểm thử đạt, 0 failure/error/skip, 77,95 giây. FULL CYCLE lặp sau nâng
Z+200 đã đến đích; mỗi lượt dùng ảnh mới, XY mới và cycle ID riêng. Không có ván
liên tục 2 giây trên frame mới thì COMPLETE với stop_reason=no_boards, không
gửi thêm MOVL/JOB hoặc HOLD. Lỗi camera không bị coi là hết ván; HOLD chặn lượt tiếp.
MOCK kiểm tra hai tấm, count=2, Z sau nâng lần lượt 530/542 và đúng 6 MOVL;
không có lệnh gắp thứ ba. Các chế độ từng giai đoạn vẫn chạy một lần.
Browser smoke hồi quy đạt desktop/tablet, không lỗi JS. Không thử chuyển động REAL.

## Tự đếm sau H2OFF và nâng Z thêm 200 mm

128/128 kiểm thử đạt, 0 failure/error/skip, 68,98 giây. H2OFF hoàn thành -> lưu tăng bộ đếm một lần theo cycle ID -> MOVL Z_drop+200, giữ XY/RX/RY/RZ -> COMPLETE. Nếu nâng thất bại, bộ đếm đã lưu vẫn giữ nguyên; restart không tự phát lại lệnh. Không dùng ACK START làm bằng chứng JOB hoàn thành.

Browser smoke đạt, không lỗi JS, không còn nút xác nhận nhả; tấm đầu kết thúc tại Z=530, count=1, next Z=342. RESET vẫn có xác nhận và trả count=0/next Z=330. Desktop/tablet đạt. Chưa thử chuyển động REAL; các mục sau là lịch sử triển khai.

## Hoàn thiện DROP Z / H2OFF / đếm ván

**126/126 kiểm thử đạt, 0 failure/error/skip, 62,14 giây** (test_result.json, test_output.txt). Nhóm mới kiểm tra Z 330/342/354, START H2OFF thật qua module JOB trên transport MOCK sau hạ Z, sai pose, lỗi/timeout/mất phản hồi/sai JOB, chống gửi lại và tăng trùng, RESET, lỗi ghi file và restart không replay. Bộ test hồi quy gắp/MOVEUNTI/laser/vacuum ON vẫn đạt.

Người vận hành xác nhận JOB DROP kết thúc ở Z safe=600 mm. Chỉ nối phần mới sau START DROP, không sửa JOB/đường nâng và đi đến DROP SAFE. XY/RX/RY/RZ giữ theo RPOSC ổn định ở điểm cuối DROP.

Browser smoke đạt desktop 1920x1080 vừa viewport, tablet 1024x768 không tràn ngang, không lỗi JS; H2OFF COMPLETE chỉ sau backend xác nhận, count=0 trước xác nhận nhả ván / count=1 sau xác nhận, next Z=342. Chưa thử chu trình REAL. Xem DROP_HEIGHT_CONTROL.md và browser_result.json. Các phần bên dưới là lịch sử triển khai.

Tốc độ mặc định mới nhất: MOVL=80 mm/s; config/operator settings, max backend và max HMI đồng bộ 80. Kiểm thử nhánh REAL với transport giả đạt: wire MOVL gửi tốc độ 80, laser ON + robot dừng -> H2ON -> COMPLETE; 80.1 bị từ chối. Chưa thử chuyển động trên robot thật trong lần đổi tốc độ này.

Bỏ giới hạn target phải dịch chuyển 50 mm giữa hai chu trình để gắp ván xếp chồng cùng XY. Xóa guard và minimum_move_distance_mm khỏi config; last_target chỉ còn ghi lịch sử. Ba kiểm thử hồi quy đạt: hai chu trình cùng XY cùng COMPLETE, 10 frame/2 giây ổn định và chặn duplicate START. Không thử chuyển động trên robot thật.

Luồng mới nhất theo yêu cầu: mặc định MOVL=50 mm/s (backend và HMI nhận tối đa 50), MOVEUNTI -> laser ON + RUNNING OFF ổn định -> H2ON một lần -> COMPLETE. Kiểm thử nhánh REAL với transport giả, laser OFF khi JOB dừng, laser ON khi còn RUNNING, laser UNKNOWN, laser tắt lại trước H2ON và JOB ngắn kết thúc giữa hai lần poll. Browser smoke xác nhận COMPLETE, H2ON hoàn tất và tốc độ 50. Chưa tự gửi lệnh MOVL/START/H2ON thử trên robot thật trong lần cập nhật này. Các mục bàn giao JOB_DISPATCHED bên dưới là lịch sử/hồi quy.

Sửa lỗi RJDIR bị cắt ở CR đầu: theo HW0483202 5.1/5.4, single-command socket đóng sau phản hồi hoàn chỉnh, danh sách dài được chia nhiều đoạn. Client hiện đọc RJDIR đến EOF với deadline/size limit, parse đủ các nhóm CR/comma. Kiểm tra READ-ONLY trên controller thật: 120 JOB, MOVEUNTI ở index 87 (thứ 88), job_control.exists trả True; xem job_directory_live.json. Test fragmentation/coalescing, EOF thiếu CR, timeout sau nhóm đầu, response limit và JOB thật sự thiếu. Sau MOVL đã xác nhận đến đích, lỗi preflight trước START không tự gửi HOLD hay gán outcome_unknown. Chưa gửi START/HOLD/MOVL trên robot thật trong lần sửa này.

Bổ sung nút NHẢ HOLD (HOLD 0): kiểm thử wire framing, xác nhận thao tác, app IDLE, command/external/pendant HOLD, RUNNING/REMOTE/ALARM, API lease và duplicate request, mất phản hồi không retry. Browser smoke xác nhận hủy hộp thoại giữ HOLD ON, chấp nhận chuyển HOLD OFF trên simulator; desktop/tablet và JavaScript đạt. Chưa gửi HOLD OFF trên robot thật.

Người vận hành xác nhận đã nghiệm thu MOVL và yêu cầu bỏ khóa TOOL/posture + cờ nghiệm thu đường MOVL. Luồng bàn giao hiện tại (full_cycle/xy_only/moveunti_only) không còn phụ thuộc các cờ tĩnh/hash nghiệm thu. Vẫn giữ kiểm tra live SERVO/REMOTE/PLAY, ALARM/ERROR/HOLD/RUNNING, camera, workspace, metadata MOVL và xác nhận đến đích. Test nhánh REAL trên transport giả xác nhận giữ nguyên tool=3/posture=1; đổi tool giữa MOVL vẫn FAULT trước START MOVEUNTI. Không tự gửi lệnh chuyển động để kiểm thử trên robot thật.

## Cập nhật mới nhất: bàn giao sau START MOVEUNTI

Thông số hiện tại: Plane Z=0, Z_safe=500, MOVL=5, RX=180, RY=0, RZ=90. Cấu hình workflow.end_after_moveunti_start=true: camera XY -> MOVL XYZ/Z_safe -> xác nhận đến đích -> START MOVEUNTI -> JOB_DISPATCHED khi nhận 0000. Không chờ laser hoặc gọi H2ON tự động. JOB_DISPATCHED không có nghĩa robot đã dừng; phần tiếp theo do người vận hành xử lý. ACK chỉ khi RUNNING OFF. Restart giữ nguyên bàn giao; mất phản hồi START vẫn FAULT/UNKNOWN và không retry. Lỗi đọc telemetry sau bàn giao không tự phát HOLD.

Browser smoke đã xác nhận JOB_DISPATCHED, không có automatic H2ON, không ghi nhận job_completion_verified, desktop/tablet và JavaScript đạt. Các mục luồng H2ON bên dưới là lịch sử và kiểm thử hồi quy, không còn là luồng mặc định. Chưa thử MOVL/START MOVEUNTI trên robot thật trong lần cập nhật này.


Khởi chạy: app.py mặc định REAL, cổng 8011; bỏ --mock khỏi CLI. Edge mở sau khi Uvicorn started, lần chạy tiếp theo tái sử dụng server REAL đúng application_id. Test xác nhận default REAL không kết nối robot, mở Edge đúng URL, chờ server sẵn sàng và không tạo server trùng. Simulator chỉ dùng nội bộ cho kiểm thử.

## Luồng V1 cập nhật

START: freeze XY của ván + Z_safe -> một MOVL -> xác nhận RSTATS/RPOSC -> MOVEUNTI -> xác nhận tìm Z -> START H2ON -> xác nhận H2ON kết thúc -> COMPLETE tại Z dừng. Test bắt đầu Z=600 chỉ gửi một MOVL đến Z_safe=500, rồi MOVEUNTI và H2ON; kết thúc mô phỏng Z=470. Không có lệnh nâng Z/HOME/OFF sau hút. Mất phản hồi H2ON -> FAULT/UNKNOWN, không retry.

Người vận hành cung cấp nội dung lệnh MOVEUNTI là IMOV P010, V80, PL=0, BF, UNTIL IN#(1)=ON (chưa có bản export để đối chiếu chính xác cú pháp và P010). Chưa có tín hiệu chứng minh nguyên nhân dừng; FULL REAL vẫn chờ nghiệm thu theo yêu cầu gốc. Kiểm thử trên simulator, chưa chạy full cycle trên robot thật.


## Cập nhật điều khiển HAND bằng JOB

Người vận hành xác nhận bốn JOB H1ON, H1OFF, H2ON, H2OFF đã hoạt động trên pendant. Bốn nút HMI gọi START đúng tên JOB một lần; nhánh REAL này không ghi IOWRITE. Worker theo dõi RJSEQ và RSTATS để xác nhận đúng JOB đã dừng; ACK 0000 chưa được coi là kết thúc. Lỗi/mất phản hồi/timeout vào FAULT, không tự gửi lại. HOLD hủy worker; không tự resume.

Hai giá trị OUTPUT 30050/30051 hiển thị riêng, không gán chúng thành phản hồi HAND 1/2 hoặc xác nhận áp suất. Chưa gửi START HAND thử qua PC; phần kiểm thử tự động dùng simulator/socket giả. Nghiệm thu full cycle REAL vẫn riêng biệt với thao tác HAND thủ công.


## Kết quả tự động

**109/109 test đạt; 0 failures, 0 errors, 0 skipped; 40,75 giây.** Kết quả ở [test_result.json](test_result.json) và [test_output.txt](test_output.txt), tạo bằng Python trong `.venv` riêng. Bộ test dùng unittest, không cần pytest.

Bổ sung telemetry cảm biến: verified=false vẫn đọc byte thật; ON/OFF/active-low, phản hồi hỏng, lỗi IOREAD độc lập với RSTATS/RPOSC và chuyển ON/OFF tới API. Đã đọc trực tiếp controller sau khi người vận hành bật REMOTE, nhận byte 4 tại IOREAD 20050,8; bit 0 OFF. Chưa thử che cảm biến để xác minh cả hai mức vật lý. Xem laser_live_read.json.

Theo yêu cầu người vận hành, calibration `needs_review` được tiếp tục sử dụng và chỉ hiển thị cảnh báo. Đã kiểm thử nhánh kết nối camera REAL với adapter giả để xác nhận quality không chặn camera; SHA-256 của hai NPZ vẫn khớp bản sao ban đầu. Không sửa thuật toán hoặc offset.

Browser smoke dùng Edge headless và server MOCK riêng: desktop 1920×1080 hiển thị đầy đủ trong viewport; tablet 1024×768 không tràn ngang. Thao tác thực tế qua DOM: nhận quyền HMI → CONNECT → READY → START → COMPLETE → vacuum 1 ON → ACK. Vị trí kết thúc mô phỏng Z=470 mm; START bị khóa tại COMPLETE. Không có JavaScript page error. Xem [browser_result.json](browser_result.json).

Ảnh: [READY](hmi_desktop_ready.png), [COMPLETE](hmi_desktop_complete.png), [tablet](hmi_tablet.png).

## Đối chiếu 20 yêu cầu

| Yêu cầu | Test/quan sát |
|---|---|
| 1. Detect và calibration | Detector nhận bbox giả, lấy đúng center; transform NPZ thật, offset +280/+215 đúng một lần |
| 2. ID nhỏ nhất | StableTarget và full cycle chọn ID 1 |
| 3. 10 frame / 2 giây | Test với cấu hình production; repeated frame, stale/gap, motion và identity reuse không đạt |
| 4. MOVL hoàn thành | Cần RSTATS không RUNNING và RPOSC đạt dung sai 3 mẫu; full cycle kết thúc đúng |
| 5. MOVL không hoàn thành | `0000` nhưng vị trí không tới → timeout, HOLD request, FAULT, không START JOB |
| 6. MOVEUNTI được kích hoạt | Một lệnh START MOVEUNTI, đúng byte count 9, không START rỗng |
| 7. JOB thiếu/chưa xác minh | Không có JOB → không START; REAL chưa nghiệm thu bị khóa |
| 8. Laser hợp lệ | RUNNING đã ON, IN1 có cạnh, robot dừng và descent đúng trong mô phỏng |
| 9. Laser không trigger | Timeout → FAULT, không vacuum |
| 10. Laser ON sớm | Chặn trước START cycle hoặc trước START JOB |
| 11. Vacuum ON/OFF | Command, readback; mất phản hồi → UNKNOWN và FAULT |
| 12. HAND bổ sung/đảo cực | Cập nhật một byte, hai HAND không ON logic đồng thời; active-low được kiểm tra |
| 13. HOLD | Cancel worker, giữ HOLD, không resume; ACK không nhả HOLD |
| 14. ALARM | Chặn tại preflight và khi đang MOVL |
| 15. Mất TCP | UNKNOWN telemetry; lệnh mất phản hồi không được gửi lại |
| 16. START nhiều lần | Duplicate request_id, busy, stale revision và state khác IDLE bị chặn |
| 17. Restart giữa cycle | Journal nonterminal/pending → FAULT, giữ pending, không phát lại lệnh |
| 18. Sau FAULT | Không START cho đến ACK; unknown cần xác nhận đã kiểm tra |
| 19. Import độc lập | AST/path checks và subprocess relocation; chặn truy cập ứng dụng tại vị trí gốc |
| 20. Assets độc lập | SHA-256 model/NPZ, resource root nội bộ, full MOCK sau relocation |

Các test bổ sung: hai process không được giữ cùng journal, lease một HMI, Host/Origin/Content-Type, kiểm tra tốc độ/tọa độ đầu vào, lưu cấu hình theo mode, target tối thiểu 50 mm, FULL REAL không thể được mở chỉ bằng cờ nghiệm thu.

`pip check` báo không có dependency hỏng trong `.venv` đã cấp. Các lỗi dự kiến do fault injection được ghi trong test report, không phải thử lỗi trên robot.

Server bàn giao đã được mở bằng `app.py --mock` tại http://127.0.0.1:8010. GET trạng thái xác nhận MOCK/IDLE, robot và camera chưa kết nối. Khởi chạy process thứ hai bị OS lock từ chối; kết quả ở [runtime_smoke.json](runtime_smoke.json). 125 tệp nguồn/tài nguyên được đối chiếu hash, không có thay đổi; xem [source_verification.json](source_verification.json).

## Giới hạn bằng chứng

Chưa kết nối hoặc thử chuyển động robot/camera thật. MOCK tạo detection mô phỏng và unit test detector dùng object giả. Sau khi cấp dependency REAL, đã nạp best.pt bằng Ultralytics/PyTorch và chạy suy luận một ảnh đen ở resolution calibration (0 detection); xem real_preflight.json. Đã load và tính transform bằng NPZ thật đã sao chép, nhưng chưa xác nhận độ chính xác nhận diện hoặc tọa độ vật lý.

Preflight REAL: MVS SDK 0x04060168 khả dụng, chưa liệt kê được camera; TCP 192.168.255.1:80 timeout trước khi gửi lệnh NX100. HMI REAL được mở riêng ở http://127.0.0.1:8011, không tự kết nối hoặc tạo chuyển động khi khởi động.

Chưa thử START/RJDIR/RJSEQ/IOREAD trên controller cụ thể; chưa xác minh HAND mapping, hành trình/tốc độ MOVEUNTI, TOOL/posture hoặc đường đi với RZ=0°. Không xác nhận đã hút chắc vật.

Không tìm thấy bản export moveunti.jbi. Không tạo hoặc sửa JOB/ladder. REAL FULL CYCLE giữ khóa trước chuyển động vì thiếu adapter chứng minh nguyên nhân dừng. Các giai đoạn REAL chỉ được mở theo [checklist](REAL_DEPLOYMENT_CHECKLIST.md).

## Cách tái lập

```powershell
.\.venv\Scripts\python.exe -m tools.run_tests
.\.venv\Scripts\python.exe -m tools.browser_smoke
.\.venv\Scripts\python.exe -m pip check
```

Test fault dùng dwell ngắn để giảm thời gian, có test riêng giữ nguyên 10 frame/2 giây production. Journal tạm của test không nhập vào runtime của ứng dụng.
