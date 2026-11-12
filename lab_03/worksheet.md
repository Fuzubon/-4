# ใบงาน Lab 03 — SO(2) CPG และการเดินหุ่นยนต์หกขา (กรอกแล้ว)

ชื่อ: ภูวเมศฐ์ กิตติธันยวัฒน์  
รหัสนักศึกษา: 6752500126  
กลุ่ม: 4  
ขอบเขต: ทุกผลในเอกสารนี้มาจาก kinematic simulator ของรายวิชา ไม่ใช่การทดลองกับหุ่นยนต์จริง

## 1. Prediction และสมการ

Prediction จากสมการ (เขียนประกอบหลังได้ผลแล้ว จึงไม่ใช่ preregistration): เพิ่ม φ ควรเร่งการเปลี่ยนเฟสและเพิ่มความถี่/ความเร็ว; เพิ่ม α ควรเพิ่ม amplitude/clearance แต่ผลความถี่ไม่จำเป็นต้องเพิ่ม เพราะ tanh ทำให้ระบบไม่เชิงเส้น. Tripod A (`LF, RM, LH`) กับ Tripod B (`RF, LM, RH`) ถูกถอดรหัสด้วยเครื่องหมายตรงข้าม จึงทำงานแบบสลับกัน.

สมการใช้ค่ารอบเก่าทั้งคู่:

```text
a1 = α(cosφ·o1 + sinφ·o2)
a2 = α(−sinφ·o1 + cosφ·o2)
o1_next = tanh(a1)
o2_next = tanh(a2)
```

เมื่อ `o1=.10`, `o2=−.20`, `α=1.10`, `φ=.20 rad`:

| ค่า | ผลคำนวณ |
|---|---:|
| a1 | 0.064100 |
| a2 | −0.237468 |
| o1_next | 0.064012 |
| o2_next | −0.233103 |

การ implement เก็บ `old_o1, old_o2` ก่อนคำนวณ จึงไม่มีการใช้ค่ารอบใหม่ข้ามสมการ.

## 2. ผล gait comparison

ใช้ dt=.05 s, duration=30 s, warmup=10 s และเปลี่ยนทีละ parameter:

| Condition | α | φ (rad) | Speed (m/s) | Frequency (Hz) | Duty factor LF | Min support | Clearance (mm) |
|---|---:|---:|---:|---:|---:|---:|---:|
| baseline | 1.10 | .20 | .077756 | .625000 | .494176 | 3 | 17.095 |
| fast | 1.10 | .40 | .155511 | 1.267123 | .500832 | 3 | 17.113 |
| high_gain | 1.30 | .20 | .094457 | .544218 | .494176 | 3 | 24.637 |

เมื่อเพิ่ม φ เป็น .40 ความเร็วประมาณสองเท่าและความถี่เพิ่มจาก .625 เป็น 1.267 Hz; clearance แทบไม่เปลี่ยน. เมื่อเพิ่ม α ความเร็วเพิ่ม แต่ความถี่ลดเป็น .544 Hz และ clearance เพิ่ม 7.542 mm. ทุกกรณี decoder รายงาน support ต่ำสุด 3 ขา; นี่ไม่ยืนยัน dynamic stability เพราะไม่มี rigid-body dynamics, contact force, friction, CoM/support polygon, torque หรือ energy model.

ผลตรวจ `grade_submission.py`: 5/5 checks ผ่าน.

## 3. Week 4 handoff

Manual bounded input: `phi=clamp(.20+.20m,.10,.45)` rad, `stride_half=clamp(.055+.010m,.040,.070)` m.

| ช่วงเวลา | m | φ (rad) | stride_half (m) | Mean speed (m/s) | Frequency (Hz) | Min support |
|---|---:|---:|---:|---:|---:|---:|
| 0–10 s | 0 | .20 | .055 | .077632 | .625000 | 3 |
| 10–20 s | 1 | .40 | .065 | .183294 | 1.263158 | 3 |
| 20–30 s | 0 | .20 | .055 | .077387 | .625000 | 3 |

เมื่อ m กลับเป็น 0 คำสั่ง phi/stride กลับค่า baseline ทันทีตาม mapping; output oscillator และความเร็วอาจยังมี transient จาก state ก่อนหน้า. Week 4 จะใช้ hormone/receptor output แทน manual m แต่ Lab 03 ยังไม่ได้จำลอง hormone.

## 4. ข้อสรุปและข้อจำกัด

ข้อมูลสนับสนุนว่า φ เป็นตัวปรับจังหวะหลักในโมเดลนี้ ส่วน α เปลี่ยน clearance และมีผลไม่เชิงเส้นต่อ frequency. ผลความเร็วเป็นการเคลื่อนที่ที่กำหนดจาก CPG/decoder ไม่ใช่ผลของหุ่นยนต์จริงหรือการวัดแรงสัมผัส. ค่า α, φ, stride และ lift เป็น proposed course model; ไม่ใช่ค่าจาก paper หรือค่าปลอดภัยสำหรับ hardware.

หลักฐานและคำสั่งทำซ้ำ:

```powershell
py -3 grade_submission.py --student-file student_cpg.py --out results\group4_grade.json
py -3 cpg_walk_sim.py --condition all --output-dir results\group4_gait_comparison
py -3 week4_bridge.py --output-dir results\group4_week4_bridge
```

ไฟล์ผล: `results/group4_grade.json`, `results/group4_gait_comparison/conditions_summary.csv`, CSV/SVG ราย condition, `results/group4_week4_bridge/week4_bridge.csv` และ `handoff_contract.json`. `student_cpg.py` มี SO(2) simultaneous update, tripod decoder และ bounded modulation ครบ.
