# Audit và nguồn triển khai

Ngày triển khai: 24/10/2026, múi giờ Asia/Bangkok. Dự án mới: `nx100_full_cycle_v1`. Chỉ tạo/chỉnh sửa trong dự án mới; không gửi lệnh robot/camera REAL.

## Nguồn đã khảo sát

| Nguồn | Kết luận áp dụng |
|---|---|
| nx100_camera_snapshot_move | Tách module tốt; tái sử dụng Cartesian, status, camera, detector, transform, tracker và tài nguyên |
| nx100_yolo_auto_tracking | Đối chiếu tracking/stability; viết cycle mới vì cần một vật/một lần START, journal và JOB laser |
| nx100_web_control | Một số adapter có sys.path tham chiếu dự án khác; không dùng cách đó |
| nx100_variables_web | Đối chiếu transport và unknown write; variable editor không nằm trong đường chạy V1 |
| nx100-remote-control-master | Sao chép transport đã có framing/validation; thu hẹp command scope V1 |
| yolo_hikrobot_robot_coordinates | Đối chiếu ray/plane, offsets và camera; lấy tests BoardTracker |
| jobs | Có các JOB khác; không thấy export MOVEUNTI, không tạo bản thay thế |
| tests | Tái áp dụng các trường hợp framing, status bit, timeout và Cartesian metadata |
| datasheet | Đọc manual HW0483202, đặc biệt START, RJDIR/RJSEQ, IOREAD/IOWRITE |

Hash baseline của mã nguồn, cấu hình, model, calibration, JOB và tài liệu trong các nguồn ở `source_hashes.json`. Đây là dữ liệu audit, không phải đường dẫn runtime. `source_verification.json` ghi kết quả so sánh cuối. Git status được kiểm tra để phát hiện chỉnh sửa tracked files ngoài dự án mới.

## Đã COPY

| File trong dự án mới | Nguồn | Điều chỉnh |
|---|---|---|
| robot/protocol.py | remote-control/module/Protocol.py | Chỉ RSTATS/RPOSC/RPOSJ/RJSEQ/RJDIR/START MOVEUNTI/MOVL/HOLD ON/IOREAD/IOWRITE; cấm SVON/RESET/resume |
| robot/cartesian.py | snapshot_move/robot | Giữ nguyên; bảo toàn TOOL/posture/trục ngoài |
| robot/status.py | snapshot_move/robot | Giữ nguyên; bit RSTATS theo vị trí cố định |
| vision/camera.py | snapshot_move/vision | Giữ adapter MVS hệ thống, không sys.path tới dự án khác |
| vision/calibration.py | snapshot_move/vision | Giữ thuật toán và offset +280/+215 đúng một lần |
| vision/detector.py | snapshot_move/vision | Giữ YOLO bbox-center; thêm thông báo thiếu dependency REAL |
| vision/tracker.py | snapshot_move/vision | Giữ association, ID và generation |
| models/best.pt | snapshot_move/models | Bản sao vật lý, SHA-256 ở asset_hashes.json |
| calibration/*.npz | snapshot_move/calibration | Bản sao vật lý cả hai NPZ; đối chiếu K/distortion |
| tests/test_tracker.py | yolo.../tests/test_board_tracker.py | Bỏ sys.path, import vision.tracker nội bộ |
| docs/source_camera_config.json | snapshot_move/config.json | Chỉ đối chiếu, không dùng runtime; RZ cũ 90° |
| docs/HW0483202.pdf | datasheet/33175396.pdf | Manual đối chiếu cục bộ; không dùng runtime |
| LICENSE, docs/UPSTREAM_LICENSE | remote-control/LICENSE | Giữ thông tin giấy phép upstream |

Chi tiết tên nguồn đầy đủ ở `copied_files.json`. Thư viện bên thứ ba được sao chép vật lý vào `.venv` riêng; bản lock ghi phiên bản. Không sao chép log, snapshot thực thi, pending command hoặc runtime state của nguồn cũ.

## Mới viết

`settings.py`, FastAPI `app.py`, robot controller/mock/I/O/JOB/vacuum, vision stability/pipeline, workflow state_machine/cycle/safety_checks, HMI HTML/CSS/JS, script Windows, test suite, công cụ kiểm thử và tài liệu triển khai.

Đường dẫn tài nguyên đều dựa trên application root. Trạng thái và log tách MOCK/REAL. Test relocation chạy subprocess ở thư mục mới, chặn truy cập mã nguồn/tài nguyên vị trí ban đầu bằng Python audit hook và xác minh module ứng dụng được import tại bản sao.

## Căn cứ kỹ thuật và giới hạn

HW0483202 của Yaskawa là tài liệu sơ cấp đã có sẵn trong workspace: §3.1 framing TCP; §3.2.1 RJDIR/RJSEQ; §3.2.2 START trang 3-18; §3.2.3 I/O trang 3-29. Không áp dụng lệnh YERC/HSES của controller đời khác cho kết nối TCP này.

Lệnh `START MOVEUNTI` đúng theo manual, nhưng khả năng/phản hồi trên controller cụ thể chưa được thử trong lần này. `IOREAD 20050,8` cần xác minh bit/cực tính tại máy. HAND chưa có mapping thực tế trong nguồn nên REAL khóa. Không có tín hiệu chứng minh nguyên nhân JOB dừng: FULL REAL bị chặn trước chuyển động; MOVEUNTI ONLY, nếu được nghiệm thu và mở riêng, vẫn không được tự chuyển tới vacuum.

MOCK không chạy model YOLO; nó tạo detection mô phỏng. Test detector dùng kết quả YOLO giả để kiểm tra bbox-center và gọi calibration; test transform sử dụng NPZ thật đã sao chép. Bổ sung REAL: đã chép dependency hệ thống vào .venv riêng, nạp model và chạy ảnh đen; MVS SDK khả dụng nhưng chưa phát hiện camera, robot TCP timeout. Chi tiết ở real_dependency_copy.json, real_preflight.json và real_robot_readonly.json. Chưa đo FPS thực tế, độ chính xác nhận diện, đường đi hoặc an toàn phần cứng.
