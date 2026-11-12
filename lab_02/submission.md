# Lab 02 — Robust Reactive Lamp: รายงานกลุ่ม 4

ชื่อ: ภูวเมศฐ์ กิตติธันยวัฒน์  
รหัสนักศึกษา: 6752500126  
Python: 3.13.7  
ขอบเขต: ผลจาก simulator เท่านั้น ไม่ใช่การทดลองกับ sensor หรือหุ่นยนต์จริง

## 1. คำถามและ prediction

คำถาม: noise และ delay ของระยะวัดมีผลต่อการสลับสถานะ false trigger และเวลาตอบสนองของ controller แบบใดบ้าง

Prediction จากโครงสร้าง controller (บันทึกประกอบหลังจากได้ผลแล้ว จึงไม่ใช่ preregistration ก่อนรัน): C1 ซึ่งใช้ threshold เดียวจะไวต่อ noise รอบ threshold และเกิดการสลับเพิ่ม; C2 ซึ่งกรองสัญญาณและใช้ hysteresis น่าจะลดการสลับโดยแลกกับ latency; C3 ซึ่งสร้างคำสั่งแบบ proportional ควรเปลี่ยนคำสั่งต่อเนื่องกว่าแบบสลับสองสถานะ ทั้งนี้ delay จะเลื่อนการตอบสนองโดยประมาณตามเวลาหน่วง

## 2. ผล comparison: noise 0.01 m, delay 0 ms, 5 trials/condition

| Controller | Mean enter latency (s) | Mean recovery (s) | False trigger/min | Extra switches | Mean absolute command change |
|---|---:|---:|---:|---:|---:|
| C0 open-loop | 0.0029 | 2.8571 | 2.9970 | 0.0 | 0.00120 |
| C1 single threshold | 0.0189 | 0.1806 | 8.3916 | 12.4 | 0.00864 |
| C2 filter + hysteresis | 0.4069 | 0.4543 | 0.0000 | 0.0 | 0.00120 |
| C3 proportional + clamp | 0.0429 | 0.1091 | 1.7982 | 1.6 | 0.00465 |

C1 สลับเพิ่มมากที่สุดในชุดนี้ ส่วน C2 ไม่มี extra switch หรือ false trigger แต่มี enter latency สูงกว่า C1 ประมาณ 0.388 s. C3 อยู่กึ่งกลาง: latency ต่ำกว่า C2 แต่ยังมี false trigger และ extra switch. ค่า C0 เป็น open-loop และ metric false-trigger ที่ออกจาก protocol นี้ไม่ควรตีความว่าเป็นการตรวจ sensor ของ C0.

## 3. Robustness ของ C2

แต่ละแถวมี 5 trials; ชุด robustness เป็นคนละ protocol/seed set กับ comparison:

| Noise (m) | Delay (ms) | Enter latency mean (s) | Recovery mean (s) | Extra switches mean | Invalid samples/trial |
|---:|---:|---:|---:|---:|---:|
| 0.00 | 0 | 0.4229 | 0.4229 | 0 | 0 |
| 0.00 | 100 | 0.5229 | 0.5229 | 0 | 0 |
| 0.00 | 300 | 0.7229 | 0.7229 | 0 | 0 |
| 0.01 | 0 | 0.4309 | 0.4337 | 0 | 0 |
| 0.03 | 0 | 0.4069 | 0.4149 | 0 | 0 |
| 0.03 | 300 | 0.5989 | 0.6406 | 0 | 15 |

เมื่อ noise เป็นศูนย์ การเพิ่ม delay 100/300 ms เพิ่ม latency จาก 0.4229 s เป็น 0.5229/0.7229 s ตามลำดับ. ผล noise ไม่ได้เพิ่ม latency แบบ monotonic ในตารางนี้ เพราะมี variation จาก trial และมี invalid samples ใน condition 0.03 m/300 ms; จึงไม่ควรสรุปสาเหตุจากตัวเลขเพียงแถวเดียว.

## 4. วิธีทำงานและหลักฐาน

- เติม `student_controller.py`: first-order low-pass filter, single threshold, hysteresis, proportional command พร้อม clamp และ safe command ศูนย์สำหรับข้อมูลใช้ไม่ได้/เก่า.
- Grader ของ controller: 10/10 checks ผ่าน; behavior tests 6/6 และ focused integration tests 4/4 ผ่าน.
- Full test suite มี 2 tests ที่ตั้งใจตรวจว่า starter ยังมี TODO/ยังไม่เสร็จ จึงไม่ผ่านหลังเติมงานตามโจทย์; ไม่แก้ test ของผู้สอน.
- ไฟล์ผลหลัก: `results/group4_grade.json`, `results/group4_comparison/run_config.json`, `summary_trials.csv`, `summary_aggregate.csv`, raw `trials/*.csv`, `results/group4_robustness/summary_aggregate.csv`.
- กราฟ C2 trial หนึ่งรายการ: `results/group4_comparison/C2_trial1.png`.

คำสั่งทำซ้ำจากโฟลเดอร์ `lab_02`:

```powershell
py -3 grade_submission.py --student-file student_controller.py --out results\group4_grade.json
py -3 lab02.py --controller-source student --student-file student_controller.py --protocol controller-comparison --out results\group4_comparison
py -3 lab02.py --protocol robustness-full --condition C2 --out results\group4_robustness
py -3 plot_trial.py results\group4_comparison\trials\C2_n0.01_d000_r01.csv --out results\group4_comparison\C2_trial1.png
```

## 5. สรุปและข้อจำกัด

ใน proposed course model นี้ hysteresis/filter ลดการสลับเทียบกับ C1 แต่เพิ่มเวลาตอบสนอง; proportional control ลดการสลับลงแต่ไม่กำจัด false trigger ทั้งหมด. ผลนี้ไม่ยืนยันความถูกต้องของ sensor จริง ความปลอดภัย ความเสถียร การใช้พลังงาน หรือความเหมาะสมของ threshold บน hardware. ก่อนใช้จริงต้องตรวจ datasheet, calibration, หน่วยและช่วง actuator, safe command และ emergency stop. ตัวเลขทุกค่าเป็นผลจำลองและต้องอ่านร่วมกับ raw CSV/config ของแต่ละ run.
