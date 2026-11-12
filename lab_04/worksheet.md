# ใบงาน Lab 04 — Artificial Hormone Mechanism (กรอกแล้ว)

ชื่อ: ภูวเมศฐ์ กิตติธันยวัฒน์  
รหัสนักศึกษา: 6752500126  
กลุ่ม: 4  
ขอบเขต: proposed course model ใน simulator; ไม่มีการทดลองกับหุ่นยนต์จริง

## A. กลไกและ prediction

`S → production P; H_old → clearance C และ receptor R_old → binding B; H_new → R_new → bounded phi/stride`. Prediction จากสมการ (เขียนประกอบหลังได้ผลแล้ว ไม่ใช่ preregistration): เพิ่ม production น่าจะเพิ่ม AUC/ทำให้อิ่มตัวเร็วขึ้น; ลด clearance น่าจะทำให้ recovery ช้าลง; ตัด binding น่าจะเพิ่ม AUC/recovery; direct C0 ไม่มีสถานะ H. ค่า H มี upper bound 1 จึงอาจทำให้ peak ของหลาย condition เท่ากัน.

เป็น course model แบบ Euler:

```text
R_old = clamp((H_old - H_min)/(H_max - H_min), 0, 1)
P = k_prod*S; C = k_clear*H_old; B = k_bind*R_old
H_raw = H_old + dt*(P-C-B)
H_new = clamp(H_raw,0,1); R_new = receptor(H_new)
phi = clamp(.20+.20*R_new,.10,.45)
stride_half = clamp(.055+.010*R_new,.040,.070)
```

ตัวอย่าง receptor: `H=.2, H_min=.1, H_max=.5` ให้ `R=.25`; ค่านอกช่วงถูก clamp เป็น 0/1 และ range ไม่ถูกต้อง/nonfinite ถูกปฏิเสธ.

## B. คำนวณสอง update แรก

สำหรับ C1: `dt=.05`, `k_prod=.8`, `k_clear=.6`, `k_bind=.2`, `S=1`.

| input time (s) | state time (s) | P | C | B | H_raw | H_new | R_new | φ (rad) | stride_half (m) |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 10.00 | 10.05 | .8000 | .0000 | .0000 | .0400 | .0400 | .0400 | .20800 | .055400 |
| 10.05 | 10.10 | .8000 | .0240 | .0080 | .0784 | .0784 | .0784 | .21568 | .055784 |

`input_time_s` คือเวลาต้น interval ส่วน `time_s` คือเวลาหลัง update; แถวเวลา 10.00 ใช้ stimulus ที่ 10.00 และสร้าง state เวลา 10.05.

## C. Controlled comparison

| Condition | peak H | AUC H (normalized H·s) | latency (s) | rise 10–90% (s) | recovery (s) | upper clamp fraction | phi TV (rad) |
|---|---:|---:|---:|---:|---:|---:|---:|
| C0 direct | N/A | N/A | .05 | 0.00 | .05 | N/A | .400000 |
| C1 baseline | .999715 | 9.999644 | .15 | 2.70 | 2.85 | .0000 | .399829 |
| C2 production สูง | 1.000000 | 10.672410 | .10 | 1.05 | 2.85 | .2900 | .399943 |
| C3 clearance ต่ำ | 1.000000 | 11.389145 | .15 | 1.45 | 5.10 | .2733 | .397890 |
| C4 binding=0 | 1.000000 | 10.754720 | .15 | 1.70 | 3.80 | .2583 | .399548 |

C3 ฟื้นช้ากว่า C1 `5.10−2.85=2.25 s`. C2 และ C3 peak เท่ากับ 1 เพราะ bounded state อิ่มตัว; AUC, rise, recovery และ clamp fraction แยกระบบได้ดีกว่า peak อย่างเดียว. C0 ไม่มี H state จึงไม่ควรกรอก peak/AUC เป็นศูนย์. C0 เป็น direct path; latency .05 s คือความละเอียด post-update ของ log ไม่ใช่ hardware delay. TV ต่ำ/สูงเพียงค่าเดียวไม่พิสูจน์คุณภาพ gait.

## D. Extreme inputs และ fault

- `zero`: S=0 ตลอด; H คง baseline 0.
- `one`: S=1 ตลอด; H ถูกจำกัดไม่เกิน 1.
- `spike`: S=1 หนึ่ง sample (.05 s) แล้วกลับ 0; เป็น pulse สั้น ไม่ใช่ sustained stimulus.
- `fault`: มี invalid input 1 ครั้งที่ input_time 15.00 s; fault row จบ state ที่ 15.05 s ด้วย `H=R=0`, `phi=.20`, `stride=.055`. Update 15.05→15.10 s เริ่มสะสมใหม่ ได้ H=.04, R=.04.

Fallback/reset ทำก่อนคำนวณ command ของ interval fault ตาม software policy. มันไม่แทน emergency stop, sensor diagnostics, actuator bounds หรือ hardware safety assessment.

## E. สรุปและหลักฐาน

ผลสนับสนุนว่าการเปลี่ยน production/clearance/binding เปลี่ยน transient และ AUC; การ clamp ทำให้ peak อย่างเดียวแยก C2/C3 ไม่ได้. ทั้งหมดเป็น deterministic simulation และไม่ได้เชื่อม CPG/body motion ใน Lab04.

`check_submission.py`: 13/13 cases ผ่าน. ไฟล์ผล: `results/group4_comparison/metrics.json`, `report.html`, CSV และ plots; รวม extreme runs `results/group4_zero`, `group4_one`, `group4_spike`, `group4_fault`. `student_hormone.py` ใช้ค่าเก่า P/C/B ก่อนคำนวณ H ใหม่และตรวจ invalid stimulus.

```powershell
py -3 check_submission.py --student-file student_hormone.py
py -3 lab04.py --controller-source student --condition all --profile step --output-dir results\group4_comparison
py -3 lab04.py --controller-source student --condition C1 --profile fault --output-dir results\group4_fault
```

อัตรา, bounds และ mapping เป็น proposed course model. ผลนี้ไม่ใช่ reproduction หรือ validation ของสมการ/ผลหุ่นยนต์ใน paper และไม่พิสูจน์ความปลอดภัยหรือ dynamic stability.
