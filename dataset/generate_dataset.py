import json
import os

# Define 50 rich, realistic medical case templates covering multiple specialties
cases = [
    {
        "id": "MED-001",
        "category": "Cardiology",
        "text": (
            "PATIENT DISCHARGE SUMMARY\n"
            "Patient: Robert Evans | Age: 58 | Gender: Male | DOB: 1968-04-12\n"
            "Admission Date: 2026-07-10 | Discharge Date: 2026-07-14\n"
            "Chief Complaint: Progressive exertional chest tightness and shortness of breath over 3 days.\n"
            "Vitals on Admission: BP 158/96 mmHg, HR 92 bpm, RR 18/min, SpO2 96% on room air, Temp 98.4 F.\n"
            "Diagnostic Workup: EKG showed sinus rhythm with T-wave inversions in leads V4-V6. Cardiac Troponin I was elevated at 0.18 ng/mL (normal <0.04 ng/mL). Echocardiogram demonstrated preserved EF of 55% with mild left ventricular hypertrophy.\n"
            "Primary Diagnosis: Non-ST-elevation myocardial infarction (NSTEMI) and Essential [[DIAG|Hypertension]].\n"
            "Procedures Performed: Diagnostic [[PROC|coronary angiography]] on 2026-07-11 showed 70% mid-LAD stenosis; successfully treated with drug-eluting [[PROC|stent placement]].\n"
            "Medications Prescribed:\n"
            "1. [[MED|Aspirin]] 81 mg oral daily.\n"
            "2. [[MED|Clopidogrel]] 75 mg oral daily for 12 months.\n"
            "3. [[MED|Atorvastatin]] 80 mg oral at bedtime.\n"
            "4. [[MED|Metoprolol Succinate]] 50 mg oral daily.\n"
            "Follow-up: Cardiology clinic appointment in 2 weeks (2026-07-28). Cardiac rehab orientation scheduled for next Monday.\n"
            "Urgency Level: Urgent."
        ),
        "evaluations": [
            {
                "q_id": 1,
                "question": "What is the patient's identity, age, and chief complaint?",
                "ground_truth": "Robert Evans, a 58-year-old male, presented with progressive exertional chest tightness and shortness of breath over 3 days."
            },
            {
                "q_id": 2,
                "question": "What were the vital signs and key diagnostic lab findings on admission?",
                "ground_truth": "BP was 158/96 mmHg, HR 92 bpm, SpO2 96%. EKG showed T-wave inversions in leads V4-V6 and Troponin I was elevated at 0.18 ng/mL."
            },
            {
                "q_id": 3,
                "question": "What primary diagnoses were confirmed for this patient?",
                "ground_truth": "Non-ST-elevation myocardial infarction (NSTEMI) and Essential Hypertension."
            },
            {
                "q_id": 4,
                "question": "What medications and dosages were prescribed at discharge?",
                "ground_truth": "Aspirin 81 mg daily, Clopidogrel 75 mg daily for 12 months, Atorvastatin 80 mg at bedtime, and Metoprolol Succinate 50 mg daily."
            },
            {
                "q_id": 5,
                "question": "What is the designated urgency level and when is the follow-up appointment?",
                "ground_truth": "Urgency level is Urgent; follow-up is scheduled at the Cardiology clinic in 2 weeks on 2026-07-28."
            }
        ]
    },
    {
        "id": "MED-002",
        "category": "Endocrinology",
        "text": (
            "OUTPATIENT CLINICAL NOTE\n"
            "Patient: Elena Rostova | Age: 46 | Gender: Female | DOB: 1980-09-22\n"
            "Date of Visit: 2026-08-05\n"
            "Chief Complaint: Polyuria, polydipsia, fatigue, and unintentional 6 kg weight loss over the past 2 months.\n"
            "Vitals: BP 124/78 mmHg, HR 76 bpm, BMI 31.4 kg/m2, Temp 98.6 F.\n"
            "Laboratory Results: Fasting plasma glucose 210 mg/dL, HbA1c 9.4%, Serum Creatinine 0.8 mg/dL, eGFR >90 mL/min/1.73m2. Urine microalbumin-to-creatinine ratio 18 mcg/mg (normal).\n"
            "Assessment: Newly diagnosed [[DIAG|Type 2 Diabetes Mellitus]] with inadequate glycemic control, [[DIAG|Obesity Class I]].\n"
            "Plan & Management:\n"
            "1. Initiate [[MED|Metformin]] 500 mg oral twice daily with meals, titrate to 1000 mg twice daily after 2 weeks.\n"
            "2. Initiate [[MED|Empagliflozin]] 10 mg oral once daily in the morning.\n"
            "3. Referred to certified diabetes educator for nutritional counseling and glucometer training.\n"
            "4. Prescribed daily home blood glucose monitoring before breakfast and 2 hours post-dinner.\n"
            "Follow-up: Repeat HbA1c and comprehensive metabolic panel in 3 months (2026-11-05).\n"
            "Urgency Level: Routine."
        ),
        "evaluations": [
            {
                "q_id": 1,
                "question": "Who is the patient and what are her presenting symptoms?",
                "ground_truth": "Elena Rostova, a 46-year-old female, presenting with polyuria, polydipsia, fatigue, and an unintentional 6 kg weight loss over 2 months."
            },
            {
                "q_id": 2,
                "question": "What were the significant laboratory results recorded during the visit?",
                "ground_truth": "Fasting plasma glucose was 210 mg/dL, HbA1c was 9.4%, serum creatinine was 0.8 mg/dL, and urine microalbumin ratio was normal at 18 mcg/mg."
            },
            {
                "q_id": 3,
                "question": "What is the clinical assessment/diagnosis for Elena Rostova?",
                "ground_truth": "Newly diagnosed Type 2 Diabetes Mellitus with inadequate glycemic control and Class I Obesity."
            },
            {
                "q_id": 4,
                "question": "Which pharmaceutical treatments and dosages were initiated?",
                "ground_truth": "Metformin 500 mg twice daily (titrated to 1000 mg twice daily after 2 weeks) and Empagliflozin 10 mg once daily."
            },
            {
                "q_id": 5,
                "question": "What is the urgency level and the scheduled follow-up interval?",
                "ground_truth": "Urgency level is Routine; repeat HbA1c and lab follow-up in 3 months on 2026-11-05."
            }
        ]
    },
    {
        "id": "MED-003",
        "category": "Pulmonology",
        "text": (
            "EMERGENCY DEPARTMENT CONSULTATION REPORT\n"
            "Patient: Marcus Thorne | Age: 34 | Gender: Male | DOB: 1992-01-15\n"
            "Encounter Date: 2026-08-14\n"
            "Chief Complaint: Acute shortness of breath, audible expiratory wheezing, and chest tightness unresponsive to home albuterol.\n"
            "Vitals: BP 138/86 mmHg, HR 112 bpm (tachycardia), RR 28/min (tachypnea), SpO2 90% on room air, improved to 95% on 2L nasal cannula.\n"
            "Physical Exam: Bilateral diffuse expiratory wheezes, accessory muscle use observed. Peak Expiratory Flow (PEF) 210 L/min (40% of predicted baseline).\n"
            "Chest X-Ray: Hyperinflation without focal infiltrates, consolidation, or pneumothorax.\n"
            "Diagnosis: Severe acute exacerbation of [[DIAG|Bronchial Asthma]].\n"
            "Emergency Treatment Given:\n"
            "1. Continuous nebulization with [[MED|Albuterol]] 5 mg and [[MED|Ipratropium Bromide]] 0.5 mg.\n"
            "2. IV [[MED|Methylprednisolone]] 60 mg single dose.\n"
            "Discharge Prescriptions:\n"
            "1. [[MED|Prednisone]] 40 mg oral once daily for 5 days (no taper needed).\n"
            "2. [[MED|Fluticasone/Salmeterol]] (Advair Diskus 250/50 mcg) 1 inhalation twice daily.\n"
            "3. [[MED|Albuterol HFA Inhaler]] 2 puffs every 4-6 hours as needed for rescue.\n"
            "Follow-up: Primary care or Pulmonologist within 48 to 72 hours (by 2026-08-17).\n"
            "Urgency Level: Urgent."
        ),
        "evaluations": [
            {
                "q_id": 1,
                "question": "What is the patient's name, age, and reason for visiting the emergency department?",
                "ground_truth": "Marcus Thorne, 34-year-old male, visited due to acute shortness of breath, expiratory wheezing, and chest tightness unresponsive to his home albuterol."
            },
            {
                "q_id": 2,
                "question": "What were the patient's respiratory rate, oxygen saturation, and peak flow findings?",
                "ground_truth": "Respiratory rate was 28/min, SpO2 was 90% on room air (improved to 95% on 2L O2), and PEF was 210 L/min (40% of predicted)."
            },
            {
                "q_id": 3,
                "question": "What was the official diagnosis and what did the chest X-ray reveal?",
                "ground_truth": "Diagnosis was severe acute exacerbation of Bronchial Asthma; Chest X-ray showed hyperinflation without infiltrates or pneumothorax."
            },
            {
                "q_id": 4,
                "question": "What medications were prescribed for the patient upon discharge?",
                "ground_truth": "Prednisone 40 mg daily for 5 days, Fluticasone/Salmeterol (250/50 mcg) 1 puff twice daily, and Albuterol HFA 2 puffs every 4-6 hours PRN."
            },
            {
                "q_id": 5,
                "question": "What is the urgency category and timeframe for follow-up?",
                "ground_truth": "Urgency is Urgent; follow-up is required within 48 to 72 hours (by 2026-08-17)."
            }
        ]
    },
    {
        "id": "MED-004",
        "category": "Gastroenterology",
        "text": (
            "GASTROENTEROLOGY PROCEDURE & CONSULT REPORT\n"
            "Patient: Priya Patel | Age: 52 | Gender: Female | DOB: 1974-11-03\n"
            "Procedure Date: 2026-07-29\n"
            "Chief Complaint: Recurrent epigastric burning pain, postprandial fullness, and nocturnal reflux over 6 months.\n"
            "Vitals: BP 118/74 mmHg, HR 68 bpm, RR 14/min, SpO2 99%.\n"
            "Procedure: Esophagogastroduodenoscopy ([[PROC|EGD]] / Upper Endoscopy).\n"
            "Endoscopy Findings: Severe distal esophageal mucosal erythema with linear ulcerations <5mm (Los Angeles Grade B [[DIAG|Esophagitis]]). 1.2 cm benign-appearing antral ulcer with clean base. Biopsies taken for CLOtest ([[DIAG|Helicobacter pylori]] urease test) returned POSITIVE.\n"
            "Assessment: [[DIAG|H. pylori-positive Peptic Ulcer Disease]] and Grade B [[DIAG|Gastroesophageal Reflux Disease (GERD)]].\n"
            "Quadruple Eradication Therapy Prescribed (14-day course):\n"
            "1. [[MED|Bismuth Subsalicylate]] 524 mg oral four times daily.\n"
            "2. [[MED|Metronidazole]] 500 mg oral three times daily.\n"
            "3. [[MED|Tetracycline]] 500 mg oral four times daily.\n"
            "4. [[MED|Omeprazole]] 40 mg oral twice daily before meals (continue 40 mg daily for 6 weeks after antibiotic course).\n"
            "Follow-up: Stool H. pylori antigen test 4 weeks post-antibiotic completion (2026-09-15) to confirm eradication.\n"
            "Urgency Level: Routine."
        ),
        "evaluations": [
            {
                "q_id": 1,
                "question": "What are the patient demographics and symptoms leading to the GI evaluation?",
                "ground_truth": "Priya Patel, a 52-year-old female, presented with 6 months of recurrent epigastric burning, postprandial fullness, and nocturnal acid reflux."
            },
            {
                "q_id": 2,
                "question": "What endoscopic findings and biopsy test results were noted?",
                "ground_truth": "EGD showed LA Grade B Esophagitis and a 1.2 cm antral ulcer; CLOtest for Helicobacter pylori was positive."
            },
            {
                "q_id": 3,
                "question": "What were the definitive diagnoses given?",
                "ground_truth": "H. pylori-positive Peptic Ulcer Disease and Grade B Gastroesophageal Reflux Disease (GERD)."
            },
            {
                "q_id": 4,
                "question": "What medications constitute the prescribed eradication regimen?",
                "ground_truth": "Bismuth Subsalicylate 524 mg QID, Metronidazole 500 mg TID, Tetracycline 500 mg QID, and Omeprazole 40 mg BID for 14 days."
            },
            {
                "q_id": 5,
                "question": "What is the follow-up plan and testing required to verify eradication?",
                "ground_truth": "Urgency is Routine; stool H. pylori antigen test is scheduled 4 weeks after antibiotic completion on 2026-09-15."
            }
        ]
    },
    {
        "id": "MED-005",
        "category": "Neurology",
        "text": (
            "NEUROLOGY CLINIC CONSULTATION NOTE\n"
            "Patient: Arthur Pendelton | Age: 67 | Gender: Male | DOB: 1959-05-18\n"
            "Date: 2026-08-02\n"
            "Chief Complaint: 8-month history of progressive resting tremor in the right hand, bradykinesia, and micrographia.\n"
            "Vitals: BP 132/82 mmHg, HR 72 bpm, RR 16/min, Temp 98.2 F.\n"
            "Neurological Examination: Asymmetric 4-5 Hz resting tremor of right upper extremity, lead-pipe rigidity in right wrist and elbow, reduced right arm swing during ambulation, subtle postural instability. Mental status intact (MoCA score 28/30).\n"
            "Brain MRI (with contrast): Age-appropriate cerebral atrophy, no focal ischemic lesions, mass effect, or normal pressure hydrocephalus.\n"
            "Impression: Idiopathic [[DIAG|Parkinson's Disease]] (Hoehn and Yahr Stage I).\n"
            "Medications Prescribed:\n"
            "1. [[MED|Carbidopa/Levodopa]] (Sinemet 25/100 mg) 1/2 tablet oral three times daily for 1 week, then 1 full tablet three times daily with meals.\n"
            "2. [[MED|Rasagiline]] 0.5 mg oral once daily.\n"
            "Non-Pharmacologic: Referral to physical therapy for gait training and PWR! (Parkinson Wellness Recovery) exercise program.\n"
            "Follow-up: Clinical evaluation in 6 weeks (2026-09-15) to evaluate medication response and motor symptom control.\n"
            "Urgency Level: Routine."
        ),
        "evaluations": [
            {
                "q_id": 1,
                "question": "What is the patient's demographic profile and presenting motor symptoms?",
                "ground_truth": "Arthur Pendelton, 67-year-old male, presented with an 8-month history of right-hand resting tremor, bradykinesia, and micrographia."
            },
            {
                "q_id": 2,
                "question": "What physical exam and brain MRI findings were recorded?",
                "ground_truth": "Asymmetric 4-5 Hz resting tremor, right upper extremity lead-pipe rigidity, decreased arm swing, and MoCA 28/30. MRI showed age-appropriate atrophy without acute lesions."
            },
            {
                "q_id": 3,
                "question": "What is the primary neurological diagnosis and disease stage?",
                "ground_truth": "Idiopathic Parkinson's Disease (Hoehn and Yahr Stage I)."
            },
            {
                "q_id": 4,
                "question": "What medications were initiated and how is the primary drug titrated?",
                "ground_truth": "Carbidopa/Levodopa 25/100 mg (1/2 tab TID for 1 week, then 1 tab TID) and Rasagiline 0.5 mg daily."
            },
            {
                "q_id": 5,
                "question": "What is the urgency level and the follow-up timeline?",
                "ground_truth": "Urgency is Routine; follow-up in neurology clinic in 6 weeks on 2026-09-15."
            }
        ]
    }
]

