# Backend Deployment Guide (Google Cloud Run)

This guide will help you deploy the Growgent backend to a live, scalable, and free-tier environment using Google Cloud Run and Supabase.

---

## Prerequisites

- A Google Cloud Account (with billing enabled)
- A Supabase Account
- [Google Cloud CLI (`gcloud`)](https://cloud.google.com/sdk/docs/install) installed and authenticated
- Docker Desktop installed and running
- Git and the project repository cloned locally

---

## Quick Start (Cloud Run + Supabase - Recommended)

This method provides a production-grade, serverless deployment with a managed PostGIS database, all within free-tier limits for a hackathon-scale project.

### 1. Set Up the Supabase Database

This will be our free, managed PostgreSQL database with PostGIS support.

1.  **Create a New Project** on [supabase.com](https://supabase.com).
2.  Give it a name and generate a **strong password**. Save this password securely.
3.  Choose a **Region** (e.g., `US East (North Virginia)`).
4.  Once the project is created, go to the **SQL Editor**.
5.  Run the following query to enable PostGIS:
    ```sql
    create extension if not exists postgis with schema extensions;
    ```
6.  Go to **Project Settings > Database** and find the **Connection string**. Copy the **`psql`** URI. It will look like `postgresql://postgres:[YOUR-PASSWORD]@db.project-ref.supabase.co:5432/postgres`.

### 2. Set Up Google Cloud Project

Prepare your Google Cloud environment using the `gcloud` CLI.

```bash
# Replace [YOUR-PROJECT-ID] with your actual GCP Project ID
gcloud config set project [YOUR-PROJECT-ID]

# Enable the necessary APIs for building and running containers
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```

### 3. Create the Artifact Registry Repository

This is a one-time setup to create a private repository to store your Docker images.

```bash
gcloud artifacts repositories create growgent-repo \
  --repository-format=docker \
  --location=us-central1 \
  --description="Growgent backend repository"
```

### 4. Build and Push the Docker Image

This command packages your application into a container and pushes it to the repository you just created. Run this from the `Backend/` directory.

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/[YOUR-PROJECT-ID]/growgent-repo/growgent-backend:latest
```

### 5. Deploy to Cloud Run

This command takes your container image and deploys it as a live, public web service.

- **Replace `[YOUR-PROJECT-ID]`**.
- **Replace `[YOUR-SUPABASE-PASSWORD]`** with the password from Step 1.
- **Replace `[YOUR-SUPABASE-HOSTNAME]`** with the hostname from your Supabase connection string.

```bash
gcloud run deploy growgent-backend \
  --image us-central1-docker.pkg.dev/[YOUR-PROJECT-ID]/growgent-repo/growgent-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-SUPABASE-PASSWORD]@[YOUR-SUPABASE-HOSTNAME]:5432/postgres"
```

### 6. Verify Deployment

The command will output a **Service URL**. Test it to confirm success.

```bash
# Test the health endpoint (replace with your URL)
curl https://your-service-url.run.app/health
# Expected output: {"status":"healthy"}

# Open the documentation in your browser
# https://your-service-url.run.app/docs
```

---

## Redeploying Updates

To deploy changes from your local machine, simply repeat **Steps 4 and 5**.

1.  **Rebuild the image** with your new code:
    ```bash
    gcloud builds submit --tag us-central1-docker.pkg.dev/[YOUR-PROJECT-ID]/growgent-repo/growgent-backend:latest
    ```

2.  **Redeploy the service** with the new image:
    ```bash
    gcloud run deploy growgent-backend \
      --image us-central1-docker.pkg.dev/[YOUR-PROJECT-ID]/growgent-repo/growgent-backend:latest \
      --platform managed \
      --region us-central1 \
      --allow-unauthenticated \
      --set-env-vars="DATABASE_URL=postgresql+asyncpg://postgres:[YOUR-SUPABASE-PASSWORD]@[YOUR-SUPABASE-HOSTNAME]:5432/postgres"
    ```

Cloud Run will perform a zero-downtime update.

---

## Troubleshooting

### `PERMISSION_DENIED` during `gcloud builds submit`
**Error**: `The caller does not have permission.`
**Solution**: Your Google Cloud user account needs the correct IAM role.
1.  Go to **IAM & Admin > IAM** in the Google Cloud Console.
2.  Click **"Grant Access"**.
3.  Add your email as the principal.
4.  Assign the role **"Cloud Build Editor"**.

### `Repository not found` during `gcloud builds submit`
**Error**: `name unknown: Repository "growgent-repo" not found.`
**Solution**: You haven't created the Artifact Registry repository yet. Run the command from **Step 3**.

### Service Fails to Start (Check Logs)
**Symptom**: The `gcloud run deploy` command times out or reports the revision is not healthy.
**Solution**: Check the logs for the specific error.
1.  Go to the **Cloud Run** page in the Google Cloud Console.
2.  Click on your `growgent-backend` service.
3.  Go to the **"Logs"** tab to see the Python traceback.

### `Unknown host` / `Network is unreachable`
**Symptom**: Your local Docker tests fail, or the deployment logs show DNS errors.
**Solution**: This is a local networking issue.
1.  Confirm you can reach the database from your machine using `nc -zv [YOUR-SUPABASE-HOSTNAME] 5432`.
2.  If you are on a restrictive network (like a university or corporate VPN), switch to a different network (like a mobile hotspot) to test and deploy.
3.  As a last resort, flushing your local DNS cache can help: `sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder`.

---

## Production Considerations

### Security

- **Use Secret Manager**: Instead of passing the `DATABASE_URL` directly, store it in Google Secret Manager and grant your Cloud Run service access to it. This is more secure.
- **Restrict Ingress**: In the Cloud Run service settings, change "Ingress" from "Allow all traffic" to "Allow internal traffic and traffic from Cloud Load Balancing" and put it behind a load balancer for production.
- **IAM Roles**: Use the principle of least privilege. Create a dedicated service account for your Cloud Run service with only the permissions it needs.

### CI/CD
- Set up a **GitHub Actions** workflow to automatically build and deploy your application on every push to the `main` branch. This removes the need for manual redeployments.

---

## Next Steps

1.  ✅ Backend is deployed and live.
2.  🔄 Connect your frontend application to the public Service URL.
3.  🔄 (Optional) Set up a CI/CD pipeline for automatic deployments.

---

## Quick Reference

| Task | Command |
|------|---------|
| Set Project | `gcloud config set project [ID]` |
| Create Repo | `gcloud artifacts repositories create ...` |
| Build Image | `gcloud builds submit --tag ...` |
| Deploy Service | `gcloud run deploy growgent-backend ...` |
| List Services | `gcloud run services list` |
| View Logs | Check the "Logs" tab in the Cloud Run UI |

---

**You're all set!** 🎉 Your backend is deployed on a scalable, serverless platform.