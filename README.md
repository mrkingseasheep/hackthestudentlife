# ResearchMatch 🔬
Tinder-style research interest matching for students & professors.

---

## Project Structure
```
researchmatch/
├── app.py              ← Flask backend (all logic lives here)
├── requirements.txt    ← Python dependencies
└── templates/
    ├── home.html         ← Landing page
    ├── professor_form.html
    ├── student_form.html
    └── results.html
```

---

## 1. Install Dependencies
```bash
pip install flask boto3
```

---

## 2. AWS Setup (5 minutes)

### Step 1 — Create an IAM User with DynamoDB access
1. Go to https://console.aws.amazon.com/iam
2. Click **Users → Add users**
3. Username: `researchmatch-user`
4. Click **Attach policies directly** → search and add `AmazonDynamoDBFullAccess`
5. Click through and create the user
6. Click the user → **Security credentials** → **Create access key** → choose "Local code"
7. Copy the **Access Key ID** and **Secret Access Key**

### Step 2 — Configure AWS credentials locally
```bash
aws configure
# OR manually create the file:
```

Create file `~/.aws/credentials`:
```
[default]
aws_access_key_id = YOUR_ACCESS_KEY_ID
aws_secret_access_key = YOUR_SECRET_ACCESS_KEY
region = us-east-1
```

---

## 3. Create DynamoDB Table (2 minutes)
1. Go to https://console.aws.amazon.com/dynamodb
2. Click **Create table**
3. Fill in:
   - **Table name:** `research_profiles`
   - **Partition key:** `id` (type: String)
4. Leave everything else as default
5. Click **Create table**
6. Wait ~30 seconds for it to become Active

---

## 4. Run the App
```bash
cd researchmatch
python app.py
```
Open http://localhost:5000 in your browser.

---

## 5. How to Demo
1. Go to **Professor** → add 2-3 professors with different interests
2. Go to **Student** → enter a student with overlapping keywords
3. See the **Results** page with match scores!

---

## How Matching Works
- Professor interests: `"machine learning, healthcare, medical imaging"`
- Student interests: `"AI, healthcare, data science"`
- Shared keywords: `healthcare` → score = 1/5 = 20%
- Higher overlap = higher score, shown as a percentage circle

---

## Optional Quick Improvements
- Add more professors via seeding: duplicate the `table.put_item()` block in app.py
- Change `region_name='us-east-1'` in app.py if your AWS region is different
- Add a "Browse all professors" page (just scan table and display all type=professor)
