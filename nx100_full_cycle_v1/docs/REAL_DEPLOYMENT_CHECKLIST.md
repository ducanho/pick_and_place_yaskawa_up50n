# Nghiệm thu REAL theo giai đoạn

Chưa thực hiện thử phần cứng trong lần triển khai này. Không mở FULL CYCLE chỉ bằng việc sửa các cờ JSON. Cần người có trách nhiệm nghiệm thu thực tế trong cell và ghi bằng chứng vào hồ sơ tại đây.

## 1. READ ONLY

- Đóng các ứng dụng khác đang sử dụng Ethernet Server hoặc giữ camera.
- PC 192.168.255.2, robot 192.168.255.1:80, camera 192.168.255.3 qua switch đồng thời; không cần đổi dây.
- Cài MVS đúng kiến trúc Python, YOLO/PyTorch, model và calibration nằm trong dự án này.
- CONNECT: so sánh cả 8 flag RSTATS với pendant; RPOSC BASE/tool/posture/trục ngoài và RPOSJ đúng. Không tự SVON/reset.
- Kiểm tra IP camera, resolution/ROI, exposure và lens thực tế; giữ ROI/kích thước khớp intrinsic, không resize ảnh trước transform. Camera adapter dùng continuous trigger và optimal packet size như nguồn sao chép; các thiết lập quang học cần giữ trên camera.
- Đối chiếu vị trí vật thực với transform trên các điểm kiểm tra, gồm offset +280/+215 đúng một lần. Theo yêu cầu người vận hành ngày 24/10/2026, dùng nguyên calibration hiện có; `needs_review` được hiển thị như cảnh báo và không khóa kết nối/transform dựa trên nhãn quality.
- Thử laser ON/OFF, xác minh `IOREAD 20050,8`, bit và cực tính với IN1 trên pendant. Đặt `laser.verified` chỉ sau khi đo.
- Đọc RJDIR và RJSEQ, xác nhận framing trên chính máy này, export MOVEUNTI để kiểm tra. Không sửa JOB.

## 2. XY ONLY

- Xác minh TOOL/TCP, posture, tải trọng, giới hạn khớp, dây và vùng robot. Điền `expected_tool` và `expected_posture`.
- RZ mới là 0° (nguồn snapshot trước là 90°). Kiểm chứng orientation RX=180/RY=0/RZ=0, singularity và giới hạn trục trước khi gửi.
- `workspace` mặc định chỉ là giới hạn kiểm tra số học, không chứng minh đường đi an toàn. Thu hẹp theo cell. Kiểm tra toàn bộ đoạn lift/hạ Z tại XY hiện tại rồi đoạn MOVL tới XY đích, gồm xoay cổ tay. Không có collision planner hoặc IK safety solver trong phần mềm này.
- Kiểm chứng Z_safe tuyệt đối và tốc độ 5 mm/s bằng chế độ thử được giám sát. Test HOLD, alarm, mất kết nối và RSTATS/RPOSC completion; phần mềm không thay safety controller.
- Ghi bằng chứng, đặt `read_only`, `path_verified`, `orientation_verified`; cấu hình hash theo hướng dẫn cuối trang. Chọn XY ONLY trên HMI, chạy một vật; xác minh lại trên pendant.

## 3. MOVEUNTI ONLY

- Xác minh JOB đã tồn tại, IMOV dùng UNTIL IN#(1), chiều Z, speed và hành trình từ chính export/pendant; điền `job.min_z`, `max_descent_mm`, `speed_mm_s`, `verified`, `start_verified` sau nghiệm thu có giám sát.
- Đưa robot tới XY/Z_safe và orientation hợp lệ bằng quy trình đã nghiệm thu. Laser phải OFF trước START. Chọn MOVEUNTI ONLY.
- Theo dõi RUNNING ON → OFF, cạnh IN1, RPOSC và hành trình. Test laser không ON phải dẫn đến HOLD request + FAULT. Nếu mất TCP, dùng quy trình an toàn tại cell; không tin software đã dừng robot.
- Backend hiện khóa sau JOB REAL vì thiếu bằng chứng nguyên nhân dừng. Cần kỹ sư xác định tín hiệu xác nhận đáng tin cậy **đang có** trên controller, kiểm chứng và tích hợp adapter có tests trước khi mở chuyển bước. Không sửa JOB/ladder để lách khóa.

## 4. VACUUM ONLY

- Xác minh HAND 1-1/1-2 là độc lập hay bổ sung; xác định đúng phương thức điều khiển và cực tính. Không giả định địa chỉ.
- Nếu có mapping network input đã hoạt động, xác minh byte riêng, bit, quyền sở hữu và readback; điền cấu hình vacuum theo IO_MAPPING.md. Nếu không có, giữ khóa và triển khai đúng phương thức được nhà máy xác minh.
- Chỉ thử khi robot đã dừng, cell được kiểm soát. Test ON/OFF từng HAND, đảo cực, chế độ bổ sung và mất phản hồi. Không bật đồng thời hai HAND bổ sung. Không dùng áp suất trong V1.

## 5. FULL CYCLE

- Cần bằng chứng hoàn thành cả READ ONLY, XY ONLY, MOVEUNTI ONLY, VACUUM ONLY và adapter xác nhận nguyên nhân dừng đã được nghiệm thu. Chỉ sau đó mới mở full_cycle.
- Thử một START/một vật, target freeze trong MOVL, laser hợp lệ, vacuum giữ tại Z dừng. Xác nhận không lift/HOME/thả/chạy tiếp.
- Thử duplicate START, stale revision, hai HMI, restart giữa lệnh, ALARM, HOLD, mất TCP và camera. Không tự resume hoặc retry lệnh chưa rõ kết quả.

## Hồ sơ và hash cấu hình

`commissioning` mặc định đều false. Hồ sơ cần người nghiệm thu, ngày, serial controller/camera, TOOL, export JOB, mapping I/O, giới hạn đường đi và kết quả từng giai đoạn. `evidence` là mô tả/đường dẫn tài liệu nằm trong dự án. Hash ràng buộc cấu hình hiện hành, không thay thế nghiệm thu thực tế:

```powershell
.\.venv\Scripts\python.exe -c "from settings import load_config; from workflow.safety_checks import commissioning_hash; print(commissioning_hash(load_config()))"
```

Ghi hash vào `commissioning.config_sha256` sau khi đã kiểm tra đúng cấu hình vận hành, gồm thông số người vận hành REAL nếu có. Thay Plane Z/Z_safe/speed/orientation hoặc mapping làm hash mất hiệu lực, REAL motion bị khóa lại. Không có hash hoặc cờ nào mở được `stop_reason_proven` hiện đang khóa REAL.
