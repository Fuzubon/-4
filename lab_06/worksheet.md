# ใบงาน Lab 06 — Student (กรอกแล้ว)

ชื่อ: ภูวเมศฐ์ กิตติธันยวัฒน์  
รหัสนักศึกษา: 6752500126  
กลุ่ม: 4  
ขอบเขต: ทุก trial ด้านล่างเป็น synthetic software simulation ไม่ใช่การทดสอบ lamp/robot/human จริง

## 1. Prediction และ FSM

Prediction จาก protocol (เขียนประกอบหลังได้ผลแล้ว ไม่ใช่ preregistration): C1 debounce/hysteresis น่าจะลดการสลับจาก bounce/noise เทียบ C0 โดยอาจหน่วง recognized time; `near` ควรเข้าสู่ afraid และ `fault` ต้องกลับ normal; touch ขณะ afraid ไม่ควรยกเลิก safety state.

Priority ที่ใช้กับ events ใน tick เดียวกัน: `fault > near > clear > touch > button > approach > timeout > idle`. `None` หมายถึงไม่มี transition/hold ปัจจุบัน ไม่ใช่ข้อมูลหาย.

| State \ Event | fault | near | clear | touch | button | approach | timeout | idle |
|---|---|---|---|---|---|---|---|---|
| normal | normal | afraid | normal | happy | interested | interested | None | sleepy |
| interested | normal | afraid | normal | happy | interested | interested | normal | None |
| happy | normal | afraid | normal | happy | interested | interested | normal | None |
| afraid | normal | afraid | normal | None | None | None | None | None |
| sleepy | normal | afraid | normal | happy | interested | interested | None | None |

จาก normal สามารถไป interested/happy/afraid/sleepy ได้ด้วย button/touch/near/idle ตามลำดับ; timeout จาก interested/happy กลับ normal; clear/fault ออกจาก afraid. Fault/near/clear guard ใช้ก่อน afraid hold.

`check_submission.py --contract group`: 40/40 transitions ผ่าน. ไม่แก้ sensor/output safety logic.

## 2. ผล paired synthetic trials

| Condition/seed | External inputs | Both onset | ≤1 s both | No both onset/status | Max observed latency (s) | State transitions |
|---|---:|---:|---:|---:|---:|---:|
| C0/41 | 10 | 7 | 7 | 3 | .24 | 67 |
| C1/41 | 10 | 7 | 7 | 3 | .14 | 9 |
| C0/42 | 10 | 6 | 6 | 4 | .18 | 72 |
| C1/42 | 10 | 7 | 7 | 3 | .14 | 10 |
| C0/43 | 10 | 6 | 6 | 4 | .04 | 63 |
| C1/43 | 10 | 7 | 7 | 3 | .14 | 9 |

ในชุด seed เหล่านี้ C1 มี transitions น้อยกว่าและ primary both-onset count 7/7 ทุก repeat. ตัวเลขเป็น paired synthetic replications จาก input CSV เดียวกันต่อ seed; 3 seeds ไม่ใช่ 3 independent physical trials. Missing/no onset ไม่ถูกแทนด้วย zero-latency.

## 3. ตัวอย่าง trace จาก C1/seed 41

| Input ID | Source (s) | Recognized (s) | Decision/queued (s) | Applied (s) | Motion/RGB onset (s) | Both latency (s) | Status |
|---|---:|---:|---:|---:|---:|---:|---|
| button_01 | 1.00 | 1.10 | 1.10 | 1.14 | 1.14 / 1.14 | .14 | responded |
| near_01 | 7.00 | 7.00 | 7.00 | 7.04 | 7.04 / 7.04 | .04 | responded; normal→afraid |
| touch_conflict | 7.00 | 7.06 | 7.06 | N/A | N/A | N/A | policy_held; afraid guard |
| invalid_01 | 11.00 | 11.00 | 11.00 | N/A | N/A | N/A | no_state_change; already normal |

`touch_conflict` ไม่ถูกทิ้งเงียบ ๆ: event log แสดง `policy_held` และ reason `no transition / afraid guard`. `invalid_01` มี fault event แต่ output neutral อยู่แล้ว จึง `no_state_change` และไม่สร้าง onset ใหม่. Status เหล่านี้ต่างจาก `preempted_before_apply` และ `censored_end`; N/A ไม่ใช่ latency=0.

## 4. การตีความและข้อจำกัด

C1 ลดจำนวน state transitions จาก 63–72 เป็น 9–10 ในสาม paired seeds และทั้งสอง condition มี both onset 6–7 จาก 10 sources. นี่เป็นผลของ policy/protocol ใน offline model; C1 รวม debounce/hysteresis จึงไม่แยกผลแต่ละส่วน. `both_latency_s` วัดถึง applied software pose/RGB output ไม่ใช่การเคลื่อนที่หรือแสงจริง. การยืนยัน hardware ต้องใช้ external camera/photodiode/encoder และ clock ที่สอบเทียบ.

Artifacts: `results/group4_completed/metrics.json`, `config.json`, `source_inputs_rNN.csv`, `inputs_rNN.csv`, `raw_C*_rNN.csv`, `events_C*_rNN.csv`, traces, report, source snapshot และ manifest.

```powershell
py -3 check_submission.py --contract group
py -3 lab06.py --policy student --condition all --repeats 3 --output-dir results\group4_completed
```

Debounce, thresholds, states, poses, scheduler และ bounds เป็น proposed course model; ไม่มี learning, ROS transport, linkage, torque, collision model หรือ human-subject data. ไม่ควรนำ mapping นี้ไปขับฮาร์ดแวร์โดยตรง.
