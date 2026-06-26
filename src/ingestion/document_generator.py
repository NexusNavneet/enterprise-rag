import os
import random

CATEGORIES = {
    "hr": [
        "leave policy", "work from home policy", "code of conduct",
        "performance review", "employee benefits", "attendance policy",
        "anti harassment policy", "travel reimbursement", "dress code",
        "onboarding process"
    ],
    "it": [
        "password policy", "data backup policy", "software installation",
        "network security", "email usage policy", "device management",
        "cloud storage guidelines", "incident response", "VPN usage",
        "cybersecurity training"
    ],
    "compliance": [
        "GDPR guidelines", "data privacy policy", "audit procedures",
        "risk management", "whistleblower policy", "financial compliance",
        "vendor compliance", "regulatory reporting", "ethics policy",
        "document retention"
    ],
    "product": [
        "user manual", "API documentation", "release notes",
        "troubleshooting guide", "installation guide", "feature overview",
        "integration guide", "FAQ document", "system requirements",
        "upgrade procedures"
    ]
}

def generate_document(category, topic, doc_number):
    content = f"""
ENTERPRISE DOCUMENT
===================
Category: {category.upper()}
Topic: {topic.title()}
Document ID: DOC-{category.upper()}-{doc_number:03d}
Version: 1.{random.randint(0,5)}
Last Updated: 2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}

1. PURPOSE
----------
This document outlines the {topic} guidelines for all employees 
and stakeholders of the organization. Compliance with this policy 
is mandatory for all staff members.

2. SCOPE
--------
This policy applies to all full-time employees, part-time staff, 
contractors, and third-party vendors who interact with company 
systems and resources related to {topic}.

3. POLICY DETAILS
-----------------
3.1 All employees must adhere to the {topic} standards as defined 
    in this document. Violations may result in disciplinary action.

3.2 The {category} department is responsible for maintaining and 
    updating this policy annually or when significant changes occur.

3.3 Employees must complete mandatory training related to {topic} 
    within 30 days of joining and annually thereafter.

4. PROCEDURES
-------------
Step 1: Review the {topic} requirements thoroughly.
Step 2: Complete the acknowledgment form available on the HR portal.
Step 3: Attend the mandatory orientation session.
Step 4: Report any violations to your immediate supervisor or the 
        {category} department directly.

5. RESPONSIBILITIES
-------------------
- Employees: Follow all guidelines outlined in this document
- Managers: Ensure team compliance and report violations
- {category.upper()} Department: Maintain and enforce this policy
- HR: Track compliance and maintain records

6. COMPLIANCE AND PENALTIES
----------------------------
Non-compliance with this {topic} policy may result in:
- Verbal or written warning (first offense)
- Suspension without pay (second offense)
- Termination of employment (repeated violations)

7. CONTACT INFORMATION
-----------------------
For questions regarding this policy, contact:
Email: {category}@company.com
Phone: +1-800-{random.randint(100,999)}-{random.randint(1000,9999)}

END OF DOCUMENT
"""
    return content

def generate_all_documents():
    os.makedirs("documents", exist_ok=True)
    
    doc_count = 0
    MAX_DOCS = 500

    for category, topics in CATEGORIES.items():
        category_path = f"documents/{category}"
        os.makedirs(category_path, exist_ok=True)
        
        for topic in topics:
            for i in range(13):
                if doc_count >= MAX_DOCS:
                    break
                doc_count += 1
                content = generate_document(category, topic, doc_count)
                filename = f"{category_path}/{topic.replace(' ', '_')}_{i+1}.txt"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
            if doc_count >= MAX_DOCS:
                break
        print(f"✅ Generated {category.upper()} documents")

    print(f"\n🎉 Total documents generated: {doc_count}")
    print("📁 Check your documents folder!")

# THIS LINE IS CRITICAL
generate_all_documents()