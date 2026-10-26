# YASKAWA NX100 — AUTO PICK V1

Ứng dụng PC độc lập cho UP50N/NX100: FastAPI, HMI tiếng Việt, HIKROBOT MVS, YOLO, Eye-to-Hand và cycle một vật. Mặc định REAL. Khởi động không kết nối phần cứng và không gửi lệnh robot.

Theo lựa chọn của người vận hành ngày 24/10/2026, tiếp tục dùng nguyên `eye_to_hand.npz` hiện có, kể cả trạng thái `needs_review`. Residual quality chỉ là cảnh báo hiển thị, không chặn kết nối camera hoặc transform tọa độ. Không sửa dữ liệu NPZ, thuật toán ray/plane hoặc offset +280/+215. Điều này không biến kết quả residual thành đạt.

## Khởi chạy REAL

```powershell
python app.py
```

Mở `app.py` và nhấn Run, hoặc chạy `python app.py`. App tự dùng Python trong `.venv` của project để có đủ thư viện REAL. Không cần file CMD/BAT/PowerShell để khởi chạy. Ứng dụng chạy REAL tại **http://127.0.0.1:8011** và tự mở tab Microsoft Edge sau khi server sẵn sàng. Nếu server REAL đã chạy, lần mở tiếp theo đưa Edge vào giao diện hiện có; không khởi tạo process server thứ hai.

Chọn NHẬN QUYỀN HMI -> CONNECT SYSTEM để kết nối phần cứng. Khởi động app không tự gửi lệnh chuyển động/vacuum. `--real` vẫn được chấp nhận để tương thích script cũ; không còn tùy chọn `--mock`. `--no-browser` dùng khi cần chạy server mà không mở Edge. Có thể đổi cổng bằng `--port`.

## Cài đặt ở máy hoặc vị trí khác

### Chạy REAL trên máy hiện tại

YOLO/PyTorch và các dependency REAL đã được chép vật lý vào `.venv` riêng. Đã nạp `models/best.pt`, chạy suy luận một ảnh đen đúng resolution calibration, và kiểm tra MVS SDK khả dụng. Đây không phải kiểm thử nhận diện vật thật hoặc chuyển động robot.

```powershell
.\.venv\Scripts\python.exe app.py --real --port 8011
```

HMI REAL: **http://127.0.0.1:8011**. Cổng mặc định là 8011; không thay đổi robot IP/port hoặc camera IP. PC cần nối LAN với robot và camera qua switch. Chọn NHẬN QUYỀN HMI → CONNECT SYSTEM để kết nối phần cứng thật. Mở server không tự gửi lệnh chuyển động.

Kết quả preflight ở `docs/real_preflight.json`: SDK có sẵn, nhưng tại thời điểm kiểm tra chưa liệt kê được camera và kết nối TCP robot bị timeout (`docs/real_robot_readonly.json`).

