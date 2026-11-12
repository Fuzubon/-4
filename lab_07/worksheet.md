# ใบงาน Lab 07 — Seven-topic ROS2 bridge and experimental design (กรอกแล้ว)

ชื่อ: ภูวเมศฐ์ กิตติธันยวัฒน์  
รหัสนักศึกษา: 6752500126  
กลุ่ม: 4  
Policy: group transition policy ที่ผ่าน checker  
ขอบเขต: รัน offline simulation เท่านั้น; ROS 2, physical robot และ human study ยังไม่ได้ทดลอง

## 1. Architecture และ topic contract

แผน architecture: sensor inputs → interaction/FSM node → bounded servo/RGB command → output collector. ในระบบจริงต้องเพิ่ม ESP32/micro-ROS Agent/driver, hardware calibration, watchdog และวัด physical onset; สิ่งเหล่านี้ไม่ได้อยู่ใน offline runner.

| Topic | Type | หน่วย/ความหมาย | QoS |
|---|---|---|---|
| `/lamp/input/button` | `std_msgs/msg/Bool` | true/false | RELIABLE, KEEP_LAST depth 10, VOLATILE |
| `/lamp/input/touch` | `std_msgs/msg/Bool` | true/false | เหมือนกัน |
| `/lamp/input/distance` | `std_msgs/msg/Float32` | m | เหมือนกัน |
| `/lamp/interaction` | `std_msgs/msg/String` | event/state transition | เหมือนกัน |
| `/lamp/emotion` | `std_msgs/msg/String` | normal/interested/happy/afraid/sleepy | เหมือนกัน |
| `/lamp/servo_command` | `std_msgs/msg/Float32MultiArray` | rad `[tilt,extend,nod]` | เหมือนกัน |
| `/lamp/rgb_command` | `std_msgs/msg/ColorRGBA` | RGB normalized จาก Lab06 integer/255; alpha=1 | เหมือนกัน |

`extend` เป็น semantic joint ไม่ใช่ระยะเชิงเส้น. Bool/String/Float32/ColorRGBA ไม่มี Header, source identity หรือ acquisition timestamp; ค่าที่รับใหม่จึงอาจเป็น sample เก่าที่ส่งซ้ำ. ก่อน hardware ต้อง calibrate joint/servo, RGB, sample freshness, clock mapping และ error bound.

## 2. Hypothesis และ protocol

Research question: combined modeled delay/jitter/drop เปลี่ยน transport age, software both-onset latency และ missing-source count อย่างไรเมื่อเทียบ ideal transport.

Prediction จาก protocol (เขียนประกอบหลังได้ผลแล้ว ไม่ใช่ preregistration): C1 น่าจะเพิ่ม transport age/drop/missing และอาจเพิ่ม latency; C0 ควรไม่มี modeled transport delay. C1 รวม jitter และ drop จึงไม่สามารถแยก causal effect ของแต่ละอย่าง.

Expected sources ประกาศไว้ก่อนการวิเคราะห์: `button_01, touch_01, approach_01, clear_01, near_01, clear_02, button_02, touch_conflict, fault_invalid, fault_stale`; primary positive subset 7 IDs แรก ยกเว้น conflict/fault ตาม contract. ทั้ง 10 sources ยังอยู่ใน source outcomes. ใช้ paired seeds 41–43, 22 s virtual duration, dt=.02 s, scheduler=.04 s, policy/bounds เดียวกัน.

## 3. ผล 3 paired offline repeats

| Pair/seed | C0 median both latency (s) | C1 median (s) | C0/C1 mean transport age (s) | C1 received / 3303 published | C1 transport dropped | C0/C1 primary pass ≤1 s | C0/C1 primary missing |
|---|---:|---:|---:|---:|---:|---:|---:|
| 41 | .04 | .15 | .0000 / .0769 | 3031 | 257 | 7/7, 6/7 | 0, 1 |
| 42 | .06 | .14 | .0000 / .0779 | 3007 | 287 | 7/7, 6/7 | 0, 1 |
| 43 | .04 | .10 | .0000 / .0765 | 2991 | 300 | 7/7, 7/7 | 0, 0 |

