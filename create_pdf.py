import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# 確保 data 資料夾存在
if not os.path.exists("data"):
    os.makedirs("data")

# --- 定義完整資料庫 (包含最新的 004) ---
patients_data = [
    # 001: EGFR (Lung)
    {
        "id": "001",
        "name": "Chang, Wei-Ming",
        "dob": "1965-04-12",
        "gender": "Male",
        "history": "Smoking (20 pack-years). Persistent cough.",
        "pathology": "Lung Adenocarcinoma. Staging: cT2aN2M0, IIIA.",
        "alterations": [
            {"gene": "EGFR Exon 19 Deletion", "vaf": "28%", "sig": "Pathogenic. Sensitizing for EGFR TKIs."},
            {"gene": "TP53 R273C", "vaf": "15%", "sig": "Pathogenic."},
            {"gene": "PD-L1 Expression (TPS)", "vaf": "45%", "sig": "Moderate expression."}
        ],
        "treatment_logic": "EGFR Exon 19 Deletion indicates high sensitivity to EGFR-TKIs.",
        "drug": "Osimertinib (Tagrisso) 80mg daily.",
        "alt_drug": "Gefitinib or Erlotinib"
    },
    # 002: KRAS (Lung)
    {
        "id": "002",
        "name": "Lee, Shu-Fen",
        "dob": "1978-08-23",
        "gender": "Female",
        "history": "Heavy smoker. Routine CXR revealed mass.",
        "pathology": "Lung Adenocarcinoma. Staging: cT3N1M0, IIIB.",
        "alterations": [
            {"gene": "KRAS G12C", "vaf": "32%", "sig": "Pathogenic. Predicts response to KRAS G12C inhibitors."},
            {"gene": "STK11 Mutation", "vaf": "18%", "sig": "Pathogenic."},
        ],
        "treatment_logic": "KRAS G12C mutation identified. NCCN recommends targeted therapy.",
        "drug": "Sotorasib (Lumakras) 960mg daily.",
        "alt_drug": "Adagrasib"
    },
    # 003: ALK (Lung)
    {
        "id": "003",
        "name": "Wang, Da-Wei",
        "dob": "1982-11-05",
        "gender": "Male",
        "history": "Never-smoker. Chest pain.",
        "pathology": "Lung Adenocarcinoma. Staging: Stage IV (Brain mets).",
        "alterations": [
            {"gene": "EML4-ALK Fusion", "vaf": "Fish Positive", "sig": "Pathogenic. Highly sensitive to ALK inhibitors."},
        ],
        "treatment_logic": "ALK Rearrangement is a potent driver.",
        "drug": "Alectinib (Alecensa) 600mg BID.",
        "alt_drug": "Brigatinib"
    },
    # 004: BRCA (Breast)
    {
        "id": "004",
        "name": "Chen, Mei-Ling",
        "dob": "1980-02-14",
        "gender": "Female",
        "history": "Family history of breast cancer (Mother). Palpable lump in left breast.",
        "pathology": "Invasive Ductal Carcinoma. ER-, PR-, HER2- (Triple Negative). Stage IIB.",
        "alterations": [
            {"gene": "BRCA1 c.68_69delAG", "vaf": "Germline", "sig": "Pathogenic. Associated with Hereditary Breast and Ovarian Cancer syndrome."},
            {"gene": "TP53 Mutation", "vaf": "40%", "sig": "Pathogenic."}
        ],
        "treatment_logic": "Patient has germline BRCA1 mutation and HER2-negative breast cancer.",
        "drug": "Olaparib (Lynparza) (PARP Inhibitor)",
        "alt_drug": "Talazoparib (Talzenna)"
    }
]

def create_pdf_smart(p):
    file_path = f"data/patient_report_{p['id']}.pdf"
    
    # 💡 關鍵邏輯：檢查檔案是否存在 (Idempotency)
    if os.path.exists(file_path):
        print(f"⏭️  [Skipped] 檔案已存在，跳過生成: {file_path}")
        return

    # --- 如果檔案不存在，才執行生成邏輯 ---
    c = canvas.Canvas(file_path, pagesize=letter)
    
    # Header
    c.setFont("Helvetica-Bold", 14)
    c.drawString(72, 750, "CONFIDENTIAL MEDICAL REPORT")
    c.setFont("Helvetica", 10)
    c.drawString(72, 735, "ACT Genomics - Precision Medicine Center")
    c.line(72, 725, 540, 725)
    
    # Patient Info
    c.drawString(72, 700, f"Patient Name: {p['name']}")
    c.drawString(72, 685, f"Patient ID: ACT-2024-{p['id']}")
    c.drawString(72, 670, f"DOB: {p['dob']} ({p['gender']})")
    
    # Clinical
    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, 630, "--- CLINICAL HISTORY & PATHOLOGY ---")
    c.setFont("Helvetica", 10)
    c.drawString(72, 610, f"History: {p['history']}")
    c.drawString(72, 595, f"Diagnosis: {p['pathology']}")
    
    # NGS Results
    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, 550, "--- DETECTED GENOMIC ALTERATIONS ---")
    y = 530
    c.setFont("Helvetica", 11)
    for i, alt in enumerate(p['alterations'], 1):
        c.setFont("Helvetica-Bold", 11)
        c.drawString(72, y, f"{i}. {alt['gene']}")
        c.setFont("Helvetica", 10)
        c.drawString(90, y-15, f"• VAF/Type: {alt['vaf']}")
        c.drawString(90, y-30, f"• Significance: {alt['sig']}")
        y -= 50

    # Treatment
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, y, "--- TREATMENT RECOMMENDATIONS ---")
    c.setFont("Helvetica", 10)
    c.drawString(72, y-20, p['treatment_logic'])
    c.setFont("Helvetica-Bold", 10)
    c.drawString(72, y-40, f"Recommended: {p['drug']}")
    c.setFont("Helvetica", 10)
    c.drawString(72, y-55, f"Alternative: {p['alt_drug']}")
    
    c.save()
    print(f"✅ [Created] 新增檔案: {file_path}")

if __name__ == "__main__":
    print(f"🚀 開始檢查 {len(patients_data)} 筆病歷資料...")
    for p in patients_data:
        create_pdf_smart(p)
    print("🎉 同步完成！")