# Generate remaining 45 clinical profiles to reach exactly 50 reports
clinical_templates = [
    # (Category, Name, Age, Gender, Complaint, Vitals, Labs/Tests, Diagnosis, Meds, Followup, Urgency)
    ("Orthopedics", "Dorothy Miller", 62, "Female", "Chronic right knee pain and stiffness exacerbated by weight bearing over 1 year",
     "BP 130/80 mmHg, HR 74 bpm, BMI 29.1", "Weight-bearing bilateral knee X-rays: medial compartment joint space narrowing, subchondral sclerosis, and osteophyte formation",
     "Severe [[DIAG|Osteoarthritis]] of the right knee",
     "[[MED|Meloxicam]] 15 mg oral once daily, [[MED|Acetaminophen]] 500 mg TID PRN, [[MED|Omeprazole]] 20 mg daily for GI protection",
     "Orthopedic surgery consult in 4 weeks (2026-09-29) to discuss total knee arthroplasty", "Routine"),

    ("Nephrology", "James Wilson", 59, "Male", "Routine screening showing declining kidney function, bilateral ankle edema, and frothy urine",
     "BP 152/92 mmHg, HR 80 bpm, Weight 88 kg", "Serum Creatinine 2.1 mg/dL (baseline 1.4), eGFR 34 mL/min/1.73m2, Spot urine protein/creatinine ratio 1200 mg/g",
     "Stage 3b [[DIAG|Chronic Kidney Disease (CKD)]] secondary to Diabetic Nephropathy",
     "[[MED|Losartan]] 50 mg oral once daily, [[MED|Dapagliflozin]] 10 mg oral once daily, [[MED|Furosemide]] 20 mg oral every morning",
     "Repeat renal function panel and nephrology follow-up in 4 weeks (2026-09-30)", "Urgent"),

    ("Infectious Disease", "Amina Al-Mansoor", 29, "Female", "High fever, productive cough with rust-colored sputum, and right-sided pleuritic chest pain for 4 days",
     "BP 110/70 mmHg, HR 104 bpm, RR 22/min, Temp 102.3 F, SpO2 93% room air", "WBC count 16,800/mcL with 88% neutrophils. Chest X-Ray shows dense right middle lobe consolidation",
     "Community-Acquired [[DIAG|Lobar Pneumonia]] (likely Streptococcus pneumoniae)",
     "[[MED|Amoxicillin/Clavulanate]] 875/125 mg oral twice daily for 7 days, [[MED|Azithromycin]] 500 mg day 1 then 250 mg daily for 4 days",
     "Clinic reassessment in 48 hours (2026-09-02); seek ER if SpO2 drops below 92%", "Urgent"),

    ("Rheumatology", "Claire Dupont", 38, "Female", "Symmetrical swelling and morning stiffness in bilateral wrists, MCP, and PIP joints lasting >2 hours",
     "BP 116/72 mmHg, HR 70 bpm, Temp 98.7 F", "Rheumatoid Factor (RF) positive at 84 IU/mL, Anti-CCP positive at >200 U/mL, ESR 48 mm/hr, CRP 24 mg/L",
     "Seropositive [[DIAG|Rheumatoid Arthritis]]",
     "[[MED|Methotrexate]] 15 mg oral once weekly, [[MED|Folic Acid]] 1 mg oral daily except MTX days, [[MED|Prednisone]] 10 mg daily taper",
     "Rheumatology follow-up with CBC and liver panel in 6 weeks (2026-10-12)", "Routine"),

    ("Psychiatry", "David Kim", 41, "Male", "Persistent low mood, anhedonia, early morning awakening, and severe concentration deficit for 3 months",
     "BP 122/78 mmHg, HR 75 bpm, PHQ-9 score 19 (Moderately Severe Depression)", "Normal thyroid panel (TSH 1.8 mIU/L), Vitamin B12 450 pg/mL, negative toxic screen",
     "Major [[DIAG|Depressive Disorder]], single episode, severe without psychotic features",
     "[[MED|Escitalopram]] 10 mg oral once daily in the morning, titrate to 20 mg after 2 weeks; [[MED|Trazodone]] 50 mg at bedtime PRN insomnia",
     "Psychiatric review in 2 weeks (2026-09-14) to assess tolerability and suicidal ideation", "Routine"),

    ("Dermatology", "Sarah Jenkins", 24, "Female", "Severe cystic facial and back acne lesions unresponsive to topical retinoids and oral doxycycline",
     "BP 112/68 mmHg, HR 66 bpm, BMI 21.5", "Baseline liver enzymes normal (ALT 18, AST 20 U/L), fasting lipid panel normal, serum pregnancy test negative (two sequential tests)",
     "Severe Recalcitrant Nodulocystic [[DIAG|Acne Vulgaris]]",
     "[[MED|Isotretinoin]] 40 mg oral once daily with high-fat meal (enrolled in iPLEDGE program), [[MED|Aquaphor]] topical balm PRN",
     "Monthly follow-up in 30 days (2026-09-30) for repeat pregnancy test, hepatic enzymes, and fasting triglycerides", "Routine"),

    ("Urology", "Harold Vance", 71, "Male", "Nocturia 4-5 times per night, weak urinary stream, hesitancy, and feeling of incomplete bladder emptying",
     "BP 142/84 mmHg, HR 72 bpm", "Digital rectal exam: enlarged, smooth, non-tender prostate ~45 grams. Serum PSA 2.8 ng/mL (age-appropriate). Post-void residual 140 mL",
     "Benign [[DIAG|Prostatic Hyperplasia (BPH)]] with moderate lower urinary tract symptoms",
     "[[MED|Tamsulosin]] 0.4 mg oral once daily 30 minutes after the same meal, [[MED|Finasteride]] 5 mg oral once daily",
     "Urology clinic visit and flow rate re-measurement in 3 months (2026-12-01)", "Routine"),

    ("Hematology", "Maria Santos", 31, "Female", "Extreme fatigue, brittle spoon-shaped nails (koilonychia), dizziness, and craving for ice chips (pica)",
     "BP 104/62 mmHg, HR 98 bpm, conjunctival pallor noted", "Hemoglobin 7.9 g/dL, Hematocrit 25%, MCV 68 fL (microcytic), Serum Ferritin 6 ng/mL, Iron saturation 8%",
     "Severe [[DIAG|Iron Deficiency Anemia]] secondary to heavy menstrual bleeding (menorrhagia)",
     "[[MED|Ferrous Sulfate]] 325 mg (65 mg elemental iron) oral once daily with Vitamin C 500 mg on empty stomach",
     "Repeat CBC and reticulocyte count in 4 weeks (2026-09-28); gynecology referral for pelvic ultrasound", "Routine"),

    ("Ophthalmology", "George Washington Lee", 66, "Male", "Gradual painless deterioration of peripheral vision in both eyes and difficulty adjusting in dim light",
     "BP 136/82 mmHg, HR 68 bpm", "Intraocular pressure (IOP) 26 mmHg OD, 28 mmHg OS. Pachymetry average 540 um. Humphrey visual field shows superior arcuate scotoma",
     "Primary Open-Angle [[DIAG|Glaucoma]] bilateral",
     "[[MED|Latanoprost 0.005% ophthalmic solution]] 1 drop both eyes every evening at bedtime, [[MED|Timolol 0.5% drops]] 1 drop BID",
     "IOP check and visual field follow-up in 4 weeks (2026-09-28)", "Routine"),

    ("Cardiology", "Teresa Cooper", 73, "Female", "Sudden onset palpitations, fatigue, and lightheadedness lasting 6 hours prior to arrival",
     "BP 118/76 mmHg, HR 134 bpm (irregularly irregular), RR 18/min, SpO2 97%", "EKG: Atrial fibrillation with rapid ventricular response (RVR). TTE: Left atrial enlargement (4.4 cm), preserved EF 50%. CHA2DS2-VASc score = 4",
     "Paroxysmal [[DIAG|Atrial Fibrillation]] with RVR, Essential [[DIAG|Hypertension]]",
     "[[MED|Diltiazem]] 180 mg CD oral once daily (rate control), [[MED|Apixaban]] 5 mg oral twice daily (anticoagulation stroke prevention)",
     "Electrophysiology consultation in 2 weeks (2026-09-14); Holter monitor ordered", "Urgent"),

    ("Endocrinology", "Nathaniel Brown", 49, "Male", "Cold intolerance, 8 kg unexplained weight gain, chronic constipation, and dry skin over past 6 months",
     "BP 128/84 mmHg, HR 56 bpm (bradycardia), Temp 97.4 F", "Serum TSH 14.2 mIU/L (markedly elevated, normal 0.4-4.0), Free T4 0.5 ng/dL (low), Anti-TPO antibodies positive at 340 IU/mL",
     "Primary [[DIAG|Hypothyroidism]] secondary to Hashimoto Thyroiditis",
     "[[MED|Levothyroxine]] 75 mcg oral once daily in the morning 30-60 minutes before breakfast with full glass of water",
     "Repeat serum TSH and Free T4 in 6 to 8 weeks (2026-10-20) to adjust dosage", "Routine"),

    ("Gastroenterology", "Siddharth Rao", 36, "Male", "Intermittent cramping lower abdominal pain, 5-6 episodes of bloody diarrhea daily, and tenesmus for 4 weeks",
     "BP 114/72 mmHg, HR 86 bpm, Temp 99.1 F, Abdominal exam: diffuse left lower quadrant tenderness", "Stool cultures negative for C. diff, Salmonella, Shigella. Fecal Calprotectin elevated at 620 mcg/g. Colonoscopy shows continuous mucosal inflammation from rectum to splenic flexure",
     "Moderate [[DIAG|Ulcerative Colitis]] (Left-sided colitis)",
     "[[MED|Mesalamine]] 4.8 g oral once daily plus [[MED|Mesalamine Enema]] 4 g rectal suspension nightly, [[MED|Prednisone]] 40 mg daily taper over 8 weeks",
     "Gastroenterology clinic review in 3 weeks (2026-09-21) to evaluate mucosal response", "Urgent"),

    ("Neurology", "Chloe Bennett", 28, "Female", "Unilateral pulsating headache on left side, photophobia, phonophobia, and nausea lasting 18 hours",
     "BP 118/74 mmHg, HR 78 bpm, Neuro exam unremarkable with normal cranial nerves", "Brain CT non-contrast negative for acute intracranial pathology. Meets ICHD-3 criteria for migraine with visual aura",
     "Acute [[DIAG|Migraine with Aura]], episodic",
     "[[MED|Sumatriptan]] 100 mg oral at onset of headache (may repeat once after 2 hours if needed, max 200 mg/24h), [[MED|Ondansetron]] 4 mg ODT PRN nausea, [[MED|Propranolol]] 40 mg daily for prophylaxis",
     "Headache clinic follow-up in 8 weeks (2026-10-26) with headache diary", "Routine"),

    ("Allergy & Immunology", "Liam O'Connor", 19, "Male", "Severe seasonal sneezing, rhinorrhea, nasal congestion, and bilateral conjunctival pruritus during spring/summer",
     "BP 116/70 mmHg, HR 64 bpm", "Skin prick test positive for Timothy grass, birch pollen, and house dust mites. Nasal exam: pale, boggy, bluish turbinates",
     "Severe Moderate-to-Severe [[DIAG|Allergic Rhinitis]] and Allergic Rhinoconjunctivitis",
     "[[MED|Fluticasone Propionate nasal spray]] 50 mcg (2 sprays per nostril daily), [[MED|Cetirizine]] 10 mg oral once daily, [[MED|Olopatadine 0.2% eye drops]] 1 drop daily PRN",
     "Immunology follow-up in 3 months (2026-11-30) to evaluate candidate eligibility for allergen immunotherapy (allergy shots)", "Routine"),

    ("Infectious Disease", "Grace Hopper", 68, "Female", "Painful vesicular rash in a unilateral dermatomal distribution along the right T6 thoracic band for 3 days",
     "BP 134/80 mmHg, HR 74 bpm, Temp 99.0 F", "Dermatologic exam: grouped clear vesicles on an erythematous base along right T6 dermatome, not crossing midline. Tzanck smear positive",
     "Acute [[DIAG|Herpes Zoster (Shingles)]] without ophthalmic involvement",
     "[[MED|Valacyclovir]] 1000 mg oral three times daily for 7 days, [[MED|Gabapentin]] 300 mg oral at bedtime for neuropathic pain control, [[MED|Calamine lotion]] topically PRN",
     "Primary care visit in 10 days (2026-09-10); monitor for post-herpetic neuralgia", "Routine"),

    ("Cardiology", "Frank Sinatra Miller", 64, "Male", "Bilateral pedal edema (2+ pitting), paroxysmal nocturnal dyspnea, and orthopnea requiring 3 pillows",
     "BP 146/88 mmHg, HR 82 bpm, RR 20/min, SpO2 94% on room air. JVP elevated at 9 cm", "Serum NT-proBNP 2450 pg/mL (normal <300). Transthoracic Echo: LVEF reduced at 32%, diffuse hypokinesis",
     "Heart Failure with Reduced Ejection Fraction ([[DIAG|HFrEF]] Stage C, NYHA Class III)",
     "[[MED|Sacubitril/Valsartan (Entresto)]] 24/26 mg oral twice daily, [[MED|Carvedilol]] 3.125 mg oral twice daily, [[MED|Spironolactone]] 25 mg oral daily, [[MED|Furosemide]] 40 mg oral twice daily",
     "Heart Failure bridge clinic appointment in 7 days (2026-09-07) for weight check and electrolyte panel", "Urgent"),

    ("Pulmonology", "Walter White", 61, "Male", "40 pack-year smoking history, progressive exertional dyspnea, and chronic productive morning cough for 2 years",
     "BP 132/86 mmHg, HR 80 bpm, SpO2 91% on room air", "Spirometry post-bronchodilator: FEV1/FVC ratio 0.58 (confirming persistent airflow limitation), FEV1 52% of predicted (GOLD 2B)",
     "Chronic Obstructive Pulmonary Disease ([[DIAG|COPD]] GOLD Grade 2 Group B), chronic [[DIAG|Nicotine Dependence]]",
     "[[MED|Tiotropium Bromide (Spiriva Respimat)]] 2.5 mcg (2 puffs once daily), [[MED|Formoterol/Budesonide]] 160/4.5 mcg 2 puffs twice daily, [[MED|Nicotine Patch]] 21 mg/24h",
     "Pulmonary rehab referral and repeat spirometry in 3 months (2026-11-30)", "Routine"),

    ("Endocrinology", "Fatima Zahra", 35, "Female", "Weight loss, heat intolerance, anxiety, tremors, and bulging eyes (proptosis) for past 3 months",
     "BP 142/76 mmHg, HR 108 bpm (resting sinus tachycardia), Temp 98.9 F", "TSH <0.01 mIU/L (suppressed), Free T4 3.4 ng/dL (elevated), Thyroid-stimulating immunoglobulin (TSI) positive at 380% baseline. Radioactive iodine uptake: diffuse elevated uptake",
     "Hyperthyroidism secondary to [[DIAG|Graves' Disease]], mild [[DIAG|Thyroid Eye Disease]]",
     "[[MED|Methimazole]] 20 mg oral once daily, [[MED|Atenolol]] 50 mg oral once daily for adrenergic symptom control",
     "Endocrinology follow-up with CBC (monitor agranulocytosis) and free thyroid panel in 4 weeks (2026-09-28)", "Urgent"),

    ("Orthopedics", "Tyler Durden", 27, "Male", "Audible pop and sudden knee buckling while pivoting during a soccer match 24 hours ago, accompanied by rapid joint effusion",
     "BP 120/75 mmHg, HR 72 bpm", "Physical exam: positive Lachman test with soft end-point, positive Anterior Drawer test. MRI right knee confirms complete tear of the anterior cruciate ligament (ACL) and minor medial meniscus fraying",
     "Complete right [[DIAG|Anterior Cruciate Ligament (ACL) Tear]] and medial [[DIAG|Meniscus Injury]]",
     "[[MED|Ibuprofen]] 600 mg oral three times daily with food, [[MED|Acetaminophen/Codeine]] 300/30 mg 1 tablet Q6H PRN severe pain (max 3 days)",
     "Pre-operative orthopedic surgical consultation in 10 days (2026-09-10) after swelling reduction with RICE protocol", "Urgent"),

    ("Gastroenterology", "Helen Mirren", 57, "Female", "Sudden onset severe right upper quadrant colicky pain radiating to right infrascapular region after eating a fatty meal",
     "BP 138/82 mmHg, HR 84 bpm, Temp 99.2 F. Abdominal exam: positive Murphy's sign", "Total Bilirubin 1.1 mg/dL, ALT 35 U/L, AST 32 U/L, Lipase 40 U/L (normal). Abdominal Ultrasound: multiple gallstones, gallbladder wall thickening (3.8 mm) without pericholecystic fluid",
     "Symptomatic [[DIAG|Cholelithiasis]] with acute [[DIAG|Biliary Colic]]",
     "[[MED|Ketorolac]] 10 mg oral every 6 hours PRN biliary spasm (max 5 days), [[MED|Dicyclomine]] 20 mg oral TID before meals PRN cramping",
     "Elective surgical consult for laparoscopic [[PROC|cholecystectomy]] within 2 weeks (2026-09-14); return to ER if jaundice or high fever occurs", "Urgent"),

    ("Rheumatology", "Victor Vance", 55, "Male", "Excruciating acute pain, swelling, erythema, and warmth in the right first metatarsophalangeal (MTP) big toe joint waking him from sleep",
     "BP 148/90 mmHg, HR 90 bpm, localized severe tenderness over right 1st MTP", "Serum Uric Acid 9.2 mg/dL. Synovial fluid aspiration: negatively birefringent needle-shaped monosodium urate crystals under polarized light microscopy",
     "Acute [[DIAG|Gouty Arthritis]] (Podagra) and Chronic [[DIAG|Hyperuricemia]]",
     "[[MED|Indomethacin]] 50 mg oral three times daily with meals for 5 days, [[MED|Colchicine]] 1.2 mg stat followed by 0.6 mg 1 hour later, then 0.6 mg daily. Hold allopurinol initiation until acute flare resolves",
     "Clinic follow-up in 2 weeks (2026-09-14) to initiate [[MED|Allopurinol]] uric acid lowering therapy", "Routine"),

    ("Neurology", "Jessica Jones", 33, "Female", "Subacute loss of vision in right eye with pain on ocular movement (optic neuritis), preceded by transient leg paresthesias 6 months ago",
     "BP 118/72 mmHg, HR 68 bpm", "Ophthalmoscopy: mild right optic disc swelling. Brain/Spine MRI with gadolinium: multiple periventricular and juxtacortical T2/FLAIR hyperintensities with callososeptal interface lesions (Dawson fingers)",
     "Relapsing-Remitting [[DIAG|Multiple Sclerosis (RRMS)]], acute [[DIAG|Optic Neuritis]] episode",
     "[[MED|IV Methylprednisolone]] 1000 mg daily infusion for 3 days followed by oral prednisone taper; plan to start disease-modifying therapy [[MED|Ocrelizumab]]",
     "Neurology demyelinating disease subspecialty clinic in 2 weeks (2026-09-14)", "Urgent"),

    ("Nephrology", "Benjamin Franklin", 47, "Male", "Severe spasmodic left flank pain radiating downward to the left groin, associated with gross hematuria and vomiting",
     "BP 160/98 mmHg (due to severe pain), HR 102 bpm, Afebrile", "Urinalysis: RBC >100/HPF, no nitrites or leukoesterase. Non-contrast CT Abdomen/Pelvis: 4.5 mm calculus lodged in the distal left ureterovesical junction without hydronephrosis",
     "Acute [[DIAG|Urolithiasis]] (Left distal ureteral stone) and gross [[DIAG|Hematuria]]",
     "[[MED|Tamsulosin]] 0.4 mg oral daily (medical expulsive therapy), [[MED|Ketorolac]] 10 mg oral Q6H PRN pain for 5 days, [[MED|Ondansetron]] 4 mg ODT PRN nausea; drink 2.5-3L water daily",
     "Urology follow-up with repeat low-dose KUB X-ray in 10 days (2026-09-10) to confirm stone passage", "Urgent"),

    ("Hematology", "Rochelle Rock", 43, "Female", "Easy bruising, spontaneous gingival bleeding while brushing teeth, and widespread petechiae over lower extremities",
     "BP 120/78 mmHg, HR 76 bpm, Afebrile. Skin exam: extensive non-palpable petechial rash on both shins", "Complete Blood Count: Platelet count 14,000/mcL (critical, normal 150,000-450,000), Hemoglobin 13.2 g/dL, WBC 6.8 k/uL. Peripheral smear confirms true thrombocytopenia without clumping",
     "Primary Immune [[DIAG|Thrombocytopenia (ITP)]]",
     "[[MED|Dexamethasone]] 40 mg oral once daily for 4 consecutive days (pulse corticosteroid therapy), [[MED|Pantoprazole]] 40 mg oral daily for mucosal protection; avoid NSAIDs/aspirin",
     "Urgent Hematology follow-up with daily platelet count monitoring in 48 hours (2026-09-02)", "Critical"),

    ("Cardiology", "Julian Bashir", 69, "Male", "Progressive dyspnea on minimal exertion, 3 episodes of near-syncope while climbing stairs, and fatigue",
     "BP 108/78 mmHg with delayed carotid pulse upstroke (pulsus parvus et tardus), HR 72 bpm. Cardiac exam: harsh cresc-decresc systolic ejection murmur radiating to carotids", "Transthoracic Echo: Aortic valve area (AVA) 0.75 cm2 (severe <1.0), mean transvalvular gradient 46 mmHg, peak jet velocity 4.2 m/s",
     "Severe symptomatic Calcific [[DIAG|Aortic Stenosis]]",
     "[[MED|Atorvastatin]] 20 mg oral daily, cautious [[MED|Lisinopril]] 2.5 mg oral daily (monitor hypotension). Avoid intense exertion",
     "Cardiothoracic Surgery / Structural Heart Team evaluation for [[PROC|Transcatheter Aortic Valve Replacement (TAVR)]] on 2026-09-08", "Critical"),

    ("Pulmonology", "Samantha Carter", 44, "Female", "Persistent non-productive cough, fatigue, bilateral ankle swelling, and tender violaceous nodules on anterior shins (erythema nodosum)",
     "BP 122/76 mmHg, HR 74 bpm, SpO2 98% room air", "Chest Radiograph & CT: Symmetrical bilateral hilar lymphadenopathy without parenchymal fibrosis (Stage 1). Serum ACE level 94 U/L (elevated). Serum Calcium 9.6 mg/dL (normal)",
     "Pulmonary [[DIAG|Sarcoidosis]] (Stage I / Löfgren-like presentation)",
     "[[MED|Naproxen]] 500 mg oral twice daily with meals for joint pain/erythema nodosum; watchful waiting without systemic corticosteroids at this stage",
     "Pulmonology clinic review and repeat pulmonary function testing in 3 months (2026-11-30)", "Routine"),

    ("Dermatology", "Gideon Graves", 39, "Male", "Sharply demarcated erythematous plaques covered with silvery-white scales on extensor surfaces of bilateral elbows and knees",
     "BP 126/80 mmHg, HR 70 bpm. Nails: pitting and onycholysis noted on thumb nails", "Skin biopsy confirms marked epidermal hyperplasia (acanthosis), parakeratosis, and Munro microabscesses",
     "Moderate-to-Severe Chronic Plaque [[DIAG|Psoriasis]]",
     "[[MED|Clobetasol Propionate 0.05% ointment]] applied topically twice daily for 2 weeks on/2 weeks off, [[MED|Calcipotriene 0.005% cream]] topical daily, plan to evaluate for biologic therapy",
     "Dermatology reassessment in 6 weeks (2026-10-12) to assess PASI score", "Routine"),

    ("Psychiatry", "Oliver Queen", 30, "Male", "Recurrent unexpected panic attacks characterized by heart palpitations, chest smothering, trembling, and fear of impending doom",
     "BP 130/84 mmHg, HR 88 bpm (normalizes between attacks), EKG and troponins negative", "Normal thyroid function, toxicology screen negative. Meets DSM-5 criteria for Panic Disorder with Agoraphobia",
     "[[DIAG|Panic Disorder]] and Mild [[DIAG|Agoraphobia]]",
     "[[MED|Sertraline]] 25 mg oral once daily for 1 week, then increase to 50 mg daily; [[MED|Clonazepam]] 0.5 mg oral PRN acute severe panic (dispensed max 10 tablets for bridge therapy)",
     "Cognitive Behavioral Therapy (CBT) intake and psychiatric review in 2 weeks (2026-09-14)", "Routine"),

    ("Gastroenterology", "Bruce Banner", 48, "Male", "Routine executive health exam found elevated liver enzymes; patient reports intermittent mild right upper quadrant fullness, denies alcohol intake",
     "BP 138/88 mmHg, HR 76 bpm, BMI 32.8 kg/m2 (Obese), Waist circumference 104 cm", "AST 58 U/L, ALT 74 U/L, Alkaline Phosphatase 88 U/L, Fasting Triglycerides 240 mg/dL. Viral hepatitis panel (A, B, C) negative. Liver Ultrasound demonstrates diffuse hepatic steatosis without focal mass",
     "Metabolic Dysfunction-Associated Steatohepatitis ([[DIAG|MASH / Non-Alcoholic Fatty Liver Disease]])",
     "[[MED|Semaglutide]] 0.25 mg subcutaneously once weekly for 4 weeks (titrate to 0.5 mg), [[MED|Vitamin E]] 800 IU oral daily, lifestyle intervention targeting 7-10% body weight loss",
     "Gastroenterology/Hepatology follow-up with repeat LFTs and FibroScan in 3 months (2026-12-01)", "Routine"),

    ("Infectious Disease", "Natasha Romanoff", 26, "Female", "Dysuria, urinary urgency, frequency, and suprapubic cramping pain for 2 days; denies flank pain, nausea, or fever",
     "BP 114/70 mmHg, HR 72 bpm, Temp 98.6 F. Physical exam: mild suprapubic tenderness without costovertebral angle (CVA) tenderness", "Urinalysis: Positive leukocyte esterase, positive nitrites, WBC 25-50/HPF, bacteria 3+. Urine pregnancy test negative",
     "Acute Uncomplicated [[DIAG|Cystitis / Urinary Tract Infection (UTI)]]",
     "[[MED|Nitrofurantoin Monohydrate/Macrocrystals (Macrobid)]] 100 mg oral twice daily with meals for 5 days, [[MED|Phenazopyridine]] 100 mg oral TID PRN urinary burning (limit to 2 days)",
     "Return to clinic if symptoms do not improve within 48 hours or if fever/back pain develops", "Routine"),

    ("Cardiology", "Leonard McCoy", 65, "Male", "Known long-standing hypertension presenting for medication adjustment; current home readings consistently 155-165 / 95-100 mmHg",
     "BP in clinic: 162/98 mmHg (both arms), HR 68 bpm, BMI 27.2", "Serum Potassium 4.4 mEq/L, BUN 16 mg/dL, Creatinine 0.9 mg/dL. EKG shows voltage criteria for left ventricular hypertrophy (LVH)",
     "Uncontrolled Essential [[DIAG|Hypertension]] (Stage 2)",
     "[[MED|Amlodipine]] 10 mg oral once daily, [[MED|Lisinopril]] 20 mg oral once daily, [[MED|Hydrochlorothiazide]] 25 mg oral once daily",
     "Nurse blood pressure check in 2 weeks (2026-09-14); comprehensive metabolic panel in 4 weeks", "Routine"),

    ("Endocrinology", "Luke Skywalker", 22, "Male", "Brought to emergency room with nausea, severe abdominal pain, Kussmaul respirations, fruity breath odor, and extreme dehydration",
     "BP 96/60 mmHg, HR 124 bpm (sinus tachycardia), RR 28/min, Temp 98.4 F", "Fingerstick blood glucose 480 mg/dL. Arterial Blood Gas: pH 7.18, HCO3 10 mEq/L, pCO2 24 mmHg. Serum beta-hydroxybutyrate 4.8 mmol/L (elevated), Anion gap 24",
     "[[DIAG|Diabetic Ketoacidosis (DKA)]] as first presentation of [[DIAG|Type 1 Diabetes Mellitus]]",
     "[[MED|IV Regular Insulin]] continuous infusion at 0.1 units/kg/hr after IV fluid resuscitation (Normal Saline 1L/hr), IV Potassium Chloride replacement protocol. Transition to subcutaneous [[MED|Insulin Glargine]] 20 units at bedtime and [[MED|Insulin Lispro]] with meals upon DKA resolution",
     "Endocrinology inpatient team care, diabetes education before discharge; outpatient follow-up in 1 week (2026-09-08)", "Critical"),

    ("Neurology", "Jean Grey", 37, "Female", "Sudden onset of right-sided facial droop, inability to close right eye, loss of taste on anterior 2/3 of tongue for 18 hours; forehead movement absent",
     "BP 120/76 mmHg, HR 70 bpm. Neurological exam: complete right lower motor neuron facial nerve palsy (House-Brackmann Grade IV), forehead involved, extremities 5/5 strength", "Non-contrast Brain CT negative for stroke or intracranial hemorrhage. Clinical diagnosis of Idiopathic Facial Palsy",
     "Acute [[DIAG|Bell's Palsy]] (Right Seventh Cranial Nerve Palsy)",
     "[[MED|Prednisone]] 60 mg oral once daily for 5 days, then tapered over 5 days, [[MED|Valacyclovir]] 1000 mg oral three times daily for 7 days, [[MED|Carboxymethylcellulose 0.5% artificial tears]] hourly and eye taping at night",
     "Neurology follow-up in 14 days (2026-09-14) to evaluate facial nerve recovery", "Urgent"),

    ("Pulmonology", "Peter Parker", 21, "Male", "Sudden onset sharp right-sided pleuritic chest pain and breathlessness while resting; tall, thin body habitus",
     "BP 124/78 mmHg, HR 96 bpm, RR 20/min, SpO2 96% room air. Physical exam: decreased breath sounds and hyperresonance on right thorax", "Upright inspiratory chest X-ray reveals a 25% right-sided apical pneumothorax without mediastinal shift or tension physiology",
     "Primary Spontaneous [[DIAG|Pneumothorax]] (Right)",
     "Conservative observation with high-flow oxygen (10L non-rebreather mask), [[MED|Acetaminophen]] 1000 mg oral TID PRN pain. Repeat chest X-ray in 4 hours showed no progression",
     "Follow-up chest radiograph in 48 hours (2026-09-02). Advised strictly against air travel and scuba diving until complete resolution", "Urgent"),

    ("Orthopedics", "Wanda Maximoff", 45, "Female", "Pain and burning tingling sensation in thumb, index, and middle fingers of right dominant hand, worsening at night and while typing",
     "BP 118/74 mmHg, HR 68 bpm. Physical exam: positive Phalen maneuver and positive Tinel sign at the right wrist. Thenar muscle bulk preserved", "Electromyography and Nerve Conduction Velocity (EMG/NCV) study shows delayed distal median sensory latency (3.9 ms) across the carpal tunnel",
     "Moderate Right [[DIAG|Carpal Tunnel Syndrome]]",
     "[[MED|Naproxen]] 375 mg oral twice daily for 2 weeks, nocturnal neutral wrist splinting, ergonomic workstation modifications",
     "Orthopedic hand clinic follow-up in 6 weeks (2026-10-12); consider ultrasound-guided steroid injection if splinting fails", "Routine"),

    ("Dermatology", "Steve Rogers", 72, "Male", "Slow-growing pearly papule with rolled borders, central ulceration, and overlying telangiectasias on the right temple for 9 months",
     "BP 130/80 mmHg, HR 64 bpm", "Dermoscopic examination reveals arborizing telangiectatic vessels and shiny white structures. Shave biopsy confirms basaloid epithelial nests with peripheral palisading",
     "Nodular [[DIAG|Basal Cell Carcinoma (BCC)]] of the right temporal skin",
     "Surgical excision via [[PROC|Mohs Micrographic Surgery]] scheduled on 2026-09-22. Topical mupirocin 2% ointment applied to biopsy site twice daily",
     "Pre-operative Mohs appointment on 2026-09-22; annual full-body skin examination", "Urgent"),

    ("Nephrology", "Peggy Carter", 60, "Female", "Persistent microscopic hematuria and microalbuminuria on annual labs; brother on hemodialysis for polycystic kidney disease",
     "BP 148/92 mmHg, HR 72 bpm. Abdominal palpation: palpable bilateral flank masses", "Serum Creatinine 1.2 mg/dL, eGFR 58 mL/min/1.73m2. Renal Ultrasound reveals bilaterally enlarged kidneys with numerous fluid-filled cortical and medullary cysts (Mayo Class 1C)",
     "Autosomal Dominant [[DIAG|Polycystic Kidney Disease (ADPKD)]], Stage 3a [[DIAG|CKD]]",
     "[[MED|Tolvaptan]] 45 mg morning / 15 mg afternoon oral daily (slows cyst growth), [[MED|Telmisartan]] 80 mg oral once daily (strict BP target <120/80)",
     "Nephrology follow-up with liver enzymes (due to tolvaptan) and electrolytes in 4 weeks (2026-09-28)", "Urgent"),

    ("Cardiology", "Anthony Stark", 51, "Male", "Substernal chest pressure brought on consistently by brisk walking or climbing 2 flights of stairs, relieved within 3 minutes of rest",
     "BP 136/84 mmHg, HR 78 bpm, BMI 26.5", "Resting EKG normal. Exercise Treadmill Stress Test: 1.5 mm horizontal ST depression in leads II, III, aVF, and V5 at 6 METs without ventricular arrhythmias",
     "Chronic Stable [[DIAG|Angina Pectoris]], Coronary Artery Disease",
     "[[MED|Nitroglycerin Sublingual tablet]] 0.4 mg PRN acute chest pain (max 3 doses 5 min apart), [[MED|Metoprolol Tartrate]] 25 mg oral twice daily, [[MED|Aspirin]] 81 mg daily, [[MED|Atorvastatin]] 40 mg daily",
     "Cardiology clinic review in 3 weeks (2026-09-21); outpatient elective coronary CT angiography scheduled for 2026-09-15", "Urgent"),

    ("Endocrinology", "Carol Danvers", 32, "Female", "Irregular oligomenorrheic menstrual cycles (every 45-60 days), worsening hirsutism on chin, and difficulty conceiving for 14 months",
     "BP 122/80 mmHg, HR 72 bpm, BMI 28.6 kg/m2, Ferriman-Gallwey score 12", "Serum Total Testosterone elevated at 68 ng/dL, Fasting insulin 18 uIU/mL, LH/FSH ratio 2.8. Pelvic Ultrasound: bilateral enlarged ovaries with 'string of pearls' peripheral follicles >20 per ovary",
     "[[DIAG|Polycystic Ovary Syndrome (PCOS)]] and mild [[DIAG|Insulin Resistance]]",
     "[[MED|Metformin]] 500 mg oral twice daily with food, [[MED|Spironolactone]] 50 mg oral once daily (anti-androgen), [[MED|Combined Oral Contraceptive]] (Drospirenone/Ethinyl Estradiol 3mg/0.03mg) daily",
     "Endocrinology/Reproductive health visit in 3 months (2026-11-30)", "Routine"),

    ("Urology", "Clint Barton", 53, "Male", "Left testicular dull ache and dragging sensation that worsens after prolonged standing or heavy lifting, relieved when lying supine",
     "BP 124/76 mmHg, HR 70 bpm. Genitourinary exam: soft, non-tender, 'bag of worms' palpable mass superior and posterior to the left testis, prominent with Valsalva maneuver", "Scrotal Color Doppler Ultrasound: multiple dilated pampiniform venous channels >3.5 mm with documented retrograde venous reflux during Valsalva",
     "Left-sided Grade III [[DIAG|Varicocele]]",
     "[[MED|Ibuprofen]] 400 mg oral twice daily PRN pain with meals, scrotal athletic supporter, avoidance of prolonged heavy lifting",
     "Urology clinic follow-up with semen analysis in 8 weeks (2026-10-26) to evaluate fertility parameters", "Routine"),

    ("Rheumatology", "Matt Murdock", 36, "Male", "Chronic low back pain and morning stiffness for over 2 years, improving with movement and physical activity but not with rest",
     "BP 120/78 mmHg, HR 72 bpm. Spinal exam: reduced lumbar flexion (modified Schober test 3.5 cm expansion), positive bilateral Faber test", "HLA-B27 genetic allele POSITIVE. Pelvic MRI (STIR sequence): bilateral subchondral bone marrow edema in the sacroiliac joints confirming active sacroiliitis",
     "[[DIAG|Ankylosing Spondylitis (Axial Spondyloarthritis)]]",
     "[[MED|Celecoxib]] 200 mg oral twice daily with meals, plan for anti-TNF biologic [[MED|Adalimumab]] 40 mg subcutaneous injection every 2 weeks, structured physical therapy",
     "Rheumatology follow-up in 4 weeks (2026-09-28) to verify latent TB testing before biologic initiation", "Urgent"),

    ("Psychiatry", "Barry Allen", 25, "Male", "Lifelong severe inattention, inability to organize daily tasks, chronic procrastination, and impulsive interruption of conversations impacting job performance",
     "BP 118/74 mmHg, HR 70 bpm, Baseline EKG normal sinus rhythm", "ASRS-v1.1 (Adult ADHD Self-Report Scale) Part A score 6/6 (highly positive). Comprehensive neurocognitive testing confirms executive function deficit",
     "Attention-Deficit/Hyperactivity Disorder ([[DIAG|ADHD]]), Combined Presentation in Adult",
     "[[MED|Methylphenidate Extended-Release (Concerta)]] 18 mg oral once daily in the morning, titrate to 36 mg after 2 weeks; CBT for executive functioning skills",
     "Psychiatric follow-up with BP and heart rate monitoring in 4 weeks (2026-09-28)", "Routine"),

    ("Neurology", "Gwen Stacy", 23, "Female", "Two unprovoked generalized tonic-clonic seizures occurring 3 weeks apart, characterized by tongue biting and 20-minute post-ictal confusion",
     "BP 114/72 mmHg, HR 76 bpm, Neurological exam between events normal", "24-hour video EEG: generalized 3 Hz spike-and-wave epileptiform discharges. 3T Brain MRI with epilepsy protocol is anatomically normal",
     "Idiopathic Generalized [[DIAG|Epilepsy]]",
     "[[MED|Levetiracetam (Keppra)]] 500 mg oral twice daily for 1 week, then increase to 1000 mg twice daily; driving restriction counseled according to state law (6 months seizure-free)",
     "Epilepsy clinic review in 4 weeks (2026-09-28); emergency seizure safety rescue plan provided with [[MED|Midazolam nasal spray]] 5 mg PRN seizure >5 minutes", "Urgent"),

    ("Orthopedics", "Thor Odinson", 40, "Male", "Severe lateral right elbow pain radiating down forearm, exacerbated by gripping and wrist extension (shaking hands, using tools)",
     "BP 128/80 mmHg, HR 68 bpm. Physical exam: point tenderness at the right lateral epicondyle; positive Cozen test and positive Mill's test", "Right elbow X-ray normal without calcification. Diagnostic musculoskeletal ultrasound: hypoechogenicity and thickening of the common extensor tendon origin",
     "Lateral Epicondylitis ([[DIAG|Tennis Elbow]]) of the right upper extremity",
     "[[MED|Diclofenac 1% topical gel]] 2 grams applied to right lateral elbow 4 times daily, counterforce forearm brace, eccentric extensor physical therapy protocol",
     "Orthopedic clinic review in 6 weeks (2026-10-12); consider PRP injection if refractory", "Routine"),

    ("Infectious Disease", "Loki Laufeyson", 37, "Male", "Persistent tick bite history followed by expanding erythematous circular rash with central clearing ('bullseye') on back, arthralgias, and fatigue",
     "BP 120/76 mmHg, HR 74 bpm, Temp 99.4 F. Skin exam: 12 cm circular erythema migrans lesion on posterior lumbar back", "Serology: Two-tier Lyme testing positive (ELISA reactive, Western blot positive for Borrelia burgdorferi IgM antibodies). EKG normal PR interval",
     "Early Localized [[DIAG|Lyme Disease]] (Erythema Migrans)",
     "[[MED|Doxycycline]] 100 mg oral twice daily with a full glass of water for 14 days, sun protection advised",
     "Primary care follow-up in 2 weeks (2026-09-14) or sooner if palpitations, syncope, or facial weakness occurs", "Routine")
]

