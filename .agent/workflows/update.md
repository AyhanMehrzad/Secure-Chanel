---
description: how to update the application with the latest changes from GitHub
---

To update the application to the latest version on your server, follow these steps:

1. **Fetch the latest code**
// turbo
```bash
git pull origin main
```

2. **Re-deploy and Restart the Service**
This command will update the systemd service configuration if needed and restart the backend server.
// turbo
```bash
sudo ./deploy_service.sh
```

3. **(Optional) Rebuild Frontend**
If you have made changes to the frontend, you should also rebuild the static files:
// turbo
```bash
cd frontend && npm install && npm run build
```

4. **Verify Service Status**
// turbo
```bash
sudo systemctl status messageapp.service
```
