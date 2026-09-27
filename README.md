# Atlas Cargo Systems — digital platform

Full-stack Django + Bootstrap 5 build implementing the phases from the
digital systems proposal: public site with live tracking and quote
requests, a client/staff portal, automated SMS/WhatsApp notifications,
and a staff mini-ERP dashboard.

Public-site copy (About, Services, homepage) and the logo/photos under
`static/img/` were pulled from the real Atlas Cargo Systems company
profile and live website — not placeholder text. Real address, phone
numbers, affiliations (UFFA, FIATA, AEO), and awards are included.

## Apps

- **accounts** — `ClientProfile` and `StaffProfile` on top of Django auth,
  with branch (Kampala/Entebbe) and role on staff.
- **shipments** — `Shipment`, `StatusUpdate` (append-only history), `Document`
  (BOL/AWB/customs uploads). A signal fires a Celery task on every new
  `StatusUpdate` to notify the client.
- **notifications** — `Notification` log + Celery task that sends via
  Africa's Talking SMS (WhatsApp stub included — swap in Meta's Cloud API
  once business verification is done).
- **quotes** — `QuoteRequest`, the data model behind the public quote form.
- **sitepages** — the public marketing site: homepage, live shipment
  tracking (by reference/BOL/AWB, no login), and the quote request form.
- **portal** — the authenticated web app: client shipment list/detail,
  staff branch dashboard, status updates, document uploads, and
  quote-to-shipment conversion.

## Site map

| URL | App | Access |
|---|---|---|
| `/` | sitepages | Public — homepage |
| `/about/` | sitepages | Public — About Us |
| `/services/` | sitepages | Public — service detail (Air/Sea/Road/Customs) |
| `/contact/` | sitepages | Public — contact form (saves to `ContactMessage`, viewable in `/admin/`) |
| `/track/` | sitepages | Public — search by reference/BOL/AWB |
| `/quote/` | sitepages | Public — quote request form |
| `/login/` | — | Public — client/staff sign-in |
| `/app/` | portal | Logged-in — routes to staff dashboard or shipment list |
| `/app/staff/` | portal | Staff only — branch stats, new quotes, recent shipments |
| `/app/shipments/` | portal | Logged-in — client's own shipments / staff's branch shipments |
| `/app/shipments/{reference}/` | portal | Logged-in — status timeline, documents; staff also get the update/upload forms |
| `/app/quotes/{id}/convert/` | portal | Staff only (POST) — turns a quote request into a shipment |
| `/app/shipments/new/` | portal | Staff only — create a shipment directly (not only via quote conversion) |
| `/app/clients/` | portal | Staff only — list every client account |
| `/app/clients/new/` | portal | Staff only — create a client account (creates the login + profile together) |
| `/app/staff-accounts/` | portal | Admin-role staff only — list every staff account |
| `/app/staff-accounts/new/` | portal | Admin-role staff only — create a staff account with branch + role |
| `/api/v1/...` | shipments, quotes | Same data via DRF, for a future mobile app |
| `/admin/` | — | Django admin — still available, but day-to-day client/shipment/staff management now lives in `/app/` above |

## Local setup

```bash
cp .env.example .env          # fill in DB/Redis/Africa's Talking values
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

Run the notification worker in a second terminal:

```bash
celery -A atlas_cargo worker -l info
```

**On Windows**, the default prefork pool doesn't work (you'll see
`PermissionError: [WinError 5] Access is denied` from `billiard`). Run
with the solo pool instead: `celery -A atlas_cargo worker -l info -P solo`.
You'll also need Redis actually running first — Docker Desktop
(`docker run -d -p 6379:6379 redis:7`) or Memurai are the easiest options
on Windows. Using Docker Compose (below) sidesteps this entirely since
the worker runs in a Linux container.

Frontend uses Bootstrap 5 via CDN (`cdnjs.cloudflare.com`) plus one small
brand stylesheet at `static/site.css` — no build step, no npm.

## Docker

```bash
cp .env.example .env
docker compose up --build
```

This starts Postgres, Redis, the Django app (Gunicorn), and a Celery worker.

## Tested end to end

Verified with Django's test client against a seeded SQLite DB (Celery in
eager mode):
- Public homepage, tracking (found + not-found cases), and quote
  submission all render and redirect correctly.
- Staff dashboard correctly scopes quote requests and shipments to the
  logged-in staff member's own branch (an Entebbe quote is invisible to
  Kampala staff, and vice versa).
- Converting a quote request creates a client account + shipment + initial
  status update, and marks the quote `converted`.
- Posting a new status update updates the shipment, appends to the
  timeline, and fires the notification signal without error.
- Uploading a document attaches it to the shipment and it's immediately
  visible to the owning client.
- A client can never see the staff-only status-update form, and cannot
  reach `/app/staff/` (redirected to their own shipment list).

## Next steps

- **Replace the remaining placeholder images.** Most photos are now real —
  extracted from the company profile PDF and saved under
  `static/img/company/` (branded trucks, warehouse, office, staff, IT room,
  Top 100 awards). Only the **Air freight** and **Ocean freight** sections
  (homepage tabs and Services page) still use `picsum.photos` placeholders,
  since no real photo of an Atlas aircraft or vessel was available. Search
  `picsum.photos` in `sitepages/templates/` to find those two spots.
- Wire the WhatsApp Business API in `notifications/tasks.py::_send_via_provider`
  (currently raises `NotImplementedError`).
- Add file-type/size validation and virus scanning to document uploads.
- Move media storage to S3 (or equivalent) via `django-storages` before
  going live with real client uploads.
- Add a `billing` app for invoices.
- Client self-registration (currently client accounts are created by staff
  when converting a quote request).