# Assemble into full 50 report items
full_dataset = []

# First 5 already defined
for c in cases:
    full_dataset.append({
        "document_id": c["id"],
        "category": c["category"],
        "document_text": c["text"],
        "evaluations": c["evaluations"]
    })

# Add remaining cases with autogenerated 5-question standard RAG evaluation harness
for idx, item in enumerate(clinical_templates, start=6):
    cat, name, age, gender, complaint, vitals, labs, diag, meds, followup, urgency = item
    
    doc_id = f"MED-{idx:03d}"
    
    doc_text = (
        f"PATIENT MEDICAL RECORD & CLINICAL SUMMARY\n"
        f"Patient: {name} | Age: {age} | Gender: {gender}\n"
        f"Chief Complaint: {complaint}.\n"
        f"Vitals & Physical Findings: {vitals}.\n"
        f"Diagnostic Tests & Laboratory Data: {labs}.\n"
        f"Assessment & Diagnosis: {diag}.\n"
        f"Management & Prescriptions: {meds}.\n"
        f"Follow-up & Disposition: {followup}.\n"
        f"Urgency Level: {urgency}."
    )
    
    evaluations = [
        {
            "q_id": 1,
            "question": "What is the patient's identity, age, gender, and chief presenting complaint?",
            "ground_truth": f"{name}, a {age}-year-old {gender.lower()}, presented with {complaint.lower()}."
        },
        {
            "q_id": 2,
            "question": "What vital signs, physical examination, or diagnostic test results were recorded?",
            "ground_truth": f"Vitals: {vitals}. Diagnostic findings: {labs}."
        },
        {
            "q_id": 3,
            "question": "What is the primary clinical diagnosis or medical condition established?",
            "ground_truth": f"{diag.replace('[[DIAG|', '').replace(']]', '')}."
        },
        {
            "q_id": 4,
            "question": "What specific medications, treatments, or dosages were prescribed in the management plan?",
            "ground_truth": f"{meds.replace('[[MED|', '').replace(']]', '').replace('[[PROC|', '').replace(']]', '')}."
        },
        {
            "q_id": 5,
            "question": "What is the urgency level and the scheduled follow-up or disposition plan?",
            "ground_truth": f"Urgency level is {urgency}. Plan: {followup}."
        }
    ]
    
    full_dataset.append({
        "document_id": doc_id,
        "category": cat,
        "document_text": doc_text,
        "evaluations": evaluations
    })

os.makedirs("c:/Learning/BriefMedAI/dataset", exist_ok=True)
output_path = "c:/Learning/BriefMedAI/dataset/eval_dataset.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(full_dataset, f, indent=2, ensure_ascii=False)

print(f"Successfully generated {len(full_dataset)} medical reports with {sum(len(d['evaluations']) for d in full_dataset)} total question-answer evaluation pairs at {output_path}")
