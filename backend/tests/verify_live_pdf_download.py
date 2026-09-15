"""
Script to test real authenticated PDF report download against the live running server (port 8001).
Uses httpx.
"""
import io
import httpx
import uuid
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

BASE_URL = "http://127.0.0.1:8001"

def test_live_pdf_download():
    print(f"[*] Testing live backend at {BASE_URL}...")
    
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Register User A
        rand_suffix = uuid.uuid4().hex[:8]
        email_a = f"pdf_tester_{rand_suffix}@hirelens.io"
        password = "SecurePassword123!"
        
        reg_res = client.post("/api/v1/auth/register", json={
            "email": email_a,
            "password": password
        })
        print(f"[*] User A registration: {reg_res.status_code}")
        assert reg_res.status_code == 201, f"Registration failed: {reg_res.text}"
        
        # Login User A
        login_res = client.post("/api/v1/auth/login", data={
            "username": email_a,
            "password": password
        })
        print(f"[*] User A login: {login_res.status_code}")
        assert login_res.status_code == 200, f"Login failed: {login_res.text}"
        token_a = login_res.json()["access_token"]
        headers_a = {"Authorization": f"Bearer {token_a}"}
        
        # 2. Upload Resume
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        c.drawString(100, 750, "Jane Candidate")
        c.drawString(100, 730, "Software Engineer with 4 years experience in Python, FastAPI, Docker, and PostgreSQL.")
        c.drawString(100, 710, "Education: B.S. in Computer Science")
        c.drawString(100, 690, "Skills: Python, FastAPI, SQL, Docker, Git, CI/CD")
        c.save()
        pdf_bytes = buf.getvalue()
        
        files = {"file": ("test_resume.pdf", pdf_bytes, "application/pdf")}
        upload_res = client.post("/api/v1/resumes/upload", headers=headers_a, files=files)
        print(f"[*] Resume upload: {upload_res.status_code}")
        assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
        resume_data = upload_res.json()
        resume_id = resume_data["id"]
        
        # 3. Analyze Resume
        jd_text = """
        Senior Python Developer
        We are looking for a Senior Python Developer with at least 3 years of experience.
        Requirements:
        - Strong proficiency with Python and FastAPI
        - Experience with PostgreSQL and Docker
        - Education: Bachelor's degree in Computer Science
        """
        analysis_res = client.post("/api/v1/analysis/run", headers=headers_a, json={
            "resume_id": resume_id,
            "job_description_text": jd_text,
            "job_title": "Senior Python Developer"
        })
        print(f"[*] Analysis run: {analysis_res.status_code}")
        assert analysis_res.status_code in [200, 201], f"Analysis failed: {analysis_res.text}"
        analysis_data = analysis_res.json()
        analysis_id = analysis_data["id"]
        print(f"[*] Analysis generated with ID: {analysis_id}, Overall Score: {analysis_data['overall_score']}")
        
        # 4. Download PDF Report (Authenticated)
        report_res = client.get(f"/api/v1/analysis/{analysis_id}/report", headers=headers_a)
        print(f"[*] Report download status: {report_res.status_code}")
        assert report_res.status_code == 200, f"Report download failed: {report_res.text}"
        
        # Verify PDF headers & content
        content_type = report_res.headers.get("content-type", "")
        content_disp = report_res.headers.get("content-disposition", "")
        print(f"[*] Content-Type: {content_type}")
        print(f"[*] Content-Disposition: {content_disp}")
        assert "application/pdf" in content_type, f"Expected application/pdf, got {content_type}"
        assert "attachment" in content_disp and ".pdf" in content_disp, f"Expected PDF attachment header, got {content_disp}"
        
        pdf_content = report_res.content
        print(f"[*] Downloaded PDF size: {len(pdf_content)} bytes")
        assert len(pdf_content) > 1000, "PDF content seems too small"
        assert pdf_content.startswith(b"%PDF-"), "Invalid PDF signature"
        print("[*] PDF starts with valid '%PDF-' magic bytes.")
        
        # 5. Security Test: Unauthenticated request should return 401
        unauth_res = client.get(f"/api/v1/analysis/{analysis_id}/report")
        print(f"[*] Unauthenticated request status: {unauth_res.status_code}")
        assert unauth_res.status_code == 401, f"Expected 401, got {unauth_res.status_code}"
        
        # 6. User Isolation Test: Another user should get 404
        email_b = f"pdf_tester_b_{rand_suffix}@hirelens.io"
        reg_b = client.post("/api/v1/auth/register", json={
            "email": email_b,
            "password": password
        })
        login_b = client.post("/api/v1/auth/login", data={
            "username": email_b,
            "password": password
        })
        token_b = login_b.json()["access_token"]
        headers_b = {"Authorization": f"Bearer {token_b}"}
        
        user_b_res = client.get(f"/api/v1/analysis/{analysis_id}/report", headers=headers_b)
        print(f"[*] User B request status: {user_b_res.status_code}")
        assert user_b_res.status_code == 404, f"Expected 404 for different user, got {user_b_res.status_code}"
        
        print("\n[SUCCESS] All live authenticated PDF download and isolation tests PASSED successfully!")
        return True

if __name__ == "__main__":
    test_live_pdf_download()