เพิ่มเติม: C0 primary max both latency=.14,.14,.14 s; C1=.20,.22,.18 s. Fault ticks C0=20 ทุก seed; C1=54,81,56. State transitions C0=9,10,9; C1=17,36,17. สัญญาณที่ได้รับแต่ out-of-order และ censored มี counters แยกใน `summary.json`; ห้ามเอา published−received ทั้งหมดไปเรียกว่า transport drop.

ผลสนับสนุนว่า C1 combined stress มี mean transport age ราว .077 s และมี 0–1 primary missing ต่อ repeat เทียบ C0 ที่ไม่มี transport age และไม่มี primary missing. ทั้งนี้ C1 มี random jitter และ drop พร้อมกัน; ไม่สามารถระบุว่าปัจจัยใดทำให้ผลเปลี่ยน. Latency เป็น virtual software output onset ไม่ใช่การตอบสนองทางกายภาพ.

## 4. Missingness, clocks และแผน real-world

Baseline invalid/stale probes ถูกนับเป็น fault ticks; C1 transport stress ไม่ใช่การจำลอง reliable DDS guarantee. ต้องแยก stale acquisition จากเวลา receipt; ROS adapter ที่ไม่มี timestamp ตรวจได้เพียง receipt freshness. Delay+jitter+drop ใน C1 เป็น composite stress และไม่ตอบคำถามแยกผลแต่ละส่วน.

Offline trace มี fixture source identity/time; ROS messages จริงไม่มี Header. ห้ามจับคู่ข้าม node ด้วย ordinal หรือ payload ซ้ำโดยเดา. ต้องเพิ่ม source ID/clock correlation method/error bound และวัด physical servo/RGB onset ด้วย encoder/camera/photodiode ที่สอบเทียบ. หากไม่มี mapping ให้ source-to-physical latency เป็น N/A.

Proposal กำหนด human scenario 600 s และ physical robot/ROS plan, safety stop, calibration, counterbalancing, consent/withdrawal, timeline และ paired seeds. สถานะจริง ณ รายงานนี้: **ยังไม่ได้ทำ human scenario 600 s และยังไม่ได้ทดลอง robot/ROS**; ไม่มีการสร้างหรือประมาณผลจริงขึ้นมาแทนข้อมูล. ก่อนเริ่มต้องได้รับอนุมัติ/ผู้ดูแล, ใช้ผู้เข้าร่วมสมัครใจและ emergency stop, จำกัดพื้นที่/command, ตรวจ watchdog และหยุดเมื่อ sensor stale, command หลุด bounds, collision หรือผู้ควบคุมสั่ง.

## 5. Proposal และหลักฐานส่งงาน

`proposal.json` กรอก research question/hypothesis, AHM equation, SO(2) CPG, integration plan, C0/C1, ≥2 metrics, 3 repeats/condition, simulation + real-robot plan, 600 s human protocol, controls, clock plan, safety stop และ timeline. ส่วน ROS/robot/human เป็นแผนที่ยัง pending ไม่ใช่ผลทดลอง.

- Group policy checker: 40/40 transitions ผ่าน.
- Proposal completeness checker: ผ่าน.
- Offline run: 6 virtual trials (C0/C1 × seeds 41/42/43).
- หลักฐาน: `results/group4_completed/summary.json`, per-trial folders, `report.html`, `source_snapshot`, `manifest.json`.

```powershell
py -3 check_submission.py --contract group
py -3 check_proposal.py proposal.json
py -3 offline_lab.py --condition all --repeats 3 --output-dir results\group4_completed
```

ค่าขนส่ง, policy, poses และ timing เป็น proposed course model. ห้ามเรียก command onset ว่า physical latency หรืออ้างว่าผลนี้ยืนยันความปลอดภัย/ประสิทธิภาพหุ่นยนต์.