Copy toàn bộ thư mục, tạo lại `.venv` vì môi trường Python Windows không có tính di động:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe app.py
```

`requirements.txt` là các dải phiên bản được hỗ trợ; `requirements-lock.txt` ghi chính xác các thư viện đã dùng để kiểm thử. `.venv` hiện tại được cấp thư viện bằng bản sao vật lý các distribution đã cài trên máy; không có `.pth`, symlink, import hoặc đường dẫn runtime tới môi trường cũ. Danh sách phiên bản nằm trong lock file.

Trên máy mới, REAL cần cài thêm `requirements-real.txt` và HIKROBOT MVS SDK Windows cùng Python wrapper của hãng. `requirements-real-lock.txt` ghi phiên bản đã cấp trên máy hiện tại; các wheel CUDA cần nguồn phân phối tương ứng. `vision.sdk_root` chỉ được dùng cho SDK hệ thống, không được trỏ vào dự án cũ. Camera được chọn bằng đúng IP `192.168.255.3`, không tự chọn thiết bị đầu tiên.

## Luồng START hiện tại

Thứ tự gắp theo vòng ID tăng dần: 1 → 2 → 3 → 4 → 1. ID nhỏ xuất hiện lại
không chen trước các ID lớn hơn đang nhìn thấy. ID không còn thấy được bỏ qua;
nếu chỉ có một ID thì vẫn gắp tiếp ID đó. Vẫn kiểm tra frame mới và độ ổn định.
ID đã gắp lưu cùng giao dịch tăng bộ đếm sau H2OFF, không đổi nếu H2OFF chưa
hoàn thành hoặc ghi bộ đếm lỗi;
khởi động lại giữ thứ tự nhưng không tự chạy robot.

Ngay sau tính Z thả, camera bắt đầu tích lũy độ ổn định cho ID gắp tiếp theo
trong lúc DROP/nhả/nâng chạy. Sau nâng Z+200, bắt buộc lấy frame mới để xác nhận
ID/instance/XY và độ tin cậy. Nếu khớp, dùng XY từ frame mới và tận dụng các
frame đã tích lũy để bớt chờ; bị che, uncertain, đổi vị trí/ID hoặc gián đoạn ảnh
thì chờ ổn định lại. Không giảm yêu cầu 5 frame/1 giây. HOLD/lỗi/restart xóa
phần chuẩn bị. Không kết luận hết ván từ ảnh trong lúc tay có thể che camera.

HMI hiển thị áp suất số IN2=20051 và IN3=20052 theo ON/OFF/UNKNOWN, đọc từ bit1/bit2
của cùng byte IOREAD 20050,8 với laser IN1. Đây là tiếp điểm số, không phải giá trị kPa;
không dùng trạng thái OUTPUT relay thay cho cảm biến áp suất.

Thông số mặc định: Plane Z=0, Z_safe=500, MOVL=80 mm/s, RX=180, RY=0, RZ=90. START lấy XY của ván ổn định -> một MOVL đến (X, Y, Z_safe) -> xác nhận RSTATS/RPOSC đã đến đích -> START MOVEUNTI -> theo dõi laser và RUNNING -> START H2ON một lần -> xác nhận H2ON kết thúc -> JOB DROP hiện có -> phần DROP HEIGHT CONTROL bên dưới.

Theo tiêu chí người vận hành yêu cầu, workflow.z_completion=laser_on_and_stopped: cần laser ON và RUNNING OFF đồng thời đủ settle_samples (3 mẫu), JOB hiện tại là MOVEUNTI, XY và orientation không đổi ngoài dung sai. Timeout chờ JOB 60 giây. Ngay trước H2ON, đọc lại trạng thái dừng, JOB và laser; điều kiện thay đổi/mất dữ liệu -> FAULT, không H2ON. Đây là tiêu chí quan sát được người vận hành chọn; không ghi nhận như tín hiệu phần cứng chứng minh nguyên nhân dừng.

Các khóa tĩnh TOOL/posture và cờ nghiệm thu MOVL đã bỏ theo xác nhận trước của người vận hành. Giữ kiểm tra live SERVO/REMOTE/PLAY, TEACH/ALARM/ERROR/HOLD/RUNNING, workspace và metadata MOVL không thay đổi. Laser phải OFF trước khi bắt đầu tìm Z. Mất phản hồi lệnh không retry; HOLD/restart không tự resume. ACK để về IDLE sau mỗi chu trình. Đầu hút ON không xác nhận áp suất.

Offset +280/+215 vẫn áp dụng một lần. Giữ 10 frame mới/2 giây, dung sai ổn định 3 mm, cho phép các chu trình liên tiếp tại cùng XY để gắp ván xếp chồng. Workflow end_after_moveunti_start=true chỉ còn là nhánh bàn giao cũ được kiểm thử hồi quy.

## DROP HEIGHT CONTROL

Sau H2ON, PC đọc P009 (DROP SAFE), lấy XY/RX/RY/RZ, hệ tọa độ, posture và tool từ P009. Chỉ thay Z bằng Z_drop=330+stacked_count*board_thickness_mm rồi ghi P010 và đọc lại xác minh trước START DROP. Người vận hành tự sửa JOB DROP để MOVL tới P010; PC không gửi MOVL hạ Z. Chờ DROP dừng đúng đích P010 -> H2OFF -> tự tăng đếm -> MOVL nâng Z thêm 200 mm -> lượt gắp tiếp theo. P009 phải là Cartesian BASE và không bị ghi đổi.

START FULL CYCLE tự gắp liên tục: sau bước nâng Z+200, lấy ảnh mới và tính lại XY cho tấm kế tiếp, mỗi tấm có cycle ID riêng chống tăng đếm trùng. Không phát hiện ván liên tục 2 giây trên các frame mới thì dừng bình thường tại COMPLETE, hiển thị lý do hết ván. Không coi lỗi/mất ảnh camera là hết ván; lỗi hoặc HOLD dừng vòng lặp, restart không tự tiếp tục. Các chế độ chạy từng giai đoạn vẫn chỉ chạy một lần.

Mặc định chiều dày 12 mm, count=0; ba tấm đầu lần lượt 330/342/354 mm. HMI cho lưu chiều dày và RESET STACK có xác nhận khi cycle không hoạt động. Bộ đếm lưu tại data/real/drop_stack.json, chống tăng trùng theo cycle ID; restart không tự gửi H2OFF hoặc tăng đếm. Xem [chi tiết và phục hồi](docs/DROP_HEIGHT_CONTROL.md).

## Nút NHẢ HOLD

Nút NHẢ HOLD gửi HOLD 0 (HW0483202, 3.2.2) sau hộp thoại xác nhận của người vận hành. Nhả HOLD có thể cho phép chuyển động đang treo tiếp tục. Cần kết nối, giữ quyền HMI, app IDLE, không worker/lệnh chưa xác định, REMOTE/PLAY ON, TEACH/RUNNING/ALARM/ERROR OFF. Chỉ nhả command HOLD; không nhả HOLD từ pendant hoặc tín hiệu ngoài. Nếu app đang HOLD/FAULT, kiểm tra và ACK về IDLE trước. Mất phản hồi -> FAULT/UNKNOWN, không retry, không tự nhả HOLD khi khởi động hoặc ACK.

POST /api/cycle/release-hold yêu cầu lease, revision, request_id duy nhất và confirmed=true. Backend kiểm tra RSTATS mới trước gửi, ghi journal trước lệnh và đọc lại command HOLD sau phản hồi. Không gửi START, MOVL, SVON hay RESET kèm thao tác này.

## Cấu trúc

```text
app.py, settings.py, config.json
robot/       protocol, controller, cartesian, status, io, job_control, vacuum, mock
vision/      camera, detector, calibration, tracker, stability, pipeline
workflow/    cycle, state_machine, safety_checks
models/      best.pt
calibration/ eye_to_hand.npz, camera_intrinsic_2.npz
templates/   index.html
static/      app.js, style.css
tests/       cycle, vision, protocol, API, tracker, independence
tools/       run_tests, browser_smoke
data/mock/, data/real/      journal và cấu hình người vận hành riêng
logs/mock/, logs/real/      log riêng
jobs/        tài liệu đối chiếu; không có JOB giả
docs/        audit, manual, checklist, mapping, báo cáo và ảnh HMI
```

## API và quyền điều khiển

GET `/api/state`, `/api/preview.jpg`, `/api/laser/status` cung cấp trạng thái và hình ảnh. POST `/api/control/claim` nhận lease 30 giây, được gia hạn khi phiên đó đọc trạng thái. Cookie HttpOnly/SameSite=Strict giữ quyền cho một phiên HMI.

POST `/api/system/connect`, `/api/cycle/start`, `/api/cycle/hold`, `/api/cycle/acknowledge`, `/api/vacuum/1`, `/api/vacuum/2`, `/api/config` cần JSON, cookie và `request_id` duy nhất. Lệnh cần `revision` hiện hành; HOLD không bị chặn bởi revision cũ. START có `stage`: `full_cycle`, `xy_only`, `moveunti_only`, `vacuum_only`. READ ONLY tương ứng CONNECT và telemetry, không START.

Vacuum có `on: true/false`; ACK có `inspected: true` sau khi đã kiểm tra trạng thái chưa xác định; config có `settings: {...}`. HMI gửi các trường này tự động. Không retry POST khi mất phản hồi; đọc trạng thái và kiểm tra robot.

Mặc định server chỉ bind localhost. Nếu cần LAN: cấu hình `host`, `allowed_hosts`, `allowed_clients` bằng IP cụ thể và đặt biến môi trường `NX100_HMI_TOKEN` tối thiểu 24 ký tự trước khi chạy. Nhập mã khi nhận quyền HMI. Không dùng wildcard hoặc mở cổng ra Internet. Với LAN không tin cậy cần HTTPS reverse proxy; token qua HTTP không được mã hóa.

## Kiểm thử và tài liệu

```powershell
.\.venv\Scripts\python.exe -m tools.run_tests
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m tools.browser_smoke
```

Browser smoke dùng Microsoft Edge đã cài, chạy server MOCK tạm với journal tạm, tự đóng khi xong. Xem [TEST_REPORT](docs/TEST_REPORT.md), [IO_MAPPING](docs/IO_MAPPING.md), [REAL checklist](docs/REAL_DEPLOYMENT_CHECKLIST.md), [audit và nguồn sao chép](docs/AUDIT_REPORT.md).
