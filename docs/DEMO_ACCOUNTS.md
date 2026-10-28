# Demo accounts

All accounts are created by `python -m app.seed`. They're local, fake users, and **every password is `pulse123`**.

Run `python -m app.seed` again at any time to reset everything to the state below.

## Start the app
```bash
# Terminal 1: backend
cd backend
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
python -m app.seed
uvicorn app.main:app --reload

# Terminal 2: frontend
cd frontend
npm run dev                   # http://localhost:5173
```

## Northwind Logistics

| Email | Password | Role | Team | Seniority | Has a report? |
|---|---|---|---|---|---|
| **asha@northwind.test** | `pulse123` | **Admin** (sees dashboard) | – | lead | – |
| priya@northwind.test | `pulse123` | Employee | Support | junior | ✅ (has a risk) |
| arjun@northwind.test | `pulse123` | Employee | Support | senior | ✅ |
| kavitha@northwind.test | `pulse123` | Employee | Support | mid | ✅ (has a risk) |
| farah@northwind.test | `pulse123` | Employee | Support | junior | ✅ |
| joseph@northwind.test | `pulse123` | Employee | Support | mid | ✅ (has a risk) |
| ananya@northwind.test | `pulse123` | Employee | Support | junior | ❌ goes to diagnostic |
| vikram@northwind.test | `pulse123` | Employee | Sales | senior | ✅ |
| rohan@northwind.test | `pulse123` | Employee | Sales | mid | ✅ |
| neha@northwind.test | `pulse123` | Employee | Sales | junior | ❌ |
| sara@northwind.test | `pulse123` | Employee | Engineering | mid | ✅ |
| dev@northwind.test | `pulse123` | Employee | Engineering | lead | ❌ |
| imran@northwind.test | `pulse123` | Employee | HR | senior | ❌ |

## Bluepeak Retail

| Email | Password | Role | Team | Seniority | Has a report? |
|---|---|---|---|---|---|
| **meera@bluepeak.test** | `pulse123` | **Admin** | – | lead | – |
| tom@bluepeak.test | `pulse123` | Employee | Stores | mid | ✅ |
| lina@bluepeak.test | `pulse123` | Employee | Stores | junior | ❌ |
| kabir@bluepeak.test | `pulse123` | Employee | Customer Care | senior | ✅ (2 risks) |

## Both organizations

| Email | Password | Northwind | Bluepeak |
|---|---|---|---|
| **ravi@consult.test** | `pulse123` | Employee (HR) | **Admin** |

## Things to try

1. **Minimum group size (client request 1):** log in as `asha`. Support is shown because it has 5 respondents; Sales, Engineering and HR are pooled into a hidden "Other teams".
2. **Right to delete (client request 2):** log in as `priya` and click **Delete my data**. Log back in as `asha`: Support has dropped to 4 respondents and moved into "Other teams".
3. **Pool becomes visible:** complete the diagnostic as `neha` and `dev`. As `asha`, "Other teams" now shows numbers (5 respondents).
4. **Seniority questions:** `dev` (lead) gets the senior engineering questions; `neha` (junior) doesn't.
5. **Risk → action (own feature):**
   - As `asha`: "Top risks and what to do" shows each risk, where it is and what to do.
   - As `priya`: each risk in her report has a "What to do" line.
6. **Multi-org:** log in as `ravi`, pick Northwind (employee, diagnostic), then **Switch org** to Bluepeak (admin dashboard, with all teams under 5 and hidden).
7. **Security checks:**
   - A wrong password shows an error.
   - Admins don't get the diagnostic.
   - Employees can't open the dashboard.
