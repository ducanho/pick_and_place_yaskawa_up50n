# TÀI LIỆU KỸ THUẬT TOÀN BỘ HỆ THỐNG NX100

Phạm vi: phân tích tĩnh 6 project trong workspace. Ngày lập: 26/10/2026 (Asia/Bangkok).  
Chế độ: DOCUMENTATION ONLY. Không chạy/import ứng dụng, không chạy test, không cài package, không kết nối robot/camera/I/O. File đầu ra duy nhất: NX100_SYSTEM_COMPLETE_TECHNICAL_DOCUMENTATION.md.

## Mục lục

1. [Phạm vi và phương pháp](#1-phạm-vi-và-phương-pháp)
2. [Kết luận kỹ thuật quan trọng](#2-kết-luận-kỹ-thuật-quan-trọng)
3. [Kiểm kê và so sánh sáu project](#3-kiểm-kê-và-so-sánh-sáu-project)
4. [Kiến trúc và kết nối](#4-kiến-trúc-và-kết-nối)
5. [Workflow thực tế](#5-workflow-thực-tế)
6. [Toán học và calibration](#6-toán-học-và-calibration)
7. [Giao thức NX100 và I/O](#7-giao-thức-nx100-và-io)
8. [Web UI và API](#8-web-ui-và-api)
9. [State machine và đồng bộ](#9-state-machine-và-đồng-bộ)
10. [Hợp đồng hàm quan trọng](#10-hợp-đồng-hàm-quan-trọng)
11. [Phần cứng và triển khai](#11-phần-cứng-và-triển-khai)
12. [Kiểm thử và giới hạn xác minh](#12-kiểm-thử-và-giới-hạn-xác-minh)
13. [Rủi ro và cải tiến](#13-rủi-ro-và-cải-tiến)
14. [Mức hoàn thiện và tích hợp](#14-mức-hoàn-thiện-và-tích-hợp)
15. [Bản đồ mã nguồn](#15-bản-đồ-mã-nguồn)
16. [Kiểm kê tài nguyên và test](#16-kiểm-kê-tài-nguyên-và-test)
17. [Cấu hình, thuật ngữ và bảo toàn](#17-cấu-hình-thuật-ngữ-và-bảo-toàn)

## 1. Phạm vi và phương pháp

### 1.1 Nhãn bằng chứng

| Nhãn | Ý nghĩa |
|---|---|
| VERIFIED | Có bằng chứng trực tiếp trong source/config/test/metadata. Không đồng nghĩa đã kiểm thử phần cứng. |
| INFERRED | Suy luận từ đường gọi và điều kiện; chưa có phép đo độc lập. |
| UNKNOWN | Không đủ dữ liệu. |
| RISK | Có thể ảnh hưởng vận hành, dữ liệu hoặc an toàn. |
| REFERENCE ONLY | Công thức/thiết kế tham khảo chưa có implementation tương ứng được tìm thấy. |
| HISTORICAL EVIDENCE | Log/báo cáo/snapshot đã có trước phiên phân tích; không phải thử nghiệm mới. |

Mọi đường dẫn tương đối với workspace C:\Data\TCP - YASKAWA. Dẫn chứng path:line chỉ dòng tại thời điểm đọc. Trong các bảng dùng đường dẫn rút gọn workflow/, robot/, vision/ mà không ghi project, mặc định thuộc nx100_full_cycle_v1.

Nguồn quyết định là mã hiện tại và cấu hình mà mã thực sự nạp. README, checklist, TEST_REPORT có nhiều lớp lịch sử; không dùng lời khẳng định cũ thay hành vi source mới. Không sao chép giá trị token/mật khẩu; chỉ ghi tên biến môi trường.

### 1.2 Thực hiện và giới hạn

Đã kiểm kê cả sáu cây gồm file ẩn; tìm AGENTS.md không thấy trong các project. Đọc source Python/JavaScript/HTML/CSS, JSON, requirements, README, test, dữ liệu và báo cáo. Đọc ZIP/NPY bằng .NET ở chế độ đọc để xem calibration; đọc danh sách thành phần và chuỗi metadata checkpoint PyTorch, không unpickle/nạp model. Log/manual text lớn được đọc/tìm kiếm tĩnh. Không đánh đồng kết quả lịch sử với trạng thái thiết bị hiện nay.

Không có file JBI trong sáu project. nx100_full_cycle_v1/jobs chỉ có README; vì thế không xác minh được chương trình INFORM trên controller. Các đường dẫn calibration ngoài sáu cây chỉ được ghi nhận là dependency, không mở/chạy. Các thư mục khác ở workspace chỉ tham gia kiểm kê/bảo toàn, không tính là project thứ bảy.

Ảnh/PDF được ghi nhận đường dẫn, kích thước, hash; không khẳng định đã thẩm định tất cả trang PDF hoặc nội dung ảnh. Các bản text manual trong docs giúp tra thuật ngữ; command được hỗ trợ vẫn căn cứ validator thực tế.

Trạng thái ban đầu được ghi bằng thao tác đọc trước khi ghi Markdown. Inventory, dữ liệu phân tích và hash giữ trong bộ nhớ công cụ; không tạo script/cache/log/tệp tạm. Đối chiếu cuối tại mục 17. Đọc file có thể chịu chính sách access-time của hệ điều hành; kiểm tra bảo toàn tập trung nội dung, tên, kích thước, last-write và Git, không tuyên bố chứng minh mọi metadata hệ thống như access-time/ACL.

## 2. Kết luận kỹ thuật quan trọng

Đây là sáu ứng dụng/thư viện độc lập, không phải sáu dịch vụ đã tích hợp. Full-cycle có điều phối rộng nhất; tracking có policy target đầy đủ nhất; web-control có HMI Cartesian phong phú; snapshot phục vụ đổi cáp thủ công; variables chuyên đọc/ghi biến; remote-control là nguồn transport/object.

| Mã | Nhãn | Phát hiện | Bằng chứng |
|---|---|---|---|
| F01 | VERIFIED / RISK | Eye-to-Hand có quality_status=needs_review, 22/22 outlier; RMS tịnh tiến 63,9673 mm, RMS quay 16,8121°, RMS reprojection 184,3329 px. Chưa chứng minh độ chính xác tọa độ. | calibration/eye_to_hand.npz::quality_status, diagnostics_json, report_json |
| F02 | VERIFIED / RISK | Load được calibration không có nghĩa đạt quality. needs_review không chặn convert/START; app tracking/snapshot có accepted_by_operator=True chỉ từ calibration khác None. | vision/calibration.py:17; vision/pipeline.py:130; nx100_yolo_auto_tracking/app.py:106,170; snapshot app.py:110,176 |
| F03 | VERIFIED / RISK | z_completion=laser_on_and_stopped làm real_gate return trước commissioning/hash/min-Z/max-descent và chặn REAL của nhánh cũ. Các cờ commissioning=false không khóa motion ở nhánh hiện tại. | workflow/safety_checks.py:42-78; config.json:19 |
| F04 | VERIFIED / RISK | Laser ON + RUNNING OFF đủ 3 mẫu và đúng JOB được dùng cho completion; không chứng minh nguyên nhân dừng, không bắt buộc Z đã giảm/running từng ON, không kiểm min-Z/max-descent ở nhánh này. | workflow/cycle.py:326-354 |
| F05 | VERIFIED / RISK | JSON mặc định MOVL=80 mm/s, nhưng operator_settings REAL lưu 350 mm/s và nạp đè. Validator cho tới 500. Instance mới từ dữ liệu hiện tại dùng 350 nếu không đổi HMI. | config.json:10; data/real/operator_settings.json:1; workflow/cycle.py:29-32; settings.py:9-10 |
| F06 | VERIFIED / RISK | IN2/IN3 được đọc/hiển thị nhưng không phải pressure guard trước nâng, không theo dõi mất vacuum liên tục. | robot/controller.py:129-135; workflow/cycle.py:422-433 |
| F07 | VERIFIED / RISK | Sau H2OFF code tự đếm dù board_release_confirmed=False; JOB completed không chứng minh vật đã nhả. | workflow/drop.py:185-193 |
| F08 | VERIFIED / UNKNOWN | Không có export MOVEUNTI/DROP/HAND; hướng/tốc độ/hành trình search và lift/place nội bộ JOB chưa xác minh. | jobs/README.md:5; inventory |
| F09 | VERIFIED / RISK | Một MOVL đồng thời XYZ tới Z_safe, không lift riêng trước XY. State MOVE_TO_SAFE trong danh sách không chứng minh có bước lift đang chạy. | workflow/cycle.py:386-408 |
| F10 | VERIFIED / RISK | Snapshot/tracking bind 0.0.0.0; Host/Origin/custom header không xác thực người dùng. File lock từng project không loại trừ project khác/PC khác. | snapshot app.py:133-151,262; tracking app.py:127-145,253 |
| F11 | VERIFIED / RISK | Tracking reset stability nếu frame ID không +1; MVS ID tăng theo delta SDK. Bỏ frame do inference chậm có thể khiến không đạt 10 frame. | tracking vision/stability.py:35-37; vision/camera.py:175-180 |
| F12 | VERIFIED / RISK | Hồ sơ inference ảnh đen 11,64 s lớn hơn frame-age 0,5–1 s. Cần đo latency thực tế; không suy thành FPS production từ một phép thử lịch sử. | docs/real_preflight.json:8; tracking config.json:9; full config.json:41 |

INFERRED: nx100_full_cycle_v1 phù hợp nhất làm nền hoàn thiện pick-and-place vì đã có journal, lease, orchestration JOB, P010 và stack. Kết luận này là đánh giá source, không phải chứng nhận đủ điều kiện chạy cell.

## 3. Kiểm kê và so sánh sáu project

### 3.1 Số liệu và entry point

Source là .py/.js/.html/.css, gồm test nhưng không gồm môi trường/cache. Tài nguyên gồm dữ liệu, log, model và license ngoài cache.

| Project | File riêng/tài nguyên | Source đọc | Mục tiêu / entry point |
|---|---:|---:|---|
| nx100_camera_snapshot_move | 35 | 23 | Camera snapshot → đổi cáp → manual MOVL; app.py:239 main |
| nx100_full_cycle_v1 | 107 | 49 | Camera → laser → HAND → DROP/stack/repeat; app.py:227 main |
| nx100_variables_web | 6 | 6 | Dashboard biến và latency; app.py:339 |
| nx100_web_control | 26 | 18 | HMI Cartesian/live camera click; app.py:221 |
| nx100_yolo_auto_tracking | 32 | 21 | Target ổn định → automatic MOVL; app.py:230 |
| nx100-remote-control-master | 38 | 32 | Library TCP/object và ví dụ; package nằm trong thư mục lồng cùng tên |
| **Tổng** | **244** | **149** | **6 project** |

Corpus ban đầu nạp 202 file text; log/manual lớn được đọc riêng. Có 130 file Python. Chỉ mục phát hiện 730 khai báo hàm/method và 110 class trong 98 file Python ngoài tests/ và tools/. Đây là số khai báo có tính bản sao giữa project, không phải 840 thuật toán độc lập. Hợp đồng semantic chọn lọc tại mục 10; chỉ mục toàn bộ tại mục 15. Có 242 khai báo test_*; số test case thực thi có thể khác do parametrization/discovery.

Số file vật lý gồm môi trường/cache: snapshot 2.656, full-cycle 22.338, variables 9, web-control 44, tracking 3.062, remote-control 66. Các file .venv không được tính thành mã riêng cần hợp nhất.

### 3.2 So sánh chức năng

| Project | Chức năng có thật | Điểm mạnh | Giới hạn | Tái sử dụng |
|---|---|---|---|---|
| Snapshot | Camera/YOLO/calibration; saved batch/fingerprint; manual send; completion/fault/HOLD release | Lưu intent trước MOVE; đổi cáp và restart vẫn giữ snapshot; không tự gửi tiếp | Không stability/frame-age gate khi capture; scene có thể đổi khi thay cáp; không vacuum/Z-search | SnapshotMove cho chế độ thao tác riêng |
| Full-cycle | StableTarget/prefetch; MOVL; MOVEUNTI/H2ON; P009→P010/readback; DROP/H2OFF; stack/Z+200/repeat | Điều phối rộng nhất; journal/revision/request-ID; lease/file lock | Thiếu pressure/release guard; JOB export; calibration và real_gate rủi ro | Cycle/DropWorkflow/StackStore/Journal/protocol |
| Variables | B/I/D/R/P; F alias R; S từ chối; polling/metrics/chart/readback | Standard library; serialization I/O; ghi chưa rõ phải đọc lại | Không gate RUNNING trước ghi biến; thiếu owner toàn robot; read-before-write không khóa host ngoài | Variable parser, normalization, diagnostic UI |
| Web-control | Flags/Cartesian/joint read; MOVL/MOVJ Cartesian; Enter/debounce slider; camera click; logs | HMI điều khiển tay, preflight và completion hai mẫu | External camera/calibration path; pulse move disabled; UI range không phải safety limit; auto-send khi chỉnh slider | Axes UI, NX100Controller |
| Tracking | 10 frame +2 s; >50 mm; BoardTracker; freeze/version; STOP→HOME | Stale/config/occlusion/instance guards đầy đủ nhất | Không pick/vacuum/Z-search; không journal intent bền; frame continuity nghiêm; không có tests riêng trong cây | Eligibility, Target bất biến, version/calibration binding |
| Remote-control | Protocol validated; command/object; callback; pygame | Nguồn transport/object | API công khai rộng hơn validator; RJDIR wrapper bị từ chối; gripper invalid; thiếu cycle owner | Chọn lọc transport/object, giữ license |

Nền điều khiển tay/HMI Cartesian tốt nhất theo phạm vi chức năng là web-control. Nền điều phối full-cycle tốt nhất là full-cycle. Camera pipeline dễ tích hợp độc lập nhất là full-cycle vì chọn đúng GigE IP và adapter nội bộ; chưa có benchmark để xếp hạng chất lượng ảnh/FPS. Tracking policy đầy đủ nhất thuộc auto-tracking. Giao diện chu trình đầy đủ nhất là full-cycle; không có đo usability thực tế.

### 3.3 Trùng lặp và xung đột

robot/status.py, robot/cartesian.py, vision/camera.py, vision/tracker.py của snapshot/tracking/full-cycle có nhiều bản sao; hash ở mục 17 phân biệt giống byte và gần giống. vision/calibration.py snapshot/full-cycle giống byte, tracking khác byte nhỏ. Không đồng nhất implementation chỉ theo tên.

nx100_web_control/robot/protocol.py:5-18 thêm đường dẫn sibling library vào sys.path rồi import transport/object. Full-cycle dùng module trong root riêng; không cần sibling này. Các project dùng tên app/robot/vision chung nên có nguy cơ va chạm sys.modules nếu import chung interpreter. Nhiều main dùng cổng 8000; full-cycle 8011, variables 8010.

Không hợp nhất policy bằng cách copy nguyên: snapshot cố ý bỏ camera-age gate cho tọa độ đã lưu; tracking khóa completed site và cần >50 mm; full-cycle cần gắp chồng cùng XY và xoay vòng ID. Completed-site suppression của tracking sẽ ngăn full-cycle gắp chồng. Full StableTarget đo XY, tracking Stability đo XYZ. Web-control không offset, ba project còn lại bù +280/+215 mm; tích hợp có nguy cơ cộng hai lần.

## 4. Kiến trúc và kết nối

### 4.1 Sơ đồ

Nét liền là đường dữ liệu/điều khiển thấy trong source; nét đứt là quan hệ phần cứng được mô tả nhưng còn phải xác minh wiring.

~~~mermaid
flowchart LR
  HMI["Web frontend"] -->|"HTTP JSON / JPEG"| API["Backend"]
  API --> OWNER["Cycle / Automation / SnapshotMove"]
  OWNER <--> JOURNAL["Journal, state, event log"]
  CAM["HIKROBOT GigE"] --> SDK["MVS wrapper / DLL"]
  SDK --> VISION["Capture thread / NumPy BGR"]
  VISION --> YOLO["Ultralytics YOLO detection"]
  CAL["K / distortion / T_base_camera"] --> TRANS["Ray intersect BASE Z plane"]
  YOLO --> TRANS
  TRANS --> TRACK["BoardTracker / stability / selection"]
  TRACK --> OWNER
  OWNER --> TCP["ASCII NX client"]
  TCP <-->|"TCP 192.168.255.1:80"| NX["NX100"]
  NX --> JOB["Existing INFORM JOB"]
  LASER["Laser digital"] -.->|"20050 bit 0 / IN1"| NX
  PRESSURE["Digital pressure IN2 / IN3"] -.-> NX
  JOB -.-> RELAY["Relay"]
  RELAY -.-> VALVE["Solenoid valve"]
  VALVE -.-> EOAT["Vacuum EOAT"]
~~~

UNKNOWN: wiring/van/relay cụ thể, logic pneumatic, safety PLC, stop category, quan hệ IN2/IN3 với vật bám thật. Không có driver áp suất analog.

### 4.2 Bảng kết nối

| Kết nối | Protocol/dữ liệu | Địa chỉ, nhịp, timeout | Xác nhận/lỗi |
|---|---|---|---|
| Browser→full-cycle | HTTP JSON, JPEG | 127.0.0.1:8011; poll 500 ms | Cookie lease, revision/request-ID; HTTP errors; không control retry |
| Browser→snapshot/tracking | HTTP JSON/JPEG | Port 8000, bind 0.0.0.0; poll 400 ms | Host/Origin/header; batch/config guard tùy workflow |
| Browser→web-control | HTTP JSON; JPEG base64 | Loopback 8000; status 1.000 ms, camera poll 250 ms | Fetch abort 45 s chỉ hủy chờ browser, không chứng minh robot hủy lệnh |
| Browser→variables | HTTP JSON/assets | Loopback 8010; UI poll 250 ms | Host/Origin/header; 400/409; worker IO riêng |
| PC→NX100 | ASCII/CSV decimal, CR/CRLF qua TCP | 192.168.255.1:80; timeout full 3 s, tracking 2 s, snapshot 5 s | ACK rồi 0000; completion polling; unknown không resend |
| PC→camera | MVS/GigE SDK buffers | Full camera IP 192.168.255.3; các bản khác index; port camera NOT FOUND | GetImageBuffer timeout 300 ms; 10 capture lỗi liên tiếp → disconnect |
| Capture→inference | NumPy BGR/frame_id/monotonic stamp | Worker tracking wait .02 s, full wait .1 s | Bỏ cùng frame ID; stale/lỗi invalid; không auto reconnect camera |
| Backend→filesystem | JSON/fsync/atomic replace; rotating logs | Journal intent trước control; không realtime | Restart không replay; lỗi lưu state không được coi là hoàn tất |
| Inputs→backend | IOREAD byte decimal→bit | 20050 byte chứa bit 0/1/2; loop motion poll .1 s, background telemetry 1 s | Đọc lỗi→UNKNOWN |
| Output→backend | IOREAD 30050,8 | Bits 0/1 tương ứng 30050/30051 | Contact state không chứng minh van/áp suất |

Các wait .1/.02/.05 s là khoảng đợi giữa vòng, không phải tần số cứng; inference và nhiều TCP transaction cộng thêm. Full telemetry age >2 s bị che thành UNKNOWN; Vision max-frame-age 1 s; raw MVS frame max-age 2 s. Không tìm thấy WebSocket hay asyncio motion queue; chủ yếu sync handler và threading, với middleware/lifespan async.

## 5. Workflow thực tế

### 5.1 Workflow A — startup

Full-cycle app.py:227-253 có thể relaunch bằng .venv/Scripts/python.exe, load config, log, kiểm tra HMI REAL đã tồn tại, create_app(mock=False), mở Edge sau Uvicorn ready. Cycle.__init__: tạo Controller/Vision; đọc NPZ và đối chiếu intrinsic; InstanceLock/Journal/StackStore; nạp operator_settings REAL. Nếu được chạy, startup có thể ghi runtime/log/file lock; vì vậy không import app trong phiên documentation.

Startup không tự nối phần cứng. Người vận hành claim HMI rồi CONNECT SYSTEM. Cycle.connect: robot.connect → telemetry poller → refresh → vision.connect. Controller.connect đọc RSTATS/RPOSC/RPOSJ; không SVON/reset. Vision REAL load model, enumerate, chọn đúng một camera GigE khớp IP. Nếu camera lỗi sau robot connect, không rollback tự động mọi kết nối.

Tracking/snapshot main mặc định REAL do create_app(mock=args.mock), dù factory mặc định mock=True. Lifespan bật robot-monitor và automation/completion worker. Camera/robot nối bằng nút riêng; model load khi camera REAL connect. Calibration load lỗi được giữ trong trạng thái để dashboard vẫn mở.

Web-control tạo controller/VisionService; thử JSON calibration bên ngoài, giữ lỗi nếu thiếu; monitor chỉ IO khi có client. Variables khởi read worker nhưng chỉ đọc sau connect/read/start. Library không có orchestration SYSTEM READY; Testing.py/XboxController.py chứa control/pygame, không được dùng làm smoke an toàn.

Ready motion full: servo=true, remote=true, play=true, teach=false, alarm/error/hold=false, running=false; camera fresh; journal IDLE; lease/revision/request-ID; laser OFF trừ stage vacuum_only. Chưa có physical pressure/safety-PLC guard.

### 5.2 Workflow B — camera và phát hiện

1. MvsCamera tìm Python wrapper của SDK cài máy và DLL runtime, kiểm tra PE architecture/pointer size. Adapter yêu cầu Windows.
2. Enum GigE/USB; full-cycle chọn GigE IP, snapshot/tracking chọn index sau scan.
3. Open exclusive; optimal packet size cho GigE; TriggerMode OFF; StartGrabbing.
4. GetImageBuffer(...,300); kiểm width×height ≤100.000.000; RGB8 Packed; copy buffer, RGB→BGR; FreeImageBuffer trong finally.
5. Stamp time.monotonic sau convert ở PC; không phải exposure timestamp đồng bộ controller.
6. Detector kiểm native resolution; model.predict với confidence config, imgsz=960, device=cpu.
7. bbox xyxy kiểm hữu hạn/biên; tâm trung bình hai góc; class ID dùng tra result.names. Object ID do BoardTracker tạo, khác class ID.
8. Pixel→Base bằng calibration và plane_z_mm. Lỗi object giữ error, không thay bằng XYZ giả.
9. BoardTracker liên kết bbox/class-name; không dùng YOLO.track/ByteTrack.
10. Stability/selection theo project; preview resize sau transform; owner nhận target rồi mới điều khiển robot.

Không tìm thấy lệnh set exposure/gain/Width/Height/ROI trong adapter riêng. Giá trị thực lấy từ camera; imgsz=960 không phải sensor resolution 5472×3648. Không dùng tâm segmentation. Confidence không đại diện sai số định vị.

Tracker giữ ID vắng mặt tối đa 10 s nhưng không xuất detection ẩn thành target. Stability không phải moving average hoặc median.

### 5.3 Ba policy target khác nhau

| Điều kiện | Snapshot | Auto-tracking | Full-cycle |
|---|---|---|---|
| Frame/timing | Lưu ngay detection hợp lệ | ≥10 frame liên tiếp rồi thêm ≥2 s từ frame đạt ngưỡng | ≥5 frame mới, khoảng mẫu đầu-cuối ≥1 s |
| Ổn định | Không gate | XYZ cách anchor ≤3 mm | XY cách từng mẫu cửa sổ ≤3 mm |
| Age | Capture không kiểm age, có test cho chủ ý này | ≤500 ms | ≤1 s |
| Gap | Không dùng | ≤500 ms, frame ID +1 | ≤0,5 s, ID tăng nhưng không cần +1 |
| Khoảng cách trước MOVE | >50 mm theo lịch sử completed | >50 mm global/cùng instance/completed site | Không có gate 50 mm; cho gắp cùng XY |
| Chọn ID | Thấp nhất eligible, từng click SEND | Thấp nhất eligible | ID lớn hơn last-picked trước, rồi wrap |
| Sau move | Chờ click mới | Reset stability, xác nhận ảnh mới | Prefetch trong DROP; sau lift phải frame mới |
| Mất camera | Snapshot đã lưu còn dùng khi đổi cáp | Fault/disarm khi vận hành | Camera lỗi/stale không được che bằng prefetch |

Nguồn: snapshot workflow/snapshot_move.py:114-176,178-247; tracking vision/stability.py:29-63 và automation/target_manager.py:10-36; full vision/stability.py:15-41, workflow/cycle.py:190-233. README full-cycle:69 còn nói 10 frame/2 s, khác config hiện tại 5/1; bảng dùng code/config.

### 5.4 Workflow C — motion và completion

MOVL/MOVJ Ethernet dùng target Cartesian. MOVL selection 0 dùng mm/s; MOVJ dùng %. Đọc RPOSJ pulse không có nghĩa pulse command được hỗ trợ: move_joint của web/snapshot/tracking trả 501. IMOV là incremental motion INFORM trong JOB, không phải command TCP full-cycle.

Web/snapshot/tracking: _move_operation nhận một intent, chờ read đang chạy tối đa timeout, không queue sau MOVE khác. hold_pending/cancel chặn pending move; đọc _status ngay trước send. 0000 chỉ tạo active motion. Monitor cần RUNNING OFF + pose trong tolerance, elapsed ≥0,5 s và hai mẫu đúng; timeout 60 s. Mất mạng/unknown không retry; disconnect không dừng robot.

Full-cycle _move giữ cycle/robot lock cho preflight/send; nhả để polling, chờ stopped+reached 3 mẫu, timeout 120 s. Trong MOVL phải giữ posture/tool/external-axis metadata. Không bắt buộc thấy RUNNING ON nếu motion ngắn. _run_once chỉ gọi bước sau khi _move hoàn tất. HAND/DROP cũng chờ completion, không dựa ACK.

Khóa chỉ bảo vệ process/project/mode, không khóa pendant/PLC/PC khác. RSTATS/RPOSC/IOREAD là nhiều transaction, không phải snapshot nguyên tử. Alarm/HOLD/servo OFF gate hoặc fault. Fault unresolved thử HOLD một lần; không xác nhận physical stop nếu TCP hỏng. Không auto servo/reset/resume.

### 5.5 Workflow D — laser Z search

Cycle._start_moveunti:270 kiểm ready, RJDIR có MOVEUNTI, laser OFF, workspace; lưu intent và START MOVEUNTI. PC không upload/sửa JOB.

HISTORICAL EVIDENCE: docs/TEST_REPORT.md:125 ghi mô tả IMOV P010, V80, PL=0, BF, UNTIL IN#(1)=ON, chưa có export. docs/DROP_HEIGHT_CONTROL.md:5 lại ghi MOVEUNTI không còn dùng P010 sau thay đổi do người vận hành. Không ghép hai mô tả thành một JOB đang chạy đã xác minh.

| Thuộc tính | Kết luận |
|---|---|
| JOB | MOVEUNTI hardcode; có trong danh sách JOB lịch sử |
| IMOV/UNTIL | Có mô tả, thiếu JBI để kiểm syntax/nội dung thực |
| Hướng/vector/hành trình | UNKNOWN; không suy từ mock giảm Z |
| Frame | Tài liệu lịch sử có BF, chưa xác nhận JOB hiện tại |
| Tốc độ | Lịch sử V80; config.job.speed_mm_s=null; tốc độ thực UNKNOWN |
| Nguyên nhân dừng | Không proof signal độc lập; laser ON và running OFF chỉ tương quan |
| Mapping PC | IOREAD 20050,8; bit 0; active_high=true; laser.verified=false |
| Z sau stop | refresh→Controller.pose→RPOSC 0,1; lưu stop_position |
| Timeout | motion.job_timeout=60 s, không phải giới hạn hành trình an toàn |
| Laser không ON | Không đủ settle → FAULT/timeout, thử HOLD khi unresolved |
| Stopping distance/collision | UNKNOWN; cần kiểm cơ khí và đo tại cell |

Nhánh cũ _job:289-324 theo running_seen/laser_edge, XY/orientation, REAL min-Z/max-descent và Z không đi lên; stop_reason_proven chỉ true cho mock nên REAL nhánh này không vào vacuum.

Nhánh hiện tại _wait_laser_and_stopped:326-354 kiểm đúng JOB, laser ON + RUNNING OFF đủ 3 mẫu, XY/orientation trong tolerance và workspace. Không gọi stop_reason_proven, không yêu cầu từng running ON hoặc Z giảm, không min-Z/max-descent riêng. Config chọn nhánh này; real_gate cũng return sớm tương ứng.

### 5.6 Workflow E — vacuum

REAL chọn method=job, H1ON/H1OFF/H2ON/H2OFF; verified=true; outputs 30050/30051; inputs 20051/20052. Network-input start/bits còn null, owned_byte=false, không được suy output address thành write address.

_execute_hand_job:533 kiểm live flags, required_pose/laser tùy caller, lưu intent và START đúng JOB một lần. Chờ RJSEQ đúng tên và running OFF hai mẫu, timeout 10 s; không cần thấy running ON. Refresh sau hoàn thành nhưng không pressure threshold/pressure guard và không bắt buộc output đạt mức mong muốn trong nhánh JOB.

Nhánh network còn tồn tại: validate byte 22010..23280 căn bit 0, hai bit khác, owned_byte, polarity/mode; read-modify-write, readback; complementary đổi bit đối nghịch. Đây là policy bit, không chứng minh loại EOAT.

Chưa triển khai: pressure kPa/bar, dwell đủ chân không, guard trước nâng, mất chân không→dừng, cảm biến release. IN2/IN3 chỉ monitor. Model DPSN1/van/relay, polarity và setpoint vật lý chưa được source chứng minh.

### 5.7 Workflow F — full-cycle hiện tại

~~~mermaid
flowchart TD
  A["Claim HMI / CONNECT"] --> B["START: ready / fresh camera / laser OFF"]
  B --> C["WAIT_TARGET: >=5 frame / >=1 s"]
  C --> D["Freeze XY + Z_safe + orientation"]
  D --> E["One MOVL XYZ"]
  E --> F["Stopped / reached 3 samples"]
  F --> G["START MOVEUNTI"]
  G --> H["Same JOB, laser ON and stopped 3 samples"]
  H --> I["START H2ON / stopped twice"]
  I --> J["SAVEV P009 / replace Z / LOADV P010 / readback"]
  J --> K["START DROP / wait stopped at P010"]
  K --> M["START H2OFF / stopped twice"]
  M --> N["Count once; physical release unconfirmed"]
  N --> O["MOVL Z_drop+200 / wait reached"]
  O --> P["COMPLETE"]
  P --> Q{"Repeat?"}
  Q -->|"yes, require new frame"| C
  Q -->|"no"| R["Wait ACK"]
  C -->|"empty fresh >=2 s and >=5 samples"| S["COMPLETE / no_boards"]
  E -->|"error"| X["FAULT / HOLD request if unresolved"]
  G -->|"error"| X
  K -->|"error"| X
~~~

| Bước tham chiếu | Tình trạng thực |
|---|---|
| Ready | Có flag/journal/lease/camera checks, chưa pressure/safety-PLC proof |
| Camera/YOLO/target/stability | REAL adapter có code; MOCK ảnh/detection tổng hợp |
| Pixel→robot XY | Ray-plane + offset; needs_review vẫn dùng |
| Move XY | Một MOVL XYZ tới Z_safe, không lift tách riêng |
| Laser Z | START JOB + polling; nội dung JOB UNKNOWN |
| Vacuum ON | H2ON, chờ JOB; không chứng minh lực hút |
| Pressure confirmation | NOT IMPLEMENTED làm guard |
| Lift sau pick | Không MOVL lift PC riêng trước DROP; có thể trong DROP, UNKNOWN |
| Place/lower | JOB DROP tới P010; quỹ đạo trong JOB UNKNOWN |
| Vacuum OFF | H2OFF tại pose được kiểm |
| Verify release | Không cảm biến/guard tự động; receipt false |
| Count | Sau H2OFF, atomic/idempotent cycle ID |
| Return/next | Z+200 sau nhả; không HOME tổng quát; repeat-until-empty |
| Manual | Claim/connect/start/ACK/settings/count/reset; JOB người vận hành quản lý |

end_after_moveunti_start=true là nhánh cũ: JOB_DISPATCHED ngay sau ACK START, robot có thể vẫn chạy, không H2ON/DROP; hiện false. xy_only/moveunti_only/vacuum_only không lặp. Stage vacuum_only vẫn cần vision.connected theo start:165; manual vacuum endpoint có điều kiện khác.

### 5.8 Sequence diagram một lượt

~~~mermaid
sequenceDiagram
  participant UI as HMI
  participant C as Cycle
  participant V as Vision
  participant J as Journal/Stack
  participant R as NX100
  UI->>C: start(request_id,revision,stage)
  C->>J: SYSTEM_CHECK / cycle_id
  loop fresh distinct frames
    V-->>C: frame_id / stamp / items
  end
  C->>J: target frozen / intent MOVL
  C->>R: MOVL
  R-->>C: 0000 accepted
  C->>R: poll stopped + reached, 3 samples
  C->>J: intent START MOVEUNTI
  C->>R: START MOVEUNTI
  C->>R: poll same JOB / laser ON / stopped
  C->>R: START H2ON, wait JOB completion
  C->>R: SAVEV 4,9
  C->>J: intent LOADV P010
  C->>R: LOADV 4,10 / SAVEV 4,10 verify
  C->>R: START DROP / wait target
  C->>R: START H2OFF / wait JOB completion
  C->>J: count once, release_confirmed=false
  C->>R: MOVL Z_drop+200 / wait reached
  C->>J: COMPLETE
  UI->>C: poll state
  Note over C,R: No physical pressure or release guard
~~~


## 6. Toán học và calibration

### 6.1 Intrinsic và dữ liệu số có thật

Nguồn VERIFIED: ba bản calibration/eye_to_hand.npz và camera_intrinsic_2.npz trong snapshot/tracking/full có cùng SHA-256 tương ứng (mục 17). Runtime PixelToRobot.__init__ tại full vision/calibration.py:17-44 đọc T_base_camera, K, distortion, image size, report; check rigid transform, đơn vị mm và định nghĩa Camera→robot Base. Không chạy calibration mới.

$$
K=\begin{bmatrix}
4674.729315190615&0&2549.9368878288115\\
0&4693.272833545705&1973.5109939985423\\
0&0&1
\end{bmatrix},\qquad (W,H)=(5472,3648)\ {\rm px}.
$$

$$
(k_1,k_2,p_1,p_2,k_3)=(-0.2532737023,\ 0.2234199981,\ -0.00316510373,\ 0.01094859233,\ 0.06345229704).
$$

fx/fy/cx/cy có đơn vị pixel; distortion không thứ nguyên. Intrinsic report ghi OpenCV pinhole 5 coefficients, 16 ảnh, RMS reprojection 0,6308834689 px; checkerboard inner corners 6×9, square=27 mm. Eye-to-Hand report ghi 22 mẫu, bảng 9×6, square=27 mm; hai layout khác nhau được warning trong metadata, không mặc định là lỗi nhưng cần đối chiếu bảng thật.

Runtime không fit K, không tối ưu distortion; chỉ dùng tài nguyên đã tính. Camera native size khác calibration sẽ bị chặn; không tự scale K hoặc resize ảnh để né gate.

### 6.2 Pixel → camera ray → Base plane

VERIFIED: PixelToRobot.convert(u,v,plane_z), full vision/calibration.py:63-85; snapshot/tracking cùng thuật toán. Pixel đầu vào là ảnh gốc còn distortion.

$$
(x_n,y_n)=\operatorname{undistortPoints}((u,v),K,\mathbf d),\quad
\mathbf q_c=\begin{bmatrix}x_n\\y_n\\1\end{bmatrix}.
$$

Không dùng trực tiếp K inverse trên pixel còn distortion. Khi đã undistort, q_c tương ứng normalized ray. Với T_base_camera=[R,t;0,1]:

$$
\mathbf o_b=\mathbf t,\quad \mathbf d_b=R\mathbf q_c,\quad
\lambda=\frac{Z_{\rm plane}-o_{b,z}}{d_{b,z}}.
$$

$$
\mathbf P_b=\mathbf o_b+\lambda\mathbf d_b,\qquad
\mathbf P_{\rm output}=\mathbf P_b+
\begin{bmatrix}280\\215\\0\end{bmatrix}\ {\rm mm}.
$$

Code chặn input NaN/Inf, pixel ngoài ảnh, |d_b,z|<10^-9, lambda≤0 hoặc kết quả không hữu hạn. Code gán Z=plane_z trước offset. lambda chính là Z camera trong biểu diễn q_c,z=1, không phải khoảng cách Euclidean dọc tia chuẩn hóa đơn vị. Z_plane do người vận hành/config nhập, không do YOLO suy độ sâu và không phải Z tìm bằng laser sau đó.

Quan hệ tổng quát sau undistort:

$$
\mathbf P_c=Z_cK^{-1}[u',v',1]^T,\qquad
\mathbf P_b=T_{base\leftarrow camera}[\mathbf P_c;1].
$$

Đây là cách diễn giải của ray-plane runtime; không có sensor depth Z_c độc lập. Sai Z_plane sẽ đổi XY vì camera ray không vuông góc tuyệt đối mặt phẳng.

Web-control Calibration.pixel_to_base tại vision/calibration.py:73-113 dùng undistortPointsIter, tối đa 50 iteration, epsilon=10^-12; cùng ray-plane nhưng **không cộng +280/+215**. Trả cả camera_mm/base_mm và accuracy_validated=False. Output từ hai họ không thể thay nhau mà không xét offset.

### 6.3 Eye-to-Hand, ma trận và quy ước

T_base_camera đọc từ NPZ, làm tròn chỉ để trình bày:

$$
T_{b\leftarrow c}\approx
\begin{bmatrix}
0.0249632891&-0.9984020258&-0.0506974258&1260.2486271\\
-0.9996650759&-0.0245844001&-0.0080835165&73.6147187\\
0.0068242335&0.0508822372&-0.9986813445&1390.5878775\\
0&0&0&1
\end{bmatrix}.
$$

Translation mm, camera OpenCV +X phải/+Y xuống/+Z trước. Cột R mô tả hướng trục camera trong Base; không giả định trục robot khớp trục ảnh. Runtime kiểm R^T R≈I, det(R)≈1, hàng cuối [0,0,0,1]; đây chỉ là tính hợp lệ rigid, không chứng minh calibration đúng vật lý.

Report NPZ có T_tool_board và hai mảng mẫu T_base_tool_samples/T_camera_board_samples shape (22,4,4). Phương trình ghi trong metadata:

$$
A_iY=XB_i,\qquad
A_i=T_{base\leftarrow tool,i},\
Y=T_{tool\leftarrow board},\
X=T_{base\leftarrow camera},\
B_i=T_{camera\leftarrow board,i}.
$$

Metadata pose_input: euler_order=xyz, convention=intrinsic, góc CSV degree; rotation residual radian. Initializer SVD_AX_XB, optimizer_success=true, nfev=29, rank Jacobian=12, condition≈44,0974. Đây là kết quả được lưu; source giải optimizer/calibrateHandEye không nằm trong sáu project. Không khẳng định đã tái tính hoặc nghiệm thu.

Loss mô tả trong metadata, không triển khai lại trong runtime:

$$
r_i=\begin{bmatrix}
(t(A_iY)-t(XB_i))/s_t\\
\operatorname{Log}(R(XB_i)^TR(A_iY))/s_r
\end{bmatrix},\qquad
C=\tfrac12\sum_j\rho(r_j^2),
$$

với s_t=1 mm, s_r=0,01 rad, loss=linear. Nguồn: eye_to_hand.npz::diagnostics_json.weighting. Optimizer success là hội tụ số, không khắc phục residual lớn.

### 6.4 Đơn vị, Euler và Rodrigues

Runtime gửi Rx/Ry/Rz theo degree trong payload Cartesian, giữ metadata tool/posture/external axes từ RPOSC. Không tìm thấy runtime chuyển Euler→matrix, Rodrigues, forward/inverse kinematics hoặc mm↔m trong các module điều khiển chính; không mặc định degree sequence firmware trùng với metadata của lần calibration.

REFERENCE ONLY, không có hàm tương ứng trong sáu project:

$$
\theta_{\rm rad}=\theta_{\rm deg}\pi/180,\qquad x_{\rm mm}=1000x_{\rm m},
$$

$$
R(\mathbf r)=I+\sin\theta[\mathbf a]_\times+
(1-\cos\theta)[\mathbf a]_\times^2,\quad \mathbf r=\theta\mathbf a.
$$

Không đưa một thứ tự Euler tự chọn vào conversion code. Posture là bitmask 0..63, tool 0..23; không phải Euler angle. BASE frame đặt prefix 0 khi build_move; tool frame chỉ được giữ theo controller, không suy TCP offset từ T_tool_board.

### 6.5 Bounding box và association

VERIFIED: full vision/detector.py:24-35:

$$
u_c=(x_1+x_2)/2,\quad v_c=(y_1+y_2)/2.
$$

Tâm bbox không bảo đảm là tâm khối lượng hoặc điểm hút hợp lệ. Numeric class ID dùng để tra class name; output item giữ name/confidence, tracker gán ID riêng.

VERIFIED: BoardTracker.match_score tại full vision/tracker.py:13-28:

$$
w_a=\max(x_{2a}-x_{1a},1),\quad h_a=\max(y_{2a}-y_{1a},1),
$$

$$
I=\max(0,\min x_2-\max x_1)\max(0,\min y_2-\max y_1),\quad
IoU=\frac I{w_ah_a+w_bh_b-I},
$$

$$
d_{\rm rel}=\frac{\|\mathbf c_a-\mathbf c_b\|_2}
{\max(\sqrt{w_a^2+h_a^2},\sqrt{w_b^2+h_b^2})},\quad
S=IoU+0.2(1-\min(d_{\rm rel},1)).
$$

Chỉ match cùng name; loại nếu tỷ lệ kích thước lớn nhất >2 hoặc IoU<0,1 và d_rel>0,5. Nếu hai candidate tranh cùng track/detection có chênh score <0,05, đánh uncertain. Greedy sort score giảm để gán one-to-one, không Hungarian/Kalman. Detection mới cùng frame sắp u rồi v; cấp số nhỏ nhất chưa reserved. Track hết 10 s mới nhả ID; generation/instance tăng khi track mới. ID tái dùng không được xem là cùng vật.

### 6.6 Stability và selection

VERIFIED tracking vision/stability.py:29-63: kiểm stamp hữu hạn, không tương lai, age≤max_age; frame_id phải mới và liên tiếp. Mỗi instance giữ anchor:

$$
\|\mathbf p_t-\mathbf p_{\rm anchor}\|_2>3\ {\rm mm}
\Longrightarrow reset,\quad
n\ge10,\quad t-t_{n=10}\ge2\ {\rm s}.
$$

Không tính 2 s từ frame đầu; thời gian đủ điều kiện thường lớn hơn 2 s cộng thời gian tích lũy 10 frame. Không average output; dùng XYZ hiện tại làm tròn 3 decimal, Target frozen dataclass.

VERIFIED full vision/stability.py:15-41: một candidate ưu tiên ID theo cursor. Identity=(id,instance). Reset khi identity đổi, gap>0,5 s, stale hoặc:

$$
\exists i:\|\mathbf p_{t,XY}-\mathbf p_{i,XY}\|_2>3\ {\rm mm}.
$$

Lock khi n≥5 và t_last−t_first≥1 s. Giữ cửa sổ bounded đủ dwell; không lọc mean/median. after_id ưu tiên tuple (id≤after_id,id), nên ID cao hơn cursor được chọn trước.

Pseudocode tóm lược đúng hai cách tính:

~~~text
TRACKING:
  reject stale/repeated sample
  if frame jump or timestamp gap: clear records
  for visible valid instance:
    if no anchor or XYZ moved beyond tolerance: reset anchor/count
    count += 1
    when count first reaches 10: confirmed_at = stamp
    ready when stamp - confirmed_at >= 2 seconds

FULL-CYCLE:
  require frame/stamp newer and fresh
  select candidate by rotating ID priority
  reset samples on identity/gap/any XY distance violation
  append current sample
  return latest item when samples >= 5 and dwell >= 1 second
~~~

VERIFIED tracking automation/target_manager.py:10-36:

$$
d_g=\|\mathbf p-\mathbf p_{\rm last}\|_2,\quad
d_o=\|\mathbf p-\mathbf p_{\rm same\ instance}\|_2.
$$

Cần d_g>50 mm và d_o>50 mm khi có lịch sử; target đúng 50 bị chặn. New instance cùng class ở completed site trong ≤50 mm cũng bị chặn. Chọn min object_id trong eligible. Snapshot target_manager tương tự global/own nhưng không completed_sites; _distance cố ý truyền now=target.timestamp,max_age=0 để snapshot đã lưu không hết hạn theo camera age.

### 6.7 Completion, error và stack height

VERIFIED workflow/safety_checks.py:81-83 và controller poll:

$$
\Delta r=((r_c-r_t+180)\bmod360)-180.
$$

Reached khi mọi XYZ có |delta|≤1 mm và góc wrapped ≤0,5°. Full cần 3 stopped samples; web/snapshot/tracking cần 2 sau elapsed≥0,5 s. Pose.verify_unchanged trong robot/cartesian.py:24-30 dùng Decimal: XYZ/góc dung sai 0,05 cho reference trước send, external 0,001; so tool/posture nguyên vẹn. Đây là hai loại check khác nhau.

VERIFIED workflow/drop.py:59-65:

$$
Z_{\rm drop}=Z_0+n\,h,\qquad Z_0=330\ {\rm mm},\ h=12\ {\rm mm}\ {\rm default}.
$$

Stack persisted hiện n=6 nên Z_next=402 mm; không tự suy stack vật lý có đúng 6 tấm. Ba lần đầu từ count=0 cho 330/342/354. Sau nhả, _after_h2off_move:198-208 đặt Z_target=Z_drop+200 hiện axis=z; code chỉ chấp nhận distance_mm đúng 200 và axis x hoặc z. Nếu chọn x sẽ là X+200, không gọi nhầm đó là lift Z.

P010.with_z tại robot/position_variable.py:17-24 dùng Decimal, giữ mọi field trừ field Z; payload thêm type=4,index=10; verify đọc lại từng Decimal bằng nhau. Nguồn P009, không lấy XY từ pose pick/P010 cũ. Không ghi P009.

REFERENCE ONLY: RMS thường diễn giải sqrt(mean(e_i²)); report chỉ lưu RMS/residual, runtime không tính lại calibration residual. Không thể đổi 184,33 px thành một mm error cố định vì ray-plane Jacobian phụ thuộc pixel/plane/pose; không có mm/px hằng được xác minh.

Có thể diễn giải đại lượng latency (REFERENCE ONLY cho mô hình tổng, chưa có trace end-to-end):
T_total=T_capture+T_transfer+T_inference+T_select+T_TCP+T_robot.
Runtime FPS=1/max(dt,0,001) trong pipeline; không đo đủ chuỗi exposure→robot. Variables metrics tính elapsed_ms=(perf_counter_end−start)×1000, rate=count_recent/min(5,elapsed), P95 lấy phần tử ceil(0,95N)−1 sau sort; nguồn nx100_variables_web/app.py:148-182,233-252. Worker đợi max(0,period/1000−roundtrip), period=0 nghĩa đọc liên tục nhanh nhất, không phải realtime deterministic.

## 7. Giao thức NX100 và I/O

### 7.1 Protocol thật

VERIFIED: NX100 Ethernet Information Server **ASCII trên TCP port 80**, không HTTP, không binary packet và không YERC UDP trong các client được đọc. HTTP chỉ dùng giữa browser/backend. Nguồn full robot/protocol.py:1-5,124-128,202-257; bản gốc module/Protocol.py; variables nx100_client.py:157-219.

Một socket cho một command; global _WIRE_LOCK serialize transaction trong process. Trình tự:

~~~text
PC -> NX: CONNECT Robot_access<CR><LF>
NX -> PC: OK: NX Information Server(...).<CR><LF>
PC -> NX: HOSTCTRL_REQUEST COMMAND N<CR><LF>
NX -> PC: OK: COMMAND<CR><LF>
PC -> NX: DATA<CR>                         [nếu có data]
NX -> PC: RESULT<CR>                       [read]
NX -> PC: 0000<CR><LF>                     [control accepted]
~~~

N=len((data+"\r").encode("ascii")); CR nằm trong length. RSTATS không data có N=0 và không payload. START MOVEUNTI có N=9, payload MOVEUNTI+CR. RPOSC 0,1 có N=4. Không có numeric command ID/byte-order binary áp dụng payload này; command được nhận bằng tên ASCII và số decimal CSV. Byte-order little-endian chỉ liên quan việc đọc NPY/checkpoint metadata, không phải protocol robot.

Reader tích lũy bytearray để xử lý fragmented/coalesced TCP; recv(4096), giới hạn 65.536 byte, deadline monotonic mỗi lần nhận frame. Payload tối đa 256 byte ở protocol full/original/snapshot/tracking. Timeout mỗi phase không phải deadline tổng toàn transaction; nhiều handshake/ACK/reply có thể cộng dồn. Không giữ session lâu hoặc retry control sau send.

Full _Reader.until_closed():138-160 đọc RJDIR tới EOF; danh sách có nhiều CR-separated group. Không dừng ở CR đầu. EOF thiếu CR cuối hoặc timeout khi chưa close coi incomplete. Nhánh gốc/snapshot/tracking không có extension này; original validator không nhận RJDIR dù Commands.read_all_job_names có wrapper.

### 7.2 Ma trận command

O=library gốc; W=web-control dùng transport O; S=snapshot; T=tracking; F=full-cycle; V=variables.

| Command | Function/input | Output | Project hỗ trợ thực | Source / xử lý lỗi |
|---|---|---|---|---|
| RSTATS | không data | hai word decimal | O/W/S/T/F | Status bit masks; malformed/range lỗi |
| RPOSC | coord,external; runtime 0,1 | XYZ/TX/TY/TZ/posture/tool/6 external =14 fields | O/W/S/T/F | Pose.parse kiểm 14 fields; không bỏ metadata |
| RPOSJ | không data | joint pulses CSV | O/W/S/T/F | Controller parse, không dùng làm Cartesian |
| RJSEQ | không data | job,line,step | O/W/F | Full kiểm 3 field, hai số cuối numeric, đúng JOB tùy wait |
| RJDIR | "*" | tên JOB nhiều group CR | F | encode whitelist + until EOF; job_control.exists validate name |
| START | tên JOB hoặc legacy rỗng ở O | 0000 | O/W transport; F allowlist JOB | F bắt explicit MOVEUNTI/configured HAND/DROP; không implicit resume |
| MOVL | 17 fields, selection/speed/frame/14 pose fields | 0000 | O/W/S/T/F | build_move preserve metadata; completion tách riêng |
| MOVJ | 16 fields, speed%/frame/14 pose fields | 0000 | O/W/S/T; F từ chối whitelist | Joint interpolation tới Cartesian, không pulse move |
| HOLD | "1"/"0" | 0000 | O/W/S/T/F theo API caller | Missing ACK/reply sau control→OutcomeUnknown |
| SVON | "1"/"0" | 0000 | O/W transport; UI W không expose servo endpoint | S/T/F từ chối; không tự bật servo |
| RESET/CANCEL | không data | 0000 | O/W transport | S/T/F không hỗ trợ; wrapper O có code |
| RALARM | không data | CSV alarm | O/W transport | Wrapper O Alarm; full không nằm allowlist |
| SETMJ | job name | 0000 | O/W transport | Full không dùng/chặn whitelist |
| IOREAD | start,count bội số8 | mỗi byte decimal | O/W/F | F read_byte chỉ nhận 0..255 cho count8 |
| IOWRITE | start,count,byte values | 0000 | O/W/F theo validator | Chỉ network inputs #22010..#23287; full JOB vacuum không gọi |
| SAVEV | type,index | scalar hoặc P fields | V; F chỉ 4,9 /4,10 | V normalize; F parse_p010 |
| LOADV | type,index,value | 0000 | V; F chỉ P010 Cartesian BASE | Ghi xong readback; unknown không tự gửi lại |
| IMOV | INFORM instruction | Không phải command TCP được hỗ trợ | Không có client TCP IMOV | Nội dung JOB chưa có export |
| JSEQ | Không tìm thấy implementation command | UNKNOWN | Không | Không suy từ RJSEQ thành write JSEQ |

Số bit RSTATS: word1 bit0 step,1 one-cycle,2 auto,3 running,4 safety-speed,5 teach,6 play,7 remote. Word2 bit1 pendant hold,2 external hold,3 command hold,4 alarm,5 error,6 servo. Word1 0..255, word2 0..127. Nguồn robot/status.py:1-52. Safety-speed flag không thay thế kiểm soát an toàn cell.

MOVL wire:
selection,speed,frame,X,Y,Z,Rx,Ry,Rz,posture,tool,external1..6.
MOVJ bỏ selection đầu. build_move dùng frame=0; selection MOVL=0. Validator protocol cho linear speed≥0,1, còn upper bound do controller/settings. Không lấy 80 từ header làm tốc độ JOB IMOV.

### 7.3 Biến B/I/D/R/P

VERIFIED nx100_variables_web/nx100_client.py:20-24,38-142:

| Loại | Type code | Phạm vi editor |
|---|---:|---|
| B | 0 | 0..255, index 0..99 |
| I | 1 | −32768..32767, index 0..99 |
| D | 2 | signed 32-bit, index 0..99 |
| R/F | 3 | R finite, max 3,4e38; nonzero min 1,18e−38; F alias R |
| P | 4 | index 0..127; Cartesian 10 fields hoặc 6-axis pulse+tool 8 fields |
| S | Không hỗ trợ | Từ chối vì parser SAVEV/LOADV này không hỗ trợ |

Cartesian P: format=1,frame,X,Y,Z,Rx,Ry,Rz,posture,tool; XYZ 3 decimal, góc 2 decimal trong editor V. Pulse P: format=0,6 pulse signed32,tool. edited_value giữ frame/posture/tool; không tự đổi loại P. Scalar R readback dùng isclose rel_tol=1e−6, abs_tol=0. V nhận exponent trong parser số nhưng UI nhập chỉ decimal; normalize serialize dạng fixed.

F LOADV chỉ cho 4,10,1,0,...: P010 Cartesian BASE, góc có thể 3 decimal theo builder F. F không mở editor biến tổng quát.

### 7.4 I/O mapping và error handling

F IOREAD start=20050,count=8, bit0 laser, bit1 contact20051, bit2 contact20052. Contacts biểu diễn chữ số cuối 0..7, không phải địa chỉ byte nhị phân liên tục 20050+8. monitor_inputs kiểm cùng nhóm address//10, đọc bit address%10. Mỗi byte value decimal, mask 1<<bit. Polarity laser áp dụng active_high; pressure monitor_inputs chỉ raw bool, chưa có polarity/setpoint model riêng.

Vacuum output read start=30050, bits0/1. IOWRITE chỉ network input #22010..#23287; không ghi trực tiếp external input 20050 hay output 30050. Read-modify-write bảo toàn bit khác trong byte nhưng không atomic với writer ngoài process; owned_byte chỉ là cấu hình tuyên bố quyền sở hữu.

ProtocolError: rejection explicit NG:/ERROR: hoặc framing sai. OutcomeUnknown: control đã có thể được gửi nhưng mất kết quả; không auto retry. attempted đặt trước send payload/zero-data header để không lờ khả năng command đã tới controller. 0000 không chứng minh robot đến đích/JOB hoàn tất/van tác động.

Error 2100: source Controller.observe:115-116 và docs/IO_MAPPING.md:7 ghi remote chưa được đặt, có log lịch sử IOREAD bị từ chối. Error START 2070 có trong logs/real/app.log; chưa thấy mapping semantic chính xác trong code, ghi UNKNOWN thay vì đoán nguyên nhân. Không có bảng đầy đủ alarm/interpreter codes trong adapter. Error codes được giữ trong message, không reset tự động.


## 8. Web UI và API

### 8.1 Giao diện và hành vi nút

| Project | Trang/assets | Hiển thị và thao tác |
|---|---|---|
| Full-cycle | templates/index.html; static/app.js; static/style.css | Mode, robot/camera, FPS, flags/pose, detection/target, laser/IN2/IN3, HAND outputs, state/error; claim/connect/START/HOLD/ACK/release-HOLD; settings, stack count/reset |
| Tracking | templates/index.html; static/app.js/style.css | Robot/camera scan/connect; pose/joint/motion, ID/eligibility/distances/confidence; START/STOP/HOLD; config stability/orientation |
| Snapshot | templates/index.html; static/app.js/style.css | Live detection và saved batch, lưu tọa độ, đổi cáp/connect robot, SEND một record, completion count; HOLD/release/ACK; storage path |
| Variables | static/index.html/app.js/style.css | Loại/index, realtime/read/stop, editor/readback, chart, actual Hz/mean/P95/error count/events; CONNECT/DISCONNECT/WRITE |
| Web-control | templates/index.html và camera.html; static/js/app.js/camera.js; static/css/style.css/camera.css | Axes number/slider/nudge, speed, MOVL/MOVJ, joint read-only; flag/position/log; camera chọn pixel, plane-Z, chuyển Base |
| Legacy remote | module/index.html và WebServer.py | Server-side placeholder JOB/status/XYZ; POST plain text servo/HOLD/start và nudge25 mm |

Web-control static/js/app.js:13-34 scheduleAutoMove debounce theo config 400 ms. Nhập số cần Enter; slider/nudge tự lên lịch MOVE sau khi ngừng chỉnh. Poll status không dispatch input/change, nên telemetry không tự gây motion. Blur/hidden hủy timer. Server vẫn phải preflight; disable button ở browser không phải interlock.

Full-cycle static/app.js:31 đặt nhãn H2OFF_COMPLETE thành “Đã nhả ván”, trong khi receipt board_release_confirmed=false. Đây là **RISK về ngữ nghĩa HMI**: JOB kết thúc được diễn đạt như physical release. IN2/IN3 hiện qua pressure1/pressure2 chỉ raw digital state, không có kPa/bar.

### 8.2 Bảo vệ truy cập

Full-cycle: TrustedHostMiddleware, allowed_clients, POST application/json, kiểm Origin, CSP/no-store/nosniff. LAN bind đòi NX100_HMI_TOKEN ≥24 ký tự; loopback không bắt buộc token. Claim phát cookie HttpOnly/SameSite strict và lease30 s; poll state của owner gia hạn. authorized kiểm cookie/expiry, revision trừ HOLD, request_id 8..100 ký tự duy nhất và ghi admission vào journal trước mutation. Process InstanceLock riêng theo đường journal/mode.

RISK: token/lease là cơ chế ứng dụng, không phải chức năng an toàn. Full API docs/openapi mặc định của FastAPI vẫn được bật vì create_app không tắt docs_url; đi qua middleware nhưng không bổ sung quyền robot. api_requests/requests lưu lịch sử không có pruning rõ, có thể tăng dần journal. Không phát hiện HTTPS server trực tiếp trong main; LAN cần thiết kế triển khai riêng nếu muốn bảo mật transport.

Snapshot/tracking: Host+port allowlist, Origin, X-NX100-Control:operator, Sec-Fetch-Site. Không login/secret token; accepted_by_operator không có hồ sơ ký nhận mà dựa load calibration. Bind0.0.0.0 nghĩa HTTP client LAN có thể tự đặt Host hợp lệ; không nên xem Host header là ACL nguồn. ProcessLease chỉ trong project. Không có lease chủ HMI như full-cycle; request song song vẫn bị owner/robot lock chặn motion trùng nhưng không phân định người vận hành.

Web-control: bind loopback, Host/Origin và X-NX100-Control:local, Pydantic extra forbid/nonfinite false. Không có user auth hoặc owner lease. Variables tương tự loopback, header operator, body≤16.384 byte; ThreadingHTTPServer, lock service.io bảo đảm read/write không overlap trong process. Legacy WebServer không có Origin/custom header/auth/lease; do_POST có thể servo/start/HOLD/nudge. Chỉ giữ làm tham khảo, không coi là HMI full-cycle.

### 8.3 Bảng endpoint mã nguồn

Các bảng sau trích decorator và handler từ source, không gọi endpoint. “State” là snapshot JSON tương ứng dự án; response error theo exception handler. Caller chính là JavaScript cùng project; endpoint chưa được UI gọi vẫn có thể được HTTP client gọi nếu qua middleware.

Schema quan trọng:
- Connection: ip/port; variables dùng host/port.
- TrackingConfig: plane_z_mm, rx/ry/rz, movl_speed, confidence và policy khác theo project; snapshot không có stability fields.
- Full control body: request_id và revision; thêm stage/on/settings/confirmed/cycle_id/stacked_count tùy route. Claim token tùy cấu hình.
- CartesianMove: motion,speed,x,y,z,rx,ry,rz,reference_id optional.
- PixelPoint: frame_id,u,v,plane_z_mm; CameraConnection: index.
- Không phải mọi POST đều gửi lệnh phần cứng: claim/config/stack có thể chỉ thay state/file.


#### nx100_camera_snapshot_move

| Method | Path | Request | Response | Caller | Handler |
|---|---|---|---|---|---|
| GET | / | — | HTML | JS/API client | app.py:167 def index(): |
| GET | /api/state | — | robot + workflow/auto + vision + calibration + events | JS/API client | app.py:171 def state(): |
| POST | /api/robot/connect | Connection: ip,port | Workflow/auto/robot snapshot | JS/API client | app.py:179 def connect(data: Connection): |
| POST | /api/robot/disconnect | JSON {} / không operand | Workflow/auto/robot snapshot | JS/API client | app.py:183 def disconnect(): |
| POST | /api/camera/scan | JSON {} / không operand | devices[] | JS/API client | app.py:187 def scan(): |
| POST | /api/camera/connect | index | Vision status | JS/API client | app.py:191 def camera_connect(data: CameraInput): |
| POST | /api/camera/disconnect | JSON {} / không operand | Vision status | JS/API client | app.py:198 def camera_disconnect(): |
| GET | /api/preview.jpg | — | image/jpeg; 404/503 nếu thiếu ảnh | JS/API client | app.py:203 def preview(): |
| POST | /api/config | TrackingConfig | Workflow/auto/robot snapshot | JS/API client | app.py:210 def configuration(data: TrackingConfig): |
| POST | /api/snapshot/capture | JSON {} / không operand | Workflow/auto/robot snapshot | JS/API client | app.py:215 def capture(): |
| POST | /api/snapshot/send | batch_id,record_id | Workflow/auto/robot snapshot | JS/API client | app.py:219 def send(data: SendInput): |
| POST | /api/fault/acknowledge | JSON {} / không operand | Workflow/auto/robot snapshot | JS/API client | app.py:223 def acknowledge(): |
| POST | /api/robot/hold | JSON {} / không operand | Workflow/auto/robot snapshot | JS/API client | app.py:228 def hold(): |
| POST | /api/robot/hold/release | JSON {} / không operand | Workflow/auto/robot snapshot | JS/API client | app.py:232 def release_hold(): |

#### nx100_full_cycle_v1

| Method | Path | Request | Response | Caller | Handler |
|---|---|---|---|---|---|
| GET | / | — | HTML | JS/API client | app.py:101 def index(): |
| POST | /api/control/claim | token optional | control=true + cookie lease | JS/API client | app.py:107 def claim(request:Request, body:dict): |
| GET | /api/state | — | Cycle snapshot; lỗi 409/422/423/403 | JS/API client | app.py:122 def state(request:Request): |
| GET | /api/preview.jpg | — | image/jpeg; 404/503 nếu thiếu ảnh | JS/API client | app.py:130 def preview(): |
| GET | /api/laser/status | — | laser_in1/raw_byte/bit/mapping_verified/error | JS/API client | app.py:138 def laser_status(): |
| POST | /api/system/connect | request_id,revision | Cycle snapshot; lỗi 409/422/423/403 | JS/API client | app.py:147 def connect(request:Request,body:dict): |
| POST | /api/cycle/start | request_id,revision,stage optional | Cycle snapshot; lỗi 409/422/423/403 | JS/API client | app.py:154 def start(request:Request,body:dict): |
| POST | /api/cycle/hold | request_id (revision không bắt buộc) | Cycle snapshot; lỗi 409/422/423/403 | JS/API client | app.py:161 def hold(request:Request,body:dict): |
| POST | /api/cycle/acknowledge | request_id,revision,inspected | Cycle snapshot; lỗi 409/422/423/403 | JS/API client | app.py:167 def acknowledge(request:Request,body:dict): |
| POST | /api/cycle/release-hold | request_id,revision,confirmed | Cycle snapshot; lỗi 409/422/423/403 | JS/API client | app.py:174 def release_hold(request:Request,body:dict): |
| POST | /api/vacuum/{channel} | request_id,revision,on:boolean | Cycle snapshot; lỗi 409/422/423/403 | JS/API client | app.py:181 def vacuum(channel:int,request:Request,body:dict): |
| POST | /api/config | request_id,revision,settings | Cycle snapshot; lỗi 409/422/423/403 | JS/API client | app.py:190 def configure(request:Request,body:dict): |
| POST | /api/drop/settings | request_id,revision,board_thickness_mm | Cycle snapshot; lỗi 409/422/423/403 | JS/API client | app.py:197 def drop_settings(request:Request,body:dict): |
| POST | /api/drop/count | request_id,revision,stacked_count | Cycle snapshot; lỗi 409/422/423/403 | JS/API client | app.py:204 def set_stack_count(request:Request,body:dict): |
| POST | /api/drop/reset | request_id,revision,confirmed | Cycle snapshot; lỗi 409/422/423/403 | JS/API client | app.py:211 def reset_stack(request:Request,body:dict): |
| POST | /api/drop/confirm | request_id,revision,cycle_id,confirmed | Cycle snapshot; lỗi 409/422/423/403 | JS/API client | app.py:218 def confirm_drop(request:Request,body:dict): |

#### nx100_web_control

| Method | Path | Request | Response | Caller | Handler |
|---|---|---|---|---|---|
| GET | / | — | HTML | JS/API client | app.py:137 def index(): |
| GET | /camera | — | HTML camera | JS/API client | app.py:141 def camera_page(): |
| GET | /api/vision/status | — | VisionService status | JS/API client | app.py:145 def vision_status(): |
| POST | /api/vision/reload | JSON {} / không operand | VisionService status | JS/API client | app.py:149 def vision_reload(): |
| POST | /api/vision/enumerate | JSON {} / không operand | devices[] | JS/API client | app.py:153 def vision_enumerate(): |
| POST | /api/vision/connect | index | VisionService status | JS/API client | app.py:157 def vision_connect(body: CameraConnection): |
| POST | /api/vision/disconnect | JSON {} / không operand | VisionService status | JS/API client | app.py:161 def vision_disconnect(): |
| GET | /api/vision/frame | — | frame metadata + JPEG base64 | JS/API client | app.py:165 def vision_frame(): |
| POST | /api/vision/pixel-to-base | PixelPoint | pixel/base_mm/camera_mm/quality/fingerprint | JS/API client | app.py:169 def vision_pixel(body: PixelPoint): |
| GET | /api/config | — | config/mode/capabilities | JS/API client | app.py:173 def get_config(): |
| GET | /api/status | refresh query optional | Robot snapshot hoặc operation receipt | JS/API client | app.py:177 def status(refresh: bool = False): |
| GET | /api/position/cartesian | — | Robot snapshot hoặc operation receipt | JS/API client | app.py:181 def cartesian(): |
| GET | /api/position/joint | — | Robot snapshot hoặc operation receipt | JS/API client | app.py:185 def joint(): |
| GET | /api/logs | after query optional | events sau id | JS/API client | app.py:189 def logs(after: int = Query(default=0, ge=0)): |
| POST | /api/connect | Connection: ip,port | Robot snapshot hoặc operation receipt | JS/API client | app.py:193 def connect(body: Connection): |
| POST | /api/disconnect | JSON {} / không operand | Robot snapshot hoặc operation receipt | JS/API client | app.py:197 def disconnect(): |
| POST | /api/move/cartesian | CartesianMove | Robot snapshot hoặc operation receipt | JS/API client | app.py:201 def move(body: CartesianMove): |
| POST | /api/move/joint | JointMove (bị từ chối) | 501 JOINT_MOVE_UNSUPPORTED | JS/API client | app.py:210 def move_joint(body: JointMove): |
| POST | /api/hold | JSON {} / không operand | Robot snapshot hoặc operation receipt | JS/API client | app.py:214 def hold(): |

#### nx100_yolo_auto_tracking

| Method | Path | Request | Response | Caller | Handler |
|---|---|---|---|---|---|
| GET | / | — | HTML | JS/API client | app.py:161 def index(): |
| GET | /api/state | — | robot + workflow/auto + vision + calibration + events | JS/API client | app.py:165 def state(): |
| POST | /api/robot/connect | Connection: ip,port | Workflow/auto/robot snapshot | JS/API client | app.py:173 def connect(data: Connection): |
| POST | /api/robot/disconnect | JSON {} / không operand | Workflow/auto/robot snapshot | JS/API client | app.py:180 def disconnect(): |
| POST | /api/camera/scan | JSON {} / không operand | devices[] | JS/API client | app.py:187 def scan(): |
| POST | /api/camera/connect | index | Vision status | JS/API client | app.py:191 def camera_connect(data: CameraInput): |
| POST | /api/camera/disconnect | JSON {} / không operand | Vision status | JS/API client | app.py:196 def camera_disconnect(): |
| GET | /api/preview.jpg | — | image/jpeg; 404/503 nếu thiếu ảnh | JS/API client | app.py:201 def preview(): |
| POST | /api/config | TrackingConfig | Workflow/auto/robot snapshot | JS/API client | app.py:208 def configuration(data: TrackingConfig): |
| POST | /api/auto/start | JSON {} / không operand | Workflow/auto/robot snapshot | JS/API client | app.py:213 def start(): |
| POST | /api/auto/stop | JSON {} / không operand | Workflow/auto/robot snapshot | JS/API client | app.py:218 def stop(): |
| POST | /api/robot/hold | JSON {} / không operand | Workflow/auto/robot snapshot | JS/API client | app.py:223 def hold(): |

#### nx100_variables_web

| Method | Path | Request | Response | Caller | Handler |
|---|---|---|---|---|---|
| GET | / | — | HTML | Browser | app.py:283 do_GET |
| GET | /app.js, /style.css | — | Asset | Browser | app.py:289 |
| GET | /api/state | — | Variables.snapshot | static/app.js poll250 ms | app.py:287 |
| POST | /api/connect | host,port | state | connection form | app.py:318 → Variables.connect |
| POST | /api/disconnect | {} | state | button | app.py:320 |
| POST | /api/read | kind,index,period_ms | state | read button | app.py:322 → choose(realtime=False) |
| POST | /api/start | kind,index,period_ms | state | start button | app.py:322 → choose(realtime=True) |
| POST | /api/stop | {} | state | stop button | app.py:324 |
| POST | /api/write | name,values:string[] | state + write_result | write button | app.py:326 |

#### Remote-control legacy

| Method | Path | Request | Response | Caller | Handler |
|---|---|---|---|---|---|
| GET | / | — | HTML thay placeholders bằng robot state | module/index.html | module/WebServer.py:56 |
| HEAD | mọi path | — | headers 200 | HTTP client | WebServer.py:60 |
| POST | current URL | plain text start_job/hold_on/hold_off/servo_on/servo_off/move_s_l/r/move_l_l/r/move_u_l/r | 200, body rỗng | index.html fetch | WebServer.py:63 |

Legacy không route JSON; start_job gửi START rỗng tức có thể resume job hiện tại. Unknown body vẫn trả 200 mà không báo invalid command. _html có phần isHold lặp command_hold và bỏ external_hold; không dùng làm nguồn truth duy nhất.

## 9. State machine và đồng bộ

### 9.1 State thật của full-cycle

Nguồn workflow/state_machine.py:8-13 định nghĩa STEPS và TERMINAL, nhưng không có bảng transition formal cưỡng chế mọi cạnh. Journal.update có thể ghi state bất kỳ caller cung cấp. State có mặt trong danh sách không bảo đảm reachable ở cấu hình hiện tại.

~~~mermaid
stateDiagram-v2
  [*] --> IDLE
  IDLE --> SYSTEM_CHECK: start guarded
  SYSTEM_CHECK --> WAIT_TARGET: full or xy
  WAIT_TARGET --> TARGET_LOCKED: stable target
  WAIT_TARGET --> COMPLETE: fresh empty scene
  TARGET_LOCKED --> MOVE_XY
  MOVE_XY --> XY_VERIFY: stopped and reached
  XY_VERIFY --> START_MOVEUNTI
  START_MOVEUNTI --> Z_DESCENDING: current laser wait mode
  START_MOVEUNTI --> JOB_DISPATCHED: legacy handoff flag
  Z_DESCENDING --> LASER_CONFIRMED
  LASER_CONFIRMED --> MOVEUNTI_COMPLETE: laser ON and stopped
  MOVEUNTI_COMPLETE --> VACUUM_ACTIVATING
  VACUUM_ACTIVATING --> WRITING_DROP_P010
  WRITING_DROP_P010 --> DROP_P010_WRITTEN: verified readback
  DROP_P010_WRITTEN --> WAIT_DROP_POSITION: START DROP
  WAIT_DROP_POSITION --> DROP_Z_REACHED
  DROP_Z_REACHED --> EXECUTING_H2OFF
  EXECUTING_H2OFF --> H2OFF_COMPLETE
  H2OFF_COMPLETE --> STACK_COUNT_UPDATED
  STACK_COUNT_UPDATED --> POST_H2OFF_MOVE
  POST_H2OFF_MOVE --> COMPLETE
  COMPLETE --> SYSTEM_CHECK: repeat and ready
  COMPLETE --> IDLE: ACK stopped
  JOB_DISPATCHED --> IDLE: ACK stopped
  FAULT --> IDLE: inspected ACK stopped
  HOLD --> IDLE: inspected ACK stopped
  SYSTEM_CHECK --> FAULT: precondition fails
  MOVE_XY --> FAULT: unresolved or timeout
  Z_DESCENDING --> FAULT: invalid or timeout
  WAIT_DROP_POSITION --> FAULT: invalid or timeout
  EXECUTING_H2OFF --> FAULT: invalid or timeout
  MOVE_XY --> HOLD: operator
  Z_DESCENDING --> HOLD: operator
~~~

Các trạng thái nhánh cũ có trong source: MOVE_TO_SAFE (không được _run_once hiện tại sử dụng), WAIT_DROP_SAFE/DROP_SAFE_REACHED/CALCULATE_DROP_Z/MOVING_TO_DROP_Z (khi drop.position_variable=None), AWAIT_DROP_CONFIRMATION (manual recovery path, không dùng để dừng luồng đếm tự động hiện tại). HMI có trạng thái kết nối riêng bằng telemetry, không state DISCONNECTED/CONNECTING trong Journal.

### 9.2 Đối chiếu state tham chiếu yêu cầu

| State tham chiếu | Có trong code/ánh xạ | Ghi chú |
|---|---|---|
| DISCONNECTED | Tracking Enum, robot connected=false | Không Journal state full |
| CONNECTING | Đề xuất | Thể hiện operation connect, không state formal |
| IDLE | Có | Full Journal và tracking |
| READY | Đề xuất/derived readiness | Flags + capability, không Journal state |
| DETECTING | WAIT_TARGET / STABILIZING | Đang đọc vision, không cùng tên |
| TARGET_LOCKED | Có full | Tracking TARGET_READY |
| MOVING_XY | MOVE_XY | Tên khác |
| SEARCHING_Z | START_MOVEUNTI/Z_DESCENDING | Tên khác |
| VACUUM_ON | VACUUM_ACTIVATING | Không state bảo đảm áp suất |
| VERIFYING_VACUUM | Đề xuất | Chưa có pressure guard |
| LIFTING | Có thể trong DROP, UNKNOWN | PC POST_H2OFF_MOVE là nâng sau nhả |
| MOVING_TO_PLACE | WAIT_DROP_POSITION | JOB DROP |
| RELEASING | EXECUTING_H2OFF/H2OFF_COMPLETE | Không physical release proof |
| RETURNING | POST_H2OFF_MOVE; tracking RETURNING_HOME | Không tương đương cùng chuyển động |
| COMPLETE | Có full | Tracking MOVE_COMPLETE/STOPPED |
| FAULT | Có | Không auto recover |
| HOLD | Có full; tracking chuyển FAULT | Phần mềm HOLD không E-STOP |

### 9.3 Transition contracts

| Cạnh/trigger | Guard/action | Thành công | Timeout | Failure |
|---|---|---|---|---|
| IDLE→SYSTEM_CHECK / START | Lease/revision/request-ID; ready/camera/laser; lưu cycle_id/worker | Worker bắt đầu | HTTP/TCP checks theo cấu hình | Reject trước send hoặc FAULT |
| WAIT_TARGET→TARGET_LOCKED | Fresh distinct frames, candidate/tolerance/dwell/workspace | Freeze target+pose | 30 s target_timeout | FAULT; empty repeat đủ2 s kết thúc no_boards |
| TARGET_LOCKED→MOVE_XY→XY_VERIFY | Fresh status/pose metadata, workspace; intent trước MOVL | Stopped+reached3 mẫu | 120 s | FAULT và HOLD nếu unresolved |
| XY_VERIFY→START_MOVEUNTI | Z_safe/orientation, JOB exists, laser OFF | START accepted | Socket3 s mỗi phase | Unknown không retry; FAULT |
| Z_DESCENDING→MOVEUNTI_COMPLETE | Same JOB, XY/orientation; laser ON+stopped3 mẫu hiện tại | Lưu stop_position/criteria | 60 s | FAULT/HOLD request |
| MOVEUNTI_COMPLETE→H2ON done | Recheck laser/same JOB/stopped, START H2ON | Same HAND JOB stopped2 mẫu | 10 s | FAULT/unknown, không retry |
| H2ON→P010 written | P009 Cartesian BASE, target bounds/height; LOADV+readback | Decimal equality toàn field | Socket deadline | Không START DROP; FAULT |
| P010→DROP_Z_REACHED | START DROP, same JOB, ready+workspace | Target pose reached, running OFF3 mẫu | 120 s | Không H2OFF; FAULT/HOLD request |
| DROP_Z_REACHED→H2OFF_COMPLETE | Recheck required_pose, START H2OFF | Same JOB stopped2 mẫu | 10 s | Không count nếu chưa complete |
| H2OFF→STACK_COUNT_UPDATED | cycle ID chưa counted; atomic stack commit | Count tăng đúng một lần | FS có thể block, không deadline riêng | Lỗi lưu giữ lỗi; không giả complete |
| STACK_COUNT_UPDATED→POST_H2OFF_MOVE | Axis z/config+200, workspace, required start | Stopped+reached | 120 s | Count đã lưu không undo; FAULT |
| COMPLETE→SYSTEM_CHECK | Repeat true, không stop_reason/cancel, robot ready, laser OFF | Cycle ID mới; fresh frame | Target timeout lượt mới | FAULT hoặc no_boards |
| Terminal→IDLE / ACK | Worker dừng, running OFF, inspected nếu unknown | Clear pending/fault journal | TCP deadline | Không ACK nếu chưa dừng |
| Any active→HOLD | cancel set trước lock; journal HOLD; HOLD1 một lần | ACK command và refresh | Socket timeout | Outcome unknown; robot có thể còn chạy |
| IDLE→release-HOLD | Confirmed, không pending/unknown, không external/pendant HOLD, ready flags riêng | HOLD0 và đọc command_hold=false | Socket | FAULT, không auto START/MOVE |

### 9.4 Tracking/snapshot và bền vững

Tracking State Enum: DISCONNECTED, IDLE, ARMED, WAITING_TARGET, STABILIZING, TARGET_READY, PRECHECK, MOVING, VERIFYING_POSITION, MOVE_COMPLETE, STOP_REQUESTED, RETURNING_HOME, STOPPED, FAULT. Automation tick mỗi .05 s sau thời gian xử lý; selected target bất biến, history commit chỉ khi MOVE COMPLETE. STOP cho hoàn tất motion hiện tại rồi phát MOVL HOME=[500,0,0,180,0,90]; đây là chuyển động mới cần đánh giá đường đi, không phải emergency stop. HOLD cố chặn rồi fault; restart backend sau kiểm tra fault, không tự tiếp tục.

Snapshot phase dẫn xuất CAMERA/SAVED/MOVING/COMPLETE/FAULT. SavedTarget.status=SAVED/SENDING/COMPLETE/UNCERTAIN. Ghi SENDING durable trước wire; restart gặp SENDING→UNCERTAIN/fault, không resend. Capture không gửi motion, send một target theo batch_id/record_id, cần click cho target sau.

Journal full ghi intent→command→accepted; accepted chỉ xóa pending sau ACK, completion state separate. Restart state không terminal hoặc pending→FAULT/unknown; terminal gồm JOB_DISPATCHED, vì handoff chưa đồng nghĩa robot dừng. StackStore cycle IDs tránh count trùng; lưu fsync và replace; không auto reset dữ liệu hỏng.

RISK: không có giao dịch nguyên tử xuyên robot và filesystem. Mất điện sau command trước accepted luôn có cửa sổ outcome unknown; journal giúp tránh replay chứ không khôi phục physical state. Job khác/pendant vẫn có thể xen vào giữa những read PC.


## 10. Hợp đồng hàm quan trọng

Các signature dưới đây được đối chiếu source. Đây là hợp đồng suy từ code, không có thực thi. pre/postcondition phần cứng chỉ là điều kiện phần mềm quan sát; không khẳng định kết quả cơ khí.

| Hàm / nguồn | Input / return | Precondition | Side effect / postcondition / exception |
|---|---|---|---|
| Cycle.__init__(cfg,mock=True,journal_path=None), workflow/cycle.py:19 | Config dict/mode/path → instance | NPZ đọc được; settings hợp lệ; lock khả dụng | Tạo Controller/Vision/Journal/StackStore; nạp settings đè; có thể ghi runtime file nếu chạy; không tự network connect; load/FS errors |
| Cycle.start(request_id,revision,stage='full_cycle'), :146 | ID/revision/stage → None | ID8..100; chưa duplicate; IDLE/not busy; real_gate nếu REAL; camera/robot/ready; laser OFF trừ vacuum_only | Clear prefetch/cancel; journal SYSTEM_CHECK; tạo worker; ValueError/RuntimeError khi reject |
| Cycle._target(), :190 | Vision samples→pose dict hoặc None khi no_boards | Camera fresh, ready robot mỗi vòng | Freeze target; target_timeout30 s; không motion; RuntimeError nếu stale/timeout/workspace |
| Cycle._move(target,state,required_start=None), :243 | 6-axis pose mm/deg → None | ready/stopped; start/target finite+workspace; required pose nếu có | Intent MOVL, wire một lần; poll metadata/stopped/reached3 mẫu; timeout120 s→RuntimeError |
| Cycle._start_moveunti(), :270 | Không operand ngoài config → start pose | Ready; MOVEUNTI exists; laser OFF; pose workspace | Intent/START một lần; job_start_attempted trước send; ProtocolError/OutcomeUnknown |
| Cycle._wait_laser_and_stopped(start), :326 | start pose → None | Sau START JOB | Same JOB, laser ON/stopped3 samples, XY/orientation stable; lưu stop_position; timeout60 s; không pressure check |
| Cycle._run_once(stage), :386 | stage → None | Worker quản lý một lượt | Gọi target→MOVL→JOB→HAND→P010→DROP; catch lỗi→FAULT; unresolved thử HOLD một lần |
| Cycle._execute_hand_job(channel,on,config=None,require_laser=False,required_pose=None), :533 | Channel1/2,bool → None | mapping/caller validated; flags; required pose/laser tùy caller | START named HAND, wait same JOB stopped2; timeout10 s; không pressure proof; lỗi propagate |
| Cycle.hold(), :456 | — → None | Không preflight motion | cancel trước lock; HOLD journal; HOLD1/refresh; lỗi vẫn giữ unknown; không tự OFF vacuum |
| Cycle.acknowledge(inspected=False), :468 | bool → None | Worker dừng; terminal; inspected nếu unknown; running OFF | IDLE/clear pending; không HOLD0/servo/reset/START |
| Cycle.release_hold(confirmed=False), :488 | bool → None | IDLE; no pending/unknown; confirmed; flags riêng | HOLD0 intent/send/readback; exception→FAULT/unknown; physical pending move có thể tiếp tục |
| DropWorkflow._prepare_drop_variable(), workflow/drop.py:96 | Config/stack/P009 → None | position_variable=10; ready; valid Cartesian BASE; target not above safe_z | SAVEV4,9→with_z→LOADV4,10→SAVEV verify; prefetch; không P009 write |
| DropWorkflow._finish_drop(), :158 | Current cycle/receipt → None | Chưa drop attempt cùng cycle; P010 receipt verified hoặc fallback safe | Wait DROP target, H2OFF, receipt false release, stack commit, Z+200, COMPLETE; không retry attempt |
| StackStore.confirm(cycle_id,picked_id=None), :82 | ID,pick ID→bool | Nonempty cycle ID; data valid | Duplicate false; otherwise atomic count+1/cursor/history→true; FS error không commit RAM |
| Journal.intent(name,payload)/accepted(), workflow/state_machine.py:83/86 | Command info→None | Journal instance | pending được fsync/replace trước command; accepted clear pending; exception FS propagate |
| Client.execute(name,data=''), robot/protocol.py:202 | ASCII name/data→result str | encode validator pass | Một socket/serialized transaction; ProtocolError hoặc OutcomeUnknown; không retry |
| Pose.parse(raw), robot/cartesian.py:14 | CSV14→Pose | Có đủ14 fields validated bằng MOVL payload | Không network; ProtocolError nếu malformed |
| build_move(command,speed,xyz,pose), :47 | MOVL/MOVJ; speed str;3/6 coordinate strings;Pose→data str | Finite, ≤3 decimal, metadata hợp lệ | Giữ pose fields còn lại; không send; full encode từ chối MOVJ dù builder có branch |
| PixelToRobot.convert(u,v,plane_z), vision/calibration.py:63 | Pixel/BASE Z mm→NumPy XYZ mm | Pixel in sensor; rigid calibration hợp lệ | Undistort/ray-plane/offset; InputError; không hardware |
| BoardTracker.update(detections,now=None), vision/tracker.py:30 | Detection list/stamp→sorted list | bbox/name/u/v của detector | Mutate item id/instance/uncertain, tracks/generation; không robot |
| StableTarget.update(frame,stamp,items,now), vision/stability.py:15 | Frame/stamp/item→item copy hoặc None | Finite coordinates/confidence/fresh | State cửa sổ stability; không average; không wire |
| Automation.tick(), tracking automation/auto_move.py:166 | Robot/vision state→None | Armed/target valid; no other active | Single MOVL hoặc HOME theo STOP; history commit sau completion; lỗi→FAULT |
| Automation._send_guard(target,pose), :144 | Frozen Target/Pose→None | Armed, no STOP, fresh, same version/calibration/eligible/workspace | Raise ControlError trước wire nếu invalid; không tự điều chỉnh đích |
| SnapshotMove.capture(), snapshot workflow/snapshot_move.py:155 | Current targets→snapshot dict | Not busy, vision/calibration ready, targets có XYZ | Ghi saved batch/fingerprint; không network motion, không age/stability gate |
| SnapshotMove.send(batch_id,record_id), :208 | IDs→snapshot dict | Batch/current next record, no fault/busy, robot connected, guard pass | Persist SENDING trước move; lỗi sau guard→UNCERTAIN; không auto SEND tiếp |
| SnapshotMove.tick(), :250 | Robot snapshot→None | Active record | MOVE COMPLETE→persist completed; lost/error→UNCERTAIN/fault |
| NX100Controller.move_cartesian(motion,speed,coordinates,reference_id=None,send_guard=None), tracking robot/controller.py:290 | mm/deg list→robot snapshot | One intent, config speed, fresh flags/pose; guard tùy caller | Send once, active monitor; unknown disconnect/no retry; snapshot version có HOLD release bổ sung |
| Variables.write(name,values), variables app.py:184 | Name,string[]→None | Đã read đúng biến; no write_unknown; values chuẩn | IO lock; LOADV+readback; store desired/actual/matched; không gate robot running |
| NX100.write_and_read(name,value), variables nx100_client.py:231 | Variable/raw value→(actual,matched) | normalize pass | LOADV rồi SAVEV; ack được nhưng read lỗi→WriteUnknown; không resend |

Call chain trọng tâm:
- Full: app.start → Cycle.start → worker _run → _run_batch → _run_once → _target/_move/_job/_execute_hand_job → _prepare_drop_variable → START DROP → _finish_drop → StackStore.confirm → _after_h2off_move.
- Tracking: inference publish → Stability.update → Automation.tick → select_next_target → NX100Controller.move_cartesian → send_guard → Client.execute; robot monitor → phase MOVE COMPLETE → history commit.
- Snapshot: camera publish → capture/persist → manual send/persist SENDING → controller move → monitor/tick → persist COMPLETE/UNCERTAIN.
- Variables: HTTP choose/write → Variables.io lock → NX100.read/write_and_read → _exchange; read worker sử dụng generation để bỏ kết quả selection cũ.

## 11. Phần cứng và triển khai

### 11.1 Bảng thiết bị

| Thiết bị | Model | IP/port/giao tiếp | Vai trò | Nguồn xác minh |
|---|---|---|---|---|
| Robot/controller | UP50N / NX100 theo mô tả project | 192.168.255.1:80 TCP ASCII | Motion/JOB/I/O | full README.md:3; config.json:2-4; protocol |
| Camera | HIKROBOT; model MV-CS200-10GM: NOT FOUND IN SOURCE được khảo sát | 192.168.255.3 ở full; GigE MVS; port UNKNOWN | Sensor ảnh | full config.json:5, pipeline.py:47-58; adapter enum model động |
| Laser | Omron E3Z-LL61 theo docs, chưa đo trong phiên | Digital; 20050 bit0→IN1 theo mapping report | Tìm Z | full docs/IO_MAPPING.md:5; robot/io.py |
| Pressure | Airtac DPSN1: NOT FOUND IN SOURCE | Digital contacts20051/20052 được UI gọi IN2/IN3 | Monitor, chưa guard | full config.json vacuum.input_contacts; controller.py:129 |
| Solenoid valve | Airtac model: NOT FOUND IN SOURCE | Wiring/coil voltage UNKNOWN | Hút/nhả theo mô tả hệ thống | Không có bill-of-material/wiring trong sáu cây |
| Relay | Omron model: NOT FOUND IN SOURCE | Output30050/30051; wiring UNKNOWN | Interface HAND | config vacuum.output_contacts; không có part number |
| EOAT | Vacuum theo calibration report; model NOT FOUND | Pneumatic/control qua JOB | Gắp vật | eye_to_hand.npz::report_json.robot_tool_frame |
| PC AI | CPU/GPU model NOT FOUND | Windows; Python310 x64 phù hợp DLL nếu dùng x64; inference config cpu | Backend/AI/HMI | pyvenv.cfg, vision/camera.py:40-62, config vision.device |

Tên phần cứng trong yêu cầu là context người dùng, không tự biến thành VERIFIED từ source. Serial/firmware/load rating/TCP/payload/safety circuit không có đủ dữ liệu để xác nhận. Banner NX Information Server(4.165) có trong log lịch sử, không khẳng định firmware hiện tại.

### 11.2 Dependency và môi trường

| Project | Khai báo thực tế |
|---|---|
| Snapshot/tracking | fastapi==0.115.12, uvicorn==0.34.3, pydantic==2.11.7; numpy>=1.26,<3; opencv-python>=4.10,<6; ultralytics>=8.3,<9; setuptools>=77.0.3 |
| Full | requirements: fastapi>=0.115,<1; uvicorn>=0.30,<1; numpy>=1.26,<3; opencv-python>=4.10,<6; httpx>=0.27,<1; real thêm ultralytics>=8.3,<9; dev playwright==1.64.0 |
| Full lock | numpy2.2.6, opencv-python5.0.0.93, fastapi0.115.12, uvicorn0.34.3, pydantic2.11.7 |
| Full real lock | torch2.13.0+cu126, torchvision0.28.0+cu126, ultralytics8.4.182; inventory lưu trong requirements-real-lock.txt, không chứng minh wheel source tái tạo hoàn toàn |
| Web-control | fastapi0.115.12, uvicorn0.34.3, pydantic2.11.7, starlette0.46.2, anyio4.9.0, numpy2.2.6, opencv-python-headless4.11.0.86 |
| Variables | Python3.10+, standard library, không requirements.txt |
| Remote-control | setup version1.0.3, python_requires>=3.6, pygame2.0.1; protocol code hiện có cần kiểm compatibility thực tế |

pyvenv.cfg các project snapshot/tracking/full ghi Python3.10.0. Snapshot/tracking include-system-site-packages=true; full false. Vì thế hai venv đầu không cô lập hoàn toàn khỏi site packages máy. MVS SDK không phải pip dependency; adapter dùng wrapper hãng và DLL Windows, không kèm SDK trong source riêng. Cần match 32/64-bit giữa Python và MVS DLL, không suy CPU/GPU model từ tên thư mục Win64.

MVS search: vision.sdk_root nếu đặt; MVCAM_COMMON_RUNENV và thư mục Development liên quan; mặc định ProgramFiles(x86)/MVS/Development/Samples/Python/MvImport. Runtime ở Common Files/MVS/Runtime/Win64_x64 hoặc Win32_i86. Adapter kiểm machine PE 0x8664 hoặc 0x14C. sdk_version lịch sử 0x04060168; phiên này không load DLL.

YOLO_CONFIG_DIR được Detector set tới project logs/ultralytics khi init model; ứng dụng có thể tạo settings/cache khi chạy, là một lý do không chạy trong nhiệm vụ này. NX100_HMI_TOKEN được full app đọc để claim HMI; giá trị token không được sao chép. Không thấy .env ứng dụng trong danh mục ngoài cache.

### 11.3 Calibration/model assets

Ba project snapshot/tracking/full cùng bộ:
- calibration/camera_intrinsic_2.npz: 3.569 byte; K, distortion, width/height, checkerboard/report.
- calibration/eye_to_hand.npz: 15.038 byte; T_base_camera/T_tool_board, K/distortion,22 sample transforms, conventions/quality/report.
- models/best.pt: 6.531.370 byte, ZIP checkpoint.

Checkpoint metadata đọc dạng chuỗi tĩnh có: date2026-10-19T11:36:25.155531+07:00, version8.4.182, DetectionModel, C2f/SPPF/Detect, yolov8n.pt, task detect, tên class van và đường training detect_van_v1. INFERRED: đây là checkpoint phát triển từ YOLOv8n cho phát hiện ván. Không unpickle/tính tensor, vì vậy không khẳng định số parameter, mAP, confusion matrix, accuracy hoặc mapping toàn bộ class chỉ từ chuỗi metadata. Runtime dùng YOLO(str(model_path)), không train/export model.

Web-control dùng JSON tại C:/Data/Calib Eye to Hand - UP50N NX100/results/eye_to_hand.json và camera_project cùng root; file không nằm trong sáu project, tồn tại thực tế ở máy khác UNKNOWN. Không thay bằng NPZ một cách âm thầm.

### 11.4 Quy trình triển khai tái dựng — chỉ ghi hướng dẫn

Các lệnh dưới lấy từ README/entry point thực, **không được thực thi trong phiên này**. Chỉ phục vụ kỹ sư triển khai sau quy trình nghiệm thu riêng; không phải chỉ dẫn kích robot ngay từ tài liệu.

Full README.md:31-41:
~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe app.py
~~~

REAL cần requirements-real.txt và MVS hãng theo README. requirements-real-lock là inventory đã cấp, CUDA wheels có thể cần wheel source riêng; không đảm bảo pip từ một index bất kỳ tái tạo đúng môi trường. Full entry main không có --mock CLI, --real chỉ tương thích; python app.py mặc định REAL cổng8011. --port thay port HMI, --no-browser không mở Edge. Factory create_app(mock=True,...) chỉ dùng mock nội bộ; khởi app cũng có thể ghi journal/log/lock.

Snapshot/tracking entry main có --mock/--real/--no-browser, tạo app theo args.mock:
~~~powershell
python app.py --mock --no-browser
python app.py --real --no-browser
~~~

Chạy từ đúng root project. Đây là cú pháp xác nhận từ argparse, không phải đề xuất tự kết nối hardware; mở app không tự connect nhưng có runtime file/log. Snapshot/tracking có thể relaunch sang .venv riêng; include-system-site-packages ảnh hưởng khả năng tái tạo.

Web-control app.py/README:
~~~powershell
python app.py --mock
python app.py
~~~
Local URL http://127.0.0.1:8000. Camera mock vẫn có thể cần calibration JSON đọc được ở configured path để dựng frame-size; không mặc định môi trường offline hoàn toàn đủ tài nguyên.

Variables app.py:339-357:
~~~powershell
python app.py --mock --no-browser --port 8010
~~~
Bỏ --mock nghĩa dùng NX100 thật khi CONNECT. Không có lệnh pip cần thiết riêng.

Full README.md:117-119 có:
~~~powershell
.\.venv\Scripts\python.exe -m tools.run_tests
.\.venv\Scripts\python.exe -m tools.browser_smoke
~~~
Không chạy ở nhiệm vụ documentation: tests dùng temporary directories/journal/log/server/mock, browser smoke có screenshot/report và write artifacts.

Trình tự nghiệm thu đề xuất (chưa làm): kiểm manifest/dependency/assets tĩnh → mock ở môi trường cho phép ghi riêng → kiểm giao diện và invalid input → read-only thiết bị với người vận hành → thử motion có giám sát theo phạm vi được đánh giá rủi ro → vacuum/load/drop dưới guard đã xác minh. Không lấy mock pass làm bằng chứng an toàn phần cứng.

IP PC192.168.255.2, robot .1, camera .3 xuất hiện trong docs/REAL_DEPLOYMENT_CHECKLIST.md:7; subnet mask/interface thực không có config đủ để xác nhận. Full yêu cầu switch đồng thời; snapshot cố ý cho đổi dây. Không thay IP hoặc cấu hình camera trong audit.

## 12. Kiểm thử và giới hạn xác minh

### 12.1 Bằng chứng đang có

| Nguồn | Ghi nhận | Giới hạn |
|---|---|---|
| docs/test_result.json | 151 tests,0 failure/error/skip,90,17 s,passed=true | File lịch sử; không chạy lại; chưa gắn chắc report vào hash/current settings |
| docs/test_output.txt | Danh sách testcase và kết quả lưu | Có thể khác bộ test/source mới; đọc không đồng nghĩa tái kiểm |
| docs/TEST_REPORT.md | Nhiều lần 126/128/… và thay đổi 5/50/80 mm/s,300/330 mm, handoff/auto | Lịch sử tích lũy, nhiều mô tả không còn default |
| docs/real_preflight.json | Model loaded; blank inference11,64 s,0 detection; MVS available nhưng camera_devices=[] | Không chứng minh vật thật/calibration/camera đang hoạt động |
| docs/real_robot_readonly.json | RSTATS timeout trước NX command | Không đại diện mọi lần kết nối khác trong log |
| docs/job_directory_live.json | 120 JOB; MOVEUNTI index87, HAND jobs trong raw | HISTORICAL; raw chưa có tên DROP trong danh sách này; không chứng minh JOB hiện tại thiếu/có |
| docs/laser_live_read.json | RSTATS194,0; IOREAD raw4 | Bit0 OFF, bit2 ON theo mapping; không có physical ON/OFF sweep |
| data/real/execution.json | COMPLETE,stop_reason=no_boards,automatic_repeat=true | Snapshot phần mềm; không chứng minh robot/cell hiện stopped hoặc cycle vật lý thành công |
| data/real/drop_stack.json | stacked_count6,thickness12,first_drop330,last_picked_id1 | Count phần mềm không phải cảm biến stack |
| logs/real/app.log | Có START error2070, MOVL timeout, HAND/cycle fault và socket errors | Log không đủ chứng minh nguyên nhân cơ khí/firmware; không tự sửa/retry |

Full data/real/operator_settings.json hiện MOVL350 khác report và config80. Stack Znext402 được suy từ dữ liệu lưu, không từ phép đo ngoài thực tế. Snapshot snapshot_real.json có saved record COMPLETE và history đã tồn tại; chỉ ghi nhận trạng thái lưu.

### 12.2 Nhóm test đã đọc

Full có tests protocol/framing/RJDIR, status bits, P009/P010, stale target/stability/identity, tracker/order/prefetch, motion completion, duplicate/revision/lease, HAND/lost reply, laser, HOLD/release, drop/count/reset/restart, repeat và independence. Có test nhánh REAL sử dụng transport giả; “REAL branch” trong tên test không có nghĩa hardware thật.

Snapshot có pytest fixtures/test immediate capture, lưu khi robot disconnected/fault, swap cable, age intentionally bypassed, manual ID order/distance50, persistence/uncertain restart, lost send, HOLD release/ACK, fingerprint/storage failure. Variables kiểm polling rate, read/write serialization, unknown readback, bounds/P metadata, lỗi3 lần dừng và HTTP Origin. Web-control kiểm preflight, no implicit motion, pending move/HOLD/disconnect races, completion2 samples, API/security và camera projection. Remote-control test wrapper/mock và gripper rejection. Tracking không có test riêng trong thư mục đang khảo sát; không suy có coverage từ log.

Phụ lục16 liệt kê từng file/test_* và dòng. Không chạy unittest/pytest/browser smoke vì tạo dữ liệu phụ có thể vi phạm read-only.

### 12.3 UNKNOWN cần hồ sơ bổ sung

- Export JOB MOVEUNTI/DROP/HAND, version/checksum và P variable usage thực; đặc biệt không để MOVEUNTI còn đọc P010 dùng làm drop.
- ON/OFF sensor thực tại pendant và IOREAD, polarity/failure mode, wiring/USER LADDER có sẵn.
- Pressure model/setpoint/unit, đủ áp/lost-vacuum/release sensing.
- TCP/tool/posture/payload, external axes, reachability/singularity và collision toàn đường.
- Calibration độc lập tại vùng làm việc, error budget sau offset và độ cao vật thay đổi.
- Camera model/serial, lens/focus/exposure/gain/ROI/frame rate thực; latency từ exposure tới send.
- Model accuracy trên vật thật/ánh sáng/occlusion; bbox center phù hợp EOAT hay không.
- Robot/controller firmware/options/remote setup và error2070 cụ thể.
- Physical state sau restart/mất điện khi đang giữ vật; journal không quan sát trạng thái khí nén khi PC tắt.
- Nguồn wheel CUDA, phiên bản SDK wrapper và cấu hình hệ điều hành đủ để triển khai lại.

## 13. Rủi ro và cải tiến

Đây là đề xuất bằng văn bản, **không sửa source/config/JOB/ladder**. Mức ưu tiên dựa ảnh hưởng có thể xảy ra, không phải định lượng PL/SIL hoặc xác suất sự cố.

| Ưu tiên | Rủi ro / đường kích hoạt | Hệ quả có thể có | Đề xuất cần đánh giá |
|---|---|---|---|
| P0 | needs_review/outliers nhưng motion được phép | Robot tới sai điểm | Nghiệm thu calibration độc lập, threshold/error budget và ràng buộc revision |
| P0 | Operator settings350 đè JSON80; báo cáo còn nói speed cũ | Người vận hành hiểu sai tốc độ | Hiển thị nguồn/effective settings rõ, kiểm giới hạn nghiệm thu thực |
| P0 | real_gate return sớm, laser true/stopped không stop-cause proof | Chuyển hút sau dừng vì nguyên nhân khác | Xác định completion tín hiệu đáng tin cậy đang có; guard search Z/hành trình |
| P0 | Không pressure gate trước DROP/lift | Rơi vật/vacuum không hình thành | Xác minh sensor/polarity/setpoint, đủ áp và mất áp; đánh giá pneumatic fail state |
| P0 | H2OFF complete→count dù physical release false | Sai stack height, kéo theo đích sai lượt sau | Xác minh release/stack, phân biệt count theo command và count vật lý |
| P0 | MOVEUNTI và DROP có thể dùng chung P010 theo docs cũ | JOB search đọc dữ liệu drop sai | Đối chiếu export/version/P ownership trước tích hợp |
| P0 | Một MOVL đồng thời XYZ; workspace chỉ axis box | Va chạm đồ gá/vật/cáp | Đánh giá toàn quỹ đạo, orientation, joint limits, load và dừng thực tế |
| P0 | Laser không phát hiện/false ON; nhánh hiện không min-Z/descent check | Đi quá hành trình hoặc hút ở độ cao sai | Giới hạn controller/cell và test failure mode theo risk assessment |
| P0 | Software HOLD/timeout bị hiểu như E-STOP | Robot chưa dừng khi mất mạng | Thiết bị safety/interlock độc lập; đo stopping distance và quy trình recovery |
| P1 | Hai project/PC/pendant cùng control | Target/JOB/variables bị thay giữa read/send | Một owner toàn robot và quản lý control mode ngoài phần mềm PC |
| P1 | Snapshot/tracking bind all interfaces, chỉ Host/header | Client ngoài có thể điều khiển | Xác thực/authorization và cấu hình network theo mô hình triển khai |
| P1 | Camera sample stamp ở PC, inference chậm | Stale target hoặc không lock được | Đo latency; kiểm acquisition timestamp và policy frame skip |
| P1 | Nhầm mm/m, deg/rad, Base/tool, offset hai lần | Sai vị trí/orientation lớn | Hợp đồng typed units/frame, calibration ID và origin offset duy nhất |
| P1 | YOLO bbox false positive/uncertain match/ID reused | Gắp sai vật/điểm không hút được | Xác minh dataset/quality, vùng hút khả dụng và detection confidence policy |
| P1 | Camera mất mạng giữa motion | Target không còn cập nhật; motion có thể tiếp tục | Quy định hành vi từng stage khi vision mất, không giả camera error đã stop robot |
| P1 | Restart/mất điện lúc giữ vật | State không khớp khí nén/cell; vật có thể rơi | Recovery thủ công theo actual payload/vacuum, không journal-only resume |
| P1 | Ghi sai I/O/ladder; RMW không atomic với host ngoài | Relay/van khác bị kích | Xác minh address/polarity/byte ownership và sơ đồ thực |
| P1 | P010/P009 bị sửa bởi pendant/host sau readback | DROP dùng đích khác | Ràng buộc owner/recipe/version, kiểm quỹ đạo chứ không chỉ endpoint |
| P1 | STOP tracking phát HOME MOVL | Đường về không được đánh giá | Tách operational STOP với HOLD/E-STOP và chứng minh HOME path |
| P2 | Journal lists/request IDs/stack history tăng không giới hạn | IO/fsync chậm, dung lượng | Chính sách retention/compaction không làm mất chống replay |
| P2 | Source/README/test report mâu thuẫn | Sai triển khai/nghiệm thu | Tài liệu versioned theo config hash/effective settings và code |
| P2 | Port/module name/venv site-packages xung đột | Import nhầm/version lệch | Đóng gói namespace riêng, môi trường được khóa và manifest |

Rủi ro cơ khí, tải nâng, rơi vật, giới hạn khớp, dừng, van/mất điện và safety interlock cần kỹ sư chịu trách nhiệm tại cell đánh giá và thử thực tế. Timeout phần mềm không phải thiết bị an toàn chức năng. Audit này không thực hiện commissioning và không thay đổi logic để lách gate.

## 14. Mức hoàn thiện và tích hợp

### 14.1 Capability matrix

IMPLEMENTED chỉ nghĩa source có implementation; phần tương tác REAL đồng thời UNVERIFIED ON HARDWARE trong phiên này.

| Capability | Mức | Lý do |
|---|---|---|
| ASCII TCP/framing/status/pose | IMPLEMENTED / UNVERIFIED ON HARDWARE | Validator/reader/mock tests; không connect hiện tại |
| Cartesian manual web control | IMPLEMENTED / UNVERIFIED ON HARDWARE | Live preflight/completion, không cell safety planner |
| Pulse joint motion UI | NOT IMPLEMENTED | move_joint501 |
| Variable scalar/P editor | IMPLEMENTED / UNVERIFIED ON HARDWARE | SAVEV/LOADV/readback; thiếu motion interlock riêng |
| MVS capture/YOLO detection | IMPLEMENTED / UNVERIFIED ON HARDWARE | REAL code + blank inference report, không vật thật hiện tại |
| Calibration runtime | IMPLEMENTED / chất lượng chưa đạt xác minh | Ray-plane/offset có thật; needs_review |
| Tracking stability/target selection | IMPLEMENTED / UNVERIFIED ON HARDWARE | 10/+2s/>50; không test riêng tìm thấy |
| Full-cycle orchestration | PARTIALLY IMPLEMENTED / UNVERIFIED ON HARDWARE | Có code đến DROP/repeat, thiếu pressure/release và JOB proof |
| Synthetic scene/motion/JOB/IO | MOCK ONLY đối với dữ liệu tổng hợp | Không mô phỏng đầy đủ physics/pressure/collision |
| Laser search controller program | UNKNOWN | PC START có; JBI không có |
| Independent stop-cause proof REAL | NOT IMPLEMENTED | stop_reason_proven chỉ mock, current bypass dùng correlation |
| Vacuum JOB dispatch/completion | IMPLEMENTED / UNVERIFIED ON HARDWARE | Không pressure proof |
| Pressure confirmation/loss reaction | NOT IMPLEMENTED | Monitor only |
| Release verification automatic | NOT IMPLEMENTED | board_release_confirmed=false |
| Stack count/Z target/idempotence | IMPLEMENTED / UNVERIFIED physical count | Count từ H2OFF completion |
| Collision/IK/safety control | NOT IMPLEMENTED trong PC | Workspace numerical box không thay safety controller |
| Restart journal/no automatic replay | IMPLEMENTED | Physical recovery vẫn manual |
| Single owner xuyên sáu project/hosts | NOT IMPLEMENTED | Locks scope riêng |

Không đưa tỷ lệ phần trăm hoàn thiện vì chưa có acceptance criteria đo lường công nghiệp và nhiều điều kiện phần cứng UNKNOWN.

### 14.2 Kiến trúc hợp nhất đề xuất — REFERENCE ONLY

~~~mermaid
flowchart TB
  UI["One HMI: cycle / manual / diagnostics"] --> AUTH["Operator authority and robot ownership"]
  AUTH --> ORCH["One orchestration state machine"]
  ORCH --> JOUR["Intent journal / recipe / recovery"]
  ORCH --> TARGET["Target contract: units, frame, age, version"]
  CAM["MVS acquisition"] --> DET["YOLO detection"]
  DET --> CAL["Validated calibration + one offset policy"]
  CAL --> TARGET
  ORCH --> MOTION["Motion / JOB completion adapters"]
  MOTION --> IO["Verified IO / vacuum / release interface"]
  MOTION --> DRIVER["One validated NX ASCII transport"]
  DRIVER --> NX["NX100 and existing JOB"]
  SAFETY["Independent cell safety / interlocks"] -.-> NX
~~~

Giữ nền full-cycle cho owner/journal/stack; chuẩn hóa driver từ full protocol (RJDIR EOF, explicit JOB allowlist, P010) và completion guard của controller họ web. Giữ Target bất biến/config-version/calibration-ID từ tracking nhưng tách policy full-cycle gắp chồng khỏi >50/completed-site suppression. Giữ snapshot thành operation mode độc lập có nhãn “stored scene”, không bỏ freshness của auto mode.

Không hợp nhất legacy Gripper/Xbox/WebServer vào đường production; giữ tham khảo/license. Không mang sys.path dependency web-control vào nền mới. Không tự thay JOB/ladder/P allocation vì thiếu export. Không gộp log lịch sử vào bằng chứng nghiệm thu config hiện tại.

### 14.3 Thứ tự công việc còn lại

1. Chốt inventory/version/hash/effective operator settings; giải quyết mâu thuẫn 80/350,5/1 so với10/2,330/300 và nhánh commissioning.
2. Thu thập export JOB/mapping/wiring/sensor/model/firmware/TCP; chứng minh P009/P010 không xung đột JOB search.
3. Nghiệm thu calibration và vùng ảnh/vật, offset, units/frame; tạo error budget độc lập.
4. Thiết kế một owner robot, operation mode và recovery từ actual payload/vacuum sau restart.
5. Xác định guard search-Z và vacuum/release có thể đo được; đánh giá mất sensor/mạng/điện và dừng cơ khí.
6. Chuẩn hóa transport/schema/state/HMI wording theo code; bảo toàn command-intent/no-retry.
7. Kiểm mock/fault injection ở môi trường được phép ghi, gồm frame skip/latency, wrong JOB, stale target, duplicate client và FS failure.
8. Nghiệm thu read-only tại cell, sau đó staged supervised motion/vacuum/drop với acceptance criteria; không dùng phần mềm PC thay safety interlock.
9. Chỉ sau có bằng chứng mới đánh giá completion/cycle-time/reliability, không suy tỷ lệ hoàn thiện từ số file/test.


## 15. Bản đồ mã nguồn

Mỗi record có PURPOSE/ENTRY POINT/CLASSES/FUNCTIONS/INPUT/OUTPUT/CALLS/CALLED BY/STATE MODIFIED/EXTERNAL DEPENDENCIES/ERROR HANDLING/MATHEMATICAL LOGIC/HARDWARE EFFECT/KNOWN LIMITATIONS.

Chỉ mục dưới đây được trích tĩnh, không import source. CALLS là tên biểu thức gọi có thể thấy trong file, CALLED BY là ứng viên lexical (reference/import cùng tên), không phải call graph động đã chứng minh; callback/reflection/alias có thể khác. Danh sách return/raise là biểu thức đọc trong block, không thay hợp đồng semantic mục10. Dòng có nhánh lồng/nested function cần đọc lại source khi dùng làm API contract. Các file test/tool liệt kê riêng ở mục16 để không trộn mock/smoke với runtime.

### nx100_camera_snapshot_move/app.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/app.py (267 dòng, 9982 byte) |
| PURPOSE | Entry point và HTTP API/HMI; tạo controller/workflow và quản lý lifecycle. |
| ENTRY POINT | Có __main__ guard; xem phần entry point/deployment |
| CLASSES | Input:42; Connection:46; CameraInput:56; SendInput:60; TrackingConfig:65; ProcessLease:75 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | _use_project_python, Path, resolve, executable.is_file, executable.resolve, SystemExit, subprocess.call, str, Input, ConfigDict, Connection, Field, field_validator, ipv4, ipaddress.IPv4Address, CameraInput, SendInput, TrackingConfig, __init__, __enter__, self.path.parent.mkdir, self.path.open, self.file.seek, msvcrt.locking, self.file.fileno, fcntl.flock, self.file.close, RuntimeError, __exit__, create_app, json.loads, read_text, NX100Controller, load_calibration, SnapshotMove, VisionPipeline, lifespan, ProcessLease, robot.start_monitor, workflow.start_worker, workflow.close, vision.close, robot.close, FastAPI, app.middleware |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | self.path, self.file |
| EXTERNAL DEPENDENCIES | import os [2]; import sys [3]; from pathlib import Path [4]; import subprocess [10]; import argparse [20]; import ipaddress [21]; import json [22]; import logging [23]; from logging.handlers import RotatingFileHandler [24]; from contextlib import asynccontextmanager [25]; from urllib.parse import urlsplit [26]; from fastapi import FastAPI, Request, HTTPException [28]; from fastapi.exceptions import RequestValidationError [29]; from fastapi.responses import FileResponse, JSONResponse, Response [30]; from fastapi.staticfiles import StaticFiles [31]; from pydantic import BaseModel, ConfigDict, Field, field_validator [32]; from robot.controller import NX100Controller, ControlError [34]; from vision.calibration import InputError [35]; from vision.pipeline import VisionPipeline, load_calibration [36]; from workflow.snapshot_move import SnapshotMove [37]; import msvcrt [86]; import fcntl [89]; import uvicorn [252]; import threading [257]; import webbrowser [258] |
| ERROR HANDLING | SystemExit, KeyboardInterrupt, OSError, RuntimeError, Exception, ValueError, HTTPException |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Entry/API có thể tạo worker/runtime file và gọi workflow; không tự coi import là read-only. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def _use_project_python | 7: def _use_project_python(): | raise SystemExit(subprocess.call([str(executable), str(Path(__file__).resolve()), *sys.argv[1:]])); raise SystemExit(130) |
| class Input | 42: class Input(BaseModel): | Class/dataclass/Enum; xem methods |
| class Connection | 46: class Connection(Input): | Class/dataclass/Enum; xem methods |
| def Connection.ipv4 | 52: def ipv4(cls, value): | return str(ipaddress.IPv4Address(value)) |
| class CameraInput | 56: class CameraInput(Input): | Class/dataclass/Enum; xem methods |
| class SendInput | 60: class SendInput(Input): | Class/dataclass/Enum; xem methods |
| class TrackingConfig | 65: class TrackingConfig(Input): | Class/dataclass/Enum; xem methods |
| class ProcessLease | 75: class ProcessLease: | Class/dataclass/Enum; xem methods |
| def ProcessLease.__init__ | 77: def __init__(self, path=None): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def ProcessLease.__enter__ | 80: def __enter__(self): | raise RuntimeError('Another backend owns this project; use one server process'); return self |
| def ProcessLease.__exit__ | 96: def __exit__(self, *args): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def create_app | 100: def create_app(mock=True, config=None, background=True, storage_dir=None): | return JSONResponse({'message': 'Host not authorized'}, status_code=403); return JSONResponse({'message': 'Invalid host'}, status_code=403); return JSONResponse({'message': 'Origin rejected'}, status_code=403); return JSONResponse({'message': 'Operator control header required'}, status_code=403) |
| def create_app.lifespan | 115: async def lifespan(app): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def create_app.protect | 134: async def protect(request: Request, call_next): | return JSONResponse({'message': 'Host not authorized'}, status_code=403); return JSONResponse({'message': 'Invalid host'}, status_code=403); return JSONResponse({'message': 'Origin rejected'}, status_code=403); return JSONResponse({'message': 'Operator control header required'}, status_code=403) |
| def create_app.control_error | 155: async def control_error(request, exc): | return JSONResponse({'code': exc.code, 'message': exc.message}, status_code=exc.status) |
| def create_app.input_error | 159: async def input_error(request, exc): | return JSONResponse({'message': str(exc)}, status_code=409) |
| def create_app.validation_error | 163: async def validation_error(request, exc): | return JSONResponse({'message': 'Invalid input', 'detail': str(exc)}, status_code=422) |
| def create_app.index | 167: def index(): | return FileResponse(BASE / 'templates/index.html') |
| def create_app.state | 171: def state(): | return dict(robot=robot.snapshot(), workflow=workflow.snapshot(), vision=vision.status(), |
| def create_app.connect | 179: def connect(data: Connection): | return workflow.connect_robot(data.ip, data.port) |
| def create_app.disconnect | 183: def disconnect(): | return workflow.disconnect_robot() |
| def create_app.scan | 187: def scan(): | return vision.scan() |
| def create_app.camera_connect | 191: def camera_connect(data: CameraInput): | return vision.status() |
| def create_app.camera_disconnect | 198: def camera_disconnect(): | return vision.status() |
| def create_app.preview | 203: def preview(): | raise HTTPException(404, 'No frame yet'); return Response(vision.preview, media_type='image/jpeg') |
| def create_app.configuration | 210: def configuration(data: TrackingConfig): | return workflow.snapshot() |
| def create_app.capture | 215: def capture(): | return workflow.capture() |
| def create_app.send | 219: def send(data: SendInput): | return workflow.send(data.batch_id, data.record_id) |
| def create_app.acknowledge | 223: def acknowledge(): | return workflow.snapshot() |
| def create_app.hold | 228: def hold(): | return workflow.hold() |
| def create_app.release_hold | 232: def release_hold(): | return workflow.release_hold() |
| def main | 239: def main(): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_camera_snapshot_move/robot/cartesian.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/robot/cartesian.py (63 dòng, 2937 byte) |
| PURPOSE | Pose Cartesian có metadata, reference check, Decimal coordinate và payload motion. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Pose:9 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | dataclass, parse, tuple, item.strip, raw.split, len, ProtocolError, encode_command, join, str, cls, verify_unchanged, list, range, Decimal, abs, coordinate, value.strip, number.is_finite, ValueError, number.quantize, m, format, build_move, isinstance, speed.strip, else, read_pose, Pose.parse, client.execute |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from dataclasses import dataclass [2]; from decimal import Decimal, InvalidOperation [3]; from .protocol import encode_command, ProtocolError [5] |
| ERROR HANDLING | ProtocolError, ValueError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 3, 28, 29, 36, 37, 39; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Pose | 9: class Pose: | Class/dataclass/Enum; xem methods |
| def Pose.parse | 14: def parse(cls, raw): | raise ProtocolError('RPOSC 0,1 cần đủ 14 giá trị gồm tư thế, tool và trục ngoài; nhận: ' + raw); raise ProtocolError('Dữ liệu vị trí chưa hợp lệ để tạo lệnh: ' + str(exc)) from exc; return cls(fields) |
| def Pose.verify_unchanged | 24: def verify_unchanged(self, current): | raise ProtocolError('Tool hoặc tư thế robot đã thay đổi; lấy lại vị trí hiện tại'); raise ProtocolError('Robot đã đổi vị trí kể từ lần lấy tọa độ; lấy lại vị trí trước khi gửi đích mới') |
| def coordinate | 33: def coordinate(value): | raise ValueError('Tọa độ phải là số hữu hạn trong phạm vi biểu diễn'); raise ValueError('X/Y/Z chỉ nhận tối đa 3 chữ số sau dấu chấm (mm)'); return format(fixed, '.3f'); raise ValueError('Tọa độ phải dùng số và dấu chấm thập phân') from exc |
| def build_move | 47: def build_move(command, speed, xyz, pose): | raise ValueError('Chọn MOVL/MOVJ và lấy vị trí từ robot trước'); raise ValueError('Cần nhập đủ XYZ hoặc XYZ/Rx/Ry/Rz'); return data |
| def read_pose | 61: def read_pose(client): | return Pose.parse(client.execute('RPOSC', '0,1')) |

### nx100_camera_snapshot_move/robot/controller.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/robot/controller.py (489 dòng, 20752 byte) |
| PURPOSE | Robot adapter/controller, preflight, serialized IO, pose/status/motion monitoring. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | ControlError:20; NX100Controller:26 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | ControlError, __init__, super, threading.Lock, deque, threading.Event, dict, _set, log, logging.getLogger, info, self.logs.append, datetime.now, astimezone, isoformat, _trace, self.log, repr, snapshot, deepcopy, self.robot_lock.locked, self.hold_pending.is_set, round, time.monotonic, events, _operation, self.robot_lock.acquire, isinstance, str, lower, self._set, self.robot_lock.release, _cancel_pending_move, self.pending_move_cancel.set, _move_operation, self.move_pending.is_set, self.move_pending.set, self._operation, cancelled.is_set, self.move_pending.clear, _require, is_connected, connect, factory, self._status |
| CALLED BY | nx100_camera_snapshot_move/app.py; nx100_camera_snapshot_move/tests/conftest.py |
| STATE MODIFIED | self.status, self.mock, self.robot_lock, self.log_lock, self.logs, self.log_id, self.client, self.reference, self.reference_id, self.hold_pending, self.move_pending, self.intent_lock, self.pending_move_cancel, self.stopping, self.thread, self.active, self.state, self.status_clock |
| EXTERNAL DEPENDENCIES | import re [3]; import threading [4]; import time [5]; import uuid [6]; from collections import deque [7]; from contextlib import contextmanager [8]; from copy import deepcopy [9]; from datetime import datetime [10]; from .mock import MockClient [12]; from .protocol import Client, OutcomeUnknown, ProtocolError [13]; from .cartesian import build_move, read_pose [14]; from .status import Status [15]; import logging [63] |
| ERROR HANDLING | ControlError, ProtocolError, ValueError, OutcomeUnknown, self |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 436; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class ControlError | 20: class ControlError(RuntimeError): | Class/dataclass/Enum; xem methods |
| def ControlError.__init__ | 21: def __init__(self, code, message, status=409): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| class NX100Controller | 26: class NX100Controller: | Class/dataclass/Enum; xem methods |
| def NX100Controller.__init__ | 27: def __init__(self, config, mock=False): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller._set | 58: def _set(self, **changes): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller.log | 62: def log(self, level, message): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller._trace | 76: def _trace(self, direction, wire): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller.snapshot | 79: def snapshot(self): | return result |
| def NX100Controller.events | 89: def events(self, after=0): | return [dict(event) for event in self.logs if event["id"] &gt; after] |
| def NX100Controller._operation | 94: def _operation(self, wait=False, timeout=None): | raise ControlError("BUSY", "Robot communication busy; command was not queued"); raise ControlError(code, str(exc), 503) from exc |
| def NX100Controller._cancel_pending_move | 129: def _cancel_pending_move(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller._move_operation | 135: def _move_operation(self): | raise ControlError("HOLD_PENDING", "HOLD pending; MOVE blocked"); raise ControlError("MOVE_PENDING", "A MOVE request is already being processed"); raise ControlError("MOTION_ACTIVE", "Previous move still being monitored"); raise ControlError("MOVE_CANCELLED", "MOVE cancelled by HOLD or disconnect") |
| def NX100Controller._require | 157: def _require(self): | raise ControlError("DISCONNECTED", "NX100 DISCONNECTED"); return self.client |
| def NX100Controller.is_connected | 162: def is_connected(self): | return self.state["connected"] |
| def NX100Controller.connect | 165: def connect(self, ip, port): | raise ControlError("ALREADY_CONNECTED", "Disconnect before changing endpoint"); raise ControlError("HOLD_PENDING", "HOLD pending"); return self.snapshot() |
| def NX100Controller.disconnect | 184: def disconnect(self): | return self.snapshot() |
| def NX100Controller._status | 202: def _status(self): | raise ProtocolError("Malformed RSTATS: " + raw); raise ProtocolError("Invalid RSTATS: " + raw) from exc; return flags |
| def NX100Controller.read_status | 231: def read_status(self): | return self.snapshot() |
| def NX100Controller._cartesian | 236: def _cartesian(self): | return pose, values |
| def NX100Controller.read_cartesian | 248: def read_cartesian(self): | raise ControlError("MOTION_ACTIVE", "Wait for motion monitoring to finish"); return {**values, "reference_id": self.reference_id} |
| def NX100Controller._joint | 258: def _joint(self): | raise ProtocolError("Malformed RPOSJ: " + raw); return values |
| def NX100Controller.read_joint | 268: def read_joint(self): | return result |
| def NX100Controller.blocked | 275: def blocked(flags): | return reasons |
| def NX100Controller.move_cartesian | 293: def move_cartesian(self, motion, speed, coordinates, reference_id=None, send_guard=None): | raise ControlError("MOTION_ACTIVE", "Previous move still being monitored"); raise ControlError("HOLD_PENDING", "HOLD pending; MOVE blocked"); raise ControlError("READ_REQUIRED", "READ CURRENT POSITION before MOVE"); raise ControlError("INVALID_SPEED", "Speed outside configured range", 422) |
| def NX100Controller.move_joint | 361: def move_joint(self, **kwargs): | raise ControlError( |
| def NX100Controller.hold | 368: def hold(self): | return {"response": response, "message": "HOLD ACCEPTED"} |
| def NX100Controller.release_hold | 389: def release_hold(self): | raise ControlError('MOTION_ACTIVE', 'Đang theo dõi MOVE; chưa thể nhả HOLD.'); raise ControlError('HOLD_PENDING', 'HOLD ON đang được gửi; chờ rồi nhả HOLD.'); raise ControlError('ROBOT_RUNNING', 'Robot còn Running; kiểm tra robot trước khi nhả HOLD.'); raise ControlError('HOLD_PENDING', 'HOLD ON vừa được yêu cầu; không nhả HOLD.') |
| def NX100Controller.poll_once | 416: def poll_once(self): | return         try:; return                 flags = self._status(); return                 _, current = self._cartesian(); return                 self._joint() |
| def NX100Controller.start_monitor | 477: def start_monitor(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller.start_monitor.monitor | 478: def monitor(): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller.close | 485: def close(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_camera_snapshot_move/robot/mock.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/robot/mock.py (55 dòng, 2075 byte) |
| PURPOSE | Phản hồi/diễn tiến mô phỏng; không đại diện physics hoặc dữ liệu thiết bị thật. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | MockClient:6 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, or, _advance, min, time.monotonic, zip, execute, self._advance, self.trace, encode, join, float, data.split, elif, ValueError, result.encode |
| CALLED BY | nx100_camera_snapshot_move/robot/controller.py |
| STATE MODIFIED | self.port, self.trace, self.pose, self.origin, self.target, self.started, self.duration, self.word2, self.word1 |
| EXTERNAL DEPENDENCIES | import time [3] |
| ERROR HANDLING | ValueError |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Chỉ mô phỏng; không suy trạng thái thiết bị thật. |
| KNOWN LIMITATIONS | Không mô phỏng collision/pressure/cell safety. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class MockClient | 6: class MockClient: | Class/dataclass/Enum; xem methods |
| def MockClient.__init__ | 7: def __init__(self, ip, port=80, timeout=3, trace=None): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def MockClient._advance | 17: def _advance(self): | return         fraction = min(1, (time.monotonic() - self.started) / self.duration) |
| def MockClient.execute | 26: def execute(self, name, data=""): | raise ValueError("Unsupported mock command"); return result |

### nx100_camera_snapshot_move/robot/protocol.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/robot/protocol.py (193 dòng, 8359 byte) |
| PURPOSE | Validate command và encode/receive ASCII NX100; serialized single-command socket. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | ProtocolError:14; OutcomeUnknown:18; _Reader:93; Client:126 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | ProtocolError, OutcomeUnknown, threading.Lock, _integer, re.fullmatch, ValueError, int, _number, number, float, math.isfinite, encode_command, isinstance, any, ord, item.strip, data.split, len, join, or, encode, __init__, bytearray, until, time.monotonic, self.buffer.find, bytes, decode, TimeoutError, repr, self.sock.settimeout, self.sock.recv, self.trace, self.buffer.extend, str, ipaddress.IPv4Address, isdigit, execute, socket.create_connection, Robot_access, _Reader, send, sock.sendall, reader.until, ack.startswith |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | self.sock, self.buffer, self.timeout, self.trace, self.ip, self.port |
| EXTERNAL DEPENDENCIES | import ipaddress [6]; import math [7]; import re [8]; import socket [9]; import threading [10]; import time [11] |
| ERROR HANDLING | ValueError, ProtocolError, TimeoutError, OutcomeUnknown |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Có đường gửi NX TCP khi hàm được gọi; không được gọi trong audit. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class ProtocolError | 14: class ProtocolError(RuntimeError): | Class/dataclass/Enum; xem methods |
| class OutcomeUnknown | 18: class OutcomeUnknown(ProtocolError): | Class/dataclass/Enum; xem methods |
| def _integer | 27: def _integer(value, lower, upper): | raise ValueError("Expected an unsigned decimal integer"); raise ValueError("Integer outside allowed range"); return number |
| def _number | 36: def _number(value): | raise ValueError("Expected a finite decimal number (no exponent)"); raise ValueError("Non-finite number"); return result |
| def encode_command | 45: def encode_command(name, data=""): | raise ValueError("Command outside tracking scope"); raise ValueError("Command and data must be strings"); raise ValueError("Only printable ASCII is accepted; CR/LF are added internally"); raise ValueError(name + " takes no data") |
| class _Reader | 93: class _Reader: | Class/dataclass/Enum; xem methods |
| def _Reader.__init__ | 94: def __init__(self, sock, timeout, trace): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def _Reader.until | 100: def until(self, ending): | return result[:-len(ending)].decode("ascii"); raise ProtocolError("Response exceeds receive limit"); raise TimeoutError("Response deadline expired; pending RX=" + repr(bytes(self.buffer))); raise TimeoutError("Receive timed out; pending RX=" + repr(bytes(self.buffer))) from exc |
| class Client | 126: class Client: | Class/dataclass/Enum; xem methods |
| def Client.__init__ | 127: def __init__(self, ip, port=80, timeout=5.0, trace=None): | raise ValueError("Port must be 1..65535"); raise ValueError("Timeout must be &gt; 0 and &lt;= 60 seconds") |
| def Client.execute | 137: def execute(self, name, data=""): | raise ProtocolError("Handshake rejected: " + greeting); raise ProtocolError("Command rejected: " + ack); raise ProtocolError(result); raise ProtocolError("Control answer must end with CRLF") |
| def Client.execute.send | 147: def send(wire): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_camera_snapshot_move/robot/status.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/robot/status.py (53 dòng, 1571 byte) |
| PURPOSE | Giải mã RSTATS bằng fixed bit masks. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Status:1 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, word, int, isinstance, value.startswith, ValueError, is_step, bool, is_one_cycle, is_auto, is_running, is_safety_speed_operation, is_teach, is_play, is_command_remote, is_programming_pendant_hold, is_external_hold, is_command_hold, is_alarm_occurring, is_error_occurring, is_servo_on |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | self.data_1, self.data_2 |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | ValueError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 52; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Status | 1: class Status: | Class/dataclass/Enum; xem methods |
| def Status.__init__ | 3: def __init__(self, data_1, data_2): | raise ValueError('Invalid RSTATS word'); return result |
| def Status.__init__.word | 4: def word(value, maximum): | raise ValueError('Invalid RSTATS word'); return result |
| def Status.is_step | 12: def is_step(self): | return bool(self.data_1 & (1 &lt;&lt; 0)) |
| def Status.is_one_cycle | 15: def is_one_cycle(self): | return bool(self.data_1 & (1 &lt;&lt; 1)) |
| def Status.is_auto | 18: def is_auto(self): | return bool(self.data_1 & (1 &lt;&lt; 2)) |
| def Status.is_running | 21: def is_running(self): | return bool(self.data_1 & (1 &lt;&lt; 3)) |
| def Status.is_safety_speed_operation | 24: def is_safety_speed_operation(self): | return bool(self.data_1 & (1 &lt;&lt; 4)) |
| def Status.is_teach | 27: def is_teach(self): | return bool(self.data_1 & (1 &lt;&lt; 5)) |
| def Status.is_play | 30: def is_play(self): | return bool(self.data_1 & (1 &lt;&lt; 6)) |
| def Status.is_command_remote | 33: def is_command_remote(self): | return bool(self.data_1 & (1 &lt;&lt; 7)) |
| def Status.is_programming_pendant_hold | 36: def is_programming_pendant_hold(self): | return bool(self.data_2 & (1 &lt;&lt; 1)) |
| def Status.is_external_hold | 39: def is_external_hold(self): | return bool(self.data_2 & (1 &lt;&lt; 2)) |
| def Status.is_command_hold | 42: def is_command_hold(self): | return bool(self.data_2 & (1 &lt;&lt; 3)) |
| def Status.is_alarm_occurring | 45: def is_alarm_occurring(self): | return bool(self.data_2 & (1 &lt;&lt; 4)) |
| def Status.is_error_occurring | 48: def is_error_occurring(self): | return bool(self.data_2 & (1 &lt;&lt; 5)) |
| def Status.is_servo_on | 51: def is_servo_on(self): | return bool(self.data_2 & (1 &lt;&lt; 6)) |

### nx100_camera_snapshot_move/robot/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/robot/__init__.py (2 dòng, 5 byte) |
| PURPOSE | Khởi tạo namespace/package; library root có endpoint global và MOCK_RESPONSE. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100_camera_snapshot_move/vision/calibration.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/vision/calibration.py (86 dòng, 4699 byte) |
| PURPOSE | Load/validate calibration và pixel→Base ray-plane; xem chính sách offset theo project. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | InputError:8; PixelToRobot:17 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | InputError, Path, resolve, __init__, np.load, np.array, reshape, int, item, str, json.loads, np.isfinite, all, np.allclose, np.eye, np.isclose, np.linalg.det, in, min, self.report.get, get, quality_message, summary.get, check_frame, convert, not, cv2.undistortPoints, abs |
| CALLED BY | nx100_camera_snapshot_move/vision/pipeline.py |
| STATE MODIFIED | self.path, self.T, self.K, self.distortion, self.size, self.quality, self.report |
| EXTERNAL DEPENDENCIES | import json [2]; from pathlib import Path [3]; import cv2 [5]; import numpy as np [6] |
| ERROR HANDLING | InputError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 14, 30, 31, 32, 36, 69; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class InputError | 8: class InputError(ValueError): | Class/dataclass/Enum; xem methods |
| class PixelToRobot | 17: class PixelToRobot: | Class/dataclass/Enum; xem methods |
| def PixelToRobot.__init__ | 18: def __init__(self, filename): | raise InputError("T_base_camera phải là ma trận 4x4 hữu hạn."); raise InputError("T_base_camera không phải rigid transform hợp lệ."); raise InputError("Intrinsic/kích thước ảnh không hợp lệ."); raise InputError("Kết quả calib phải dùng đơn vị mm.") |
| def PixelToRobot.quality_message | 46: def quality_message(self): | return message |
| def PixelToRobot.check_frame | 57: def check_frame(self, frame): | raise InputError(f"Ảnh {width}x{height} khác calib {self.size[0]}x{self.size[1]}. " |
| def PixelToRobot.convert | 63: def convert(self, u, v, plane_z): | raise InputError("Pixel và Z phải là số hữu hạn."); raise InputError("Pixel nằm ngoài ảnh gốc."); raise InputError("Tia nhìn song song mặt phẳng Z; không xác định giao điểm."); raise InputError("Mặt phẳng nằm phía sau camera theo tia nhìn. Kiểm tra Z và calib.") |

### nx100_camera_snapshot_move/vision/camera.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/vision/camera.py (234 dòng, 11867 byte) |
| PURPOSE | Adapter MVS SDK Windows: enum/open/grab/convert/free/lifecycle. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | _InstalledSdkFinder:17; MvsCamera:29 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | _InstalledSdkFinder, __init__, folder.glob, find_spec, importlib.machinery.PathFinder.find_spec, str, threading.RLock, threading.Event, Path, os.environ.get, ProgramFiles, roots.extend, roots.append, next, is_file, struct.calcsize, not, InputError, dll.open, stream.seek, struct.unpack, stream.read, os.add_dll_directory, ct.WinDLL, sys.meta_path.insert, importlib.import_module, sys.meta_path.remove, self.module.MvCamera.MV_CC_GetSDKVersion, hasattr, self.check, self.module.MvCamera.MV_CC_Initialize, check, status, or, text, bytes, split, decode, enumerate, m.MV_CC_DEVICE_INFO_LIST, m.MvCamera.MV_CC_EnumDevices, range, ct.cast, ct.POINTER, result.append |
| CALLED BY | nx100_camera_snapshot_move/tests/conftest.py; nx100_camera_snapshot_move/vision/pipeline.py |
| STATE MODIFIED | self.folder, self.names, self.module, self.cam, self.devices, self.latest, self.thread, self.dll_directory, self.connected, self.latest_at, self.frame_id, self.sdk_frame_id, self.error, self.lock, self.stop, self.sdk_version |
| EXTERNAL DEPENDENCIES | import ctypes as ct [2]; import importlib [3]; import importlib.abc [4]; import importlib.machinery [5]; import os [6]; import struct [7]; import sys [8]; import threading [9]; import time [10]; from pathlib import Path [11]; import cv2 [12]; import numpy as np [13]; from .calibration import InputError [14] |
| ERROR HANDLING | InputError, Exception, self |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Có thể mở/cấu hình/capture camera khi gọi connect; không thực thi. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class _InstalledSdkFinder | 17: class _InstalledSdkFinder(importlib.abc.MetaPathFinder): | Class/dataclass/Enum; xem methods |
| def _InstalledSdkFinder.__init__ | 19: def __init__(self, folder): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def _InstalledSdkFinder.find_spec | 23: def find_spec(self, fullname, path=None, target=None): | return importlib.machinery.PathFinder.find_spec(fullname, [str(self.folder)]); return None |
| class MvsCamera | 29: class MvsCamera: | Class/dataclass/Enum; xem methods |
| def MvsCamera.__init__ | 30: def __init__(self, sdk_root=None): | raise InputError("Không tìm thấy Python wrapper MVS của hãng cho Windows."); raise InputError("DLL MVS khác architecture với Python.") |
| def MvsCamera.check | 82: def check(code, operation): | raise InputError(f"MVS: {operation} lỗi 0x{code & 0xFFFFFFFF:08X}; kiểm tra cáp/camera và đóng MVS nếu đang giữ camera.") |
| def MvsCamera.status | 86: def status(self): | return {"available": self.module is not None, "connected": self.connected, "sdk_version": self.sdk_version, |
| def MvsCamera.text | 92: def text(array): | return bytes(array).split(b"\0", 1)[0].decode("utf-8", errors="replace") |
| def MvsCamera.enumerate | 95: def enumerate(self): | raise InputError(self.error); raise InputError("Ngắt camera trước khi liệt kê lại."); return result |
| def MvsCamera.connect | 111: def connect(self, index): | raise InputError(self.error); raise InputError("Camera đã mở; hãy ngắt trước khi đổi camera."); raise InputError("Liệt kê và chọn camera hợp lệ trước."); raise             self.connected, self.error = True, "" |
| def MvsCamera._grab | 142: def _grab(self): | raise InputError("Mất frame/camera ngắt kết nối; kiểm tra cáp và kết nối lại."); raise InputError("Frame camera có kích thước không hợp lệ/quá lớn."); raise InputError("MVS trả buffer RGB có độ dài không đúng.") |
| def MvsCamera.frame | 186: def frame(self): | raise InputError(self.error or "Camera chưa có frame mới. Kết nối và chờ preview trước khi chụp."); return self.latest.copy() |
| def MvsCamera.sample | 192: def sample(self): | return self.frame_id, self.latest_at, self.frame() |
| def MvsCamera.disconnect | 196: def disconnect(self): | raise InputError("SDK chưa dừng lấy frame; thử ngắt lại, không giải phóng buffer khi còn đang dùng."); raise InputError(self.error) |
| def MvsCamera.close | 222: def close(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_camera_snapshot_move/vision/detector.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/vision/detector.py (35 dòng, 1546 byte) |
| PURPOSE | YOLO predict native-image bbox center/confidence/class-name rồi transform. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Detector:6 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, os.environ.setdefault, str, YOLO, detect, calibration.check_frame, self.model.predict, tuple, ValueError, float, cpu, tolist, all, math.isfinite, not, dict, item, int, calibration.convert, items.append |
| CALLED BY | nx100_camera_snapshot_move/vision/pipeline.py |
| STATE MODIFIED | self.model, self.config |
| EXTERNAL DEPENDENCIES | import math [2]; import os [3]; from ultralytics import YOLO [9] |
| ERROR HANDLING | ValueError, Exception |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 26; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Detector | 6: class Detector: | Class/dataclass/Enum; xem methods |
| def Detector.__init__ | 7: def __init__(self, model_path, config): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Detector.detect | 13: def detect(self, frame, calibration, cfg): | raise ValueError('YOLO original image size differs from calibration'); return items |

### nx100_camera_snapshot_move/vision/pipeline.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/vision/pipeline.py (147 dòng, 6528 byte) |
| PURPOSE | Vision worker/camera/model/calibration/tracker, preview và publication target. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | VisionPipeline:26 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | load_calibration, PixelToRobot, np.load, np.array_equal, ravel, or, int, InputError, hashlib.sha256, path.read_bytes, hexdigest, __init__, threading.RLock, threading.Lock, threading.Event, BoardTracker, scan, dict, MvsCamera, get, self.camera.enumerate, connect, self.thread.is_alive, Detector, self.camera.connect, self.stop.clear, threading.Thread, self.thread.start, self.auto.robot.log, connected, _work, time.monotonic, self.stop.wait, deepcopy, np.full, enumerate, items.append, float, self.camera.sample, self.calibration.check_frame, self.detector.detect, self.tracker.update, in, self.auto.publish, max |
| CALLED BY | nx100_camera_snapshot_move/app.py |
| STATE MODIFIED | self.calibration, self.mock, self.lock, self.lifecycle_lock, self.camera, self.detector, self.thread, self.stop, self.connected, self.error, self.preview, self.fps, self.frame_id, self.tracker |
| EXTERNAL DEPENDENCIES | import hashlib [1]; import threading [2]; import time [3]; from copy import deepcopy [4]; import cv2 [6]; import numpy as np [7]; from .calibration import PixelToRobot, InputError [9]; from .camera import MvsCamera [10]; from .detector import Detector [11]; from .tracker import BoardTracker [12] |
| ERROR HANDLING | InputError, Exception |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 100; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def load_calibration | 15: def load_calibration(base): | raise InputError('Intrinsic differs from Eye-to-Hand calibration'); return calibration, hashlib.sha256(path.read_bytes()).hexdigest() |
| class VisionPipeline | 26: class VisionPipeline: | Class/dataclass/Enum; xem methods |
| def VisionPipeline.__init__ | 27: def __init__(self, base, auto, calibration): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def VisionPipeline.scan | 41: def scan(self): | return [dict(index=0, name='MOCK HIKROBOT + synthetic detections')]; return self.camera.enumerate() |
| def VisionPipeline.connect | 49: def connect(self, index): | raise InputError('Disconnect camera before connecting again'); raise InputError('Mock camera index must be 0'); raise InputError('Invalid calibration'); raise InputError('Scan camera first') |
| def VisionPipeline._work | 69: def _work(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def VisionPipeline._render | 112: def _render(self, frame, items): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def VisionPipeline.status | 125: def status(self): | return dict(connected=self.connected, fps=round(self.fps, 1), error=self.error, |
| def VisionPipeline.disconnect | 129: def disconnect(self): | raise InputError('Inference still running; wait before disconnecting again') |
| def VisionPipeline.close | 143: def close(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_camera_snapshot_move/vision/target.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/vision/target.py (17 dòng, 355 byte) |
| PURPOSE | Dataclass Target bất biến cho snapshot. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Target:6 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | dataclass |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from dataclasses import dataclass [2] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Target | 6: class Target: | Class/dataclass/Enum; xem methods |

### nx100_camera_snapshot_move/vision/tracker.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/vision/tracker.py (71 dòng, 3455 byte) |
| PURPOSE | Greedy bbox association, uncertain, reserved ID10 s và instance generation. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | BoardTracker:6 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, match_score, max, min, math.hypot, update, time.monotonic, self.tracks.items, enumerate, self.match_score, candidates.append, set, any, and, abs, sorted, assigned_ids.add, assigned_indices.add, range, len, reserved_ids.add, self.tracks.get, dict |
| CALLED BY | nx100_camera_snapshot_move/vision/pipeline.py |
| STATE MODIFIED | self.missing_timeout, self.tracks, self.generation |
| EXTERNAL DEPENDENCIES | import math [2]; import time [3] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 23, 24, 25; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class BoardTracker | 6: class BoardTracker: | Class/dataclass/Enum; xem methods |
| def BoardTracker.__init__ | 7: def __init__(self, missing_timeout=10.0): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def BoardTracker.match_score | 13: def match_score(previous, current): | return None; return None; return None; return iou + .2 * (1 - min(relative_distance, 1)) |
| def BoardTracker.update | 30: def update(self, detections, now=None): | return sorted(detections, key=lambda item: item["id"]) |

### nx100_camera_snapshot_move/vision/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/vision/__init__.py (2 dòng, 5 byte) |
| PURPOSE | Khởi tạo namespace/package; library root có endpoint global và MOCK_RESPONSE. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100_camera_snapshot_move/workflow/snapshot_move.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/workflow/snapshot_move.py (388 dòng, 19648 byte) |
| PURPOSE | Lưu scene target, batch/fingerprint, manual send và completion/uncertain recovery. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | SavedTarget:19; SnapshotMove:29 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, threading.RLock, uuid.uuid4, threading.Event, self._restore, cfg, fingerprint, dict, self.config.get, hashlib.sha256, json.dumps, encode, hexdigest, _dump, asdict, _parse, deepcopy, value.pop, tuple, SavedTarget, Target, len, all, math.isfinite, any, abs, in, ValueError, _restore, self.storage.exists, json.loads, self.storage.read_text, self._parse, max, int, bool, content.get, _persist, self._dump, self.storage.parent.mkdir, self.storage.with_suffix, temporary.open, json.dump, stream.flush, os.fsync |
| CALLED BY | nx100_camera_snapshot_move/app.py; nx100_camera_snapshot_move/tests/conftest.py; nx100_camera_snapshot_move/tests/test_snapshot_move.py |
| STATE MODIFIED | self.calibration_id, self.clock, self.storage, self.lock, self.version, self.session, self.vision_ready, self.frame_time, self.completed, self.batch_id, self.batch_fingerprint, self.active_id, self.fault, self.message, self.hold_intent, self.shutdown, self.thread, self.saved, self.items, self.targets |
| EXTERNAL DEPENDENCIES | import hashlib [2]; import json [3]; import math [4]; import os [5]; import threading [6]; import time [7]; import uuid [8]; from copy import deepcopy [9]; from dataclasses import asdict, dataclass [10]; from datetime import datetime, timezone [11]; from robot.controller import ControlError [13]; from vision.target import Target [14]; from .target_manager import eligibility, in_workspace [15] |
| ERROR HANDLING | ValueError, Exception, ControlError, self, wire_ready |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class SavedTarget | 19: class SavedTarget: | Class/dataclass/Enum; xem methods |
| class SnapshotMove | 29: class SnapshotMove: | Class/dataclass/Enum; xem methods |
| def SnapshotMove.__init__ | 30: def __init__(self, robot, config, calibration_id, storage, calibration_valid=True, clock=time.monotonic): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def SnapshotMove.cfg | 51: def cfg(self): | return self.config['tracking'] |
| def SnapshotMove.fingerprint | 54: def fingerprint(self): | return hashlib.sha256(json.dumps(content, sort_keys=True, allow_nan=False).encode()).hexdigest() |
| def SnapshotMove._dump | 59: def _dump(self, record): | return asdict(record) |
| def SnapshotMove._parse | 62: def _parse(self, value): | raise ValueError('Snapshot không hợp lệ'); return record |
| def SnapshotMove._restore | 75: def _restore(self): | return         try:; raise ValueError('Sai định dạng hoặc chế độ snapshot') |
| def SnapshotMove._persist | 99: def _persist(self): | raise ControlError('STORAGE_ERROR', f'Không lưu được tọa độ: {exc}', 503) from exc |
| def SnapshotMove.publish | 114: def publish(self, items, frame_id, stamp, version, ready=True): | return             self.vision_ready, self.frame_time = ready, stamp |
| def SnapshotMove.vision_failed | 136: def vision_failed(self, message): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def SnapshotMove._busy | 144: def _busy(self): | raise ControlError('MOTION_ACTIVE', 'Đang MOVE; chờ xác minh hoàn thành trước.') |
| def SnapshotMove._distance | 148: def _distance(self, target, session): | return eligibility(target, own, last, self.cfg['minimum_move_distance_mm'], |
| def SnapshotMove.capture | 155: def capture(self): | raise ControlError('CAMERA_NOT_READY', 'Camera/calibration chưa sẵn sàng.'); raise ControlError('NO_DETECTION', 'YOLO chưa phát hiện vật có tọa độ hợp lệ để lưu.'); raise             self.message = f'Đã lưu {len(self.saved)} target. Ngắt camera, đổi dây sang robot rồi CONNECT ROBOT.'; return self.snapshot() |
| def SnapshotMove._saved_eligibility | 178: def _saved_eligibility(self, record): | return False, record.message or record.status, None, None; return False, 'Có MOVE chưa xác minh; không gửi tiếp.', None, None; return False, 'Đang MOVE', None, None; return False, 'Cấu hình/calibration đã đổi; cần chụp và lưu lại.', None, None |
| def SnapshotMove._next | 189: def _next(self): | return min((v for v in self.saved if self._saved_eligibility(v)[0]), |
| def SnapshotMove._guard | 193: def _guard(self, record, pose): | raise ControlError('HOLD_PENDING', 'Đã yêu cầu HOLD'); raise ControlError('SNAPSHOT_CHANGED', 'Snapshot/calibration không còn hợp lệ.'); raise ControlError('DISTANCE_BLOCKED', 'Target không đạt điều kiện khoảng cách/workspace.'); raise ControlError('PATH_BLOCKED', 'Vị trí hiện tại ngoài workspace cấu hình.') |
| def SnapshotMove.send | 208: def send(self, batch_id, record_id): | raise ControlError('STALE_REQUEST', 'Bộ tọa độ đã đổi; tải lại giao diện.'); raise ControlError('NO_SAVED_TARGET', 'Không có tọa độ đã lưu hợp lệ để gửi.'); raise ControlError('STALE_REQUEST', 'ID được chọn đã đổi; tải lại trạng thái.'); raise ControlError('DISCONNECTED', 'Đổi dây và CONNECT ROBOT trước khi gửi.') |
| def SnapshotMove.send.guard | 228: def guard(pose): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def SnapshotMove.tick | 250: def tick(self): | return             record = next(v for v in self.saved if v.record_id == self.active_id) |
| def SnapshotMove.connect_robot | 271: def connect_robot(self, ip, port): | return self.robot.read_status(); raise ControlError('ALREADY_CONNECTED', 'Ngắt robot trước khi đổi địa chỉ.'); return self.robot.connect(ip, port) |
| def SnapshotMove.disconnect_robot | 281: def disconnect_robot(self): | return self.robot.disconnect() |
| def SnapshotMove.acknowledge_fault | 286: def acknowledge_fault(self): | raise ControlError('ROBOT_NOT_READY', 'Robot chưa dừng hoặc còn alarm/HOLD/servo/remote chưa sẵn sàng.') |
| def SnapshotMove.hold | 299: def hold(self): | raise ControlError('DISCONNECTED', 'Chưa kết nối robot; không gửi HOLD.'); return self.robot.hold() |
| def SnapshotMove.release_hold | 313: def release_hold(self): | return result |
| def SnapshotMove.update_config | 325: def update_config(self, changes): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def SnapshotMove.snapshot | 335: def snapshot(self): | return dict(phase='FAULT' if self.fault else 'MOVING' if self.active_id else |
| def SnapshotMove.start_worker | 370: def start_worker(self): | return         def work(): |
| def SnapshotMove.start_worker.work | 373: def work(): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def SnapshotMove.close | 384: def close(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_camera_snapshot_move/workflow/target_manager.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/workflow/target_manager.py (32 dòng, 1676 byte) |
| PURPOSE | Selection thuần theo workspace/khoảng cách/ID; không trực tiếp gửi wire. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | in_workspace, len, all, isfinite, zip, eligibility, dist, completed_by_instance.get, select_next_target, min |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from math import dist, isfinite [2] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def in_workspace | 5: def in_workspace(xyz, workspace): | return len(xyz) == 3 and all(isfinite(v) and workspace[a][0] &lt;= v &lt;= workspace[a][1] |
| def eligibility | 10: def eligibility(target, completed_by_instance, last_completed, minimum_distance_mm, now, max_age, workspace): | return False, 'stale frame', None, None; return False, 'outside workspace', None, None; return False, 'distance from last MOVE &lt;= minimum', global_distance, own_distance; return False, 'same track unchanged', global_distance, own_distance |
| def select_next_target | 26: def select_next_target(tracked_objects, completed_targets_by_id, last_completed_robot_target, minimum_distance_mm=50.0, *, now, max_age, workspace): | return min(eligible, key=lambda t: t.object_id, default=None) |

### nx100_camera_snapshot_move/workflow/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_camera_snapshot_move/workflow/__init__.py (2 dòng, 5 byte) |
| PURPOSE | Khởi tạo namespace/package; library root có endpoint global và MOCK_RESPONSE. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100_full_cycle_v1/app.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/app.py (258 dòng, 11140 byte) |
| PURPOSE | Entry point và HTTP API/HMI; tạo controller/workflow và quản lý lifecycle. |
| ENTRY POINT | Có __main__ guard; xem phần entry point/deployment |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Path, resolve, project_python.is_file, project_python.resolve, SystemExit, subprocess.call, str, create_app, load_config, threading.RLock, os.environ.get, in, len, RuntimeError, Cycle, lifespan, cycle.close, FastAPI, app.add_middleware, app.middleware, access, JSONResponse, request.headers.get, split, rstrip, call_next, app.exception_handler, runtime_error, value_error, authorized, request.cookies.get, time.monotonic, HTTPException, body.get, isinstance, cycle.journal.state.get, cycle.journal.save, app.get, index, FileResponse, owned, app.mount, StaticFiles, app.post, claim |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from pathlib import Path [5]; import subprocess [6]; import sys [7]; import argparse [14]; from contextlib import asynccontextmanager [15]; import logging [16]; from logging.handlers import RotatingFileHandler [17]; import os [18]; import secrets [19]; import threading [20]; import time [21]; from fastapi import FastAPI, Request, HTTPException [24]; from fastapi.responses import FileResponse, Response, JSONResponse [25]; from fastapi.staticfiles import StaticFiles [26]; from starlette.middleware.trustedhost import TrustedHostMiddleware [27]; from settings import ROOT, owned, load_config [31]; from launcher import APPLICATION_ID, existing_real_hmi, hmi_url, open_edge, open_when_ready [32]; from workflow.cycle import Cycle [34]; import uvicorn [249] |
| ERROR HANDLING | SystemExit, ImportError, RuntimeError, HTTPException, ValueError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 185; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Entry/API có thể tạo worker/runtime file và gọi workflow; không tự coi import là read-only. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def create_app | 39: def create_app(mock=False, config=None, journal_path=None): | raise RuntimeError('LAN yêu cầu NX100_HMI_TOKEN tối thiểu 24 ký tự và allowed_clients/allowed_hosts cụ thể'); return JSONResponse({'detail':'Client không được phép'},status_code=403); return JSONResponse({'detail':'Cần application/json'},status_code=415); return JSONResponse({'detail':'Origin bị từ chối'},status_code=403) |
| def create_app.lifespan | 49: async def lifespan(app): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def create_app.access | 58: async def access(request,call_next): | return JSONResponse({'detail':'Client không được phép'},status_code=403); return JSONResponse({'detail':'Cần application/json'},status_code=415); return JSONResponse({'detail':'Origin bị từ chối'},status_code=403); return response |
| def create_app.runtime_error | 74: async def runtime_error(request,exc): | return JSONResponse({'detail':str(exc)},status_code=409) |
| def create_app.value_error | 78: async def value_error(request,exc): | return JSONResponse({'detail':str(exc)},status_code=422) |
| def create_app.authorized | 81: def authorized(request, body, stale=True): | raise HTTPException(423,'Phiên HMI không giữ quyền điều khiển'); raise HTTPException(409,'Yêu cầu cũ; tải lại trạng thái'); raise HTTPException(422,'request_id không hợp lệ'); raise HTTPException(409,'Yêu cầu đã xử lý; không tự retry') |
| def create_app.index | 101: def index(): | return FileResponse(owned('templates/index.html')) |
| def create_app.claim | 107: def claim(request:Request, body:dict): | raise HTTPException(403,'Mã điều khiển không hợp lệ'); raise HTTPException(403,'Chưa cấu hình mã điều khiển LAN'); raise HTTPException(423,'Một phiên HMI khác đang điều khiển'); return response |
| def create_app.state | 122: def state(request:Request): | return {**cycle.snapshot(),'control':control,'application_id':APPLICATION_ID} |
| def create_app.preview | 130: def preview(): | raise HTTPException(503,'Camera chưa có frame mới'); return Response(data,media_type='image/jpeg') |
| def create_app.laser_status | 138: def laser_status(): | return {'laser_in1':'UNKNOWN' if value is None else 'ON' if value else 'OFF','mapping':'20050 → IN#(1)', |
| def create_app.connect | 147: def connect(request:Request,body:dict): | return cycle.snapshot() |
| def create_app.start | 154: def start(request:Request,body:dict): | return cycle.snapshot() |
| def create_app.hold | 161: def hold(request:Request,body:dict): | return cycle.snapshot() |
| def create_app.acknowledge | 167: def acknowledge(request:Request,body:dict): | return cycle.snapshot() |
| def create_app.release_hold | 174: def release_hold(request:Request,body:dict): | return cycle.snapshot() |
| def create_app.vacuum | 181: def vacuum(channel:int,request:Request,body:dict): | raise ValueError('Cần channel 1/2 và on boolean'); return cycle.snapshot() |
| def create_app.configure | 190: def configure(request:Request,body:dict): | return cycle.snapshot() |
| def create_app.drop_settings | 197: def drop_settings(request:Request,body:dict): | return cycle.snapshot() |
| def create_app.set_stack_count | 204: def set_stack_count(request:Request,body:dict): | return cycle.snapshot() |
| def create_app.reset_stack | 211: def reset_stack(request:Request,body:dict): | return cycle.snapshot() |
| def create_app.confirm_drop | 218: def confirm_drop(request:Request,body:dict): | return cycle.snapshot() |
| def main | 227: def main(): | return     import uvicorn |

### nx100_full_cycle_v1/launcher.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/launcher.py (52 dòng, 1500 byte) |
| PURPOSE | Nhận diện HMI REAL đã chạy, URL và mở Edge sau server ready. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | hmi_url, in, existing_real_hmi, urllib.request.urlopen, json.load, state.get, open_edge, shutil.which, PROGRAMFILES, os.environ.get, Path, candidate.is_file, str, logging.warning, subprocess.Popen, logging.exception, open_when_ready, time.sleep |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | import json [2]; import logging [3]; import os [4]; from pathlib import Path [5]; import shutil [6]; import subprocess [7]; import time [8]; import urllib.request [9] |
| ERROR HANDLING | OSError |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def hmi_url | 14: def hmi_url(host,port): | return f'http://{"127.0.0.1" if host in ("0.0.0.0","::") else host}:{port}' |
| def existing_real_hmi | 18: def existing_real_hmi(url): | return state.get('application_id')==APPLICATION_ID and state.get('mode')=='REAL'; return False |
| def open_edge | 27: def open_edge(url): | return     try: |
| def open_when_ready | 46: def open_when_ready(server,url): | return         time.sleep(.1) |

### nx100_full_cycle_v1/settings.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/settings.py (37 dòng, 1312 byte) |
| PURPOSE | Đường dẫn owned, load config, validation operator settings và fingerprint. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Path, resolve, owned, path.is_relative_to, ValueError, load_config, json.loads, read_text, validate_settings, isinstance, set, values.items, math.isfinite, fingerprint, hashlib.sha256, json.dumps, encode, hexdigest |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | import hashlib [2]; import json [3]; import math [4]; from pathlib import Path [5] |
| ERROR HANDLING | ValueError |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def owned | 13: def owned(relative): | raise ValueError('Resource must be inside application root'); return path |
| def load_config | 20: def load_config(): | return json.loads(owned('config.json').read_text(encoding='utf-8')) |
| def validate_settings | 24: def validate_settings(values): | raise ValueError('Chỉ cho phép Plane Z, Z_safe, speed, RX/RY/RZ'); raise ValueError(f'{key}: cần số hữu hạn'); raise ValueError(f'{key}: ngoài giới hạn {LIMITS[key]}'); return values |
| def fingerprint | 35: def fingerprint(config): | return hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest() |

### nx100_full_cycle_v1/robot/cartesian.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/robot/cartesian.py (63 dòng, 2937 byte) |
| PURPOSE | Pose Cartesian có metadata, reference check, Decimal coordinate và payload motion. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Pose:9 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | dataclass, parse, tuple, item.strip, raw.split, len, ProtocolError, encode_command, join, str, cls, verify_unchanged, list, range, Decimal, abs, coordinate, value.strip, number.is_finite, ValueError, number.quantize, m, format, build_move, isinstance, speed.strip, else, read_pose, Pose.parse, client.execute |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from dataclasses import dataclass [2]; from decimal import Decimal, InvalidOperation [3]; from .protocol import encode_command, ProtocolError [5] |
| ERROR HANDLING | ProtocolError, ValueError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 3, 28, 29, 36, 37, 39; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Pose | 9: class Pose: | Class/dataclass/Enum; xem methods |
| def Pose.parse | 14: def parse(cls, raw): | raise ProtocolError('RPOSC 0,1 cần đủ 14 giá trị gồm tư thế, tool và trục ngoài; nhận: ' + raw); raise ProtocolError('Dữ liệu vị trí chưa hợp lệ để tạo lệnh: ' + str(exc)) from exc; return cls(fields) |
| def Pose.verify_unchanged | 24: def verify_unchanged(self, current): | raise ProtocolError('Tool hoặc tư thế robot đã thay đổi; lấy lại vị trí hiện tại'); raise ProtocolError('Robot đã đổi vị trí kể từ lần lấy tọa độ; lấy lại vị trí trước khi gửi đích mới') |
| def coordinate | 33: def coordinate(value): | raise ValueError('Tọa độ phải là số hữu hạn trong phạm vi biểu diễn'); raise ValueError('X/Y/Z chỉ nhận tối đa 3 chữ số sau dấu chấm (mm)'); return format(fixed, '.3f'); raise ValueError('Tọa độ phải dùng số và dấu chấm thập phân') from exc |
| def build_move | 47: def build_move(command, speed, xyz, pose): | raise ValueError('Chọn MOVL/MOVJ và lấy vị trí từ robot trước'); raise ValueError('Cần nhập đủ XYZ hoặc XYZ/Rx/Ry/Rz'); return data |
| def read_pose | 61: def read_pose(client): | return Pose.parse(client.execute('RPOSC', '0,1')) |

### nx100_full_cycle_v1/robot/controller.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/robot/controller.py (136 dòng, 6116 byte) |
| PURPOSE | Robot adapter/controller, preflight, serialized IO, pose/status/motion monitoring. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Controller:12 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, threading.RLock, tuple, get, values, else, MockClient, Client, dict, connect, self.status, self.pose, self.client.execute, status, re.fullmatch, RuntimeError, Status, map, raw.split, s.is_servo_on, s.is_command_remote, s.is_play, s.is_teach, s.is_running, s.is_alarm_occurring, s.is_error_occurring, s.is_command_hold, s.is_external_hold, s.is_programming_pendant_hold, pose, read_pose, zip, laser, io.laser_sample, move, build_move, str, hold, release_hold, set_vacuum, vacuum.write, start_hand_job, vacuum.validate_mapping, current_job, p.strip |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | self.mock, self.lock, self.connected, self.client, self.vacuum, self.laser_raw_byte, self.vacuum_raw_byte, self.vacuum_config, self.laser_config |
| EXTERNAL DEPENDENCIES | import re [2]; import threading [3]; from settings import AXES [4]; from .protocol import Client [5]; from .mock import MockClient [6]; from .status import Status [7]; from .cartesian import read_pose, build_move [8]; from . import io, job_control, vacuum [9] |
| ERROR HANDLING | RuntimeError, Exception, def |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Controller | 12: class Controller: | Class/dataclass/Enum; xem methods |
| def Controller.__init__ | 13: def __init__(self, config, mock): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Controller.connect | 27: def connect(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Controller.status | 34: def status(self): | raise RuntimeError('RSTATS malformed'); return dict(servo=s.is_servo_on(), remote=s.is_command_remote(), play=s.is_play(), |
| def Controller.pose | 45: def pose(self): | return dict(zip(AXES, map(float, pose.fields[:6]))), pose |
| def Controller.laser | 50: def laser(self): | return value; raise |
| def Controller.move | 59: def move(self, target, speed, reference): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Controller.hold | 63: def hold(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Controller.release_hold | 67: def release_hold(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Controller.set_vacuum | 71: def set_vacuum(self, channel, on): | raise |
| def Controller.start_hand_job | 79: def start_hand_job(self,channel,on,config=None): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Controller.current_job | 86: def current_job(self): | raise RuntimeError('RJSEQ không hợp lệ: '+raw); return parts[0] |
| def Controller.observe | 94: def observe(self): | raise RuntimeError('; '.join(errors.values())); return dict(flags=flags, position=pose, laser=laser, laser_raw_byte=self.laser_raw_byte, |

### nx100_full_cycle_v1/robot/io.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/robot/io.py (23 dòng, 815 byte) |
| PURPOSE | Đọc digital byte/laser, lỗi không bị chuyển thành OFF. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | read_byte, client.execute, re.fullmatch, int, RuntimeError, laser_sample, bool, laser |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | import re [2] |
| ERROR HANDLING | RuntimeError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 16; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def read_byte | 5: def read_byte(client, start): | raise RuntimeError('IOREAD: phản hồi không hợp lệ'); return int(raw) |
| def laser_sample | 12: def laser_sample(client, cfg): | raise RuntimeError('Laser mapping không hợp lệ'); return bool(raw & (1 &lt;&lt; cfg['bit'])) == cfg['active_high'], raw |
| def laser | 19: def laser(client, cfg): | return laser_sample(client, cfg)[0] |

### nx100_full_cycle_v1/robot/job_control.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/robot/job_control.py (30 dòng, 1106 byte) |
| PURPOSE | RJDIR/RJSEQ/START MOVEUNTI và proof stop-cause (mock-only). |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | exists, client.execute, name.strip, re.split, any, re.fullmatch, RuntimeError, current, raw.split, len, all, v.strip, isdigit, start, stop_reason_proven |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | import re [2] |
| ERROR HANDLING | RuntimeError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 1; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def exists | 5: def exists(client): | raise RuntimeError('RJDIR framing/names chưa được xác minh'); return 'MOVEUNTI' in names |
| def current | 13: def current(client): | raise RuntimeError('RJSEQ không xác nhận MOVEUNTI'); return raw |
| def start | 21: def start(client): | return client.execute('START', 'MOVEUNTI') |
| def stop_reason_proven | 25: def stop_reason_proven(robot, observed): | return robot.mock and observed['running_seen'] and observed['laser_edge'] |

### nx100_full_cycle_v1/robot/mock.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/robot/mock.py (95 dòng, 4167 byte) |
| PURPOSE | Phản hồi/diễn tiến mô phỏng; không đại diện physics hoặc dữ liệu thiết bị thật. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | MockClient:7 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, set, execute, self.commands.append, OutcomeUnknown, time.monotonic, list, map, join, data.split, str, int, data.startswith, RuntimeError, ValueError |
| CALLED BY | nx100_full_cycle_v1/robot/controller.py |
| STATE MODIFIED | self.pose, self.posture, self.running, self.holding, self.alarm, self.laser, self.available_job, self.scenario, self.commands, self.deadline, self.activity, self.byte, self.pressure_inputs, self.hand_jobs, self.last_job, self.drop_pose, self.p010, self.p009, self.drop_uses_p010, self.target |
| EXTERNAL DEPENDENCIES | import time [2]; from settings import AXES [3]; from .protocol import OutcomeUnknown [4] |
| ERROR HANDLING | OutcomeUnknown, RuntimeError, ValueError |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Chỉ mô phỏng; không suy trạng thái thiết bị thật. |
| KNOWN LIMITATIONS | Không mô phỏng collision/pressure/cell safety. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class MockClient | 7: class MockClient: | Class/dataclass/Enum; xem methods |
| def MockClient.__init__ | 8: def __init__(self,hand_jobs=()): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def MockClient.execute | 26: def execute(self, name, data=''): | raise OutcomeUnknown('TCP lost; robot may be moving'); return f'{194 + (8 if self.running else 0)},{64 + (8 if self.holding else 0) + (16 if self.alarm else 0)}'; return ','.join(map(str, self.pose + [self.posture, self.tool] + [0]*6)); return ','.join(['0']*6) |

### nx100_full_cycle_v1/robot/position_variable.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/robot/position_variable.py (31 dòng, 1180 byte) |
| PURPOSE | P009/P010 Cartesian BASE, thay Z và xác minh SAVEV readback. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | parse_p010, tuple, v.strip, raw.split, encode_command, join, ProtocolError, str, with_z, Decimal, value.is_finite, value.quantize, ValueError, format, dict, zip, map, verify_p010, any |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from decimal import Decimal [2]; from settings import AXES [3]; from .protocol import encode_command, ProtocolError [4] |
| ERROR HANDLING | ValueError, ProtocolError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 2, 18, 19, 29; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def parse_p010 | 7: def parse_p010(raw,source='P010'): | raise ProtocolError(source+' cần dữ liệu Cartesian BASE hợp lệ: '+str(exc)) from exc; return fields |
| def with_z | 17: def with_z(fields,z): | raise ValueError('Z P010 cần số hữu hạn, tối đa 3 chữ số thập phân'); return result,payload,dict(zip(AXES,map(float,result[2:8]))) |
| def verify_p010 | 27: def verify_p010(expected,raw): | raise ProtocolError('Đọc lại P010 không khớp; không gọi DROP') |

### nx100_full_cycle_v1/robot/protocol.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/robot/protocol.py (258 dòng, 11940 byte) |
| PURPOSE | Validate command và encode/receive ASCII NX100; serialized single-command socket. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | ProtocolError:14; OutcomeUnknown:18; _Reader:131; Client:188 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | ProtocolError, OutcomeUnknown, threading.Lock, _integer, re.fullmatch, ValueError, int, _number, number, float, math.isfinite, encode_command, and, isinstance, any, ord, item.strip, data.split, len, join, or, in, encode, __init__, bytearray, until_closed, answer, packets, time.monotonic, TimeoutError, self.sock.settimeout, self.sock.recv, bytes, self.buffer.clear, wire.endswith, wire.decode, self.trace, self.buffer.extend, until, self.buffer.find, decode, repr, tuple, str, ipaddress.IPv4Address |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | self.sock, self.buffer, self.timeout, self.trace, self.allowed_start_jobs, self.ip, self.port |
| EXTERNAL DEPENDENCIES | import ipaddress [6]; import math [7]; import re [8]; import socket [9]; import threading [10]; import time [11] |
| ERROR HANDLING | ValueError, ProtocolError, TimeoutError, OutcomeUnknown |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Có đường gửi NX TCP khi hàm được gọi; không được gọi trong audit. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class ProtocolError | 14: class ProtocolError(RuntimeError): | Class/dataclass/Enum; xem methods |
| class OutcomeUnknown | 18: class OutcomeUnknown(ProtocolError): | Class/dataclass/Enum; xem methods |
| def _integer | 27: def _integer(value, lower, upper): | raise ValueError("Expected an unsigned decimal integer"); raise ValueError("Integer outside allowed range"); return number |
| def _number | 36: def _number(value): | raise ValueError("Expected a finite decimal number (no exponent)"); raise ValueError("Non-finite number"); return result |
| def encode_command | 45: def encode_command(name, data="", allowed_start_jobs=()): | raise ValueError('Command outside Auto Pick V1 scope'); raise ValueError('START requires an explicitly configured JOB; never resume'); raise ValueError("Command and data must be strings"); raise ValueError("Only printable ASCII is accepted; CR/LF are added internally") |
| class _Reader | 131: class _Reader: | Class/dataclass/Enum; xem methods |
| def _Reader.__init__ | 132: def __init__(self, sock, timeout, trace): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def _Reader.until_closed | 138: def until_closed(self): | raise ProtocolError('Response exceeds receive limit'); raise TimeoutError('Incomplete directory: socket did not close before deadline'); raise ProtocolError('Incomplete directory: missing final CR'); return wire.decode('ascii') |
| def _Reader.until | 162: def until(self, ending): | return result[:-len(ending)].decode("ascii"); raise ProtocolError("Response exceeds receive limit"); raise TimeoutError("Response deadline expired; pending RX=" + repr(bytes(self.buffer))); raise TimeoutError("Receive timed out; pending RX=" + repr(bytes(self.buffer))) from exc |
| class Client | 188: class Client: | Class/dataclass/Enum; xem methods |
| def Client.__init__ | 189: def __init__(self, ip, port=80, timeout=5.0, trace=None, allowed_start_jobs=()): | raise ValueError('Invalid configured JOB name'); raise ValueError("Port must be 1..65535"); raise ValueError("Timeout must be &gt; 0 and &lt;= 60 seconds") |
| def Client.execute | 202: def execute(self, name, data=""): | raise ProtocolError("Handshake rejected: " + greeting); raise ProtocolError("Command rejected: " + ack); raise ProtocolError(result); raise ProtocolError("Control answer must end with CRLF") |
| def Client.execute.send | 212: def send(wire): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_full_cycle_v1/robot/status.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/robot/status.py (53 dòng, 1571 byte) |
| PURPOSE | Giải mã RSTATS bằng fixed bit masks. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Status:1 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, word, int, isinstance, value.startswith, ValueError, is_step, bool, is_one_cycle, is_auto, is_running, is_safety_speed_operation, is_teach, is_play, is_command_remote, is_programming_pendant_hold, is_external_hold, is_command_hold, is_alarm_occurring, is_error_occurring, is_servo_on |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | self.data_1, self.data_2 |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | ValueError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 52; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Status | 1: class Status: | Class/dataclass/Enum; xem methods |
| def Status.__init__ | 3: def __init__(self, data_1, data_2): | raise ValueError('Invalid RSTATS word'); return result |
| def Status.__init__.word | 4: def word(value, maximum): | raise ValueError('Invalid RSTATS word'); return result |
| def Status.is_step | 12: def is_step(self): | return bool(self.data_1 & (1 &lt;&lt; 0)) |
| def Status.is_one_cycle | 15: def is_one_cycle(self): | return bool(self.data_1 & (1 &lt;&lt; 1)) |
| def Status.is_auto | 18: def is_auto(self): | return bool(self.data_1 & (1 &lt;&lt; 2)) |
| def Status.is_running | 21: def is_running(self): | return bool(self.data_1 & (1 &lt;&lt; 3)) |
| def Status.is_safety_speed_operation | 24: def is_safety_speed_operation(self): | return bool(self.data_1 & (1 &lt;&lt; 4)) |
| def Status.is_teach | 27: def is_teach(self): | return bool(self.data_1 & (1 &lt;&lt; 5)) |
| def Status.is_play | 30: def is_play(self): | return bool(self.data_1 & (1 &lt;&lt; 6)) |
| def Status.is_command_remote | 33: def is_command_remote(self): | return bool(self.data_1 & (1 &lt;&lt; 7)) |
| def Status.is_programming_pendant_hold | 36: def is_programming_pendant_hold(self): | return bool(self.data_2 & (1 &lt;&lt; 1)) |
| def Status.is_external_hold | 39: def is_external_hold(self): | return bool(self.data_2 & (1 &lt;&lt; 2)) |
| def Status.is_command_hold | 42: def is_command_hold(self): | return bool(self.data_2 & (1 &lt;&lt; 3)) |
| def Status.is_alarm_occurring | 45: def is_alarm_occurring(self): | return bool(self.data_2 & (1 &lt;&lt; 4)) |
| def Status.is_error_occurring | 48: def is_error_occurring(self): | return bool(self.data_2 & (1 &lt;&lt; 5)) |
| def Status.is_servo_on | 51: def is_servo_on(self): | return bool(self.data_2 & (1 &lt;&lt; 6)) |

### nx100_full_cycle_v1/robot/vacuum.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/robot/vacuum.py (69 dòng, 3384 byte) |
| PURPOSE | Validate mapping, read contacts và nhánh network byte write/readback. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | validate_mapping, cfg.get, set, len, names.values, any, isinstance, re.fullmatch, RuntimeError, in, type, monitor_inputs, ValueError, bool, read_outputs, read_byte, write, zip, client.execute |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | import re [2]; from .io import read_byte [3] |
| ERROR HANDLING | RuntimeError, ValueError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 32, 51, 58; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def validate_mapping | 6: def validate_mapping(cfg): | raise RuntimeError('Chưa xác nhận đúng bốn JOB HAND ON/OFF trên pendant'); return     if cfg.get('start') is None or any(b is None for b in cfg.get('bits',[])):; raise RuntimeError('Đã xác định OUTPUT 30050/30051; còn thiếu network input 22xxx liên kết tới hai relay để gửi ON/OFF qua TCP.'); raise RuntimeError('HAND REAL bị khóa: chưa xác minh mapping, cực tính, loại HAND và quyền sở hữu byte') |
| def monitor_inputs | 25: def monitor_inputs(raw_byte, byte_start, contacts): | return [None,None]; raise ValueError('Địa chỉ I/O vacuum không thuộc byte đang đọc'); return [None,None]; return [bool(raw_byte & (1&lt;&lt;(a%10))) for a in contacts] |
| def read_outputs | 35: def read_outputs(client,cfg): | return None,None; return monitor_inputs(raw,start,contacts),raw |
| def write | 46: def write(client, cfg, channel, on): | raise RuntimeError('HAND JOB phải được theo dõi qua workflow, không dùng IOWRITE'); raise RuntimeError('HAND readback không khớp; kết quả chưa xác định'); raise RuntimeError('Network input đã đổi nhưng OUTPUT relay chưa đúng yêu cầu; kiểm tra mapping, không tự gửi lại'); return outputs |

### nx100_full_cycle_v1/robot/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/robot/__init__.py (1 dòng, 0 byte) |
| PURPOSE | Khởi tạo namespace/package; library root có endpoint global và MOCK_RESPONSE. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100_full_cycle_v1/vision/calibration.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/vision/calibration.py (86 dòng, 4699 byte) |
| PURPOSE | Load/validate calibration và pixel→Base ray-plane; xem chính sách offset theo project. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | InputError:8; PixelToRobot:17 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | InputError, Path, resolve, __init__, np.load, np.array, reshape, int, item, str, json.loads, np.isfinite, all, np.allclose, np.eye, np.isclose, np.linalg.det, in, min, self.report.get, get, quality_message, summary.get, check_frame, convert, not, cv2.undistortPoints, abs |
| CALLED BY | nx100_full_cycle_v1/tests/test_vision.py; nx100_full_cycle_v1/vision/pipeline.py |
| STATE MODIFIED | self.path, self.T, self.K, self.distortion, self.size, self.quality, self.report |
| EXTERNAL DEPENDENCIES | import json [2]; from pathlib import Path [3]; import cv2 [5]; import numpy as np [6] |
| ERROR HANDLING | InputError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 14, 30, 31, 32, 36, 69; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class InputError | 8: class InputError(ValueError): | Class/dataclass/Enum; xem methods |
| class PixelToRobot | 17: class PixelToRobot: | Class/dataclass/Enum; xem methods |
| def PixelToRobot.__init__ | 18: def __init__(self, filename): | raise InputError("T_base_camera phải là ma trận 4x4 hữu hạn."); raise InputError("T_base_camera không phải rigid transform hợp lệ."); raise InputError("Intrinsic/kích thước ảnh không hợp lệ."); raise InputError("Kết quả calib phải dùng đơn vị mm.") |
| def PixelToRobot.quality_message | 46: def quality_message(self): | return message |
| def PixelToRobot.check_frame | 57: def check_frame(self, frame): | raise InputError(f"Ảnh {width}x{height} khác calib {self.size[0]}x{self.size[1]}. " |
| def PixelToRobot.convert | 63: def convert(self, u, v, plane_z): | raise InputError("Pixel và Z phải là số hữu hạn."); raise InputError("Pixel nằm ngoài ảnh gốc."); raise InputError("Tia nhìn song song mặt phẳng Z; không xác định giao điểm."); raise InputError("Mặt phẳng nằm phía sau camera theo tia nhìn. Kiểm tra Z và calib.") |

### nx100_full_cycle_v1/vision/camera.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/vision/camera.py (234 dòng, 11867 byte) |
| PURPOSE | Adapter MVS SDK Windows: enum/open/grab/convert/free/lifecycle. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | _InstalledSdkFinder:17; MvsCamera:29 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | _InstalledSdkFinder, __init__, folder.glob, find_spec, importlib.machinery.PathFinder.find_spec, str, threading.RLock, threading.Event, Path, os.environ.get, ProgramFiles, roots.extend, roots.append, next, is_file, struct.calcsize, not, InputError, dll.open, stream.seek, struct.unpack, stream.read, os.add_dll_directory, ct.WinDLL, sys.meta_path.insert, importlib.import_module, sys.meta_path.remove, self.module.MvCamera.MV_CC_GetSDKVersion, hasattr, self.check, self.module.MvCamera.MV_CC_Initialize, check, status, or, text, bytes, split, decode, enumerate, m.MV_CC_DEVICE_INFO_LIST, m.MvCamera.MV_CC_EnumDevices, range, ct.cast, ct.POINTER, result.append |
| CALLED BY | nx100_full_cycle_v1/tests/test_vision.py; nx100_full_cycle_v1/vision/pipeline.py |
| STATE MODIFIED | self.folder, self.names, self.module, self.cam, self.devices, self.latest, self.thread, self.dll_directory, self.connected, self.latest_at, self.frame_id, self.sdk_frame_id, self.error, self.lock, self.stop, self.sdk_version |
| EXTERNAL DEPENDENCIES | import ctypes as ct [2]; import importlib [3]; import importlib.abc [4]; import importlib.machinery [5]; import os [6]; import struct [7]; import sys [8]; import threading [9]; import time [10]; from pathlib import Path [11]; import cv2 [12]; import numpy as np [13]; from .calibration import InputError [14] |
| ERROR HANDLING | InputError, Exception, self |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Có thể mở/cấu hình/capture camera khi gọi connect; không thực thi. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class _InstalledSdkFinder | 17: class _InstalledSdkFinder(importlib.abc.MetaPathFinder): | Class/dataclass/Enum; xem methods |
| def _InstalledSdkFinder.__init__ | 19: def __init__(self, folder): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def _InstalledSdkFinder.find_spec | 23: def find_spec(self, fullname, path=None, target=None): | return importlib.machinery.PathFinder.find_spec(fullname, [str(self.folder)]); return None |
| class MvsCamera | 29: class MvsCamera: | Class/dataclass/Enum; xem methods |
| def MvsCamera.__init__ | 30: def __init__(self, sdk_root=None): | raise InputError("Không tìm thấy Python wrapper MVS của hãng cho Windows."); raise InputError("DLL MVS khác architecture với Python.") |
| def MvsCamera.check | 82: def check(code, operation): | raise InputError(f"MVS: {operation} lỗi 0x{code & 0xFFFFFFFF:08X}; kiểm tra cáp/camera và đóng MVS nếu đang giữ camera.") |
| def MvsCamera.status | 86: def status(self): | return {"available": self.module is not None, "connected": self.connected, "sdk_version": self.sdk_version, |
| def MvsCamera.text | 92: def text(array): | return bytes(array).split(b"\0", 1)[0].decode("utf-8", errors="replace") |
| def MvsCamera.enumerate | 95: def enumerate(self): | raise InputError(self.error); raise InputError("Ngắt camera trước khi liệt kê lại."); return result |
| def MvsCamera.connect | 111: def connect(self, index): | raise InputError(self.error); raise InputError("Camera đã mở; hãy ngắt trước khi đổi camera."); raise InputError("Liệt kê và chọn camera hợp lệ trước."); raise             self.connected, self.error = True, "" |
| def MvsCamera._grab | 142: def _grab(self): | raise InputError("Mất frame/camera ngắt kết nối; kiểm tra cáp và kết nối lại."); raise InputError("Frame camera có kích thước không hợp lệ/quá lớn."); raise InputError("MVS trả buffer RGB có độ dài không đúng.") |
| def MvsCamera.frame | 186: def frame(self): | raise InputError(self.error or "Camera chưa có frame mới. Kết nối và chờ preview trước khi chụp."); return self.latest.copy() |
| def MvsCamera.sample | 192: def sample(self): | return self.frame_id, self.latest_at, self.frame() |
| def MvsCamera.disconnect | 196: def disconnect(self): | raise InputError("SDK chưa dừng lấy frame; thử ngắt lại, không giải phóng buffer khi còn đang dùng."); raise InputError(self.error) |
| def MvsCamera.close | 222: def close(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_full_cycle_v1/vision/detector.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/vision/detector.py (38 dòng, 1743 byte) |
| PURPOSE | YOLO predict native-image bbox center/confidence/class-name rồi transform. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Detector:6 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, os.environ.setdefault, str, RuntimeError, YOLO, detect, calibration.check_frame, self.model.predict, tuple, ValueError, float, cpu, tolist, all, math.isfinite, not, dict, item, int, calibration.convert, items.append |
| CALLED BY | nx100_full_cycle_v1/tests/test_vision.py; nx100_full_cycle_v1/vision/pipeline.py |
| STATE MODIFIED | self.model, self.config |
| EXTERNAL DEPENDENCIES | import math [2]; import os [3]; from ultralytics import YOLO [10] |
| ERROR HANDLING | ImportError, RuntimeError, ValueError, Exception |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 29; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Detector | 6: class Detector: | Class/dataclass/Enum; xem methods |
| def Detector.__init__ | 7: def __init__(self, model_path, config): | raise RuntimeError('REAL cần ultralytics/PyTorch. Chạy .venv\\Scripts\\python -m pip install -r requirements-real.txt') from exc |
| def Detector.detect | 16: def detect(self, frame, calibration, cfg): | raise ValueError('YOLO original image size differs from calibration'); return items |

### nx100_full_cycle_v1/vision/pipeline.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/vision/pipeline.py (149 dòng, 6950 byte) |
| PURPOSE | Vision worker/camera/model/calibration/tracker, preview và publication target. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Vision:14 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, threading.RLock, threading.Event, PixelToRobot, owned, np.load, list, np.allclose, reshape, RuntimeError, BoardTracker, connect, self.thread.is_alive, self.clear_next_pick, Detector, self.camera.close, MvsCamera, self.camera.enumerate, ct.cast, ct.POINTER, str, ipaddress.IPv4Address, matches.append, len, self.camera.connect, self.stop.clear, threading.Thread, self.thread.start, _work, time.monotonic, self.stop.wait, deepcopy, np.full, dict, range, self.camera.sample, self.detector.detect, self.tracker.update, min, cv2.resize, round, cv2.rectangle, item.get, cv2.putText, max |
| CALLED BY | nx100_full_cycle_v1/tests/test_vision.py; nx100_full_cycle_v1/workflow/cycle.py |
| STATE MODIFIED | self.mock, self.lock, self.stop, self.thread, self.camera, self.detector, self.calibration, self.intrinsic_keys, self.connected, self.error, self.preview, self.fps, self.tracker, self._next_target, self.items |
| EXTERNAL DEPENDENCIES | import threading [1]; import time [2]; from copy import deepcopy [3]; import cv2 [4]; import numpy as np [5]; from settings import owned [6]; from .calibration import PixelToRobot [7]; from .detector import Detector [8]; from .camera import MvsCamera [9]; from .tracker import BoardTracker [10]; from .stability import StableTarget [11]; import ctypes as ct [48]; import ipaddress [49] |
| ERROR HANDLING | RuntimeError, Exception |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 26, 75, 93; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Vision | 14: class Vision: | Class/dataclass/Enum; xem methods |
| def Vision.__init__ | 15: def __init__(self, cfg, mock): | raise RuntimeError('Intrinsic và Eye-to-Hand không khớp') |
| def Vision.connect | 35: def connect(self): | return         if self.thread and self.thread.is_alive():; raise RuntimeError('Camera worker vẫn đang dừng'); raise RuntimeError('Không tìm thấy đúng một camera GigE tại IP đã cấu hình') |
| def Vision._work | 64: def _work(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Vision.prepare_next_pick | 108: def prepare_next_pick(self,after_id): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Vision.take_next_pick | 112: def take_next_pick(self,after_id): | return deepcopy(target); return None |
| def Vision.clear_next_pick | 120: def clear_next_pick(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Vision.sample | 124: def sample(self): | raise RuntimeError(self.error or 'Camera không có frame mới'); return self.frame_id, self.stamp, deepcopy(self.items) |
| def Vision.status | 130: def status(self): | return dict(connected=self.connected and time.monotonic()-self.stamp &lt;= self.cfg['vision']['max_frame_age'], |
| def Vision.close | 139: def close(self): | raise RuntimeError('Vision worker chưa dừng') |

### nx100_full_cycle_v1/vision/stability.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/vision/stability.py (43 dòng, 1953 byte) |
| PURPOSE | Cửa sổ frame/timing/identity; tracking và full dùng policy khác nhau. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | StableTarget:6 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, update, self.samples.clear, i.get, all, math.isfinite, min, any, math.dist, self.samples.append, deepcopy, len, self.samples.pop |
| CALLED BY | nx100_full_cycle_v1/tests/test_pick_order.py; nx100_full_cycle_v1/tests/test_prefetch.py; nx100_full_cycle_v1/tests/test_vision.py; nx100_full_cycle_v1/vision/pipeline.py; nx100_full_cycle_v1/workflow/cycle.py |
| STATE MODIFIED | self.cfg, self.after_id, self.last_frame, self.last_stamp, self.samples, self.identity |
| EXTERNAL DEPENDENCIES | import math [2]; from copy import deepcopy [3] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 33; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class StableTarget | 6: class StableTarget: | Class/dataclass/Enum; xem methods |
| def StableTarget.__init__ | 7: def __init__(self, cfg, after_id=None): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def StableTarget.update | 15: def update(self, frame, stamp, items, now): | return None; return None; return None; return deepcopy(item) |

### nx100_full_cycle_v1/vision/tracker.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/vision/tracker.py (71 dòng, 3455 byte) |
| PURPOSE | Greedy bbox association, uncertain, reserved ID10 s và instance generation. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | BoardTracker:6 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, match_score, max, min, math.hypot, update, time.monotonic, self.tracks.items, enumerate, self.match_score, candidates.append, set, any, and, abs, sorted, assigned_ids.add, assigned_indices.add, range, len, reserved_ids.add, self.tracks.get, dict |
| CALLED BY | nx100_full_cycle_v1/tests/test_tracker.py; nx100_full_cycle_v1/vision/pipeline.py |
| STATE MODIFIED | self.missing_timeout, self.tracks, self.generation |
| EXTERNAL DEPENDENCIES | import math [2]; import time [3] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 23, 24, 25; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class BoardTracker | 6: class BoardTracker: | Class/dataclass/Enum; xem methods |
| def BoardTracker.__init__ | 7: def __init__(self, missing_timeout=10.0): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def BoardTracker.match_score | 13: def match_score(previous, current): | return None; return None; return None; return iou + .2 * (1 - min(relative_distance, 1)) |
| def BoardTracker.update | 30: def update(self, detections, now=None): | return sorted(detections, key=lambda item: item["id"]) |

### nx100_full_cycle_v1/vision/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/vision/__init__.py (1 dòng, 0 byte) |
| PURPOSE | Khởi tạo namespace/package; library root có endpoint global và MOCK_RESPONSE. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100_full_cycle_v1/workflow/cycle.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/workflow/cycle.py (604 dòng, 32788 byte) |
| PURPOSE | Owner chu trình, telemetry, target, motion, MOVEUNTI, HAND và fault/recovery. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Cycle:18 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Cycle, __init__, deepcopy, threading.RLock, threading.Event, Controller, Vision, owned, InstanceLock, journal_path.with_suffix, Journal, StackStore, self.cfg.get, saved_settings.exists, update, validate_settings, json.loads, saved_settings.read_text, dict, in, busy, self.thread.is_alive, connect, RuntimeError, self.robot.connect, threading.Thread, self.poller.start, self.refresh, self.vision.connect, _poll, self.stopping.wait, refresh, self.robot.observe, time.monotonic, self.telemetry.update, str, snapshot, self.journal.snapshot, t.update, result.update, self.vision.status, round, self.robot.vacuum_config.get, get, operator_motion_workflow |
| CALLED BY | nx100_full_cycle_v1/app.py; nx100_full_cycle_v1/tests/test_cycle.py; nx100_full_cycle_v1/tests/test_dispatch_cycle.py; nx100_full_cycle_v1/tests/test_drop.py; nx100_full_cycle_v1/tests/test_hand_jobs.py; nx100_full_cycle_v1/tests/test_hold_release.py; nx100_full_cycle_v1/tests/test_laser_h2_cycle.py; nx100_full_cycle_v1/tests/test_position_variable.py; nx100_full_cycle_v1/tests/test_prefetch.py; nx100_full_cycle_v1/tests/test_repeat.py; nx100_full_cycle_v1/tests/test_vacuum.py; nx100_full_cycle_v1/workflow/drop.py |
| STATE MODIFIED | self.mock, self.lock, self.cancel, self.robot, self.vision, self.instance_lock, self.journal, self.stack, self.thread, self.telemetry, self.telemetry_stamp, self.stopping, self.poller, self.monitor_requested |
| EXTERNAL DEPENDENCIES | import logging [1]; import math [2]; import threading [3]; import time [4]; import uuid [5]; from copy import deepcopy [6]; from settings import AXES, owned, validate_settings [7]; from robot.controller import Controller [8]; from robot import job_control [9]; from vision.pipeline import Vision [10]; from vision.stability import StableTarget [11]; from .state_machine import Journal, InstanceLock [12]; from .safety_checks import ready, workspace, reached, real_gate, manual_io_ready, hold_release_ready, operator_motion_workflow [13]; from robot.vacuum import validate_mapping [14]; from .drop import DropWorkflow,StackStore [15]; import json [31]; import json [585] |
| ERROR HANDLING | RuntimeError, Exception, def, ValueError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 308, 310, 341, 343, 509; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Cycle | 18: class Cycle(DropWorkflow): | Class/dataclass/Enum; xem methods |
| def Cycle.__init__ | 19: def __init__(self, cfg, mock=True, journal_path=None): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Cycle.busy | 42: def busy(self): | return self.thread is not None and self.thread.is_alive() |
| def Cycle.connect | 45: def connect(self): | raise RuntimeError('Cycle đang chạy') |
| def Cycle._poll | 57: def _poll(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Cycle.refresh | 65: def refresh(self): | return data; raise |
| def Cycle.snapshot | 81: def snapshot(self): | raise RuntimeError('Kết nối robot trước khi điều khiển vacuum'); raise RuntimeError('Kết nối robot trước khi nhả HOLD'); return result |
| def Cycle._step | 129: def _step(self, state, **values): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Cycle._check_cancel | 135: def _check_cancel(self): | raise RuntimeError('Cycle đã bị HOLD/dừng; không tự resume') |
| def Cycle._command | 139: def _command(self, name, payload, action): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Cycle.start | 146: def start(self, request_id, revision, stage='full_cycle'): | raise ValueError('request_id không hợp lệ'); raise RuntimeError('Duplicate START; không gửi lại'); raise RuntimeError('Yêu cầu cũ; tải lại trạng thái HMI'); raise RuntimeError('Cần ACK; chỉ một cycle được phép chạy') |
| def Cycle._wait | 180: def _wait(self, seconds): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Cycle._prefetch_next_pick | 185: def _prefetch_next_pick(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Cycle._target | 190: def _target(self): | return None; return pose; raise RuntimeError('Hết thời gian chờ target ổn định') |
| def Cycle._pose_checks | 235: def _pose_checks(self, reference): | return  # Preserve live RPOSC metadata; no static expected-tool gate.; raise RuntimeError(f'{key} thay đổi') |
| def Cycle._move | 243: def _move(self, target, state, required_start=None): | raise RuntimeError('DROP SAFE đã thay đổi trước khi hạ Z; không gửi MOVL'); raise RuntimeError('Tool/posture/trục ngoài thay đổi trong MOVL'); return             self._wait(self.cfg['motion']['poll_seconds']); raise RuntimeError('MOVL timeout; ACK không chứng minh đã tới đích') |
| def Cycle._start_moveunti | 270: def _start_moveunti(self): | raise RuntimeError('JOB MOVEUNTI không tồn tại'); raise RuntimeError('Laser ON/UNKNOWN trước Z; khóa START JOB'); return start |
| def Cycle._job | 285: def _job(self): | return self._wait_laser_and_stopped(start); raise RuntimeError('Laser UNKNOWN khi JOB đang chạy'); raise RuntimeError('Không quan sát RUNNING trước laser; cần kiểm tra'); raise RuntimeError('Orientation thay đổi trong MOVEUNTI') |
| def Cycle._wait_laser_and_stopped | 326: def _wait_laser_and_stopped(self,start): | raise RuntimeError('JOB hiện tại không còn là MOVEUNTI; không gọi H2ON'); raise RuntimeError('Laser UNKNOWN khi chờ MOVEUNTI; không gọi H2ON'); raise RuntimeError('XY thay đổi trong MOVEUNTI'); raise RuntimeError('Orientation thay đổi trong MOVEUNTI') |
| def Cycle._run | 356: def _run(self,stage): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Cycle._run_batch | 362: def _run_batch(self,stage): | return             try:; raise RuntimeError('Laser ON/UNKNOWN trước lượt gắp tiếp theo'); return |
| def Cycle._run_once | 386: def _run_once(self,stage): | return                 motion_sent = True; raise RuntimeError('XY verification failed'); raise RuntimeError('JOB yêu cầu robot ở Z_safe và tư thế đã xác minh'); return                 self._job() |
| def Cycle.hold | 456: def hold(self): | raise |
| def Cycle.acknowledge | 468: def acknowledge(self, inspected=False): | raise RuntimeError('Chờ worker kết thúc'); raise RuntimeError('Cần xác nhận đã kiểm tra robot và kết quả lệnh chưa xác định'); raise RuntimeError('Không có trạng thái cần ACK'); raise RuntimeError('Chưa xác minh robot dừng') |
| def Cycle._hold_release_state_ready | 482: def _hold_release_state_ready(self): | raise RuntimeError('ACK về IDLE và chờ worker dừng trước khi nhả HOLD'); raise RuntimeError('Kiểm tra và ACK lệnh chưa xác định trước khi nhả HOLD') |
| def Cycle.release_hold | 488: def release_hold(self,confirmed=False): | raise ValueError('Cần xác nhận nhả HOLD có thể cho phép chuyển động đang treo tiếp tục'); raise RuntimeError('Đã gửi HOLD OFF nhưng chưa đọc được command HOLD OFF'); raise |
| def Cycle.vacuum | 506: def vacuum(self, channel, on): | raise ValueError('Cần channel 1/2 và on boolean'); raise RuntimeError('Vacuum manual bị khóa trong cycle/HOLD/FAULT'); return             self.journal.intent('VACUUM',dict(channel=channel,on=on)); raise |
| def Cycle._execute_hand_job | 533: def _execute_hand_job(self,channel,on,config=None,require_laser=False,required_pose=None): | raise RuntimeError('Robot không còn ở Z_DROP; không gọi H2OFF'); raise RuntimeError('Điều kiện MOVEUNTI/laser đã thay đổi trước H2ON; không gửi lệnh'); raise RuntimeError(f'JOB hiện tại {current}, cần {name}; kiểm tra pendant'); return             self._wait(self.cfg['motion']['poll_seconds']) |
| def Cycle._manual_hand_job | 567: def _manual_hand_job(self,channel,on,previous): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Cycle.configure | 579: def configure(self, values): | raise RuntimeError('Chỉ sửa cấu hình khi IDLE') |
| def Cycle.close | 592: def close(self): | raise RuntimeError('Cycle worker chưa dừng; giữ khóa process và journal') |

### nx100_full_cycle_v1/workflow/drop.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/workflow/drop.py (260 dòng, 13367 byte) |
| PURPOSE | Persistent stack count, tính Z thả, P009/P010, DROP/H2OFF và nâng sau nhả. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | StackStore:14; DropWorkflow:95 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, threading.RLock, dict, config.get, path.exists, self.data.update, json.loads, path.read_text, RuntimeError, self._validate, self._save, _validate, any, type, in, math.isfinite, ValueError, Decimal, str, quantize, data.get, and, isinstance, _save, self.path.parent.mkdir, self.path.with_suffix, temp.open, json.dump, stream.flush, os.fsync, stream.fileno, os.replace, _commit, snapshot, deepcopy, result.pop, float, configure, self._commit, reset, set_count, confirm, self.data.get, _prepare_drop_variable, self.cfg.get |
| CALLED BY | nx100_full_cycle_v1/tests/test_api.py; nx100_full_cycle_v1/tests/test_drop.py; nx100_full_cycle_v1/tests/test_pick_order.py; nx100_full_cycle_v1/workflow/cycle.py |
| STATE MODIFIED | self.path, self.lock, self.data |
| EXTERNAL DEPENDENCIES | from copy import deepcopy [2]; from decimal import Decimal [3]; import json [4]; import math [5]; import os [6]; import threading [7]; import time [8]; from .safety_checks import ready,reached,workspace [10]; from robot.position_variable import parse_p010,with_z,verify_p010 [11] |
| ERROR HANDLING | RuntimeError, ValueError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 3, 35, 64, 65, 205; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class StackStore | 14: class StackStore: | Class/dataclass/Enum; xem methods |
| def StackStore.__init__ | 15: def __init__(self,path,config): | raise RuntimeError('Không đọc được bộ đếm DROP; không tự đặt lại số tấm') from exc |
| def StackStore._validate | 31: def _validate(data): | raise ValueError('Chiều cao/chiều dày phải là số hữu hạn'); raise ValueError('Chiều dày cần &gt;0, &lt;=1000 mm, tối đa 3 số thập phân'); raise ValueError('Bộ đếm DROP không hợp lệ'); raise ValueError('ID gắp cuối không hợp lệ') |
| def StackStore._save | 45: def _save(self,data): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def StackStore._commit | 54: def _commit(self,data): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def StackStore.snapshot | 59: def snapshot(self): | return result |
| def StackStore.configure | 68: def configure(self,thickness): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def StackStore.reset | 72: def reset(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def StackStore.set_count | 76: def set_count(self,count): | raise ValueError('Số tấm phải là số nguyên không âm hợp lệ') |
| def StackStore.confirm | 82: def confirm(self,cycle_id,picked_id=None): | raise ValueError('Thiếu cycle ID'); return False; return True |
| class DropWorkflow | 95: class DropWorkflow: | Class/dataclass/Enum; xem methods |
| def DropWorkflow._prepare_drop_variable | 96: def _prepare_drop_variable(self): | return         if self.cfg['drop']['position_variable']!=10:; raise RuntimeError('Chỉ hỗ trợ biến DROP P010'); raise RuntimeError('Z thả cao hơn DROP SAFE; không ghi P010 hoặc gọi DROP') |
| def DropWorkflow._wait_drop_variable_target | 117: def _wait_drop_variable_target(self,target): | raise RuntimeError('JOB hiện tại không còn DROP; không gọi H2OFF'); return             self._wait(self.cfg['motion']['poll_seconds']); raise RuntimeError('DROP chưa dừng tại đích P010; không gọi H2OFF') |
| def DropWorkflow._wait_drop_safe | 134: def _wait_drop_safe(self): | raise RuntimeError('JOB hiện tại không còn DROP; không hạ Z hoặc gọi H2OFF'); return p; raise RuntimeError(f'DROP chưa dừng tại Z safe={safe_z}; không hạ Z hoặc gọi H2OFF') |
| def DropWorkflow._finish_drop | 158: def _finish_drop(self): | raise RuntimeError('DROP đã được xử lý cho cycle này; không tự gửi lại H2OFF'); raise RuntimeError('Chưa xác minh P010; không gọi H2OFF'); raise RuntimeError('Z thả cao hơn DROP SAFE; không thực hiện chuyển động lên thay cho hạ Z'); raise RuntimeError('DROP yêu cầu đúng JOB H2OFF có sẵn') |
| def DropWorkflow._after_h2off_move | 198: def _after_h2off_move(self,drop_pose): | return         axis=motion.get('axis'); raise RuntimeError('Chưa xác nhận đúng trục di chuyển sau H2OFF') |
| def DropWorkflow._can_confirm_drop | 210: def _can_confirm_drop(self): | return (not self.busy and s['state'] in ('AWAIT_DROP_CONFIRMATION','FAULT') |
| def DropWorkflow.confirm_drop | 217: def confirm_drop(self,cycle_id,confirmed=False): | raise ValueError('Cần xác nhận đã nhìn thấy ván nhả khỏi đầu hút'); raise RuntimeError('Cycle xác nhận không khớp'); return             if not self._can_confirm_drop():; raise RuntimeError('Chưa xác nhận H2OFF hoàn thành; không tăng bộ đếm') |
| def DropWorkflow._stack_edit_ready | 235: def _stack_edit_ready(self): | raise RuntimeError('Chỉ sửa/reset bộ đếm khi cycle không hoạt động và không chờ xác nhận thả'); raise RuntimeError('Robot đang RUNNING hoặc chưa xác định; không sửa/reset bộ đếm') |
| def DropWorkflow.configure_drop | 241: def configure_drop(self,thickness): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def DropWorkflow.reset_stack | 247: def reset_stack(self,confirmed=False): | raise ValueError('Cần xác nhận RESET STACK') |
| def DropWorkflow.set_stack_count | 255: def set_stack_count(self,count): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_full_cycle_v1/workflow/safety_checks.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/workflow/safety_checks.py (84 dòng, 4305 byte) |
| PURPOSE | Readiness/workspace/reached và gate commissioning/nhánh operator. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | ready, items, flags.get, RuntimeError, workspace, math.isfinite, manual_io_ready, hold_release_ready, commissioning_hash, fingerprint, cfg.items, in, operator_motion_workflow, cfg.get, flow.get, real_gate, get, validate_mapping, any, c.get, not, isinstance, reached, all, abs, a.startswith |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | import math [1]; from settings import AXES, fingerprint [2]; from robot.vacuum import validate_mapping [55]; from robot.vacuum import validate_mapping [75] |
| ERROR HANDLING | RuntimeError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 82; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def ready | 5: def ready(flags, allow_running=False): | raise RuntimeError(f'Robot chưa sẵn sàng: {key}={flags.get(key)}'); raise RuntimeError('Robot RUNNING hoặc UNKNOWN') |
| def workspace | 14: def workspace(pose, cfg): | raise RuntimeError('Tọa độ không hữu hạn'); raise RuntimeError(f'Ngoài workspace: {axis}') |
| def manual_io_ready | 22: def manual_io_ready(flags,allow_running=False): | raise RuntimeError(f'Chưa thể điều khiển I/O: {key}={flags.get(key)}') |
| def hold_release_ready | 30: def hold_release_ready(flags): | raise RuntimeError(f'Chưa thể nhả HOLD: {key}={flags.get(key)}') |
| def commissioning_hash | 38: def commissioning_hash(cfg): | return fingerprint({k: v for k, v in cfg.items() if k not in ('commissioning', 'web')}) |
| def operator_motion_workflow | 42: def operator_motion_workflow(cfg): | return flow.get('end_after_moveunti_start',False) or flow.get('z_completion')=='laser_on_and_stopped' |
| def real_gate | 47: def real_gate(cfg, stage='full_cycle'): | raise RuntimeError('Luồng bàn giao yêu cầu đúng JOB MOVEUNTI'); return     c = cfg['commissioning']; raise RuntimeError('Chưa xác minh TOOL/posture'); raise RuntimeError('REAL bị khóa: thiếu nghiệm thu hoặc cấu hình đã thay đổi; xem checklist') |
| def reached | 81: def reached(current, target, cfg): | return all(abs((current[a]-target[a]+180) % 360-180) &lt;= cfg['motion']['angle_tolerance'] |

### nx100_full_cycle_v1/workflow/state_machine.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/workflow/state_machine.py (88 dòng, 3634 byte) |
| PURPOSE | Journal atomic intent/accepted/restart và process file lock. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | InstanceLock:16; Journal:47 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, path.parent.mkdir, path.open, self.stream.seek, self.stream.tell, self.stream.write, self.stream.flush, msvcrt.locking, self.stream.fileno, fcntl.flock, self.stream.close, RuntimeError, close, __del__, self.close, threading.RLock, dict, path.exists, self.state.update, json.loads, path.read_text, self.save, save, self.path.with_suffix, temp.open, json.dump, stream.flush, os.fsync, stream.fileno, os.replace, update, time.time, snapshot, deepcopy, intent, self.update, accepted |
| CALLED BY | nx100_full_cycle_v1/tests/test_cycle.py; nx100_full_cycle_v1/tests/test_dispatch_cycle.py; nx100_full_cycle_v1/tests/test_drop.py; nx100_full_cycle_v1/workflow/cycle.py |
| STATE MODIFIED | self.stream, self.path, self.lock, self.state |
| EXTERNAL DEPENDENCIES | import json [2]; import os [3]; import threading [4]; import time [5]; from copy import deepcopy [6]; import msvcrt [28]; import fcntl [31] |
| ERROR HANDLING | OSError, RuntimeError, Exception |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class InstanceLock | 16: class InstanceLock: | Class/dataclass/Enum; xem methods |
| def InstanceLock.__init__ | 18: def __init__(self,path): | raise RuntimeError('Mode này đã có server đang giữ quyền điều khiển; không chạy process thứ hai') from exc |
| def InstanceLock.close | 38: def close(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def InstanceLock.__del__ | 43: def __del__(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| class Journal | 47: class Journal: | Class/dataclass/Enum; xem methods |
| def Journal.__init__ | 48: def __init__(self, path): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Journal.save | 63: def save(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Journal.update | 71: def update(self, **values): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Journal.snapshot | 79: def snapshot(self): | return deepcopy(self.state) |
| def Journal.intent | 83: def intent(self, name, payload): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Journal.accepted | 86: def accepted(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_full_cycle_v1/workflow/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_full_cycle_v1/workflow/__init__.py (1 dòng, 0 byte) |
| PURPOSE | Khởi tạo namespace/package; library root có endpoint global và MOCK_RESPONSE. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100_variables_web/app.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_variables_web/app.py (358 dòng, 16724 byte) |
| PURPOSE | Entry point và HTTP API/HMI; tạo controller/workflow và quản lý lifecycle. |
| ENTRY POINT | Có __main__ guard; xem phần entry point/deployment |
| CLASSES | MockNX100:41; Variables:58; make_server.Handler:262 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Path, resolve, selection, ValueError, isinstance, re.fullmatch, str, variable, milliseconds, float, __init__, connect, read, time.sleep, self.values.get, name.startswith, write_and_read, self.read, matches, threading.RLock, threading.Lock, threading.Event, deque, self.reset_metrics, threading.Thread, self.worker.start, reset_metrics, time.monotonic, event, self.events.append, datetime.now, strftime, ipaddress.IPv4Address, isdigit, int, self.factory, candidate.connect, self.event, disconnect, choose, NXError, self.wake.set, self.read_once, stop, read_once |
| CALLED BY | nx100_variables_web/tests/test_variables.py |
| STATE MODIFIED | self.values, self.mock, self.io, self.closed, self.wake, self.client, self.connected, self.realtime, self.port, self.name, self.period_ms, self.generation, self.value, self.updated_at, self.error, self.write_result, self.write_unknown, self.uncertain_name, self.write_ms, self.events, self.worker, self.samples, self.reads, self.errors, self.consecutive_errors, self.started, self.stopped |
| EXTERNAL DEPENDENCIES | from __future__ import annotations [2]; import argparse [4]; from collections import deque [5]; from datetime import datetime, timezone [6]; from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer [7]; import ipaddress [8]; import json [9]; from pathlib import Path [10]; import re [11]; import statistics [12]; import threading [13]; import time [14]; from urllib.parse import urlsplit [15]; import webbrowser [16]; from nx100_client import NX100, NXError, WriteUnknown, edited_value, editor_data, matches, variable [18] |
| ERROR HANDLING | ValueError, NXError, Exception, elapsed, with, ConnectionError, KeyboardInterrupt |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Entry/API có thể tạo worker/runtime file và gọi workflow; không tự coi import là read-only. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def selection | 24: def selection(kind, index): | raise ValueError('Loại biến không hợp lệ.'); raise ValueError('S là biến chuỗi. SAVEV/LOADV trong tài liệu NX100 HW0483202 không hỗ trợ S.'); raise ValueError('Số biến chỉ được nhập chữ số, ví dụ 0, 10 hoặc 99.'); return variable(f'{kind}{index}')[2] |
| def milliseconds | 35: def milliseconds(value): | raise ValueError('Chu kỳ đọc phải từ 0 đến 10000 ms.'); return float(value) |
| class MockNX100 | 41: class MockNX100: | Class/dataclass/Enum; xem methods |
| def MockNX100.__init__ | 42: def __init__(self, host='', port=80, timeout=3): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def MockNX100.connect | 45: def connect(self): | return 'MOCK — không kết nối robot thật' |
| def MockNX100.read | 48: def read(self, name): | return self.values.get(name, '1,0,530.000,0.000,0.000,180.00,0.00,90.00,17,0' if name.startswith('P') else '0') |
| def MockNX100.write_and_read | 52: def write_and_read(self, name, value): | return actual, matches(name[0], value, actual) |
| class Variables | 58: class Variables: | Class/dataclass/Enum; xem methods |
| def Variables.__init__ | 59: def __init__(self, factory=NX100, mock=False): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Variables.reset_metrics | 82: def reset_metrics(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Variables.event | 88: def event(self, action, message): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Variables.connect | 91: def connect(self, host, port): | raise ValueError('Port phải từ 1 đến 65535.') |
| def Variables.disconnect | 109: def disconnect(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Variables.choose | 117: def choose(self, kind, index, period_ms, realtime=False): | raise NXError('Chưa kết nối robot.') |
| def Variables.stop | 140: def stop(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Variables.read_once | 148: def read_once(self, generation=None): | return                 if not self.connected or self.client is None:; raise NXError('Chưa kết nối robot.'); raise             elapsed = (time.perf_counter() - start) * 1000 |
| def Variables.write | 184: def write(self, name, values): | raise ValueError('Giá trị ghi không hợp lệ.'); raise ValueError('Cần đọc đúng biến đang chọn trước khi ghi.'); raise ValueError('Lần ghi trước chưa rõ kết quả. Đọc lại trước khi ghi tiếp.'); raise             with self.lock: |
| def Variables._loop | 217: def _loop(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Variables.snapshot | 233: def snapshot(self): | return dict(mode='MOCK' if self.mock else 'REAL', connected=self.connected, |
| def Variables.close | 255: def close(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def make_server | 261: def make_server(service, port=8010): | return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'}; return self.reply(403, {'message': 'Host không hợp lệ.'}); return self.reply(200, service.snapshot()); return self.reply(404, {'message': 'Không tìm thấy.'}) |
| class make_server.Handler | 262: class Handler(BaseHTTPRequestHandler): | Class/dataclass/Enum; xem methods |
| def make_server.Handler.log_message | 263: def log_message(self, *args): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def make_server.Handler.reply | 266: def reply(self, status, data, content_type='application/json; charset=utf-8'): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def make_server.Handler.local | 280: def local(self): | return self.headers.get('Host') in {f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}'} |
| def make_server.Handler.do_GET | 283: def do_GET(self): | return self.reply(403, {'message': 'Host không hợp lệ.'}); return self.reply(200, service.snapshot()); return self.reply(404, {'message': 'Không tìm thấy.'}) |
| def make_server.Handler.do_POST | 297: def do_POST(self): | return self.reply(403, {'message': 'Yêu cầu điều khiển không hợp lệ.'}); raise ValueError('Kích thước dữ liệu không hợp lệ.'); raise ValueError('Cần dữ liệu JSON object.'); return self.reply(404, {'message': 'Không tìm thấy.'}) |

### nx100_variables_web/nx100_client.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_variables_web/nx100_client.py (240 dòng, 10172 byte) |
| PURPOSE | Variable normalization/editor và SAVEV/LOADV TCP client, phân biệt WriteUnknown. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | NXError:26; ControllerError:30; WriteUnknown:34; NX100:145 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | SAVEV, LOADV, NXError, ControllerError, WriteUnknown, variable, re.fullmatch, name.strip, upper, ValueError, match.groups, int, integer, len, text.strip, str, number, Decimal, result.is_finite, abs, fixed, value.quantize, scaleb, format, normalize, part.strip, raw.strip, rstrip, split, range, join, editor_data, canonical.split, get, X, Y, Z, TX, TY, TZ, S, L, U, R, B |
| CALLED BY | nx100_variables_web/app.py; nx100_variables_web/tests/test_variables.py |
| STATE MODIFIED | self.timeout |
| EXTERNAL DEPENDENCIES | from __future__ import annotations [9]; import math [11]; import queue [12]; import re [13]; import socket [14]; import threading [15]; import time [16]; from decimal import Decimal, InvalidOperation [17]; from datetime import datetime [18] |
| ERROR HANDLING | ValueError, InvalidOperation, NXError, TimeoutError, ConnectionError, ControllerError, except, WriteUnknown, Exception |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 17, 60, 65, 68, 75, 77, 79, 88, 90, 141; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Có đường gửi NX TCP khi hàm được gọi; không được gọi trong audit. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class NXError | 26: class NXError(Exception): | Class/dataclass/Enum; xem methods |
| class ControllerError | 30: class ControllerError(NXError): | Class/dataclass/Enum; xem methods |
| class WriteUnknown | 34: class WriteUnknown(NXError): | Class/dataclass/Enum; xem methods |
| def variable | 38: def variable(name: str) -&gt; tuple[str, int, str]: | raise ValueError('Nhập tên biến như I099, D010, R010, B099 hoặc P099.'); raise ValueError(f'Bản này hỗ trợ {kind}000..{kind}{maximum:03d}.'); return kind, index, f'{kind}{index:03d}' |
| def integer | 51: def integer(text: str, low: int, high: int) -&gt; str: | raise ValueError('Giá trị phải là số nguyên.'); raise ValueError(f'Giá trị phải trong [{low}, {high}].'); return str(value) |
| def number | 60: def number(text: str) -&gt; Decimal: | raise ValueError('Số không hợp lệ; dùng dấu chấm thập phân.'); raise ValueError('Số không hợp lệ.') from exc; raise ValueError('Giá trị ngoài phạm vi.'); return result |
| def fixed | 73: def fixed(text: str, places: int) -&gt; str: | raise ValueError('Tọa độ quá lớn cho công cụ này.'); raise ValueError(f'Chỉ nhập tối đa {places} chữ số thập phân.'); return format(value if value else Decimal(0), f'.{places}f') |
| def normalize | 82: def normalize(kind: str, raw: str) -&gt; str: | return integer(raw, *LIMITS[kind]); raise ValueError('Giá trị R khác 0 nhưng quá nhỏ.'); return format(value if value else Decimal(0), 'f'); raise ValueError('Chỉ hỗ trợ B, I, D, R, P.') |
| def editor_data | 108: def editor_data(kind: str, raw: str) -&gt; tuple[list[str], list[str], str]: | return ['Giá trị'], [canonical], kind + ' - biến số'; return labels, parts[2:8], info + ' - giữ nguyên cấu hình P'; return ['S (pulse)', 'L (pulse)', 'U (pulse)', 'R (pulse)', 'B (pulse)', 'T (pulse)'], parts[1:7], f'PULSE ∣ Tool {parts[7]}' |
| def edited_value | 122: def edited_value(kind: str, before: str, values: list[str]) -&gt; str: | raise ValueError('Thiếu giá trị biến.'); return normalize(kind, values[0]); raise ValueError('P cần 6 giá trị.'); return normalize(kind, ','.join(fields)) |
| def matches | 138: def matches(kind: str, expected: str, actual: str) -&gt; bool: | return math.isclose(float(left), float(right), rel_tol=1e-6, abs_tol=0.0); return left == right |
| class NX100 | 145: class NX100: | Class/dataclass/Enum; xem methods |
| def NX100.__init__ | 151: def __init__(self, host: str = HOST, port: int = PORT, timeout: float = 5.0): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100.connect | 154: def connect(self) -&gt; str: | return self._exchange() |
| def NX100._exchange | 157: def _exchange(self, command: str = '', data: str = '') -&gt; str: | raise ValueError('Chỉ cho phép SAVEV/LOADV.'); raise ValueError('Dữ liệu giao thức không hợp lệ.'); return value.decode('ascii'); raise NXError('Phản hồi quá dài.') |
| def NX100._exchange.receive | 170: def receive(delimiter: bytes) -&gt; str: | return value.decode('ascii'); raise NXError('Phản hồi quá dài.'); raise TimeoutError('Timeout'); raise ConnectionError('NX100 đóng kết nối trước khi trả đủ dữ liệu.') |
| def NX100.read | 221: def read(self, name: str) -&gt; str: | return normalize(kind, raw) |
| def NX100.write | 226: def write(self, name: str, value: str) -&gt; str: | return self._exchange('LOADV', f'{TYPE_CODES[kind]},{index},{value}') |
| def NX100.write_and_read | 231: def write_and_read(self, name: str, value: str) -&gt; tuple[str, bool]: | raise WriteUnknown('LOADV đã trả 0000, nhưng đọc lại bị lỗi. Không tự ghi lại.\n' + str(exc)) from exc; return actual, matches(kind, value, actual) |

### nx100_web_control/app.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_web_control/app.py (235 dòng, 7868 byte) |
| PURPOSE | Entry point và HTTP API/HMI; tạo controller/workflow và quản lý lifecycle. |
| ENTRY POINT | Có __main__ guard; xem phần entry point/deployment |
| CLASSES | Input:23; Connection:27; CartesianMove:37; JointMove:49; CameraConnection:59; PixelPoint:63 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Path, resolve, Input, ConfigDict, Connection, Field, field_validator, validate_ip, str, ipaddress.IPv4Address, CartesianMove, JointMove, CameraConnection, PixelPoint, create_app, json.loads, read_text, config.setdefault, ValueError, NX100Controller, VisionService, config.get, lifespan, robot.start_monitor, robot.close, vision.close, FastAPI, app.middleware, local_only, Origin, urlsplit, request.headers.get, JSONResponse, call_next, app.exception_handler, control_error, bad_value, validation_error, join, map, exc.errors, app.get, index, FileResponse, camera_page |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | import argparse [3]; import ipaddress [4]; import json [5]; from contextlib import asynccontextmanager [6]; from pathlib import Path [7]; from typing import Literal [8]; from urllib.parse import urlsplit [9]; from fastapi import FastAPI, Query, Request [11]; from fastapi.exceptions import RequestValidationError [12]; from fastapi.responses import FileResponse, JSONResponse [13]; from fastapi.staticfiles import StaticFiles [14]; from pydantic import BaseModel, ConfigDict, Field, field_validator [15]; from robot.nx100_controller import ControlError, NX100Controller [17]; from vision.camera import VisionService [18]; import uvicorn [232] |
| ERROR HANDLING | ValueError |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Input | 23: class Input(BaseModel): | Class/dataclass/Enum; xem methods |
| class Connection | 27: class Connection(Input): | Class/dataclass/Enum; xem methods |
| def Connection.validate_ip | 33: def validate_ip(cls, value): | return str(ipaddress.IPv4Address(value)) |
| class CartesianMove | 37: class CartesianMove(Input): | Class/dataclass/Enum; xem methods |
| class JointMove | 49: class JointMove(Input): | Class/dataclass/Enum; xem methods |
| class CameraConnection | 59: class CameraConnection(Input): | Class/dataclass/Enum; xem methods |
| class PixelPoint | 63: class PixelPoint(Input): | Class/dataclass/Enum; xem methods |
| def create_app | 70: def create_app(mock=False, controller=None): | raise ValueError("auto_send_delay_ms must be 100..2000"); raise ValueError("poll_interval_ms must be 500..10000"); return JSONResponse(; return JSONResponse( |
| def create_app.lifespan | 81: async def lifespan(app): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def create_app.local_only | 92: async def local_only(request: Request, call_next): | return JSONResponse(; return JSONResponse(; return JSONResponse(; return response |
| def create_app.control_error | 119: async def control_error(request, exc): | return JSONResponse({"code": exc.code, "message": exc.message}, status_code=exc.status) |
| def create_app.bad_value | 123: async def bad_value(request, exc): | return JSONResponse({"code": "INVALID_INPUT", "message": str(exc)}, status_code=422) |
| def create_app.validation_error | 127: async def validation_error(request, exc): | return JSONResponse( |
| def create_app.index | 137: def index(): | return FileResponse(BASE / "templates" / "index.html") |
| def create_app.camera_page | 141: def camera_page(): | return FileResponse(BASE / "templates" / "camera.html") |
| def create_app.vision_status | 145: def vision_status(): | return vision.status() |
| def create_app.vision_reload | 149: def vision_reload(): | return vision.reload() |
| def create_app.vision_enumerate | 153: def vision_enumerate(): | return {"devices": vision.enumerate()} |
| def create_app.vision_connect | 157: def vision_connect(body: CameraConnection): | return vision.connect(body.index) |
| def create_app.vision_disconnect | 161: def vision_disconnect(): | return vision.disconnect() |
| def create_app.vision_frame | 165: def vision_frame(): | return vision.frame() |
| def create_app.vision_pixel | 169: def vision_pixel(body: PixelPoint): | return vision.convert(body.frame_id, body.u, body.v, body.plane_z_mm) |
| def create_app.get_config | 173: def get_config(): | return {**config, "mode": robot.state["mode"], "move_joint_supported": False} |
| def create_app.status | 177: def status(refresh: bool = False): | return robot.read_status() if refresh else robot.snapshot() |
| def create_app.cartesian | 181: def cartesian(): | return robot.read_cartesian() |
| def create_app.joint | 185: def joint(): | return robot.read_joint() |
| def create_app.logs | 189: def logs(after: int = Query(default=0, ge=0)): | return {"events": robot.events(after)} |
| def create_app.connect | 193: def connect(body: Connection): | return robot.connect(body.ip, body.port) |
| def create_app.disconnect | 197: def disconnect(): | return robot.disconnect() |
| def create_app.move | 201: def move(body: CartesianMove): | return robot.move_cartesian( |
| def create_app.move_joint | 210: def move_joint(body: JointMove): | return robot.move_joint(**body.model_dump()) |
| def create_app.hold | 214: def hold(): | return robot.hold() |

### nx100_web_control/robot/mock.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_web_control/robot/mock.py (52 dòng, 1914 byte) |
| PURPOSE | Phản hồi/diễn tiến mô phỏng; không đại diện physics hoặc dữ liệu thiết bị thật. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | MockClient:6 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, or, _advance, min, time.monotonic, zip, execute, self._advance, self.trace, encode, join, float, data.split, elif, ValueError, result.encode |
| CALLED BY | nx100_web_control/robot/nx100_controller.py |
| STATE MODIFIED | self.port, self.trace, self.pose, self.origin, self.target, self.started, self.duration, self.word2, self.word1 |
| EXTERNAL DEPENDENCIES | import time [3] |
| ERROR HANDLING | ValueError |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Chỉ mô phỏng; không suy trạng thái thiết bị thật. |
| KNOWN LIMITATIONS | Không mô phỏng collision/pressure/cell safety. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class MockClient | 6: class MockClient: | Class/dataclass/Enum; xem methods |
| def MockClient.__init__ | 7: def __init__(self, ip, port=80, timeout=3, trace=None): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def MockClient._advance | 17: def _advance(self): | return         fraction = min(1, (time.monotonic() - self.started) / self.duration) |
| def MockClient.execute | 26: def execute(self, name, data=""): | raise ValueError("Unsupported mock command"); return result |

### nx100_web_control/robot/nx100_controller.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_web_control/robot/nx100_controller.py (451 dòng, 18551 byte) |
| PURPOSE | Robot adapter/controller, preflight, serialized IO, pose/status/motion monitoring. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | ControlError:18; NX100Controller:24 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | ControlError, __init__, super, threading.Lock, deque, threading.Event, dict, _set, log, self.logs.append, datetime.now, astimezone, isoformat, _trace, self.log, repr, snapshot, deepcopy, self.robot_lock.locked, self.hold_pending.is_set, round, time.monotonic, events, _operation, self.robot_lock.acquire, isinstance, str, lower, self._set, self.robot_lock.release, _cancel_pending_move, self.pending_move_cancel.set, _move_operation, self.move_pending.is_set, self.move_pending.set, self._operation, cancelled.is_set, self.move_pending.clear, _require, is_connected, connect, factory, self._status, self._cartesian, self._joint |
| CALLED BY | nx100_web_control/app.py; nx100_web_control/tests/test_web.py |
| STATE MODIFIED | self.status, self.mock, self.robot_lock, self.log_lock, self.logs, self.log_id, self.client, self.reference, self.reference_id, self.hold_pending, self.move_pending, self.intent_lock, self.pending_move_cancel, self.stopping, self.thread, self.active, self.state, self.status_clock |
| EXTERNAL DEPENDENCIES | import re [3]; import threading [4]; import time [5]; import uuid [6]; from collections import deque [7]; from contextlib import contextmanager [8]; from copy import deepcopy [9]; from datetime import datetime [10]; from .mock import MockClient [12]; from .protocol import Client, OutcomeUnknown, ProtocolError, Status, build_move, read_pose [13] |
| ERROR HANDLING | ControlError, ProtocolError, ValueError, OutcomeUnknown, self |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 398; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class ControlError | 18: class ControlError(RuntimeError): | Class/dataclass/Enum; xem methods |
| def ControlError.__init__ | 19: def __init__(self, code, message, status=409): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| class NX100Controller | 24: class NX100Controller: | Class/dataclass/Enum; xem methods |
| def NX100Controller.__init__ | 25: def __init__(self, config, mock=False): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller._set | 56: def _set(self, **changes): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller.log | 60: def log(self, level, message): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller._trace | 72: def _trace(self, direction, wire): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller.snapshot | 75: def snapshot(self): | return result |
| def NX100Controller.events | 85: def events(self, after=0): | return [dict(event) for event in self.logs if event["id"] &gt; after] |
| def NX100Controller._operation | 90: def _operation(self, wait=False, timeout=None): | raise ControlError("BUSY", "Robot communication busy; command was not queued"); raise ControlError(code, str(exc), 503) from exc |
| def NX100Controller._cancel_pending_move | 125: def _cancel_pending_move(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller._move_operation | 131: def _move_operation(self): | raise ControlError("HOLD_PENDING", "HOLD pending; MOVE blocked"); raise ControlError("MOVE_PENDING", "A MOVE request is already being processed"); raise ControlError("MOTION_ACTIVE", "Previous move still being monitored"); raise ControlError("MOVE_CANCELLED", "MOVE cancelled by HOLD or disconnect") |
| def NX100Controller._require | 153: def _require(self): | raise ControlError("DISCONNECTED", "NX100 DISCONNECTED"); return self.client |
| def NX100Controller.is_connected | 158: def is_connected(self): | return self.state["connected"] |
| def NX100Controller.connect | 161: def connect(self, ip, port): | raise ControlError("ALREADY_CONNECTED", "Disconnect before changing endpoint"); raise ControlError("HOLD_PENDING", "HOLD pending"); return self.snapshot() |
| def NX100Controller.disconnect | 180: def disconnect(self): | return self.snapshot() |
| def NX100Controller._status | 198: def _status(self): | raise ProtocolError("Malformed RSTATS: " + raw); raise ProtocolError("Invalid RSTATS: " + raw) from exc; return flags |
| def NX100Controller.read_status | 224: def read_status(self): | return self.snapshot() |
| def NX100Controller._cartesian | 229: def _cartesian(self): | return pose, values |
| def NX100Controller.read_cartesian | 241: def read_cartesian(self): | raise ControlError("MOTION_ACTIVE", "Wait for motion monitoring to finish"); return {**values, "reference_id": self.reference_id} |
| def NX100Controller._joint | 251: def _joint(self): | raise ProtocolError("Malformed RPOSJ: " + raw); return values |
| def NX100Controller.read_joint | 261: def read_joint(self): | return result |
| def NX100Controller.blocked | 268: def blocked(flags): | return reasons |
| def NX100Controller.move_cartesian | 284: def move_cartesian(self, motion, speed, coordinates, reference_id=None): | raise ControlError("MOTION_ACTIVE", "Previous move still being monitored"); raise ControlError("HOLD_PENDING", "HOLD pending; MOVE blocked"); raise ControlError("READ_REQUIRED", "READ CURRENT POSITION before MOVE"); raise ControlError("INVALID_SPEED", "Speed outside configured range", 422) |
| def NX100Controller.move_joint | 350: def move_joint(self, **kwargs): | raise ControlError( |
| def NX100Controller.hold | 357: def hold(self): | return {"response": response, "message": "HOLD ACCEPTED"} |
| def NX100Controller.poll_once | 378: def poll_once(self): | return         try:; return                 flags = self._status(); return                 _, current = self._cartesian(); return                 self._joint() |
| def NX100Controller.start_monitor | 439: def start_monitor(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller.start_monitor.monitor | 440: def monitor(): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller.close | 447: def close(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_web_control/robot/protocol.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_web_control/robot/protocol.py (21 dòng, 744 byte) |
| PURPOSE | Adapter import transport/object từ sibling project qua sys.path. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Path, resolve, SOURCE.is_dir, RuntimeError, sys.path.insert, str |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | import sys [3]; from pathlib import Path [4]; from nx100_remote_control.module.Cartesian import Pose, build_move, read_pose  # noqa: E402 [16]; from nx100_remote_control.module.Protocol import Client, OutcomeUnknown, ProtocolError  # noqa: E402 [17]; from nx100_remote_control.objects.Status import Status  # noqa: E402 [18] |
| ERROR HANDLING | RuntimeError |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100_web_control/robot/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_web_control/robot/__init__.py (2 dòng, 1 byte) |
| PURPOSE | Khởi tạo namespace/package; library root có endpoint global và MOCK_RESPONSE. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100_web_control/vision/calibration.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_web_control/vision/calibration.py (114 dòng, 5129 byte) |
| PURPOSE | Load/validate calibration và pixel→Base ray-plane; xem chính sách offset theo project. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | VisionError:12; Calibration:16 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | VisionError, __init__, Path, resolve, self.path.read_bytes, json.loads, hashlib.sha256, hexdigest, report.get, get, np.asarray, reshape, all, np.isfinite, np.allclose, np.eye, np.isclose, np.linalg.det, in, int, summary, self.report.get, dict, str, diagnostics.get, self.T.tolist, self.K.tolist, self.distortion.tolist, pixel_to_base, math.isfinite, float, not, cv2.undistortPointsIter, np.array, abs, np.max, np.abs, zip, point.tolist, camera_point.tolist |
| CALLED BY | nx100_web_control/tests/test_vision.py; nx100_web_control/vision/camera.py |
| STATE MODIFIED | self.path, self.report, self.fingerprint, self.T, self.K, self.distortion, self.height |
| EXTERNAL DEPENDENCIES | import hashlib [3]; import json [4]; import math [5]; from pathlib import Path [6]; import cv2 [8]; import numpy as np [9] |
| ERROR HANDLING | VisionError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 36, 37, 38, 44, 45, 46, 82, 109; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class VisionError | 12: class VisionError(ValueError): | Class/dataclass/Enum; xem methods |
| class Calibration | 16: class Calibration: | Class/dataclass/Enum; xem methods |
| def Calibration.__init__ | 17: def __init__(self, path): | raise VisionError("Calib phải khai báo translation=mm."); raise VisionError("Chưa xác nhận chiều ma trận Camera -&gt; robot Base."); raise VisionError("T_base_camera phải 4x4, K phải 3x3."); raise VisionError("Calib chứa NaN/Inf.") |
| def Calibration.summary | 55: def summary(self): | return dict( |
| def Calibration.pixel_to_base | 73: def pixel_to_base(self, u, v, plane_z_mm, frame_width, frame_height): | raise VisionError(; raise VisionError("Pixel và Z phải hữu hạn."); raise VisionError("Pixel ngoài ảnh gốc."); raise VisionError("Tia nhìn song song mặt phẳng Z; không có giao điểm duy nhất.") |

### nx100_web_control/vision/camera.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_web_control/vision/camera.py (198 dòng, 7491 byte) |
| PURPOSE | VisionService qua adapter ngoài, frame registry/TTL và pixel conversion. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | VisionService:18 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, threading.RLock, OrderedDict, self.reload, reload, self.frames.clear, Calibration, str, self.status, _calibration, VisionError, _adapter, Path, resolve, not, is_file, sys.path.insert, importlib.import_module, MvsCamera, sys.path.remove, status, dict, self.adapter.status, self.calibration.summary, self.config.get, enumerate, self._adapter, connect, disconnect, self.adapter.disconnect, _mock_image, min, round, np.full, range, cv2.line, cv2.putText, cv2.drawMarker, frame, self._calibration, self._mock_image, cv2.resize, cv2.imencode, uuid.uuid4, time.time |
| CALLED BY | nx100_web_control/app.py; nx100_web_control/tests/test_vision.py |
| STATE MODIFIED | self.mock, self.lock, self.adapter, self.mock_connected, self.frames, self.calibration, self.calibration_error, self.mock_preview |
| EXTERNAL DEPENDENCIES | import base64 [3]; import importlib [4]; import sys [5]; import threading [6]; import time [7]; import uuid [8]; from collections import OrderedDict [9]; from pathlib import Path [10]; import cv2 [12]; import numpy as np [13]; from .calibration import Calibration, VisionError [15] |
| ERROR HANDLING | VisionError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 129; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class VisionService | 18: class VisionService: | Class/dataclass/Enum; xem methods |
| def VisionService.__init__ | 19: def __init__(self, config, mock=False): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def VisionService.reload | 30: def reload(self): | return self.status() |
| def VisionService._calibration | 42: def _calibration(self): | raise VisionError("Chưa đọc được calib: " + str(self.calibration_error)); return self.calibration |
| def VisionService._adapter | 47: def _adapter(self): | raise VisionError("Không tìm thấy calib_mvs.py trong camera_project."); return self.adapter |
| def VisionService.status | 63: def status(self): | return dict( |
| def VisionService.enumerate | 82: def enumerate(self): | return ( |
| def VisionService.connect | 90: def connect(self, index): | raise VisionError("Chọn MOCK camera index 0."); return self.status() |
| def VisionService.disconnect | 101: def disconnect(self): | return self.status() |
| def VisionService._mock_image | 110: def _mock_image(self, calibration): | return self.mock_preview |
| def VisionService.frame | 134: def frame(self): | raise VisionError("Camera chưa kết nối."); raise VisionError("Không mã hóa được ảnh camera."); return { |
| def VisionService.convert | 174: def convert(self, frame_id, u, v, plane_z_mm): | raise VisionError("Frame đã hết hạn; nhấn LIVE rồi chọn lại điểm."); raise VisionError("Calib đã thay đổi; lấy frame mới trước khi chuyển đổi."); return { |
| def VisionService.close | 192: def close(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_web_control/vision/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_web_control/vision/__init__.py (2 dòng, 70 byte) |
| PURPOSE | Khởi tạo namespace/package; library root có endpoint global và MOCK_RESPONSE. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100_yolo_auto_tracking/app.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/app.py (258 dòng, 9782 byte) |
| PURPOSE | Entry point và HTTP API/HMI; tạo controller/workflow và quản lý lifecycle. |
| ENTRY POINT | Có __main__ guard; xem phần entry point/deployment |
| CLASSES | Input:42; Connection:46; CameraInput:56; TrackingConfig:60; ProcessLease:75 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | _use_project_python, Path, resolve, executable.is_file, executable.resolve, SystemExit, subprocess.call, str, Input, ConfigDict, Connection, Field, field_validator, ipv4, ipaddress.IPv4Address, CameraInput, TrackingConfig, __enter__, mkdir, open, self.file.seek, msvcrt.locking, self.file.fileno, fcntl.flock, self.file.close, RuntimeError, __exit__, create_app, json.loads, read_text, NX100Controller, load_calibration, Automation, VisionPipeline, lifespan, ProcessLease, robot.start_monitor, auto.start_worker, auto.close, vision.close, robot.close, FastAPI, app.middleware, protect, request.headers.get |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | self.file |
| EXTERNAL DEPENDENCIES | import os [2]; import sys [3]; from pathlib import Path [4]; import subprocess [10]; import argparse [20]; import ipaddress [21]; import json [22]; import logging [23]; from logging.handlers import RotatingFileHandler [24]; from contextlib import asynccontextmanager [25]; from urllib.parse import urlsplit [26]; from fastapi import FastAPI, Request, HTTPException [28]; from fastapi.exceptions import RequestValidationError [29]; from fastapi.responses import FileResponse, JSONResponse, Response [30]; from fastapi.staticfiles import StaticFiles [31]; from pydantic import BaseModel, ConfigDict, Field, field_validator [32]; from robot.controller import NX100Controller, ControlError [34]; from vision.calibration import InputError [35]; from vision.pipeline import VisionPipeline, load_calibration [36]; from automation.auto_move import Automation [37]; import msvcrt [83]; import fcntl [86]; import uvicorn [243]; import threading [248]; import webbrowser [249] |
| ERROR HANDLING | SystemExit, KeyboardInterrupt, OSError, RuntimeError, Exception, ValueError, ControlError, HTTPException |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Entry/API có thể tạo worker/runtime file và gọi workflow; không tự coi import là read-only. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def _use_project_python | 7: def _use_project_python(): | raise SystemExit(subprocess.call([str(executable), str(Path(__file__).resolve()), *sys.argv[1:]])); raise SystemExit(130) |
| class Input | 42: class Input(BaseModel): | Class/dataclass/Enum; xem methods |
| class Connection | 46: class Connection(Input): | Class/dataclass/Enum; xem methods |
| def Connection.ipv4 | 52: def ipv4(cls, value): | return str(ipaddress.IPv4Address(value)) |
| class CameraInput | 56: class CameraInput(Input): | Class/dataclass/Enum; xem methods |
| class TrackingConfig | 60: class TrackingConfig(Input): | Class/dataclass/Enum; xem methods |
| class ProcessLease | 75: class ProcessLease: | Class/dataclass/Enum; xem methods |
| def ProcessLease.__enter__ | 77: def __enter__(self): | raise RuntimeError('Another backend owns this project; use one server process'); return self |
| def ProcessLease.__exit__ | 93: def __exit__(self, *args): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def create_app | 97: def create_app(mock=True, config=None, background=True): | return JSONResponse({'message': 'Host not authorized'}, status_code=403); return JSONResponse({'message': 'Invalid host'}, status_code=403); return JSONResponse({'message': 'Origin rejected'}, status_code=403); return JSONResponse({'message': 'Operator control header required'}, status_code=403) |
| def create_app.lifespan | 111: async def lifespan(app): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def create_app.protect | 128: async def protect(request: Request, call_next): | return JSONResponse({'message': 'Host not authorized'}, status_code=403); return JSONResponse({'message': 'Invalid host'}, status_code=403); return JSONResponse({'message': 'Origin rejected'}, status_code=403); return JSONResponse({'message': 'Operator control header required'}, status_code=403) |
| def create_app.control_error | 149: async def control_error(request, exc): | return JSONResponse({'code': exc.code, 'message': exc.message}, status_code=exc.status) |
| def create_app.input_error | 153: async def input_error(request, exc): | return JSONResponse({'message': str(exc)}, status_code=409) |
| def create_app.validation_error | 157: async def validation_error(request, exc): | return JSONResponse({'message': 'Invalid input', 'detail': str(exc)}, status_code=422) |
| def create_app.index | 161: def index(): | return FileResponse(BASE / 'templates/index.html') |
| def create_app.state | 165: def state(): | return dict(robot=robot.snapshot(), auto=auto.snapshot(), vision=vision.status(), |
| def create_app.connect | 173: def connect(data: Connection): | raise ControlError('RECONNECT_BLOCKED', 'Inspect motion/fault before restarting backend'); return robot.connect(data.ip, data.port) |
| def create_app.disconnect | 180: def disconnect(): | return robot.disconnect() |
| def create_app.scan | 187: def scan(): | return vision.scan() |
| def create_app.camera_connect | 191: def camera_connect(data: CameraInput): | return vision.status() |
| def create_app.camera_disconnect | 196: def camera_disconnect(): | return vision.status() |
| def create_app.preview | 201: def preview(): | raise HTTPException(404, 'No frame yet'); return Response(vision.preview, media_type='image/jpeg') |
| def create_app.configuration | 208: def configuration(data: TrackingConfig): | return auto.snapshot() |
| def create_app.start | 213: def start(): | return auto.snapshot() |
| def create_app.stop | 218: def stop(): | return auto.snapshot() |
| def create_app.hold | 223: def hold(): | return auto.hold() |
| def main | 230: def main(): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_yolo_auto_tracking/automation/auto_move.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/automation/auto_move.py (273 dòng, 13284 byte) |
| PURPOSE | Automation owner, stability publish, selection, send guard, STOP/HOME và fault. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Automation:13 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, threading.RLock, Stability, threading.Event, transition, or, self.robot.log, fault, self.transition, _vision_check, ControlError, self.clock, cfg, _real_check, self.config.get, v.get, int, start, self._vision_check, self._real_check, self.robot.read_status, self.robot.snapshot, self.robot.blocked, join, self.stop_requested.clear, self.stability.reset, stop, in, self.stop_requested.set, hold, self.robot.hold_pending.set, self.robot.hold, self.fault, update_config, self.cfg.update, publish, self.stability.update, vision_failed, _assess, eligibility, _send_guard, self.stop_requested.is_set, self._assess, in_workspace, tuple |
| CALLED BY | nx100_yolo_auto_tracking/app.py |
| STATE MODIFIED | self.clock, self.calibration_valid, self.lock, self.stability, self.version, self.state, self.armed, self.stop_requested, self.shutdown, self.thread, self.vision_ready, self.frame_time, self.targets, self.selected, self.last_completed_robot_target, self.completed_targets_by_id, self.completed_sites, self.home_active, self.message, self.last_decisions, self.items |
| EXTERNAL DEPENDENCIES | import threading [2]; import time [3]; from dataclasses import asdict [4]; from copy import deepcopy [5]; from robot.controller import ControlError [7]; from vision.stability import Stability [8]; from .state_machine import State [9]; from .target_manager import eligibility, in_workspace, select_next_target [10] |
| ERROR HANDLING | ControlError, Exception |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Automation | 13: class Automation: | Class/dataclass/Enum; xem methods |
| def Automation.__init__ | 14: def __init__(self, robot, config, calibration_id, calibration_valid=True, clock=time.monotonic): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Automation.transition | 36: def transition(self, state, message=''): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Automation.fault | 43: def fault(self, message): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Automation._vision_check | 48: def _vision_check(self): | raise ControlError('CALIBRATION_INVALID', 'Calibration is invalid'); raise ControlError('VISION_NOT_READY', 'Camera / YOLO frame unavailable or stale') |
| def Automation.cfg | 55: def cfg(self): | return self.config['tracking'] |
| def Automation._real_check | 58: def _real_check(self, pose=None): | return         v = self.config.get('robot_pose', {}); raise ControlError('TOOL_POSTURE_CHANGED', 'Tool / posture differs from configured value') |
| def Automation.start | 67: def start(self): | return             if self.state == State.FAULT:; raise ControlError('FAULT_LATCHED', 'Restart backend after inspecting the fault; automatic recovery disabled'); raise ControlError('MOTION_ACTIVE', 'Wait for current motion'); raise ControlError('START_BLOCKED', '; '.join(reasons)) |
| def Automation.stop | 88: def stop(self): | return         self.stop_requested.set()  # Set before waiting for the automation lock.; return             self.armed = False |
| def Automation.hold | 99: def hold(self): | return result |
| def Automation.update_config | 110: def update_config(self, changes): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Automation.publish | 118: def publish(self, items, frame_id, stamp, version, ready=True): | return             self.vision_ready, self.frame_time = ready, stamp |
| def Automation.vision_failed | 131: def vision_failed(self, message): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Automation._assess | 139: def _assess(self, target): | return eligibility(target, self.completed_targets_by_id, self.last_completed_robot_target, |
| def Automation._send_guard | 144: def _send_guard(self, target, pose): | raise ControlError('TARGET_CANCELLED', 'STOP before MOVE send'); raise ControlError('TARGET_CANCELLED', 'Target invalidated'); raise ControlError('TARGET_CANCELLED', 'Target no longer eligible'); raise ControlError('PATH_BLOCKED', 'Current pose outside validated convex workspace') |
| def Automation._home_guard | 156: def _home_guard(self, pose): | raise ControlError('HOME_BLOCKED', 'HOME path endpoints outside workspace') |
| def Automation._return_home | 161: def _return_home(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Automation.tick | 166: def tick(self): | return             try:; return                     phase = motion.get('phase'); return                         t = self.selected; return                 if self.stop_requested.is_set(): |
| def Automation._decorate | 233: def _decorate(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Automation.snapshot | 249: def snapshot(self): | return dict(state=self.state.value, armed=self.armed, stop_requested=self.stop_requested.is_set(), |
| def Automation.start_worker | 259: def start_worker(self): | return             def work(): |
| def Automation.start_worker.work | 263: def work(): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Automation.close | 269: def close(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_yolo_auto_tracking/automation/state_machine.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/automation/state_machine.py (19 dòng, 474 byte) |
| PURPOSE | Enum state của automation. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | State:4 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | State |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from enum import Enum [1] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class State | 4: class State(str, Enum): | Class/dataclass/Enum; xem methods |

### nx100_yolo_auto_tracking/automation/target_manager.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/automation/target_manager.py (37 dòng, 2148 byte) |
| PURPOSE | Selection thuần theo workspace/khoảng cách/ID; không trực tiếp gửi wire. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | in_workspace, len, all, isfinite, zip, eligibility, dist, completed_by_instance.get, any, select_next_target, min |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from math import dist, isfinite [2] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def in_workspace | 5: def in_workspace(xyz, workspace): | return len(xyz) == 3 and all(isfinite(v) and workspace[a][0] &lt;= v &lt;= workspace[a][1] |
| def eligibility | 10: def eligibility(target, completed_by_instance, last_completed, minimum_distance_mm, now, max_age, workspace, completed_sites=()): | return False, 'stale frame', None, None; return False, 'outside workspace', None, None; return False, 'distance from last MOVE &lt;= minimum', global_distance, own_distance; return False, 'same track unchanged', global_distance, own_distance |
| def select_next_target | 31: def select_next_target(tracked_objects, completed_targets_by_id, last_completed_robot_target, minimum_distance_mm=50.0, *, now, max_age, workspace, completed_sites=()): | return min(eligible, key=lambda t: t.object_id, default=None) |

### nx100_yolo_auto_tracking/automation/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/automation/__init__.py (2 dòng, 5 byte) |
| PURPOSE | Khởi tạo namespace/package; library root có endpoint global và MOCK_RESPONSE. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100_yolo_auto_tracking/robot/cartesian.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/robot/cartesian.py (63 dòng, 2937 byte) |
| PURPOSE | Pose Cartesian có metadata, reference check, Decimal coordinate và payload motion. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Pose:9 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | dataclass, parse, tuple, item.strip, raw.split, len, ProtocolError, encode_command, join, str, cls, verify_unchanged, list, range, Decimal, abs, coordinate, value.strip, number.is_finite, ValueError, number.quantize, m, format, build_move, isinstance, speed.strip, else, read_pose, Pose.parse, client.execute |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from dataclasses import dataclass [2]; from decimal import Decimal, InvalidOperation [3]; from .protocol import encode_command, ProtocolError [5] |
| ERROR HANDLING | ProtocolError, ValueError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 3, 28, 29, 36, 37, 39; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Pose | 9: class Pose: | Class/dataclass/Enum; xem methods |
| def Pose.parse | 14: def parse(cls, raw): | raise ProtocolError('RPOSC 0,1 cần đủ 14 giá trị gồm tư thế, tool và trục ngoài; nhận: ' + raw); raise ProtocolError('Dữ liệu vị trí chưa hợp lệ để tạo lệnh: ' + str(exc)) from exc; return cls(fields) |
| def Pose.verify_unchanged | 24: def verify_unchanged(self, current): | raise ProtocolError('Tool hoặc tư thế robot đã thay đổi; lấy lại vị trí hiện tại'); raise ProtocolError('Robot đã đổi vị trí kể từ lần lấy tọa độ; lấy lại vị trí trước khi gửi đích mới') |
| def coordinate | 33: def coordinate(value): | raise ValueError('Tọa độ phải là số hữu hạn trong phạm vi biểu diễn'); raise ValueError('X/Y/Z chỉ nhận tối đa 3 chữ số sau dấu chấm (mm)'); return format(fixed, '.3f'); raise ValueError('Tọa độ phải dùng số và dấu chấm thập phân') from exc |
| def build_move | 47: def build_move(command, speed, xyz, pose): | raise ValueError('Chọn MOVL/MOVJ và lấy vị trí từ robot trước'); raise ValueError('Cần nhập đủ XYZ hoặc XYZ/Rx/Ry/Rz'); return data |
| def read_pose | 61: def read_pose(client): | return Pose.parse(client.execute('RPOSC', '0,1')) |

### nx100_yolo_auto_tracking/robot/controller.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/robot/controller.py (459 dòng, 18873 byte) |
| PURPOSE | Robot adapter/controller, preflight, serialized IO, pose/status/motion monitoring. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | ControlError:20; NX100Controller:26 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | ControlError, __init__, super, threading.Lock, deque, threading.Event, dict, _set, log, logging.getLogger, info, self.logs.append, datetime.now, astimezone, isoformat, _trace, self.log, repr, snapshot, deepcopy, self.robot_lock.locked, self.hold_pending.is_set, round, time.monotonic, events, _operation, self.robot_lock.acquire, isinstance, str, lower, self._set, self.robot_lock.release, _cancel_pending_move, self.pending_move_cancel.set, _move_operation, self.move_pending.is_set, self.move_pending.set, self._operation, cancelled.is_set, self.move_pending.clear, _require, is_connected, connect, factory, self._status |
| CALLED BY | nx100_yolo_auto_tracking/app.py |
| STATE MODIFIED | self.status, self.mock, self.robot_lock, self.log_lock, self.logs, self.log_id, self.client, self.reference, self.reference_id, self.hold_pending, self.move_pending, self.intent_lock, self.pending_move_cancel, self.stopping, self.thread, self.active, self.state, self.status_clock |
| EXTERNAL DEPENDENCIES | import re [3]; import threading [4]; import time [5]; import uuid [6]; from collections import deque [7]; from contextlib import contextmanager [8]; from copy import deepcopy [9]; from datetime import datetime [10]; from .mock import MockClient [12]; from .protocol import Client, OutcomeUnknown, ProtocolError [13]; from .cartesian import build_move, read_pose [14]; from .status import Status [15]; import logging [63] |
| ERROR HANDLING | ControlError, ProtocolError, ValueError, OutcomeUnknown, self |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 406; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class ControlError | 20: class ControlError(RuntimeError): | Class/dataclass/Enum; xem methods |
| def ControlError.__init__ | 21: def __init__(self, code, message, status=409): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| class NX100Controller | 26: class NX100Controller: | Class/dataclass/Enum; xem methods |
| def NX100Controller.__init__ | 27: def __init__(self, config, mock=False): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller._set | 58: def _set(self, **changes): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller.log | 62: def log(self, level, message): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller._trace | 76: def _trace(self, direction, wire): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller.snapshot | 79: def snapshot(self): | return result |
| def NX100Controller.events | 89: def events(self, after=0): | return [dict(event) for event in self.logs if event["id"] &gt; after] |
| def NX100Controller._operation | 94: def _operation(self, wait=False, timeout=None): | raise ControlError("BUSY", "Robot communication busy; command was not queued"); raise ControlError(code, str(exc), 503) from exc |
| def NX100Controller._cancel_pending_move | 129: def _cancel_pending_move(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller._move_operation | 135: def _move_operation(self): | raise ControlError("HOLD_PENDING", "HOLD pending; MOVE blocked"); raise ControlError("MOVE_PENDING", "A MOVE request is already being processed"); raise ControlError("MOTION_ACTIVE", "Previous move still being monitored"); raise ControlError("MOVE_CANCELLED", "MOVE cancelled by HOLD or disconnect") |
| def NX100Controller._require | 157: def _require(self): | raise ControlError("DISCONNECTED", "NX100 DISCONNECTED"); return self.client |
| def NX100Controller.is_connected | 162: def is_connected(self): | return self.state["connected"] |
| def NX100Controller.connect | 165: def connect(self, ip, port): | raise ControlError("ALREADY_CONNECTED", "Disconnect before changing endpoint"); raise ControlError("HOLD_PENDING", "HOLD pending"); return self.snapshot() |
| def NX100Controller.disconnect | 184: def disconnect(self): | return self.snapshot() |
| def NX100Controller._status | 202: def _status(self): | raise ProtocolError("Malformed RSTATS: " + raw); raise ProtocolError("Invalid RSTATS: " + raw) from exc; return flags |
| def NX100Controller.read_status | 228: def read_status(self): | return self.snapshot() |
| def NX100Controller._cartesian | 233: def _cartesian(self): | return pose, values |
| def NX100Controller.read_cartesian | 245: def read_cartesian(self): | raise ControlError("MOTION_ACTIVE", "Wait for motion monitoring to finish"); return {**values, "reference_id": self.reference_id} |
| def NX100Controller._joint | 255: def _joint(self): | raise ProtocolError("Malformed RPOSJ: " + raw); return values |
| def NX100Controller.read_joint | 265: def read_joint(self): | return result |
| def NX100Controller.blocked | 272: def blocked(flags): | return reasons |
| def NX100Controller.move_cartesian | 290: def move_cartesian(self, motion, speed, coordinates, reference_id=None, send_guard=None): | raise ControlError("MOTION_ACTIVE", "Previous move still being monitored"); raise ControlError("HOLD_PENDING", "HOLD pending; MOVE blocked"); raise ControlError("READ_REQUIRED", "READ CURRENT POSITION before MOVE"); raise ControlError("INVALID_SPEED", "Speed outside configured range", 422) |
| def NX100Controller.move_joint | 358: def move_joint(self, **kwargs): | raise ControlError( |
| def NX100Controller.hold | 365: def hold(self): | return {"response": response, "message": "HOLD ACCEPTED"} |
| def NX100Controller.poll_once | 386: def poll_once(self): | return         try:; return                 flags = self._status(); return                 _, current = self._cartesian(); return                 self._joint() |
| def NX100Controller.start_monitor | 447: def start_monitor(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller.start_monitor.monitor | 448: def monitor(): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def NX100Controller.close | 455: def close(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_yolo_auto_tracking/robot/mock.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/robot/mock.py (52 dòng, 1914 byte) |
| PURPOSE | Phản hồi/diễn tiến mô phỏng; không đại diện physics hoặc dữ liệu thiết bị thật. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | MockClient:6 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, or, _advance, min, time.monotonic, zip, execute, self._advance, self.trace, encode, join, float, data.split, elif, ValueError, result.encode |
| CALLED BY | nx100_yolo_auto_tracking/robot/controller.py |
| STATE MODIFIED | self.port, self.trace, self.pose, self.origin, self.target, self.started, self.duration, self.word2, self.word1 |
| EXTERNAL DEPENDENCIES | import time [3] |
| ERROR HANDLING | ValueError |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Chỉ mô phỏng; không suy trạng thái thiết bị thật. |
| KNOWN LIMITATIONS | Không mô phỏng collision/pressure/cell safety. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class MockClient | 6: class MockClient: | Class/dataclass/Enum; xem methods |
| def MockClient.__init__ | 7: def __init__(self, ip, port=80, timeout=3, trace=None): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def MockClient._advance | 17: def _advance(self): | return         fraction = min(1, (time.monotonic() - self.started) / self.duration) |
| def MockClient.execute | 26: def execute(self, name, data=""): | raise ValueError("Unsupported mock command"); return result |

### nx100_yolo_auto_tracking/robot/protocol.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/robot/protocol.py (193 dòng, 8371 byte) |
| PURPOSE | Validate command và encode/receive ASCII NX100; serialized single-command socket. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | ProtocolError:14; OutcomeUnknown:18; _Reader:93; Client:126 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | ProtocolError, OutcomeUnknown, threading.Lock, _integer, re.fullmatch, ValueError, int, _number, number, float, math.isfinite, encode_command, isinstance, any, ord, item.strip, data.split, len, join, or, encode, __init__, bytearray, until, time.monotonic, self.buffer.find, bytes, decode, TimeoutError, repr, self.sock.settimeout, self.sock.recv, self.trace, self.buffer.extend, str, ipaddress.IPv4Address, isdigit, execute, socket.create_connection, Robot_access, _Reader, send, sock.sendall, reader.until, ack.startswith |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | self.sock, self.buffer, self.timeout, self.trace, self.ip, self.port |
| EXTERNAL DEPENDENCIES | import ipaddress [6]; import math [7]; import re [8]; import socket [9]; import threading [10]; import time [11] |
| ERROR HANDLING | ValueError, ProtocolError, TimeoutError, OutcomeUnknown |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Có đường gửi NX TCP khi hàm được gọi; không được gọi trong audit. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class ProtocolError | 14: class ProtocolError(RuntimeError): | Class/dataclass/Enum; xem methods |
| class OutcomeUnknown | 18: class OutcomeUnknown(ProtocolError): | Class/dataclass/Enum; xem methods |
| def _integer | 27: def _integer(value, lower, upper): | raise ValueError("Expected an unsigned decimal integer"); raise ValueError("Integer outside allowed range"); return number |
| def _number | 36: def _number(value): | raise ValueError("Expected a finite decimal number (no exponent)"); raise ValueError("Non-finite number"); return result |
| def encode_command | 45: def encode_command(name, data=""): | raise ValueError("Command outside tracking scope"); raise ValueError("Command and data must be strings"); raise ValueError("Only printable ASCII is accepted; CR/LF are added internally"); raise ValueError(name + " takes no data") |
| class _Reader | 93: class _Reader: | Class/dataclass/Enum; xem methods |
| def _Reader.__init__ | 94: def __init__(self, sock, timeout, trace): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def _Reader.until | 100: def until(self, ending): | return result[:-len(ending)].decode("ascii"); raise ProtocolError("Response exceeds receive limit"); raise TimeoutError("Response deadline expired; pending RX=" + repr(bytes(self.buffer))); raise TimeoutError("Receive timed out; pending RX=" + repr(bytes(self.buffer))) from exc |
| class Client | 126: class Client: | Class/dataclass/Enum; xem methods |
| def Client.__init__ | 127: def __init__(self, ip, port=80, timeout=5.0, trace=None): | raise ValueError("Port must be 1..65535"); raise ValueError("Timeout must be &gt; 0 and &lt;= 60 seconds") |
| def Client.execute | 137: def execute(self, name, data=""): | raise ProtocolError("Handshake rejected: " + greeting); raise ProtocolError("Command rejected: " + ack); raise ProtocolError(result); raise ProtocolError("Control answer must end with CRLF") |
| def Client.execute.send | 147: def send(wire): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_yolo_auto_tracking/robot/status.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/robot/status.py (53 dòng, 1571 byte) |
| PURPOSE | Giải mã RSTATS bằng fixed bit masks. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Status:1 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, word, int, isinstance, value.startswith, ValueError, is_step, bool, is_one_cycle, is_auto, is_running, is_safety_speed_operation, is_teach, is_play, is_command_remote, is_programming_pendant_hold, is_external_hold, is_command_hold, is_alarm_occurring, is_error_occurring, is_servo_on |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | self.data_1, self.data_2 |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | ValueError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 52; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Status | 1: class Status: | Class/dataclass/Enum; xem methods |
| def Status.__init__ | 3: def __init__(self, data_1, data_2): | raise ValueError('Invalid RSTATS word'); return result |
| def Status.__init__.word | 4: def word(value, maximum): | raise ValueError('Invalid RSTATS word'); return result |
| def Status.is_step | 12: def is_step(self): | return bool(self.data_1 & (1 &lt;&lt; 0)) |
| def Status.is_one_cycle | 15: def is_one_cycle(self): | return bool(self.data_1 & (1 &lt;&lt; 1)) |
| def Status.is_auto | 18: def is_auto(self): | return bool(self.data_1 & (1 &lt;&lt; 2)) |
| def Status.is_running | 21: def is_running(self): | return bool(self.data_1 & (1 &lt;&lt; 3)) |
| def Status.is_safety_speed_operation | 24: def is_safety_speed_operation(self): | return bool(self.data_1 & (1 &lt;&lt; 4)) |
| def Status.is_teach | 27: def is_teach(self): | return bool(self.data_1 & (1 &lt;&lt; 5)) |
| def Status.is_play | 30: def is_play(self): | return bool(self.data_1 & (1 &lt;&lt; 6)) |
| def Status.is_command_remote | 33: def is_command_remote(self): | return bool(self.data_1 & (1 &lt;&lt; 7)) |
| def Status.is_programming_pendant_hold | 36: def is_programming_pendant_hold(self): | return bool(self.data_2 & (1 &lt;&lt; 1)) |
| def Status.is_external_hold | 39: def is_external_hold(self): | return bool(self.data_2 & (1 &lt;&lt; 2)) |
| def Status.is_command_hold | 42: def is_command_hold(self): | return bool(self.data_2 & (1 &lt;&lt; 3)) |
| def Status.is_alarm_occurring | 45: def is_alarm_occurring(self): | return bool(self.data_2 & (1 &lt;&lt; 4)) |
| def Status.is_error_occurring | 48: def is_error_occurring(self): | return bool(self.data_2 & (1 &lt;&lt; 5)) |
| def Status.is_servo_on | 51: def is_servo_on(self): | return bool(self.data_2 & (1 &lt;&lt; 6)) |

### nx100_yolo_auto_tracking/robot/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/robot/__init__.py (2 dòng, 5 byte) |
| PURPOSE | Khởi tạo namespace/package; library root có endpoint global và MOCK_RESPONSE. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100_yolo_auto_tracking/vision/calibration.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/vision/calibration.py (86 dòng, 4698 byte) |
| PURPOSE | Load/validate calibration và pixel→Base ray-plane; xem chính sách offset theo project. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | InputError:8; PixelToRobot:17 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | InputError, Path, resolve, __init__, np.load, np.array, reshape, int, item, str, json.loads, np.isfinite, all, np.allclose, np.eye, np.isclose, np.linalg.det, in, min, self.report.get, get, quality_message, summary.get, check_frame, convert, not, cv2.undistortPoints, abs |
| CALLED BY | nx100_yolo_auto_tracking/vision/pipeline.py |
| STATE MODIFIED | self.path, self.T, self.K, self.distortion, self.size, self.quality, self.report |
| EXTERNAL DEPENDENCIES | import json [2]; from pathlib import Path [3]; import cv2 [5]; import numpy as np [6] |
| ERROR HANDLING | InputError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 14, 30, 31, 32, 36, 69; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class InputError | 8: class InputError(ValueError): | Class/dataclass/Enum; xem methods |
| class PixelToRobot | 17: class PixelToRobot: | Class/dataclass/Enum; xem methods |
| def PixelToRobot.__init__ | 18: def __init__(self, filename): | raise InputError("T_base_camera phải là ma trận 4x4 hữu hạn."); raise InputError("T_base_camera không phải rigid transform hợp lệ."); raise InputError("Intrinsic/kích thước ảnh không hợp lệ."); raise InputError("Kết quả calib phải dùng đơn vị mm.") |
| def PixelToRobot.quality_message | 46: def quality_message(self): | return message |
| def PixelToRobot.check_frame | 57: def check_frame(self, frame): | raise InputError(f"Ảnh {width}x{height} khác calib {self.size[0]}x{self.size[1]}. " |
| def PixelToRobot.convert | 63: def convert(self, u, v, plane_z): | raise InputError("Pixel và Z phải là số hữu hạn."); raise InputError("Pixel nằm ngoài ảnh gốc."); raise InputError("Tia nhìn song song mặt phẳng Z; không xác định giao điểm."); raise InputError("Mặt phẳng nằm phía sau camera theo tia nhìn. Kiểm tra Z và calib.") |

### nx100_yolo_auto_tracking/vision/camera.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/vision/camera.py (234 dòng, 11867 byte) |
| PURPOSE | Adapter MVS SDK Windows: enum/open/grab/convert/free/lifecycle. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | _InstalledSdkFinder:17; MvsCamera:29 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | _InstalledSdkFinder, __init__, folder.glob, find_spec, importlib.machinery.PathFinder.find_spec, str, threading.RLock, threading.Event, Path, os.environ.get, ProgramFiles, roots.extend, roots.append, next, is_file, struct.calcsize, not, InputError, dll.open, stream.seek, struct.unpack, stream.read, os.add_dll_directory, ct.WinDLL, sys.meta_path.insert, importlib.import_module, sys.meta_path.remove, self.module.MvCamera.MV_CC_GetSDKVersion, hasattr, self.check, self.module.MvCamera.MV_CC_Initialize, check, status, or, text, bytes, split, decode, enumerate, m.MV_CC_DEVICE_INFO_LIST, m.MvCamera.MV_CC_EnumDevices, range, ct.cast, ct.POINTER, result.append |
| CALLED BY | nx100_yolo_auto_tracking/vision/pipeline.py |
| STATE MODIFIED | self.folder, self.names, self.module, self.cam, self.devices, self.latest, self.thread, self.dll_directory, self.connected, self.latest_at, self.frame_id, self.sdk_frame_id, self.error, self.lock, self.stop, self.sdk_version |
| EXTERNAL DEPENDENCIES | import ctypes as ct [2]; import importlib [3]; import importlib.abc [4]; import importlib.machinery [5]; import os [6]; import struct [7]; import sys [8]; import threading [9]; import time [10]; from pathlib import Path [11]; import cv2 [12]; import numpy as np [13]; from .calibration import InputError [14] |
| ERROR HANDLING | InputError, Exception, self |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Có thể mở/cấu hình/capture camera khi gọi connect; không thực thi. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class _InstalledSdkFinder | 17: class _InstalledSdkFinder(importlib.abc.MetaPathFinder): | Class/dataclass/Enum; xem methods |
| def _InstalledSdkFinder.__init__ | 19: def __init__(self, folder): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def _InstalledSdkFinder.find_spec | 23: def find_spec(self, fullname, path=None, target=None): | return importlib.machinery.PathFinder.find_spec(fullname, [str(self.folder)]); return None |
| class MvsCamera | 29: class MvsCamera: | Class/dataclass/Enum; xem methods |
| def MvsCamera.__init__ | 30: def __init__(self, sdk_root=None): | raise InputError("Không tìm thấy Python wrapper MVS của hãng cho Windows."); raise InputError("DLL MVS khác architecture với Python.") |
| def MvsCamera.check | 82: def check(code, operation): | raise InputError(f"MVS: {operation} lỗi 0x{code & 0xFFFFFFFF:08X}; kiểm tra cáp/camera và đóng MVS nếu đang giữ camera.") |
| def MvsCamera.status | 86: def status(self): | return {"available": self.module is not None, "connected": self.connected, "sdk_version": self.sdk_version, |
| def MvsCamera.text | 92: def text(array): | return bytes(array).split(b"\0", 1)[0].decode("utf-8", errors="replace") |
| def MvsCamera.enumerate | 95: def enumerate(self): | raise InputError(self.error); raise InputError("Ngắt camera trước khi liệt kê lại."); return result |
| def MvsCamera.connect | 111: def connect(self, index): | raise InputError(self.error); raise InputError("Camera đã mở; hãy ngắt trước khi đổi camera."); raise InputError("Liệt kê và chọn camera hợp lệ trước."); raise             self.connected, self.error = True, "" |
| def MvsCamera._grab | 142: def _grab(self): | raise InputError("Mất frame/camera ngắt kết nối; kiểm tra cáp và kết nối lại."); raise InputError("Frame camera có kích thước không hợp lệ/quá lớn."); raise InputError("MVS trả buffer RGB có độ dài không đúng.") |
| def MvsCamera.frame | 186: def frame(self): | raise InputError(self.error or "Camera chưa có frame mới. Kết nối và chờ preview trước khi chụp."); return self.latest.copy() |
| def MvsCamera.sample | 192: def sample(self): | return self.frame_id, self.latest_at, self.frame() |
| def MvsCamera.disconnect | 196: def disconnect(self): | raise InputError("SDK chưa dừng lấy frame; thử ngắt lại, không giải phóng buffer khi còn đang dùng."); raise InputError(self.error) |
| def MvsCamera.close | 222: def close(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_yolo_auto_tracking/vision/detector.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/vision/detector.py (35 dòng, 1546 byte) |
| PURPOSE | YOLO predict native-image bbox center/confidence/class-name rồi transform. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Detector:6 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, os.environ.setdefault, str, YOLO, detect, calibration.check_frame, self.model.predict, tuple, ValueError, float, cpu, tolist, all, math.isfinite, not, dict, item, int, calibration.convert, items.append |
| CALLED BY | nx100_yolo_auto_tracking/vision/pipeline.py |
| STATE MODIFIED | self.model, self.config |
| EXTERNAL DEPENDENCIES | import math [2]; import os [3]; from ultralytics import YOLO [9] |
| ERROR HANDLING | ValueError, Exception |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 26; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Detector | 6: class Detector: | Class/dataclass/Enum; xem methods |
| def Detector.__init__ | 7: def __init__(self, model_path, config): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Detector.detect | 13: def detect(self, frame, calibration, cfg): | raise ValueError('YOLO original image size differs from calibration'); return items |

### nx100_yolo_auto_tracking/vision/pipeline.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/vision/pipeline.py (146 dòng, 6496 byte) |
| PURPOSE | Vision worker/camera/model/calibration/tracker, preview và publication target. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | VisionPipeline:26 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | load_calibration, PixelToRobot, np.load, np.array_equal, ravel, or, int, InputError, hashlib.sha256, path.read_bytes, hexdigest, __init__, threading.RLock, threading.Lock, threading.Event, BoardTracker, scan, dict, MvsCamera, get, self.camera.enumerate, connect, self.thread.is_alive, Detector, self.camera.connect, self.stop.clear, threading.Thread, self.thread.start, self.auto.robot.log, connected, _work, time.monotonic, self.stop.wait, deepcopy, np.full, enumerate, items.append, float, self.camera.sample, self.calibration.check_frame, self.detector.detect, self.tracker.update, in, self.auto.publish, max |
| CALLED BY | nx100_yolo_auto_tracking/app.py |
| STATE MODIFIED | self.calibration, self.mock, self.lock, self.lifecycle_lock, self.camera, self.detector, self.thread, self.stop, self.connected, self.error, self.preview, self.fps, self.frame_id, self.tracker |
| EXTERNAL DEPENDENCIES | import hashlib [1]; import threading [2]; import time [3]; from copy import deepcopy [4]; import cv2 [6]; import numpy as np [7]; from .calibration import PixelToRobot, InputError [9]; from .camera import MvsCamera [10]; from .detector import Detector [11]; from .tracker import BoardTracker [12] |
| ERROR HANDLING | InputError, Exception |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 99; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def load_calibration | 15: def load_calibration(base): | raise InputError('Intrinsic differs from Eye-to-Hand calibration'); return calibration, hashlib.sha256(path.read_bytes()).hexdigest() |
| class VisionPipeline | 26: class VisionPipeline: | Class/dataclass/Enum; xem methods |
| def VisionPipeline.__init__ | 27: def __init__(self, base, auto, calibration): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def VisionPipeline.scan | 41: def scan(self): | return [dict(index=0, name='MOCK HIKROBOT + synthetic detections')]; return self.camera.enumerate() |
| def VisionPipeline.connect | 49: def connect(self, index): | raise InputError('Disconnect camera before connecting again'); raise InputError('Mock camera index must be 0'); raise InputError('Invalid calibration'); raise InputError('Scan camera first') |
| def VisionPipeline._work | 69: def _work(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def VisionPipeline._render | 111: def _render(self, frame, items): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def VisionPipeline.status | 124: def status(self): | return dict(connected=self.connected, fps=round(self.fps, 1), error=self.error, |
| def VisionPipeline.disconnect | 128: def disconnect(self): | raise InputError('Inference still running; wait before disconnecting again') |
| def VisionPipeline.close | 142: def close(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100_yolo_auto_tracking/vision/stability.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/vision/stability.py (64 dòng, 2709 byte) |
| PURPOSE | Cửa sổ frame/timing/identity; tracking và full dùng policy khác nhau. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Target:7; Stability:20 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | dataclass, __init__, reset, self.records.clear, update, isfinite, self.reset, and, set, tuple, item.get, len, all, self.records.pop, item.update, present.add, self.records.get, dist, dict, round, ready.append, Target, in, self.records.items |
| CALLED BY | nx100_yolo_auto_tracking/automation/auto_move.py |
| STATE MODIFIED | self.records, self.last_frame, self.last_time |
| EXTERNAL DEPENDENCIES | from dataclasses import dataclass [2]; from math import dist, isfinite [3] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Target | 7: class Target: | Class/dataclass/Enum; xem methods |
| class Stability | 20: class Stability: | Class/dataclass/Enum; xem methods |
| def Stability.__init__ | 21: def __init__(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Stability.reset | 26: def reset(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Stability.update | 29: def update(self, items, frame_id, stamp, now, cfg, version, calibration_id): | return []; return []; return ready |

### nx100_yolo_auto_tracking/vision/tracker.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/vision/tracker.py (71 dòng, 3455 byte) |
| PURPOSE | Greedy bbox association, uncertain, reserved ID10 s và instance generation. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | BoardTracker:6 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, match_score, max, min, math.hypot, update, time.monotonic, self.tracks.items, enumerate, self.match_score, candidates.append, set, any, and, abs, sorted, assigned_ids.add, assigned_indices.add, range, len, reserved_ids.add, self.tracks.get, dict |
| CALLED BY | nx100_yolo_auto_tracking/vision/pipeline.py |
| STATE MODIFIED | self.missing_timeout, self.tracks, self.generation |
| EXTERNAL DEPENDENCIES | import math [2]; import time [3] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 23, 24, 25; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class BoardTracker | 6: class BoardTracker: | Class/dataclass/Enum; xem methods |
| def BoardTracker.__init__ | 7: def __init__(self, missing_timeout=10.0): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def BoardTracker.match_score | 13: def match_score(previous, current): | return None; return None; return None; return iou + .2 * (1 - min(relative_distance, 1)) |
| def BoardTracker.update | 30: def update(self, detections, now=None): | return sorted(detections, key=lambda item: item["id"]) |

### nx100_yolo_auto_tracking/vision/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100_yolo_auto_tracking/vision/__init__.py (2 dòng, 5 byte) |
| PURPOSE | Khởi tạo namespace/package; library root có endpoint global và MOCK_RESPONSE. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100-remote-control-master/nx100-remote-control-master/setup.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/setup.py (13 dòng, 264 byte) |
| PURPOSE | Packaging setuptools, không chạy trong audit. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | setup |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from setuptools import setup [1] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100-remote-control-master/nx100-remote-control-master/Testing.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/Testing.py (109 dòng, 3364 byte) |
| PURPOSE | Ví dụ development gọi start_app ngay top-level, hiện có đọc robot; không import để audit. |
| ENTRY POINT | start_app() top-level |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | callback_success, print, callback_failed, start_app, logging.basicConfig, os.environ.get, WebServer.run, Commands.read_alarms, Commands.read_current_joint_coordinate_position, Commands.read_current_specified_coordinate_system_position, Commands.read_status, Commands.read_current_job_details, Commands.write_hold, Commands.write_reset, Commands.write_cancel, Commands.write_servo_power, Commands.write_start_job, Commands.write_linear_move, MoveL.MoveL, Utils.binary_to_decimal, Commands.read_all_job_names, Commands.write_master_job, Gripper.write_gripper_close, Gripper.write_gripper_open, Gripper.read_gripper_closed_command_register, Gripper.gripper_is_closed, Gripper.read_gripper_hit, Commands.robot_in_target_point_callback, LinearMove.LinearMove, linear_move.go, MoveJ.MoveJ, JointMove.JointMove |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | import nx100_remote_control [5]; from nx100_remote_control.module import Commands, WebServer, Utils, JointMove [6]; from nx100_remote_control.objects import MoveJ [7]; from nx100_remote_control.objects import MoveJ [8]; import logging [9]; import os [10] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def callback_success | 13: def callback_success(): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def callback_failed | 17: def callback_failed(): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def start_app | 21: def start_app(): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100-remote-control-master/nx100-remote-control-master/XboxController.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/XboxController.py (110 dòng, 3193 byte) |
| PURPOSE | Ví dụ pygame loop, joystick có thể phát servo/START/MOVL trực tiếp. |
| ENTRY POINT | Vòng pygame top-level |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | pygame.display.set_mode, pygame.display.set_caption, pygame.time.Clock, xbox360_controller.Controller, Time.Time, Time.Time.get_current_millis, get_position, Commands.read_current_specified_coordinate_system_position, str, pygame.event.get, Commands.write_servo_power, print, Commands.write_start_job, controller.get_id, controller.get_left_stick, time.has_seconds_passed, time.set_time_now, time.get_current_millis, Commands.write_linear_move, MoveL.MoveL, int, abs, c_pos.get_x, c_pos.get_y, c_pos.get_z, c_pos.get_tx, c_pos.get_ty, c_pos.get_tz, Utils.binary_to_decimal, screen.fill, pygame.draw.circle, pygame.display.flip, clock.tick, pygame.quit |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from nx100_remote_control.module import xbox360_controller, Commands, Utils [6]; from nx100_remote_control.objects import Time, MoveL [7]; import pygame [8] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def get_position | 40: def get_position(): | return Commands.read_current_specified_coordinate_system_position(str(COORDINATE_SYSTEM), '0') |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/__init__.py (12 dòng, 264 byte) |
| PURPOSE | Khởi tạo namespace/package; library root có endpoint global và MOCK_RESPONSE. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Cartesian.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Cartesian.py (63 dòng, 2964 byte) |
| PURPOSE | Pose Cartesian có metadata, reference check, Decimal coordinate và payload motion. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Pose:9 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | dataclass, parse, tuple, item.strip, raw.split, len, ProtocolError, encode_command, join, str, cls, verify_unchanged, list, range, Decimal, abs, coordinate, value.strip, number.is_finite, ValueError, number.quantize, m, format, build_move, isinstance, speed.strip, else, read_pose, Pose.parse, client.execute |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from dataclasses import dataclass [2]; from decimal import Decimal, InvalidOperation [3]; from nx100_remote_control.module.Protocol import encode_command, ProtocolError [5] |
| ERROR HANDLING | ProtocolError, ValueError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 3, 28, 29, 36, 37, 39; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Pose | 9: class Pose: | Class/dataclass/Enum; xem methods |
| def Pose.parse | 14: def parse(cls, raw): | raise ProtocolError('RPOSC 0,1 cần đủ 14 giá trị gồm tư thế, tool và trục ngoài; nhận: ' + raw); raise ProtocolError('Dữ liệu vị trí chưa hợp lệ để tạo lệnh: ' + str(exc)) from exc; return cls(fields) |
| def Pose.verify_unchanged | 24: def verify_unchanged(self, current): | raise ProtocolError('Tool hoặc tư thế robot đã thay đổi; lấy lại vị trí hiện tại'); raise ProtocolError('Robot đã đổi vị trí kể từ lần lấy tọa độ; lấy lại vị trí trước khi gửi đích mới') |
| def coordinate | 33: def coordinate(value): | raise ValueError('Tọa độ phải là số hữu hạn trong phạm vi biểu diễn'); raise ValueError('X/Y/Z chỉ nhận tối đa 3 chữ số sau dấu chấm (mm)'); return format(fixed, '.3f'); raise ValueError('Tọa độ phải dùng số và dấu chấm thập phân') from exc |
| def build_move | 47: def build_move(command, speed, xyz, pose): | raise ValueError('Chọn MOVL/MOVJ và lấy vị trí từ robot trước'); raise ValueError('Cần nhập đủ XYZ hoặc XYZ/Rx/Ry/Rz'); return data |
| def read_pose | 61: def read_pose(client): | return Pose.parse(client.execute('RPOSC', '0,1')) |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Commands.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Commands.py (198 dòng, 8422 byte) |
| PURPOSE | Legacy wrapper command và callback chờ vị trí; bề mặt API rộng hơn validator. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | read_alarms, Socket.exec_single_command, Command.Command, Utils.print_response_details, Alarm.Alarm, logging.info, str, alarms.get_alarms, read_current_joint_coordinate_position, read_current_specified_coordinate_system_position, CurrentPos.CurrentPos, read_status, response_data.split, Utils.decimal_to_binary, int, Status.Status, s.is_command_remote, s.is_play, s.is_teach, s.is_safety_speed_operation, s.is_running, s.is_auto, s.is_one_cycle, s.is_step, s.is_servo_on, s.is_error_occurring, s.is_alarm_occurring, s.is_command_hold, s.is_external_hold, s.is_programming_pendant_hold, read_current_job_details, JobDetail.JobDetail, write_hold, in, ValueError, Response.Response, response.get_response, response.is_success, write_reset, write_cancel, write_servo_power, write_start_job, write_linear_move, move_l.get_command, write_joint_motion_move |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from nx100_remote_control.objects import Command, Status, JobDetail, CurrentPos, Alarm, Response [1]; from nx100_remote_control.module import Socket, Utils [2]; import logging [3]; import time [4] |
| ERROR HANDLING | ValueError |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Có đường gửi NX TCP khi hàm được gọi; không được gọi trong audit. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def read_alarms | 8: def read_alarms(): | return alarms |
| def read_current_joint_coordinate_position | 17: def read_current_joint_coordinate_position(): | return response_data |
| def read_current_specified_coordinate_system_position | 26: def read_current_specified_coordinate_system_position(coordinate_system, include_external_axis='0'): | return CurrentPos.CurrentPos(position_response) |
| def read_status | 35: def read_status(): | return s |
| def read_current_job_details | 60: def read_current_job_details(): | return JobDetail.JobDetail(response_data) |
| def write_hold | 67: def write_hold(command): | raise ValueError('HOLD requires exactly 1 or 0'); return response |
| def write_reset | 77: def write_reset(): | return response |
| def write_cancel | 85: def write_cancel(): | return response |
| def write_servo_power | 93: def write_servo_power(command): | raise ValueError('SVON requires exactly 1 or 0'); return response |
| def write_start_job | 103: def write_start_job(job_name): | return response |
| def write_linear_move | 112: def write_linear_move(move_l): | return response |
| def write_joint_motion_move | 124: def write_joint_motion_move(move_j): | return response |
| def robot_in_target_point_callback | 135: def robot_in_target_point_callback(move_l, timeout=10, _callback_success=None, _callback_failed=None): | return True; return False |
| def read_io_signals | 159: def read_io_signals(io): | return response |
| def write_io_signals | 170: def write_io_signals(io): | return response |
| def read_all_job_names | 181: def read_all_job_names(): | return response |
| def write_master_job | 192: def write_master_job(job_name): | return response |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Gripper.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Gripper.py (63 dòng, 2367 byte) |
| PURPOSE | Mapping gripper custom legacy chưa tương thích IO byte validator; không dùng cho EOAT hiện tại. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | signal, write_gripper_close, IO.IO, io_out.set_first_eight_io_contracts, Commands.write_io_signals, write_gripper_open, read_gripper_closed_command_register, Gripper.Gripper, gripper_status.set_closed_status, Commands.read_io_signals, read_gripper_acknowledge, get_response, logging.info, gripper_status.is_gripper_closed, gripper_is_closed, off, read_gripper_hit |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from nx100_remote_control.module import Commands [1]; from nx100_remote_control.objects import IO, Gripper [2]; import logging [3] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def write_gripper_close | 17: def write_gripper_close(): | return Commands.write_io_signals(io_out) |
| def write_gripper_open | 23: def write_gripper_open(): | return Commands.write_io_signals(io_out) |
| def read_gripper_closed_command_register | 30: def read_gripper_closed_command_register(): | return gripper_status |
| def read_gripper_acknowledge | 39: def read_gripper_acknowledge(): | return gripper_status.is_gripper_closed() |
| def gripper_is_closed | 48: def gripper_is_closed(): | return gripper_status.is_gripper_closed() |
| def read_gripper_hit | 57: def read_gripper_hit(): | return gripper_status |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/JointMove.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/JointMove.py (51 dòng, 1578 byte) |
| PURPOSE | Legacy blocking commander, poll mỗi1 s/timeout, stop gửi HOLD. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | JointMove:9 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | JointMove, __init__, go, Commands.write_joint_motion_move, response.is_success, range, time.sleep, Commands.read_current_specified_coordinate_system_position, str, move_j.get_coordinate_specification, Utils.is_in_position, stop, Commands.write_hold |
| CALLED BY | nx100-remote-control-master/nx100-remote-control-master/Testing.py |
| STATE MODIFIED | self.stopped |
| EXTERNAL DEPENDENCIES | from nx100_remote_control.module import Commands, Utils [5]; import time [6] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class JointMove | 9: class JointMove(object): | Class/dataclass/Enum; xem methods |
| def JointMove.__init__ | 12: def __init__(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def JointMove.go | 15: def go(self, move_j, wait=True, poll_limit_seconds=30): | return False; return True; return False; return True |
| def JointMove.stop | 45: def stop(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/LinearMove.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/LinearMove.py (51 dòng, 1574 byte) |
| PURPOSE | Legacy blocking commander, poll mỗi1 s/timeout, stop gửi HOLD. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | LinearMove:9 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | LinearMove, __init__, go, Commands.write_linear_move, response.is_success, range, time.sleep, Commands.read_current_specified_coordinate_system_position, str, move_l.get_coordinate_specification, Utils.is_in_position, stop, Commands.write_hold |
| CALLED BY | nx100-remote-control-master/nx100-remote-control-master/Testing.py |
| STATE MODIFIED | self.stopped |
| EXTERNAL DEPENDENCIES | from nx100_remote_control.module import Commands, Utils [5]; import time [6] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class LinearMove | 9: class LinearMove(object): | Class/dataclass/Enum; xem methods |
| def LinearMove.__init__ | 12: def __init__(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def LinearMove.go | 15: def go(self, move_l, wait=True, poll_limit_seconds=30): | return False; return True; return False; return True |
| def LinearMove.stop | 45: def stop(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/MockResponse.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/MockResponse.py (90 dòng, 2324 byte) |
| PURPOSE | Phản hồi/diễn tiến mô phỏng; không đại diện physics hoặc dữ liệu thiết bị thật. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | get_mock_response |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Chỉ mô phỏng; không suy trạng thái thiết bị thật. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def get_mock_response | 55: def get_mock_response(command): | return RALARM; return RPOSJ; return RPOSC; return RSTATS |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Protocol.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Protocol.py (212 dòng, 9486 byte) |
| PURPOSE | Validate command và encode/receive ASCII NX100; serialized single-command socket. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | ProtocolError:14; OutcomeUnknown:18; _Reader:112; Client:145 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | ProtocolError, OutcomeUnknown, threading.Lock, _integer, re.fullmatch, ValueError, int, _number, number, float, math.isfinite, encode_command, isinstance, any, ord, item.strip, data.split, len, join, or, encode, __init__, bytearray, until, time.monotonic, self.buffer.find, bytes, decode, TimeoutError, repr, self.sock.settimeout, self.sock.recv, self.trace, self.buffer.extend, str, ipaddress.IPv4Address, isdigit, execute, socket.create_connection, Robot_access, _Reader, send, sock.sendall, reader.until, ack.startswith |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | self.sock, self.buffer, self.timeout, self.trace, self.ip, self.port |
| EXTERNAL DEPENDENCIES | import ipaddress [6]; import math [7]; import re [8]; import socket [9]; import threading [10]; import time [11] |
| ERROR HANDLING | ValueError, ProtocolError, TimeoutError, OutcomeUnknown |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Có đường gửi NX TCP khi hàm được gọi; không được gọi trong audit. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class ProtocolError | 14: class ProtocolError(RuntimeError): | Class/dataclass/Enum; xem methods |
| class OutcomeUnknown | 18: class OutcomeUnknown(ProtocolError): | Class/dataclass/Enum; xem methods |
| def _integer | 27: def _integer(value, lower, upper): | raise ValueError("Expected an unsigned decimal integer"); raise ValueError("Integer outside allowed range"); return number |
| def _number | 36: def _number(value): | raise ValueError("Expected a finite decimal number (no exponent)"); raise ValueError("Non-finite number"); return result |
| def encode_command | 45: def encode_command(name, data=""): | raise ValueError("Command and data must be strings"); raise ValueError("Only printable ASCII is accepted; CR/LF are added internally"); raise ValueError(name + " takes no data"); raise ValueError(name + " requires exactly 0 or 1") |
| class _Reader | 112: class _Reader: | Class/dataclass/Enum; xem methods |
| def _Reader.__init__ | 113: def __init__(self, sock, timeout, trace): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def _Reader.until | 119: def until(self, ending): | return result[:-len(ending)].decode("ascii"); raise ProtocolError("Response exceeds receive limit"); raise TimeoutError("Response deadline expired; pending RX=" + repr(bytes(self.buffer))); raise TimeoutError("Receive timed out; pending RX=" + repr(bytes(self.buffer))) from exc |
| class Client | 145: class Client: | Class/dataclass/Enum; xem methods |
| def Client.__init__ | 146: def __init__(self, ip, port=80, timeout=5.0, trace=None): | raise ValueError("Port must be 1..65535"); raise ValueError("Timeout must be &gt; 0 and &lt;= 60 seconds") |
| def Client.execute | 156: def execute(self, name, data=""): | raise ProtocolError("Handshake rejected: " + greeting); raise ProtocolError("Command rejected: " + ack); raise ProtocolError(result); raise ProtocolError("Control answer must end with CRLF") |
| def Client.execute.send | 166: def send(wire): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Socket.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Socket.py (17 dòng, 712 byte) |
| PURPOSE | Compatibility adapter single-command và mock; multiple-command chưa triển khai. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | exec_single_command, encode_command, Utils.clean_response, MockResponse.get_mock_response, Client, execute, exec_multiple_commands, NotImplementedError |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | import nx100_remote_control [2]; from nx100_remote_control.module import Utils, MockResponse [3]; from nx100_remote_control.module.Protocol import Client, encode_command [4] |
| ERROR HANDLING | NotImplementedError |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def exec_single_command | 7: def exec_single_command(command): | return Utils.clean_response(MockResponse.get_mock_response(command)); return Client(nx100_remote_control.NX100_IP_ADDRESS, |
| def exec_multiple_commands | 15: def exec_multiple_commands(commands): | raise NotImplementedError("Use explicit sequential single commands") |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Utils.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Utils.py (61 dòng, 1532 byte) |
| PURPOSE | Length/binary/response utility và tolerance check legacy. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | utf8len, len, s.encode, command_data_length, print_response_details, logging.info, decimal_to_binary, bin, binary_to_decimal, pow, clean_response, replace, equivalent, abs, is_in_position, cp.get_x, move_l.get_x, cp.get_y, move_l.get_y, cp.get_z, move_l.get_z, cp.get_tx, move_l.get_tx, cp.get_ty, move_l.get_ty, cp.get_tz, move_l.get_tz |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | import logging [1] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def utf8len | 7: def utf8len(s): | return len(s.encode('utf-8')) |
| def command_data_length | 12: def command_data_length(command): | return 0; return utf8len(command.data + CR) |
| def print_response_details | 20: def print_response_details(command_response): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def decimal_to_binary | 27: def decimal_to_binary(num): | return bin(num) |
| def binary_to_decimal | 32: def binary_to_decimal(binary): | return decimal |
| def clean_response | 43: def clean_response(response): | return response \ |
| def equivalent | 50: def equivalent(a, b, tolerance): | return abs(a - b) &lt; tolerance |
| def is_in_position | 55: def is_in_position(move_l, cp): | return equivalent(cp.get_x(), move_l.get_x(), t) and equivalent(cp.get_y(), move_l.get_y(), t) and equivalent( |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/WebServer.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/WebServer.py (128 dòng, 5607 byte) |
| PURPOSE | Legacy HTTP handler có servo/start/HOLD/nudge, không quyền HMI hiện đại. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | S:18 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | os.path.dirname, get_position, Commands.read_current_specified_coordinate_system_position, S, _set_headers, self.send_response, self.send_header, self.end_headers, _html, str, Commands.read_current_job_details, job_name, Commands.read_status, open, os.path.join, f.read, replace, status.is_command_remote, status.is_play, status.is_command_hold, status.is_programming_pendant_hold, status.is_teach, status.is_running, status.is_servo_on, status.is_error_occurring, html_content.encode, encode, do_GET, self._set_headers, self.wfile.write, self._html, do_HEAD, do_POST, int, self.rfile.read, logging.info, post_data.decode, Commands.write_start_job, Commands.write_hold, Commands.write_servo_power, Commands.write_linear_move, MoveL.MoveL, c_pos.get_x, else, c_pos.get_y |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | from http.server import HTTPServer, BaseHTTPRequestHandler [1]; from nx100_remote_control.objects import MoveL [2]; from nx100_remote_control.module import Commands, Utils [3]; import logging [4]; import os [5] |
| ERROR HANDLING | Exception |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Gọi tầng điều khiển robot/JOB/I/O qua dependency; xem call chain. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| def get_position | 13: def get_position(): | return Commands.read_current_specified_coordinate_system_position('0', '0') |
| class S | 18: class S(BaseHTTPRequestHandler): | Class/dataclass/Enum; xem methods |
| def S._set_headers | 19: def _set_headers(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def S._html | 24: def _html(self, message): | return html_content.encode("utf8")  # NOTE: must return a bytes object!; return "".encode('utf-8'); return html_content.encode("utf8") |
| def S.do_GET | 56: def do_GET(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def S.do_HEAD | 60: def do_HEAD(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def S.do_POST | 63: def do_POST(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def run | 122: def run(server_class=HTTPServer, handler_class=S, addr="localhost", port=8080): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/xbox360_controller.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/xbox360_controller.py (301 dòng, 8928 byte) |
| PURPOSE | Pygame controller mapping và dead-zone remapping. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Controller:93 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Copyright, sys.platform.startswith, __init__, sticks, pygame.joystick.init, pygame.joystick.Joystick, self.joystick.init, get_triggers, get_id, self.joystick.get_id, dead_zone_adjustment, get_buttons, self.joystick.get_button, get_left_stick, self.dead_zone_adjustment, self.joystick.get_axis, get_right_stick, get_pad, form, self.joystick.get_hat, int |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | self.joystick, self.dead_zone, self.left_trigger_used, self.right_trigger_used |
| EXTERNAL DEPENDENCIES | import pygame [9]; import sys [10] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 269; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Controller | 93: class Controller: | Class/dataclass/Enum; xem methods |
| def Controller.__init__ | 96: def __init__(self, dead_zone=0.15): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Controller.get_id | 117: def get_id(self): | return self.joystick.get_id() |
| def Controller.dead_zone_adjustment | 125: def dead_zone_adjustment(self, value): | return (value - self.dead_zone) / (1 - self.dead_zone); return (value + self.dead_zone) / (1 - self.dead_zone); return 0 |
| def Controller.get_buttons | 144: def get_buttons(self): | return (self.joystick.get_button(A),; return (self.joystick.get_button(A),; return (0,  # Unused |
| def Controller.get_left_stick | 194: def get_left_stick(self): | return (left_stick_x, left_stick_y) |
| def Controller.get_right_stick | 212: def get_right_stick(self): | return (right_stick_x, right_stick_y) |
| def Controller.get_triggers | 230: def get_triggers(self): | return trigger_axis |
| def Controller.get_pad | 276: def get_pad(self): | return up, right, down, left |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/__init__.py (1 dòng, 0 byte) |
| PURPOSE | Khởi tạo namespace/package; library root có endpoint global và MOCK_RESPONSE. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Không có bằng chứng runtime/hardware mới; hợp đồng thực tế phụ thuộc caller/config. Các lỗi và đề xuất chỉ ghi văn bản ở mục2/13. |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Alarm.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Alarm.py (12 dòng, 323 byte) |
| PURPOSE | Legacy value/response object Alarm.py, getter/parser và serialization. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Alarm:1 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Alarm, __init__, str, split, get_alarm, get_alarms |
| CALLED BY | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Commands.py |
| STATE MODIFIED | self.alarms |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Object/serialization legacy không tự xác minh readiness/tool/path; xem rủi ro caller. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Alarm | 1: class Alarm(object): | Class/dataclass/Enum; xem methods |
| def Alarm.__init__ | 4: def __init__(self, response): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Alarm.get_alarm | 8: def get_alarm(self, position=0): | return self.alarms[position] if position &lt; 10 else 'N/A' |
| def Alarm.get_alarms | 11: def get_alarms(self): | return self.alarms |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Command.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Command.py (7 dòng, 140 byte) |
| PURPOSE | Legacy value/response object Command.py, getter/parser và serialization. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Command:1 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Command, __init__ |
| CALLED BY | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Commands.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Protocol.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Utils.py |
| STATE MODIFIED | self.name, self.data |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Object/serialization legacy không tự xác minh readiness/tool/path; xem rủi ro caller. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Command | 1: class Command(object): | Class/dataclass/Enum; xem methods |
| def Command.__init__ | 4: def __init__(self, command, data): | Không thấy explicit return; có thể None hoặc exception từ dependency |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/CurrentPos.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/CurrentPos.py (30 dòng, 658 byte) |
| PURPOSE | Legacy value/response object CurrentPos.py, getter/parser và serialization. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | CurrentPos:1 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | CurrentPos, __init__, position_data.split, float, get_x, get_y, get_z, get_tx, get_ty, get_tz |
| CALLED BY | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Commands.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/JointMove.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/LinearMove.py |
| STATE MODIFIED | self.position, self.x, self.y, self.z, self.tx, self.ty, self.tz |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Object/serialization legacy không tự xác minh readiness/tool/path; xem rủi ro caller. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class CurrentPos | 1: class CurrentPos(object): | Class/dataclass/Enum; xem methods |
| def CurrentPos.__init__ | 4: def __init__(self, position_data): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def CurrentPos.get_x | 13: def get_x(self): | return self.x |
| def CurrentPos.get_y | 16: def get_y(self): | return self.y |
| def CurrentPos.get_z | 19: def get_z(self): | return self.z |
| def CurrentPos.get_tx | 22: def get_tx(self): | return self.tx |
| def CurrentPos.get_ty | 25: def get_ty(self): | return self.ty |
| def CurrentPos.get_tz | 28: def get_tz(self): | return self.tz |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Gripper.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Gripper.py (26 dòng, 689 byte) |
| PURPOSE | Legacy value/response object Gripper.py, getter/parser và serialization. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Gripper:1 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Gripper, __init__, set_closed_status, int, is_gripper_closed, set_acknowledge, is_acknowledge, set_hit, is_hit |
| CALLED BY | nx100-remote-control-master/nx100-remote-control-master/Testing.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Gripper.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/tests/test_gripper.py |
| STATE MODIFIED | self.is_closed, self.is_acknowledge, self.is_hit |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Object/serialization legacy không tự xác minh readiness/tool/path; xem rủi ro caller. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Gripper | 1: class Gripper(object): | Class/dataclass/Enum; xem methods |
| def Gripper.__init__ | 4: def __init__(self): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Gripper.set_closed_status | 9: def set_closed_status(self, register_value): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Gripper.is_gripper_closed | 12: def is_gripper_closed(self): | return self.is_closed |
| def Gripper.set_acknowledge | 15: def set_acknowledge(self, register_value): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Gripper.is_acknowledge | 18: def is_acknowledge(self): | return self.is_acknowledge |
| def Gripper.set_hit | 21: def set_hit(self, register_value): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Gripper.is_hit | 24: def is_hit(self): | return self.is_hit |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/IO.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/IO.py (25 dòng, 847 byte) |
| PURPOSE | Legacy value/response object IO.py, getter/parser và serialization. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | IO:6 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | IO, __init__, get_io_read_command, str, set_first_eight_io_contracts, get_io_write_command |
| CALLED BY | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Commands.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Gripper.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/tests/test_commands.py |
| STATE MODIFIED | self.contact_point_start_no, self.num_of_contact_points, self.first_eight_contacts_in |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Object/serialization legacy không tự xác minh readiness/tool/path; xem rủi ro caller. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class IO | 6: class IO(object): | Class/dataclass/Enum; xem methods |
| def IO.__init__ | 9: def __init__(self, contact_point_start_no, num_of_contact_points=8): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def IO.get_io_read_command | 14: def get_io_read_command(self): | return str(self.contact_point_start_no) + ', ' + str(self.num_of_contact_points) |
| def IO.set_first_eight_io_contracts | 18: def set_first_eight_io_contracts(self, eight_contacts_data): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def IO.get_io_write_command | 21: def get_io_write_command(self): | return str(self.contact_point_start_no) + ', ' + \ |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/JobDetail.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/JobDetail.py (18 dòng, 438 byte) |
| PURPOSE | Legacy value/response object JobDetail.py, getter/parser và serialization. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | JobDetail:1 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | JobDetail, __init__, response.split, job_name, len, line_no, step_no |
| CALLED BY | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Commands.py |
| STATE MODIFIED | self.parts |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Object/serialization legacy không tự xác minh readiness/tool/path; xem rủi ro caller. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class JobDetail | 1: class JobDetail(object): | Class/dataclass/Enum; xem methods |
| def JobDetail.__init__ | 4: def __init__(self, response): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def JobDetail.job_name | 7: def job_name(self): | return self.parts[p] if len(self.parts) &gt; p else 'Job name N/A' |
| def JobDetail.line_no | 11: def line_no(self): | return self.parts[p] if len(self.parts) &gt; p else 'N/A' |
| def JobDetail.step_no | 15: def step_no(self): | return self.parts[p] if len(self.parts) &gt; p else 'N/A' |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/MoveJ.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/MoveJ.py (75 dòng, 2010 byte) |
| PURPOSE | Legacy value/response object MoveJ.py, getter/parser và serialization. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | MoveJ:1 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | MoveJ, __init__, get_command, separator.join, str, get_coordinate_specification, get_x, get_y, get_z, get_tx, get_ty, get_tz |
| CALLED BY | nx100-remote-control-master/nx100-remote-control-master/Testing.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/JointMove.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/tests/test_commands.py |
| STATE MODIFIED | self.motion_speed_percentage, self.coordinate_specification, self.x, self.y, self.z, self.tx, self.ty, self.tz, self.d_10, self.d_11, self.d_12, self.d_13, self.d_14, self.d_15, self.d_16, self.d_17 |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Object/serialization legacy không tự xác minh readiness/tool/path; xem rủi ro caller. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class MoveJ | 1: class MoveJ(object): | Class/dataclass/Enum; xem methods |
| def MoveJ.__init__ | 15: def __init__(self, motion_speed_percentage, coordinate_specification, x, y, z, tx, ty, tz, d_10, d_11=0, d_12=0, d_13=0, d_14=0, d_15=0, d_16=0, d_17=0): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def MoveJ.get_command | 34: def get_command(self): | return separator.join([ |
| def MoveJ.get_coordinate_specification | 55: def get_coordinate_specification(self): | return self.coordinate_specification |
| def MoveJ.get_x | 58: def get_x(self): | return self.x |
| def MoveJ.get_y | 61: def get_y(self): | return self.y |
| def MoveJ.get_z | 64: def get_z(self): | return self.z |
| def MoveJ.get_tx | 67: def get_tx(self): | return self.tx |
| def MoveJ.get_ty | 70: def get_ty(self): | return self.ty |
| def MoveJ.get_tz | 73: def get_tz(self): | return self.tz |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/MoveL.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/MoveL.py (76 dòng, 2272 byte) |
| PURPOSE | Legacy value/response object MoveL.py, getter/parser và serialization. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | MoveL:1 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | MoveL, __init__, get_command, separator.join, str, get_coordinate_specification, get_x, get_y, get_z, get_tx, get_ty, get_tz |
| CALLED BY | nx100-remote-control-master/nx100-remote-control-master/Testing.py; nx100-remote-control-master/nx100-remote-control-master/XboxController.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/LinearMove.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/WebServer.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/tests/test_commands.py |
| STATE MODIFIED | self.motion_speed_selection, self.motion_speed, self.coordinate_specification, self.x, self.y, self.z, self.tx, self.ty, self.tz, self.d_10, self.d_11, self.d_12, self.d_13, self.d_14, self.d_15, self.d_16, self.d_17 |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Object/serialization legacy không tự xác minh readiness/tool/path; xem rủi ro caller. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class MoveL | 1: class MoveL(object): | Class/dataclass/Enum; xem methods |
| def MoveL.__init__ | 14: def __init__(self, motion_speed_selection, motion_speed, coordinate_specification, x, y, z, tx, ty, tz, d_10, d_11=0, d_12=0, d_13=0, d_14=0, d_15=0, d_16=0, d_17=0): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def MoveL.get_command | 34: def get_command(self): | return separator.join([ |
| def MoveL.get_coordinate_specification | 56: def get_coordinate_specification(self): | return self.coordinate_specification |
| def MoveL.get_x | 59: def get_x(self): | return self.x |
| def MoveL.get_y | 62: def get_y(self): | return self.y |
| def MoveL.get_z | 65: def get_z(self): | return self.z |
| def MoveL.get_tx | 68: def get_tx(self): | return self.tx |
| def MoveL.get_ty | 71: def get_ty(self): | return self.ty |
| def MoveL.get_tz | 74: def get_tz(self): | return self.tz |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Response.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Response.py (13 dòng, 322 byte) |
| PURPOSE | Legacy value/response object Response.py, getter/parser và serialization. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Response:2 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Response, __init__, get_response, is_success, isinstance |
| CALLED BY | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Commands.py; nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Protocol.py |
| STATE MODIFIED | self.response |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Object/serialization legacy không tự xác minh readiness/tool/path; xem rủi ro caller. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Response | 2: class Response(object): | Class/dataclass/Enum; xem methods |
| def Response.__init__ | 5: def __init__(self, response): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Response.get_response | 8: def get_response(self): | return self.response |
| def Response.is_success | 11: def is_success(self): | return isinstance(self.response, str) and self.response == '0000' |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Status.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Status.py (53 dòng, 1571 byte) |
| PURPOSE | Giải mã RSTATS bằng fixed bit masks. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Status:1 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | __init__, word, int, isinstance, value.startswith, ValueError, is_step, bool, is_one_cycle, is_auto, is_running, is_safety_speed_operation, is_teach, is_play, is_command_remote, is_programming_pendant_hold, is_external_hold, is_command_hold, is_alarm_occurring, is_error_occurring, is_servo_on |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | self.data_1, self.data_2 |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | ValueError |
| MATHEMATICAL LOGIC | Các dòng tính/check liên quan: 13, 16, 19, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49, 52; công thức vật lý và đơn vị tại mục6 |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Object/serialization legacy không tự xác minh readiness/tool/path; xem rủi ro caller. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Status | 1: class Status: | Class/dataclass/Enum; xem methods |
| def Status.__init__ | 3: def __init__(self, data_1, data_2): | raise ValueError('Invalid RSTATS word'); return result |
| def Status.__init__.word | 4: def word(value, maximum): | raise ValueError('Invalid RSTATS word'); return result |
| def Status.is_step | 12: def is_step(self): | return bool(self.data_1 & (1 &lt;&lt; 0)) |
| def Status.is_one_cycle | 15: def is_one_cycle(self): | return bool(self.data_1 & (1 &lt;&lt; 1)) |
| def Status.is_auto | 18: def is_auto(self): | return bool(self.data_1 & (1 &lt;&lt; 2)) |
| def Status.is_running | 21: def is_running(self): | return bool(self.data_1 & (1 &lt;&lt; 3)) |
| def Status.is_safety_speed_operation | 24: def is_safety_speed_operation(self): | return bool(self.data_1 & (1 &lt;&lt; 4)) |
| def Status.is_teach | 27: def is_teach(self): | return bool(self.data_1 & (1 &lt;&lt; 5)) |
| def Status.is_play | 30: def is_play(self): | return bool(self.data_1 & (1 &lt;&lt; 6)) |
| def Status.is_command_remote | 33: def is_command_remote(self): | return bool(self.data_1 & (1 &lt;&lt; 7)) |
| def Status.is_programming_pendant_hold | 36: def is_programming_pendant_hold(self): | return bool(self.data_2 & (1 &lt;&lt; 1)) |
| def Status.is_external_hold | 39: def is_external_hold(self): | return bool(self.data_2 & (1 &lt;&lt; 2)) |
| def Status.is_command_hold | 42: def is_command_hold(self): | return bool(self.data_2 & (1 &lt;&lt; 3)) |
| def Status.is_alarm_occurring | 45: def is_alarm_occurring(self): | return bool(self.data_2 & (1 &lt;&lt; 4)) |
| def Status.is_error_occurring | 48: def is_error_occurring(self): | return bool(self.data_2 & (1 &lt;&lt; 5)) |
| def Status.is_servo_on | 51: def is_servo_on(self): | return bool(self.data_2 & (1 &lt;&lt; 6)) |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Time.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Time.py (19 dòng, 396 byte) |
| PURPOSE | Legacy value/response object Time.py, getter/parser và serialization. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Time:4 |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Time, __init__, set_time_now, has_seconds_passed, self.get_current_millis, get_current_millis, round, time.time |
| CALLED BY | nx100-remote-control-master/nx100-remote-control-master/XboxController.py |
| STATE MODIFIED | self.millis |
| EXTERNAL DEPENDENCIES | import time [1] |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Object/serialization legacy không tự xác minh readiness/tool/path; xem rủi ro caller. |

| Loại / symbol | Dòng / signature | Return / exception đáng chú ý (tĩnh) |
|---|---|---|
| class Time | 4: class Time(object): | Class/dataclass/Enum; xem methods |
| def Time.__init__ | 7: def __init__(self, millis): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Time.set_time_now | 10: def set_time_now(self, millis): | Không thấy explicit return; có thể None hoặc exception từ dependency |
| def Time.has_seconds_passed | 13: def has_seconds_passed(self, seconds): | return (self.millis + (seconds * 1000)) &lt; self.get_current_millis() |
| def Time.get_current_millis | 17: def get_current_millis(): | return round(time.time() * 1000) |

### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/__init__.py

| Trường | Phân tích / bằng chứng |
|---|---|
| FILE / PATH | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/__init__.py (1 dòng, 0 byte) |
| PURPOSE | Legacy value/response object __init__.py, getter/parser và serialization. |
| ENTRY POINT | Module được import/call; không main guard |
| CLASSES | Không có |
| FUNCTIONS / INPUT | Signature và parameters nguyên tên trong bảng symbol bên dưới |
| OUTPUT | Return expressions trong bảng symbol; ngoại lệ/callback cũng là đường ra |
| CALLS | Không thấy call biểu thức |
| CALLED BY | Không xác định lexical chắc từ class đặc trưng; xem entry/import/call chain mục10 |
| STATE MODIFIED | Không thấy assignment self.attr; có thể mutate input/local/module state |
| EXTERNAL DEPENDENCIES | Không import |
| ERROR HANDLING | Không thấy raise/except; lỗi caller/built-in có thể propagate |
| MATHEMATICAL LOGIC | Không thấy công thức geometry/stability đặc trưng; getter/serialization/control flow xem source |
| HARDWARE EFFECT | Không thấy wire/device transaction trực tiếp; caller vẫn có thể gây side effect. |
| KNOWN LIMITATIONS | Object/serialization legacy không tự xác minh readiness/tool/path; xem rủi ro caller. |


## 16. Kiểm kê tài nguyên và test

### 16.1 Toàn bộ file riêng ngoài cache/môi trường

Gồm file ẩn, dữ liệu, binary, license và log. Ảnh/PDF kiểm kê/hash, không xác minh toàn nội dung. Không có JBI trong sáu project.

| Đường dẫn | Byte | Cách khảo sát / vai trò |
|---|---:|---|
| nx100_camera_snapshot_move/.gitignore | 64 | Inventory/hash |
| nx100_camera_snapshot_move/app.py | 9982 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/config.json | 723 | Đọc text |
| nx100_camera_snapshot_move/requirements.txt | 128 | Đọc text |
| nx100_camera_snapshot_move/calibration/camera_intrinsic_2.npz | 3569 | NPY/metadata/hash; calibration |
| nx100_camera_snapshot_move/calibration/eye_to_hand.npz | 15038 | NPY/metadata/hash; calibration |
| nx100_camera_snapshot_move/data/snapshot_real.json | 9146 | Đọc text |
| nx100_camera_snapshot_move/logs/controller.lock | 0 | Lock đã tồn tại; không acquire/write |
| nx100_camera_snapshot_move/logs/events.log | 1373644 | Đọc/tìm kiếm text lớn; log/manual lịch sử |
| nx100_camera_snapshot_move/logs/snapshot_workflow_mock.png | 189837 | Inventory/hash; artifact, không xác minh toàn ảnh/trang |
| nx100_camera_snapshot_move/logs/ultralytics/Ultralytics/settings.json | 495 | Đọc text |
| nx100_camera_snapshot_move/models/best.pt | 6531370 | ZIP entries/chuỗi metadata/hash; không unpickle |
| nx100_camera_snapshot_move/robot/cartesian.py | 2937 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/robot/controller.py | 20752 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/robot/mock.py | 2075 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/robot/protocol.py | 8359 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/robot/status.py | 1571 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/robot/UPSTREAM_LICENSE | 34461 | License nguồn AGPL; inventory/hash; giữ khi tái sử dụng |
| nx100_camera_snapshot_move/robot/__init__.py | 5 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/static/app.js | 8000 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/static/style.css | 4050 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/templates/index.html | 5169 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/tests/conftest.py | 1829 | Đọc test, không chạy |
| nx100_camera_snapshot_move/tests/test_snapshot_move.py | 12683 | Đọc test, không chạy |
| nx100_camera_snapshot_move/tests/test_web_workflow.py | 3996 | Đọc test, không chạy |
| nx100_camera_snapshot_move/vision/calibration.py | 4699 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/vision/camera.py | 11867 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/vision/detector.py | 1546 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/vision/pipeline.py | 6528 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/vision/target.py | 355 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/vision/tracker.py | 3455 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/vision/__init__.py | 5 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/workflow/snapshot_move.py | 19648 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/workflow/target_manager.py | 1676 | Đọc source tĩnh, không thực thi |
| nx100_camera_snapshot_move/workflow/__init__.py | 5 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/.gitignore | 81 | Inventory/hash |
| nx100_full_cycle_v1/app.py | 11140 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/config.json | 2605 | Đọc text |
| nx100_full_cycle_v1/launcher.py | 1500 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/LICENSE | 34461 | License nguồn AGPL; inventory/hash; giữ khi tái sử dụng |
| nx100_full_cycle_v1/README.md | 11980 | Đọc text |
| nx100_full_cycle_v1/requirements-dev.txt | 39 | Đọc text |
| nx100_full_cycle_v1/requirements-lock.txt | 373 | Đọc text |
| nx100_full_cycle_v1/requirements-real-lock.txt | 1045 | Đọc text |
| nx100_full_cycle_v1/requirements-real.txt | 124 | Đọc text |
| nx100_full_cycle_v1/requirements.txt | 88 | Đọc text |
| nx100_full_cycle_v1/settings.py | 1312 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/calibration/camera_intrinsic_2.npz | 3569 | NPY/metadata/hash; calibration |
| nx100_full_cycle_v1/calibration/eye_to_hand.npz | 15038 | NPY/metadata/hash; calibration |
| nx100_full_cycle_v1/data/mock/execution.json | 174 | Đọc text |
| nx100_full_cycle_v1/data/mock/execution.lock | 1 | Lock đã tồn tại; không acquire/write |
| nx100_full_cycle_v1/data/real/.gitkeep | 0 | File rỗng/marker; inventory/hash |
| nx100_full_cycle_v1/data/real/drop_stack.json | 2421 | Đọc text |
| nx100_full_cycle_v1/data/real/execution.before_auto_count.json | 12410 | Đọc text |
| nx100_full_cycle_v1/data/real/execution.json | 16782 | Đọc text |
| nx100_full_cycle_v1/data/real/execution.lock | 1 | Lock đã tồn tại; không acquire/write |
| nx100_full_cycle_v1/data/real/operator_settings.json | 81 | Đọc text |
| nx100_full_cycle_v1/docs/33175396.txt | 78247 | Đọc text |
| nx100_full_cycle_v1/docs/343135.txt | 589377 | Đọc/tìm kiếm text lớn; log/manual lịch sử |
| nx100_full_cycle_v1/docs/35567548.txt | 381835 | Đọc/tìm kiếm text lớn; log/manual lịch sử |
| nx100_full_cycle_v1/docs/41605397.txt | 522297 | Đọc/tìm kiếm text lớn; log/manual lịch sử |
| nx100_full_cycle_v1/docs/asset_hashes.json | 303 | Đọc text |
| nx100_full_cycle_v1/docs/AUDIT_REPORT.md | 5442 | Đọc text |
| nx100_full_cycle_v1/docs/browser_result.json | 499 | Đọc text |
| nx100_full_cycle_v1/docs/browser_server.log | 0 | File rỗng/marker; inventory/hash |
| nx100_full_cycle_v1/docs/copied_files.json | 1134 | Đọc text |
| nx100_full_cycle_v1/docs/DROP_HEIGHT_CONTROL.md | 6391 | Đọc text |
| nx100_full_cycle_v1/docs/hmi_desktop_complete.png | 85634 | Inventory/hash; artifact, không xác minh toàn ảnh/trang |
| nx100_full_cycle_v1/docs/hmi_desktop_ready.png | 81895 | Inventory/hash; artifact, không xác minh toàn ảnh/trang |
| nx100_full_cycle_v1/docs/hmi_tablet.png | 78273 | Inventory/hash; artifact, không xác minh toàn ảnh/trang |
| nx100_full_cycle_v1/docs/HW0483202.pdf | 565876 | Inventory/hash; artifact, không xác minh toàn ảnh/trang |
| nx100_full_cycle_v1/docs/IO_MAPPING.md | 3577 | Đọc text |
| nx100_full_cycle_v1/docs/job_directory_live.json | 2153 | Đọc text |
| nx100_full_cycle_v1/docs/laser_live_read.json | 115 | Đọc text |
| nx100_full_cycle_v1/docs/real_before_v1_update.json | 491 | Đọc text |
| nx100_full_cycle_v1/docs/real_dependency_copy.json | 939 | Đọc text |
| nx100_full_cycle_v1/docs/REAL_DEPLOYMENT_CHECKLIST.md | 5850 | Đọc text |
| nx100_full_cycle_v1/docs/real_preflight.json | 477 | Đọc text |
| nx100_full_cycle_v1/docs/real_robot_readonly.json | 297 | Đọc text |
| nx100_full_cycle_v1/docs/real_runtime_smoke.json | 154 | Đọc text |
| nx100_full_cycle_v1/docs/runtime_smoke.json | 171 | Đọc text |
| nx100_full_cycle_v1/docs/source_camera_config.json | 723 | Đọc text |
| nx100_full_cycle_v1/docs/source_hashes.json | 16391 | Đọc text |
| nx100_full_cycle_v1/docs/source_verification.json | 74 | Đọc text |
| nx100_full_cycle_v1/docs/test_output.txt | 13030 | Đọc text |
| nx100_full_cycle_v1/docs/TEST_REPORT.md | 20598 | Đọc text |
| nx100_full_cycle_v1/docs/test_result.json | 111 | Đọc text |
| nx100_full_cycle_v1/docs/UPSTREAM_LICENSE | 34461 | License nguồn AGPL; inventory/hash; giữ khi tái sử dụng |
| nx100_full_cycle_v1/jobs/README.md | 1498 | Đọc text |
| nx100_full_cycle_v1/logs/mock/.gitkeep | 0 | File rỗng/marker; inventory/hash |
| nx100_full_cycle_v1/logs/mock/app.log | 0 | File rỗng/marker; inventory/hash |
| nx100_full_cycle_v1/logs/real/.gitkeep | 0 | File rỗng/marker; inventory/hash |
| nx100_full_cycle_v1/logs/real/app.log | 100886 | Đọc/tìm kiếm text lớn; log/manual lịch sử |
| nx100_full_cycle_v1/logs/ultralytics/Ultralytics/settings.json | 502 | Đọc text |
| nx100_full_cycle_v1/models/best.pt | 6531370 | ZIP entries/chuỗi metadata/hash; không unpickle |
| nx100_full_cycle_v1/robot/cartesian.py | 2937 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/robot/controller.py | 6116 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/robot/io.py | 815 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/robot/job_control.py | 1106 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/robot/mock.py | 4167 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/robot/position_variable.py | 1180 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/robot/protocol.py | 11940 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/robot/status.py | 1571 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/robot/vacuum.py | 3384 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/robot/__init__.py | 0 | File rỗng/marker; inventory/hash |
| nx100_full_cycle_v1/static/app.js | 9213 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/static/style.css | 9566 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/templates/index.html | 4405 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/tests/test_api.py | 9747 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_cycle.py | 15843 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_dispatch_cycle.py | 5735 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_drop.py | 12988 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_hand_jobs.py | 4230 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_hold_release.py | 3672 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_independence.py | 4050 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_job_directory.py | 2243 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_laser_h2_cycle.py | 5471 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_launcher.py | 3707 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_pick_order.py | 1944 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_position_variable.py | 6029 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_prefetch.py | 4019 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_protocol.py | 3850 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_repeat.py | 5273 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_sensor.py | 3370 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_tracker.py | 2430 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_vacuum.py | 2671 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/test_vision.py | 4633 | Đọc test, không chạy |
| nx100_full_cycle_v1/tests/upstream_board_tracker.txt | 2472 | Đọc text |
| nx100_full_cycle_v1/tools/browser_smoke.py | 8233 | Đọc script kiểm thử, không chạy |
| nx100_full_cycle_v1/tools/run_tests.py | 1015 | Đọc script kiểm thử, không chạy |
| nx100_full_cycle_v1/vision/calibration.py | 4699 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/vision/camera.py | 11867 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/vision/detector.py | 1743 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/vision/pipeline.py | 6950 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/vision/stability.py | 1953 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/vision/tracker.py | 3455 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/vision/__init__.py | 0 | File rỗng/marker; inventory/hash |
| nx100_full_cycle_v1/workflow/cycle.py | 32788 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/workflow/drop.py | 13367 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/workflow/safety_checks.py | 4305 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/workflow/state_machine.py | 3634 | Đọc source tĩnh, không thực thi |
| nx100_full_cycle_v1/workflow/__init__.py | 0 | File rỗng/marker; inventory/hash |
| nx100_variables_web/app.py | 16724 | Đọc source tĩnh, không thực thi |
| nx100_variables_web/nx100_client.py | 10172 | Đọc source tĩnh, không thực thi |
| nx100_variables_web/static/app.js | 10053 | Đọc source tĩnh, không thực thi |
| nx100_variables_web/static/index.html | 6543 | Đọc source tĩnh, không thực thi |
| nx100_variables_web/static/style.css | 9967 | Đọc source tĩnh, không thực thi |
| nx100_variables_web/tests/test_variables.py | 7268 | Đọc test, không chạy |
| nx100_web_control/.gitignore | 32 | Inventory/hash |
| nx100_web_control/app.py | 7868 | Đọc source tĩnh, không thực thi |
| nx100_web_control/config.json | 1646 | Đọc text |
| nx100_web_control/pyproject.toml | 116 | Đọc text |
| nx100_web_control/README.md | 14019 | Đọc text |
| nx100_web_control/requirements-dev.txt | 66 | Đọc text |
| nx100_web_control/requirements.txt | 129 | Đọc text |
| nx100_web_control/qa/desktop.png | 138261 | Inventory/hash; artifact, không xác minh toàn ảnh/trang |
| nx100_web_control/qa/mobile.png | 123041 | Inventory/hash; artifact, không xác minh toàn ảnh/trang |
| nx100_web_control/robot/mock.py | 1914 | Đọc source tĩnh, không thực thi |
| nx100_web_control/robot/nx100_controller.py | 18551 | Đọc source tĩnh, không thực thi |
| nx100_web_control/robot/protocol.py | 744 | Đọc source tĩnh, không thực thi |
| nx100_web_control/robot/__init__.py | 1 | Đọc source tĩnh, không thực thi |
| nx100_web_control/static/css/camera.css | 1822 | Đọc source tĩnh, không thực thi |
| nx100_web_control/static/css/style.css | 11701 | Đọc source tĩnh, không thực thi |
| nx100_web_control/static/js/app.js | 17838 | Đọc source tĩnh, không thực thi |
| nx100_web_control/static/js/camera.js | 7753 | Đọc source tĩnh, không thực thi |
| nx100_web_control/templates/camera.html | 3632 | Đọc source tĩnh, không thực thi |
| nx100_web_control/templates/index.html | 6024 | Đọc source tĩnh, không thực thi |
| nx100_web_control/tests/browser_smoke.py | 6604 | Đọc script kiểm thử, không chạy |
| nx100_web_control/tests/camera_smoke.py | 3181 | Đọc script kiểm thử, không chạy |
| nx100_web_control/tests/test_vision.py | 6251 | Đọc test, không chạy |
| nx100_web_control/tests/test_web.py | 16980 | Đọc test, không chạy |
| nx100_web_control/vision/calibration.py | 5129 | Đọc source tĩnh, không thực thi |
| nx100_web_control/vision/camera.py | 7491 | Đọc source tĩnh, không thực thi |
| nx100_web_control/vision/__init__.py | 70 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/.gitignore | 57 | Inventory/hash |
| nx100_yolo_auto_tracking/app.py | 9782 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/config.json | 910 | Đọc text |
| nx100_yolo_auto_tracking/requirements.txt | 128 | Đọc text |
| nx100_yolo_auto_tracking/automation/auto_move.py | 13284 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/automation/state_machine.py | 474 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/automation/target_manager.py | 2148 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/automation/__init__.py | 5 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/calibration/camera_intrinsic_2.npz | 3569 | NPY/metadata/hash; calibration |
| nx100_yolo_auto_tracking/calibration/eye_to_hand.npz | 15038 | NPY/metadata/hash; calibration |
| nx100_yolo_auto_tracking/logs/controller.lock | 0 | Lock đã tồn tại; không acquire/write |
| nx100_yolo_auto_tracking/logs/events.log | 1254018 | Đọc/tìm kiếm text lớn; log/manual lịch sử |
| nx100_yolo_auto_tracking/logs/events.log.1 | 1999974 | Đọc/tìm kiếm text lớn; log/manual lịch sử |
| nx100_yolo_auto_tracking/logs/ultralytics/Ultralytics/settings.json | 467 | Đọc text |
| nx100_yolo_auto_tracking/models/best.pt | 6531370 | ZIP entries/chuỗi metadata/hash; không unpickle |
| nx100_yolo_auto_tracking/robot/cartesian.py | 2937 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/robot/controller.py | 18873 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/robot/mock.py | 1914 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/robot/protocol.py | 8371 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/robot/status.py | 1571 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/robot/UPSTREAM_LICENSE | 34461 | License nguồn AGPL; inventory/hash; giữ khi tái sử dụng |
| nx100_yolo_auto_tracking/robot/__init__.py | 5 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/static/app.js | 6883 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/static/style.css | 4050 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/templates/index.html | 3995 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/vision/calibration.py | 4698 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/vision/camera.py | 11867 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/vision/detector.py | 1546 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/vision/pipeline.py | 6496 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/vision/stability.py | 2709 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/vision/tracker.py | 3455 | Đọc source tĩnh, không thực thi |
| nx100_yolo_auto_tracking/vision/__init__.py | 5 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/.gitignore | 1857 | Inventory/hash |
| nx100-remote-control-master/nx100-remote-control-master/LICENSE | 34461 | License nguồn AGPL; inventory/hash; giữ khi tái sử dụng |
| nx100-remote-control-master/nx100-remote-control-master/pyproject.toml | 90 | Đọc text |
| nx100-remote-control-master/nx100-remote-control-master/README.md | 9692 | Đọc text |
| nx100-remote-control-master/nx100-remote-control-master/requirements.txt | 13 | Đọc text |
| nx100-remote-control-master/nx100-remote-control-master/setup.cfg | 666 | Đọc text |
| nx100-remote-control-master/nx100-remote-control-master/setup.py | 264 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/Testing.py | 3364 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/XboxController.py | 3193 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/__init__.py | 264 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Cartesian.py | 2964 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Commands.py | 8422 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Gripper.py | 2367 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/index.html | 6929 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/JointMove.py | 1578 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/LinearMove.py | 1574 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/MockResponse.py | 2324 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Protocol.py | 9486 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Socket.py | 712 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/Utils.py | 1532 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/WebServer.py | 5607 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/xbox360_controller.py | 8928 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/__init__.py | 0 | File rỗng/marker; inventory/hash |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Alarm.py | 323 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Command.py | 140 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/CurrentPos.py | 658 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Gripper.py | 689 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/IO.py | 847 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/JobDetail.py | 438 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/MoveJ.py | 2010 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/MoveL.py | 2272 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Response.py | 322 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Status.py | 1571 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Time.py | 396 | Đọc source tĩnh, không thực thi |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/__init__.py | 0 | File rỗng/marker; inventory/hash |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/tests/test_commands.py | 3205 | Đọc test, không chạy |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/tests/test_gripper.py | 680 | Đọc test, không chạy |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/tests/__init__.py | 0 | File rỗng/marker; inventory/hash |

### 16.2 Frontend: DOM, timer và API callers

Bản đồ nguồn, không phải browser smoke mới. CSS không gửi command; JS phát HTTP tới backend.

#### nx100_camera_snapshot_move/static/app.js

- Vai trò: HTTP caller/render/state/forms; control qua backend.
- Endpoint literal: /api/preview.jpg?t. Đường ghép xem bảng API.
- Timer/debounce dòng: 77; nhịp tại mục4/8.

#### nx100_camera_snapshot_move/static/style.css

- Vai trò: CSS layout/theme/responsive; không handler phần cứng.

#### nx100_camera_snapshot_move/templates/index.html

- Vai trò: Trang và controls gọi JavaScript/backend.
- DOM IDs: mode, network, phase, message, hold, release-hold, error, saved-count, next-id, completed-count, minimum, camera-status, scan, cameras, camera-connect, camera-disconnect, preview, preview-empty, vision-info, capture, robot-status, robot-form, robot-disconnect, flags, pose, motion, send, send-note, ack, saved-at, saved, storage, live, config-form, calibration, events.

#### nx100_full_cycle_v1/static/app.js

- Vai trò: HTTP caller/render/state/forms; control qua backend.
- DOM IDs: flag-${key}, pos-${key}.
- Endpoint literal: /api/control/claim, /api/state, /api/preview.jpg?t, /api/system/connect, /api/cycle/start, /api/cycle/acknowledge, /api/vacuum/, /api/cycle/hold, /api/cycle/release-hold, /api/config, /api/drop/reset, /api/drop/count. Đường ghép xem bảng API.
- Timer/debounce dòng: 81; nhịp tại mục4/8.

#### nx100_full_cycle_v1/static/style.css

- Vai trò: CSS layout/theme/responsive; không handler phần cứng.

#### nx100_full_cycle_v1/templates/index.html

- Vai trò: Trang và controls gọi JavaScript/backend.
- DOM IDs: robotLink, cameraLink, mode, ready, fps, preview, cameraNote, detected, calib, flags, position, target, lease, notice, connect, start, hold, ack, laser, pressure1, pressure2, settings, dropStatus, firstDropZ, dropThickness, stackCountForm, stackedCount, saveStackCount, resetStack, dropNotice, state.

#### nx100_variables_web/static/app.js

- Vai trò: HTTP caller/render/state/forms; control qua backend.
- Timer/debounce dòng: 42; nhịp tại mục4/8.

#### nx100_variables_web/static/index.html

- Vai trò: Trang và controls gọi JavaScript/backend.
- DOM IDs: mode, dashboard-status, connection-badge, alert, connection-form, host, port, connect, disconnect, hz, rate-caption, avg-ms, read-count, error-count, last-ms, p95, variable-tag, kind, index, type-help, period, read, start, stop, read-note, live-badge, value-name, current-value, updated-at, copy-current, value-inputs, value-info, write-note, write, chart, chart-empty, chart-window, event-count, events.

#### nx100_variables_web/static/style.css

- Vai trò: CSS layout/theme/responsive; không handler phần cứng.

#### nx100_web_control/static/css/camera.css

- Vai trò: CSS layout/theme/responsive; không handler phần cứng.

#### nx100_web_control/static/css/style.css

- Vai trò: CSS layout/theme/responsive; không handler phần cứng.

#### nx100_web_control/static/js/app.js

- Vai trò: HTTP caller/render/state/forms; control qua backend.
- DOM IDs: current-${key}, axis-${key}.
- Endpoint literal: /api/move/cartesian, /api/status, /api/logs?after, /api/config, /api/connect, /api/disconnect, /api/status?refresh, /api/hold. Đường ghép xem bảng API.
- Timer/debounce dòng: 13, 21, 41, 45, 102, 119, 234; nhịp tại mục4/8.

#### nx100_web_control/static/js/camera.js

- Vai trò: HTTP caller/render/state/forms; control qua backend.
- Endpoint literal: /api/vision/frame, /api/vision/pixel-to-base, /api/vision/enumerate, /api/vision/connect, /api/vision/disconnect, /api/vision/reload, /api/vision/status. Đường ghép xem bảng API.
- Timer/debounce dòng: 67; nhịp tại mục4/8.

#### nx100_web_control/templates/camera.html

- Vai trò: Trang và controls gọi JavaScript/backend.
- DOM IDs: visionMode, quality, findCamera, cameraDevice, openCamera, closeCamera, cameraStatus, live, frameInfo, cameraCanvas, emptyCamera, pixelValue, planeZ, convertPoint, pointPhase, baseX, baseY, baseZ, pointMessage, reloadCalibration, calibrationSource, calibrationDetails, cameraError.

#### nx100_web_control/templates/index.html

- Vai trò: Trang và controls gọi JavaScript/backend.
- DOM IDs: modeBadge, mockBanner, connection, ip, port, connect, disconnect, heartbeat, freshness, statusGrid, frameLabel, cartTab, jointTab, motion, motionHint, jointNotice, axes, autoNotice, referenceInfo, reset, speedNumber, speedUnit, speedMinus, speedSlider, speedPlus, speedMin, speedMax, readiness, blockedReason, hold, readStatus, xyzTolerance, angleTolerance, motionPhase, motionMessage, positionTime, positionRows, rawToggle, log, toast.

#### nx100_yolo_auto_tracking/static/app.js

- Vai trò: HTTP caller/render/state/forms; control qua backend.
- Endpoint literal: /api/preview.jpg?t. Đường ghép xem bảng API.
- Timer/debounce dòng: 83; nhịp tại mục4/8.

#### nx100_yolo_auto_tracking/static/style.css

- Vai trò: CSS layout/theme/responsive; không handler phần cứng.

#### nx100_yolo_auto_tracking/templates/index.html

- Vai trò: Trang và controls gọi JavaScript/backend.
- DOM IDs: mode, network, state, message, start, stop, hold, error, selected, minimum, eligible, completed, robot-status, robot-form, robot-disconnect, flags, pose, joint, motion, camera-status, scan, cameras, camera-connect, camera-disconnect, preview, preview-empty, vision-info, targets, selected-pose, config-form, calibration, stop-status, events.

#### nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/module/index.html

- Vai trò: Trang và controls gọi JavaScript/backend.
- DOM IDs: statusTable.

### 16.3 Chỉ mục test

Có 242 khai báo test_* trong cây Python; không chạy lại. Tên test chỉ intent; các test nhánh REAL có thể dùng transport giả, không đồng nghĩa hardware thật.

| File | Dòng / test |
|---|---|
| nx100_camera_snapshot_move/tests/conftest.py | Package/fixture/setup, không test_* |
| nx100_camera_snapshot_move/tests/test_snapshot_move.py | 11: def test_new_snapshot_can_revisit_earlier_completed_site(rig):; 28: def test_save_works_without_robot_connected(rig):; 35: def test_robot_fault_does_not_block_camera_save_but_still_blocks_move(rig):; 48: def test_camera_startup_error_does_not_hide_motion_fault(rig):; 57: def test_hold_without_connected_robot_does_not_create_fault(rig):; 64: def test_capture_immediately_with_any_detection_count(rig,count):; 70: def test_position_changes_can_be_saved_immediately(rig):; 78: def test_detection_must_have_valid_coordinates_to_save(rig,invalid):; 90: def test_saved_coordinates_survive_camera_disconnect_and_age(rig):; 102: def test_no_motion_on_capture_connect_or_poll(rig):; 110: def test_read_only_reconnect_does_not_need_restart(rig):; 118: def test_manual_sequence_prioritizes_lowest_id_and_never_auto_sends(rig):; 140: def test_strict_fifty_mm_before_next_send(rig,distance,allowed):; 146: def test_euclidean_distance_and_processed_track(rig):; 157: def test_pending_reloads_but_does_not_auto_move(rig):; 167: def test_inflight_reload_is_uncertain_and_cannot_resend(rig):; 175: def test_real_preflight_conditions_still_required(rig,word1,word2):; 183: def test_configuration_invalidates_unsent_saved_positions(rig):; 191: def test_wrong_or_old_batch_request_rejected(rig):; 198: def test_unknown_move_result_never_retried(rig,monkeypatch):; 211: def test_connection_lost_after_accept_does_not_commit(rig,monkeypatch):; 219: def test_hold_never_sends_home_or_another_move(rig):; 226: def test_release_hold_then_ack_does_not_resend_interrupted_move(rig):; 238: def test_idle_hold_release_ack_restores_manual_send_readiness(rig):; 247: def test_command_release_cannot_clear_external_or_pendant_hold(rig):; 258: def test_release_is_blocked_when_controller_is_running(rig):; 265: def test_save_outside_workspace_but_do_not_move_and_reject_invalid_calibration(rig):; 273: def test_storage_failure_prevents_any_wire_send(rig,monkeypatch):; 281: def test_calibration_or_config_changed_after_reload_blocks_old_snapshot(rig):; 287: def test_malformed_saved_data_cannot_trigger_move(rig):; 296: def test_capture_latest_displayed_coordinates_without_a_frame_age_gate(rig):; 302: def test_new_live_detection_cannot_change_saved_xyz(rig):; 311: def test_completed_history_survives_restart(rig):; 319: def test_explicit_fault_ack_does_not_requeue_uncertain_move(rig): |
| nx100_camera_snapshot_move/tests/test_web_workflow.py | 16: def test_camera_save_unplug_robot_connect_manual_move_and_reload(config,tmp_path):; 47: def test_api_has_no_login_and_protects_origin_and_stale_send(config,tmp_path):; 58: def test_mock_and_real_snapshot_files_are_separate(config,tmp_path):; 67: def test_release_hold_api_then_ack_has_no_automatic_motion(config,tmp_path): |
| nx100_full_cycle_v1/tests/test_api.py | 29: def test_startup_sends_nothing_and_assets(self):; 36: def test_control_requires_lease_and_single_hmi(self):; 43: def test_cross_origin_and_invalid_host_rejected(self):; 48: def test_duplicate_and_stale_mutation(self):; 57: def test_connect_preview_and_config(self):; 68: def test_lan_needs_token(self):; 74: def test_drop_config_and_reset_do_not_start_jobs_or_motion(self):; 87: def test_drop_confirmation_requires_job_receipt_and_counts_once(self):; 101: def test_edit_stack_count_recomputes_height_and_preserves_history(self):; 117: def test_edit_stack_count_rejects_bad_values_and_active_robot(self):; 132: def test_hold_release_requires_lease_confirmation_and_deduplicates(self):; 146: def test_hand_endpoints_dispatch_four_jobs_without_iowrite(self):; 166: def test_sensor_off_on_reaches_hmi_api_without_verified_flag(self): |
| nx100_full_cycle_v1/tests/test_cycle.py | 53: def test_complete_one_target_one_movl_one_job_vacuum_kept(self):; 67: def test_production_ten_frames_two_seconds(self):; 75: def test_v1_single_xyz_move_then_moveunti_then_h2on_at_stop_z(self):; 99: def test_v1_lost_h2on_reply_does_not_repeat_or_complete(self):; 116: def test_move_ack_alone_does_not_finish(self):; 124: def test_job_missing(self):; 132: def test_unverified_real_job_blocked_before_write(self):; 138: def test_laser_never_triggers(self):; 146: def test_laser_on_before_z(self):; 152: def test_laser_appears_after_xy_before_job(self):; 162: def test_unproven_job_stop_blocks_vacuum(self):; 168: def test_hold_cancels_and_never_resumes(self):; 176: def test_alarm_preflight(self):; 182: def test_alarm_during_movl(self):; 192: def test_tcp_lost_after_movl_never_retries(self):; 200: def test_failed_tcp_telemetry_is_unknown(self):; 211: def test_duplicate_start_and_stale_revision(self):; 221: def test_restart_between_intent_and_result_is_fault(self):; 229: def test_second_server_process_is_blocked(self):; 233: def test_fault_does_not_restart_and_requires_inspection_ack(self):; 245: def test_manual_vacuum_on_off(self):; 251: def test_complementary_hands_never_simultaneously_on(self):; 261: def test_real_hands_unknown_are_blocked(self):; 266: def test_inverted_hand_polarity(self):; 273: def test_lost_vacuum_reply_becomes_unknown(self):; 287: def test_real_stop_reason_is_never_faked_by_config(self):; 292: def test_full_real_is_blocked_even_after_commissioning_flags(self):; 306: def test_all_not_ready_flags_block(self):; 313: def test_config_validation_and_durable_settings(self):; 321: def test_same_xy_stack_is_allowed_on_second_cycle(self): |
| nx100_full_cycle_v1/tests/test_dispatch_cycle.py | 40: def test_stops_pc_work_after_ack_without_waiting_for_laser_or_h2on(self):; 64: def test_lost_start_response_remains_fault_and_is_never_retried(self):; 79: def test_real_dispatch_does_not_require_laser_stop_adapter_or_vacuum(self):; 94: def test_real_branch_runs_with_live_metadata_and_without_static_tool_or_path_flags(self):; 104: def test_tool_change_during_move_still_faults_before_start_job(self):; 116: def test_read_failure_after_accepted_handoff_does_not_send_hold(self): |
| nx100_full_cycle_v1/tests/test_drop.py | 44: def test_first_second_third_heights_and_automatic_count(self):; 58: def test_h2off_is_real_start_after_drop_z_is_reached_and_stopped(self):; 77: def test_lift_is_z_plus_200_after_h2off_and_count_is_saved_first(self):; 97: def test_lift_failure_does_not_undo_or_duplicate_completed_h2off_count(self):; 110: def test_position_not_reached_blocks_h2off(self):; 121: def test_h2off_lost_response_faults_and_never_retries_or_counts(self):; 137: def test_h2off_timeout_does_not_count(self):; 151: def test_unverified_h2off_completion_never_counts(self):; 161: def test_same_drop_cycle_cannot_send_h2off_twice(self):; 168: def test_wrong_drop_safe_z_blocks_descent_and_h2off(self):; 175: def test_height_above_safe_is_rejected(self):; 182: def test_duplicate_confirmation_and_reset_preserve_thickness_and_do_not_send_commands(self):; 199: def test_reset_blocked_when_busy_or_in_drop_phase(self):; 207: def test_restart_keeps_count_and_never_replays_jobs(self):; 217: def test_restart_after_count_write_failure_never_recounts_or_replays(self):; 229: def test_restart_with_h2off_intent_never_counts_or_replays(self):; 239: def test_stack_commit_is_atomic_and_idempotent_after_restart(self): |
| nx100_full_cycle_v1/tests/test_hand_jobs.py | 35: def test_four_buttons_start_only_their_named_job(self):; 46: def test_ack_is_not_completion_and_second_command_is_blocked(self):; 53: def test_lost_start_reply_is_not_retried(self):; 68: def test_hold_cancels_without_resuming(self):; 74: def test_wrong_current_job_is_fault(self):; 81: def test_running_after_ack_times_out(self):; 92: def test_configured_job_wire_bytes_and_no_implicit_resume(self): |
| nx100_full_cycle_v1/tests/test_hold_release.py | 25: def test_explicit_release_sends_only_hold_off_and_verifies_readback(self):; 33: def test_unconfirmed_or_unacknowledged_release_sends_nothing(self):; 41: def test_external_pendant_running_or_remote_off_blocks_release(self):; 52: def test_lost_release_response_is_fault_without_retry(self):; 68: def test_wire_framing_for_release_and_lost_reply(self): |
| nx100_full_cycle_v1/tests/test_independence.py | 15: def test_application_imports_have_no_legacy_path(self):; 34: def test_owned_path_cannot_escape(self):; 38: def test_copied_assets_integrity(self):; 43: def test_relocated_mock_cycle_without_access_to_original_project(self): |
| nx100_full_cycle_v1/tests/test_job_directory.py | 10: def test_moveunti_after_first_twenty_names_in_full_fragmented_directory(self):; 22: def test_missing_job_only_after_complete_directory(self):; 27: def test_timeout_after_first_complete_record_is_not_a_missing_job(self):; 34: def test_eof_without_final_record_terminator_is_incomplete(self):; 40: def test_response_limit_prevents_unbounded_directory(self): |
| nx100_full_cycle_v1/tests/test_laser_h2_cycle.py | 41: def test_real_branch_eighty_mm_s_and_h2on_only_after_laser_and_stopped(self):; 67: def test_stopped_with_laser_off_never_starts_h2on(self):; 74: def test_laser_on_while_running_never_starts_h2on(self):; 89: def test_laser_unknown_during_job_never_starts_h2on(self):; 102: def test_laser_drops_before_h2on_command_is_blocked(self):; 112: def test_short_job_can_finish_between_status_polls(self): |
| nx100_full_cycle_v1/tests/test_launcher.py | 15: def test_factory_defaults_to_real_without_connecting_hardware(self):; 26: def test_main_defaults_to_real_and_schedules_edge_after_startup(self):; 41: def test_second_launch_opens_existing_real_hmi_without_second_server(self):; 49: def test_edge_launch_uses_argument_list(self):; 55: def test_edge_waits_for_server_ready_and_does_not_open_failed_server(self):; 67: def test_existing_server_must_match_application_and_real_mode(self): |
| nx100_full_cycle_v1/tests/test_pick_order.py | 18: def test_reappearing_low_ids_wait_until_higher_ids_are_picked(self):; 26: def test_missing_ids_skipped_and_single_visible_id_remains_pickable(self):; 31: def test_failed_commit_does_not_advance_and_restart_keeps_order(self): |
| nx100_full_cycle_v1/tests/test_position_variable.py | 15: def test_only_z_changes_and_other_fields_are_preserved(self):; 26: def test_invalid_variable_and_coordinate_data_rejected(self):; 34: def test_loadv_lost_reply_is_unknown_and_not_retried(self):; 67: def test_write_and_verify_before_drop_no_pc_descent_first_three_boards(self):; 83: def test_wrong_readback_blocks_drop_h2off_and_count(self):; 98: def test_drop_must_stop_at_p010_before_h2off(self):; 113: def test_p010_uses_p009_safe_xy_and_posture_instead_of_old_p010_or_pick(self): |
| nx100_full_cycle_v1/tests/test_prefetch.py | 39: def test_prepared_history_accepts_one_fresh_frame_and_uses_fresh_xy(self):; 54: def test_occluded_uncertain_moved_or_new_instance_must_stabilize_again(self):; 69: def test_cached_frame_cannot_be_used_after_lift(self):; 77: def test_camera_error_cannot_be_hidden_by_prepared_target(self):; 83: def test_wrong_pick_order_or_hold_discards_preparation(self): |
| nx100_full_cycle_v1/tests/test_protocol.py | 34: def test_fragmented_and_coalesced_status(self):; 42: def test_start_explicit_job_and_exact_size(self):; 48: def test_lost_start_reply_never_retries(self):; 55: def test_no_payload_before_ack(self):; 62: def test_invalid_command_does_not_open_socket(self):; 70: def test_movl_preserves_metadata(self):; 76: def test_every_status_bit(self): |
| nx100_full_cycle_v1/tests/test_repeat.py | 34: def test_two_boards_then_empty_stops_without_third_move(self):; 59: def test_empty_initial_scene_completes_without_motion(self):; 70: def test_repeated_full_cycles_pick_12341_even_when_id_one_reappears(self):; 92: def test_camera_loss_after_first_board_faults_without_next_pick(self):; 106: def test_hold_after_lift_prevents_next_pick(self): |
| nx100_full_cycle_v1/tests/test_sensor.py | 10: def test_pressure_in2_in3_are_independent_of_laser_and_outputs(self):; 21: def test_unverified_mapping_still_reads_actual_byte_for_display(self):; 31: def test_active_low(self):; 36: def test_bad_or_missing_reply_is_not_off(self):; 43: def test_ioread_failure_preserves_robot_status_and_position(self):; 60: def test_sensor_reads_even_if_position_reply_fails(self): |
| nx100_full_cycle_v1/tests/test_tracker.py | 12: def test_arrival_order_survives_confidence_and_detection_order_changes(self):; 20: def test_return_before_ten_seconds_keeps_id_and_resets_absence_timer(self):; 30: def test_missing_id_reserved_then_reused_without_renumbering_other_boards(self):; 38: def test_simultaneous_arrivals_sorted_by_position_and_ids_are_unique(self):; 45: def test_expired_tracks_do_not_produce_stale_detections(self): |
| nx100_full_cycle_v1/tests/test_vacuum.py | 12: def test_read_confirmed_relay_addresses_without_write_mapping(self):; 19: def test_bad_readback_addresses_fail_before_io(self):; 25: def test_physical_output_is_not_silently_used_as_network_input(self):; 30: def test_manual_io_does_not_require_servo_or_motion_commissioning(self):; 47: def test_network_echo_does_not_prove_physical_relay_changed(self): |
| nx100_full_cycle_v1/tests/test_vision.py | 19: def test_lowest_id_and_two_seconds(self):; 26: def test_repeated_frame_never_counts(self):; 31: def test_gap_stale_and_uncertain_reset(self):; 40: def test_motion_over_three_mm_resets(self):; 45: def test_identity_reuse_resets(self):; 50: def test_low_confidence_and_nan_never_lock(self):; 57: def test_real_camera_connect_accepts_existing_needs_review_calibration(self):; 79: def test_actual_copied_calibration_offset_once(self):; 93: def test_detector_bbox_center_uses_calibration_once(self): |
| nx100_variables_web/tests/test_variables.py | 26: def test_types_and_numeric_index(self):; 34: def test_connect_sends_no_variable_command_and_selection_sends_no_write(self):; 41: def test_realtime_measures_actual_rate_and_stops(self):; 56: def test_requested_period_is_separate_from_roundtrip(self):; 63: def test_manual_write_readback_and_bounds(self):; 74: def test_write_rejected_for_different_variable(self):; 79: def test_position_edit_preserves_frame_tool_posture(self):; 84: def test_unknown_write_never_retries_and_requires_correct_readback(self):; 98: def test_errors_stop_polling_after_three_failures(self):; 108: def test_no_overlapping_poll_and_manual_write(self):; 128: def test_http_assets_and_control_origin(self): |
| nx100_web_control/tests/browser_smoke.py | Package/fixture/setup, không test_* |
| nx100_web_control/tests/camera_smoke.py | Package/fixture/setup, không test_* |
| nx100_web_control/tests/test_vision.py | 45: def test_center_uses_camera_to_base_direction_and_mm(self):; 51: def test_distorted_projection_round_trip_on_translated_plane(self):; 60: def test_rejects_invalid_pixel_resolution_and_plane_behind_camera(self):; 71: def test_parallel_ray_rejected(self):; 78: def test_bad_transform_or_units_rejected(self):; 90: def test_frames_expire_and_reload_invalidates_old_clicks(self):; 106: def test_camera_click_has_no_robot_commands_and_requires_explicit_z(self): |
| nx100_web_control/tests/test_web.py | 32: def test_live_poll_reads_positions_without_sending_motion(self):; 41: def test_auto_move_without_read_uses_fresh_tool_and_preflight(self):; 59: def test_auto_move_still_blocks_running_and_hold_without_queue(self):; 67: def test_hold_intent_stops_poll_before_next_wire_exchange(self):; 81: def test_preflight_each_blocker_sends_no_move(self):; 104: def test_no_implicit_motion_on_read_or_connect(self):; 111: def test_stale_reference_never_moves(self):; 119: def test_payload_and_completion_need_two_stopped_samples(self):; 138: def test_running_at_target_is_not_complete(self):; 146: def test_unknown_send_disconnects_and_reconnect_does_not_replay(self):; 169: def test_lock_prevents_overlap_and_hold_blocks_new_move(self):; 195: def test_move_waits_for_inflight_poll_then_sends_once_without_overlap(self):; 242: def test_hold_or_disconnect_cancels_move_waiting_for_read(self):; 273: def test_wait_timeout_drops_move_and_never_sends_after_lock_release(self):; 286: def test_off_target_and_confirmation_timeout_are_not_complete(self):; 311: def test_auto_api_accepts_no_reference_and_no_read_button_step(self):; 319: def test_every_route_and_static_assets(self):; 351: def test_bad_inputs_and_cross_origin_send_no_commands(self):; 377: def test_read_failure_returns_reconnectable_error(self): |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/tests/test_commands.py | 10: def test_read_alarms(self):; 14: def test_read_current_joint_coordinate_position(self):; 18: def test_write_hold(self):; 22: def test_write_reset(self):; 26: def test_write_cancel(self):; 30: def test_write_servo_power(self):; 34: def test_write_start_job(self):; 38: def test_read_io_signals(self):; 43: def test_write_io_signals(self):; 49: def test_write_io_signals_without_byte_value_is_rejected(self):; 53: def test_read_all_job_names(self):; 58: def test_write_master_job(self):; 62: def test_linear_motion_move(self):; 75: def test_joint_motion_move(self): |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/tests/test_gripper.py | 9: def test_write_gripper_close(self):; 15: def test_write_gripper_open(self): |
| nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/tests/__init__.py | Package/fixture/setup, không test_* |

### 16.4 Tính toán phụ trợ và legacy

Các phép tính này có trong source nhưng không phải thuật toán full-cycle:

- module/Utils.py:7-16: command byte length = len(UTF8(data+CR)) nếu có data, ngược lại0. Protocol hiện tại chỉ ASCII sau validation.
- module/Utils.py:32-39: binary_to_decimal coi integer chứa chữ số nhị phân, tính tổng digit_i·2^i, khác việc dùng một bitmask machine bất kỳ.
- module/Utils.py:50-60: equivalent=|a−b|<t, legacy is_in_position dùng tXYZ=0,01 mm và tAngle=0,1°, không angular wrap/RUNNING check như controller mới.
- objects/Time.py:13-19: millis+seconds×1000 < round(time.time()×1000), dùng wall-clock và strict inequality, khác monotonic workflow mới.
- module/WebServer.py:79-104: nudge±25 mm trên X/Y/Z, speed50. Label S/L/U của web không biến chúng thành pulse joint command.
- module/xbox360_controller.py:125-142: dead-zone remap, d=self.dead_zone, v=axis raw, output vô thứ nguyên:

$$
f(v)=\begin{cases}
(v-d)/(1-d),&v>d\\
(v+d)/(1-d),&v<-d\\
0,&|v|\le d.
\end{cases}
$$

XboxController.py có pygame loop/FPS60/cooldown WAIT_FOR0,25 s, có thể phát servo/START/MOVL; không chạy audit. Legacy Gripper.py dùng custom addresses22010/10022/25/27 và count4/1 không hợp whole-byte validator. tests/test_gripper.py cố ý xác nhận ValueError trước transmission; không tái sử dụng mapping cho vacuum.

RISK objects/Gripper.py: attributes is_acknowledge/is_hit trùng tên method, có thể che callable; không sửa. Commands.read_all_job_names gọi RJDIR nhưng original Protocol.encode_command từ chối command này; wrapper tồn tại không chứng minh feature hoạt động. Commands.read_io_signals bọc Response.is_success so0000 không phù hợp diễn giải mọi read-value.

Preview dùng s=min(1,W_preview/W_native), kích thước/bbox overlay nhân s rồi round. Web camera JS chuyển click canvas về pixel sensor; VisionService registry UUID/TTL60 s/fingerprint. Đây là quy đổi hiển thị, không phải mm/pixel calibration.

## 17. Cấu hình, thuật ngữ và bảo toàn

### 17.1 Cấu hình có hiệu lực và lịch sử

| Trường | Config trên đĩa | Override/dữ liệu lưu | Ý nghĩa |
|---|---|---|---|
| full robot | 192.168.255.1:80,timeout3 s | Không override endpoint qua operator settings | TCP ASCII |
| full camera | 192.168.255.3 | Chọn exact GigE IP | SDK camera port không ghi |
| full plane/Z_safe | 0 /500 mm | operator settings cùng0/500 | Plane vision khác safe motion/search stop |
| full MOVL | 80 mm/s | **350 mm/s REAL persisted** | Cycle.__init__ nạp đè; LIMITS max500 |
| full orientation | Rx180,Ry0,Rz90° | REAL persisted cùng giá trị | Checklist cũ có Rz0, không áp dụng thay source |
| full stability | 5 frames/1 s/3 mm | cfg dùng trực tiếp | README còn10/2 là mâu thuẫn |
| full frame age/gap | 1 /0,5 s | Pipeline/StableTarget | Latency thực UNKNOWN |
| full motion | timeout120,target30,job60,poll0,1 s | Settle3;XYZ1 mm;angle0,5° | Không chức năng safety |
| full workflow | laser_on_and_stopped,repeat=true,empty2 s,end_after_start=false | Journal có trạng thái lịch sử | Không nhầm handoff cũ |
| full drop | P010;safe600;first330;thickness12;Z+200 | Stack count6→next402 | Dữ liệu thực ở stack được load ưu tiên config default |
| full commissioning | Các cờ false/hash/evidence rỗng | operator_motion_workflow bypass nhánh tương ứng | Không chứng minh REAL bị khóa |
| full laser | 20050 bit0/high,verified=false | Telemetry vẫn đọc | Chưa đo mapping physical trong audit |
| full vacuum | method job/4 HAND jobs,verified=true | Outputs30050/51; inputs20051/52 | Không pressure guard |
| full web | loopback8011,allowed hosts/clients | Token từ NX100_HMI_TOKEN nếu đặt | Lease30 s |
| tracking | speed5;10 frame;+2 s;3 mm;>50;age/gap500 ms | Config version runtime | No durable command journal |
| snapshot | speed5;>50 mm;không stability | saved batch/fingerprint/history | Capture không age gate; đổi cáp được phép |
| web-control | timeout3,poll1000,debounce400,move60 s | Các axes range phục vụ UI | Không backend safety workspace từ UI range |
| variables | I099,period100 ms,timeout3 s connect | Realtime metrics/rate | Period0 không real-time deterministic |

Operator settings chỉ cho plane_z_mm,z_safe,movl_speed,rx,ry,rz hữu hạn và phạm vi LIMITS. configure lưu riêng mock/real; config JSON gốc không tự được rewrite bởi endpoint settings. Documentation audit không gọi endpoint này.

### 17.2 Thuật ngữ

| Thuật ngữ | Nghĩa trong hệ thống |
|---|---|
| NX100 / INFORM JOB | Controller / chương trình robot trên controller |
| MOVL / MOVJ / IMOV | Nội suy thẳng / nội suy khớp tới target / incremental INFORM trong JOB |
| BASE / TOOL / TCP | Hệ Base / hệ tool / tool center point; không thay thế lẫn nhau |
| Intrinsic K / distortion | Camera pinhole và méo ống kính |
| Eye-to-Hand | Camera cố định ngoài robot, transform camera→Base |
| Plane Z | Mặt phẳng giả định cho ray-plane, không phải laser height đo online |
| Posture | Bitmask tư thế robot, không phải ba góc Euler |
| RSTATS / RPOSC / RPOSJ | Trạng thái / Cartesian pose / joint pulses |
| SAVEV / LOADV | Đọc / ghi biến controller |
| IOREAD / IOWRITE | Đọc contacts / ghi network input theo validator |
| HAND / EOAT | JOB/output cơ cấu / end-of-arm tooling |
| Confidence / object ID / instance | Score class / số hiển thị track / thế hệ track chống nhầm ID tái dùng |
| ACK / accepted / complete | Nhận command / xác nhận giao thức / hoàn thành theo tiêu chí ứng dụng; không tương đương |
| OutcomeUnknown | Command có thể đã thực thi, không được tự resend |
| Lease / revision / request_id | Quyền HMI có hạn / phiên bản state / định danh chống request trùng |
| Journal / stack store | Intent và tiến trình bền / bộ đếm và lịch sử chống count trùng |
| HOLD / E-STOP | Hold phần mềm controller / chức năng dừng khẩn độc lập, không thay thế nhau |

### 17.3 Manifest và bảo toàn

Trước lần ghi Markdown đầu tiên: metadata toàn workspace gồm 41.913 entries, 37.985 file; SHA-256 được tính cho toàn bộ 37.985 file, gồm .git/.venv/.runtime/cache. Hash tổng tạo từ các dòng path-relative + "|" + SHA256(file), sắp theo FullName rồi join LF và băm UTF-8. Hash metadata tạo từ path, loại file/thư mục, length và LastWriteTimeUtc ticks. Không dùng Git clean thay bằng chứng hash.

- Git HEAD ban đầu: 606c8ff3cb543ed78c33f9cbf404da553b28abbb.
- git --no-optional-locks status --porcelain=v1 --untracked-files=normal ban đầu rỗng.
- SHA-256 manifest nội dung toàn workspace ban đầu: 3398301E9EBC145072EBF6570E30397A1C0BE2E5F4177AB03D1371BA5A0438D5.
- Metadata manifest ban đầu: FBE6142AC6FAFCB9E81CD413C3E54ADBD5FC85FAD1106F3FD65DD5FE5AC30222.
- Ngoài hash tổng, giữ 312 record file ngoài env/cache/runtime/.git theo path,length,last-write,SHA để đối chiếu chi tiết first-party assets/source/data.
- Chỉ loại đúng file Markdown này khỏi phép so sánh cuối; không loại cả đuôi .md hoặc thư mục gốc.

| Cây project | File vật lý | SHA-256 manifest nội dung trước ghi |
|---|---:|---|
| nx100_camera_snapshot_move | 2656 | A02163014D10F702697DF1A12B1FB9784B5E3A612C59B7C6E2CE81CBC20BF3F6 |
| nx100_full_cycle_v1 | 22338 | A3828AFEBBEE4ED5A0D1100D011F150FCCF3D7DE8FC09688BC88EB330EB77B08 |
| nx100_variables_web | 9 | 5439D85B6F8B50722B50C600A909FC5B37D4DE11E962AF6918E0970E709700AB |
| nx100_web_control | 44 | 70D58ABD9584B45369ED2EE2970C7713164FCC6AD4B7C8013C32EC7044098DA3 |
| nx100_yolo_auto_tracking | 3062 | F2D78EFA8A940BBD0B1CB87B448F2449D98ECCEA8E2622E9F0D73D3DFB3D7A4B |
| nx100-remote-control-master | 66 | 0C665A1BCE2823674CDE7EFFA2BC6C6551D0FC4F9304997572CECC3397E8A4E9 |

### 17.4 Tài nguyên/module giống byte đã xác nhận

| SHA-256 | Đường dẫn trong sáu project |
|---|---|
| 69B8BCFCC67746448419676E59E4BC479DA5BF532D92FD251E60B2F13BEAC912 | nx100-remote-control-master/nx100-remote-control-master/LICENSE; nx100_camera_snapshot_move/robot/UPSTREAM_LICENSE; nx100_full_cycle_v1/LICENSE; nx100_full_cycle_v1/docs/UPSTREAM_LICENSE; nx100_yolo_auto_tracking/robot/UPSTREAM_LICENSE |
| B7903BA5109F964D8E4A49536304D0945838ED12F207125AC322C08189DA00A2 | nx100-remote-control-master/nx100-remote-control-master/src/nx100_remote_control/objects/Status.py; nx100_camera_snapshot_move/robot/status.py; nx100_full_cycle_v1/robot/status.py; nx100_yolo_auto_tracking/robot/status.py |
| A0843042AD74A8F34BE8BD87E3665EDA2D13DA0C609544756D287F36DC2B5F0A | nx100_camera_snapshot_move/config.json; nx100_full_cycle_v1/docs/source_camera_config.json |
| 4A076E1CF0D8820B2FC1A5B6501B27AD8AE4BECC7B2566A4D100632F68A402BE | nx100_camera_snapshot_move/requirements.txt; nx100_yolo_auto_tracking/requirements.txt |
| C792A9B572E935C2F12BF21F71B4E0C821D6F7AF9C40920D16166A8109D1D418 | nx100_camera_snapshot_move/calibration/camera_intrinsic_2.npz; nx100_full_cycle_v1/calibration/camera_intrinsic_2.npz; nx100_yolo_auto_tracking/calibration/camera_intrinsic_2.npz |
| 6773BBFED8C7AB5A75BDBB851B9FBD2D13276B59F65055EAB81EC456E1C21A6F | nx100_camera_snapshot_move/calibration/eye_to_hand.npz; nx100_full_cycle_v1/calibration/eye_to_hand.npz; nx100_yolo_auto_tracking/calibration/eye_to_hand.npz |
| F4FA0E39C43BD09842314FFEC8331B6AE7ACD3357EB3696C42C8DF845C93F8B5 | nx100_camera_snapshot_move/models/best.pt; nx100_full_cycle_v1/models/best.pt; nx100_yolo_auto_tracking/models/best.pt |
| 28F45F4063131484329FEE72A4F85A598D991E1DED41CAF39144B3C553B6BEEA | nx100_camera_snapshot_move/robot/cartesian.py; nx100_full_cycle_v1/robot/cartesian.py; nx100_yolo_auto_tracking/robot/cartesian.py |
| 835962036BFDD00B4720E631543571ABC932C960AA3E5E1132FEA891CC9CE067 | nx100_camera_snapshot_move/static/style.css; nx100_yolo_auto_tracking/static/style.css |
| 90A1454634BE7E06D99BDF5A653F4BB4ECD8D469BBB8AAE0534850BFBC7417B8 | nx100_camera_snapshot_move/vision/calibration.py; nx100_full_cycle_v1/vision/calibration.py |
| 9C09892944A0D40C801DDA5491C5CAACE83BD023C2F973997D55EACD6FA5EFDB | nx100_camera_snapshot_move/vision/camera.py; nx100_full_cycle_v1/vision/camera.py; nx100_yolo_auto_tracking/vision/camera.py |
| 979367EEFB9F1798CABDFCFFFC66C7E4A3FCE61B968C73A4589C9CD06AC29401 | nx100_camera_snapshot_move/vision/detector.py; nx100_yolo_auto_tracking/vision/detector.py |
| FCE99D24EAD5B5346E71043870443AFCD201687B691635E06A3CC58BCEC891A1 | nx100_camera_snapshot_move/vision/tracker.py; nx100_full_cycle_v1/vision/tracker.py; nx100_yolo_auto_tracking/vision/tracker.py |
| 5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9 | nx100_full_cycle_v1/data/mock/execution.lock; nx100_full_cycle_v1/data/real/execution.lock |
| E4D8C253C1A07AAA2797DCC17186F37A17C3E7DDA83CC52E06531272BD21991B | nx100_web_control/robot/mock.py; nx100_yolo_auto_tracking/robot/mock.py |

### 17.5 Kết quả kiểm tra cuối

**PASS — bảo toàn dữ liệu ngoài file tài liệu.**

Sau khi tạo Markdown, đã đọc lại và băm toàn bộ 37.985 file ban đầu, chỉ loại đúng đường dẫn file tài liệu khỏi so sánh. Kết quả:

| Kiểm tra | Kết quả |
|---|---|
| Tổng file ban đầu ngoài tài liệu | 37.985 trước và sau |
| Nội dung SHA-256 toàn workspace | Trùng manifest 3398301E9EBC145072EBF6570E30397A1C0BE2E5F4177AB03D1371BA5A0438D5 |
| Từng nhóm root, gồm 6 project, .git, môi trường/cache và tài nguyên khác | Số file và manifest hash đều trùng |
| Metadata path/type/length/LastWriteTimeUtc | Trùng FBE6142AC6FAFCB9E81CD413C3E54ADBD5FC85FAD1106F3FD65DD5FE5AC30222 |
| 312 record chi tiết ngoài môi trường/cache/runtime/.git | 0 thay đổi nội dung/kích thước/last-write, 0 thêm, 0 xóa |
| Source/config/calibration/model/JOB/dữ liệu/log cũ | Không phát hiện chỉnh sửa, tạo, xóa, đổi tên hay di chuyển |
| Git HEAD | Giữ 606c8ff3cb543ed78c33f9cbf404da553b28abbb |
| Git status | Chỉ ?? NX100_SYSTEM_COMPLETE_TECHNICAL_DOCUMENTATION.md |
| Chạy/import ứng dụng hoặc test | Không |
| Kết nối/gửi lệnh robot, camera, I/O; bật servo; ghi biến/output | Không |
| Cài package, đổi môi trường/branch/commit/index | Không |
| File được tạo/cập nhật trong nhiệm vụ | Chỉ Markdown này |

Kiểm tra nội dung tài liệu: đủ17 mục; source paths trong inventory tồn tại; dẫn chứng đầy đủ dạng path:line được kiểm giới hạn dòng; code fence cân bằng; phân biệt mock/REAL branch/hardware proof, proposal/implementation và log lịch sử. Chỉ mục symbol là phân tích lexical, không thay runtime verification. Không tuyên bố đã chạy test hay xác minh cơ khí.

Kết luận kiến trúc: nên dùng nx100_full_cycle_v1 làm nền điều phối và tái sử dụng có chọn lọc các thành phần khác theo mục14. Các khoảng thiếu lớn nhất là chất lượng calibration, effective speed350, proof search-Z, pressure/release guards, nội dung JOB/mapping và quyền sở hữu robot xuyên ứng dụng. Tất cả đề xuất chỉ ghi trong tài liệu; mã nguồn và cấu hình được bảo toàn.


