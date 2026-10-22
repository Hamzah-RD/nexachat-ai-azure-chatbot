# Hamzah RD AI — Azure GPT-4.1-mini chatbot

A lightweight Flask chatbot for Azure App Service (Linux). Includes a responsive interface, English/Urdu/Roman Urdu replies, conversation context, New Chat, and readable API errors. Messages remain in the browser tab's memory and are sent to Azure for responses; refreshing clears the conversation. The last 10 completed exchanges are included in each request.

## Azure par deploy karna

1. Azure Portal > Create a resource > Web App.
2. Apni Azure for Students subscription select karein. Publish: Code; Runtime: a currently supported Python 3.11+ version; OS: Linux.
3. Apni allowed region select karein jahan App Service available ho. Region policy, App Service availability aur model quota alag cheezen hain.
4. Pricing plan khud check karein. Free F1 agar available ho to learning ke liye choose kar sakte hain. Paid plan hosting charges leta hai; Azure model requests ka kharcha alag hota hai. Create karne se pehle portal ki price check karein.
5. Web App khol kar Settings > Environment variables (kuch portal views mein Configuration > Application settings) mein ye add karein:

| Name | Value |
| --- | --- |
| AZURE_OPENAI_API_KEY | Existing Azure AI resource ki key |
| AZURE_OPENAI_ENDPOINT | https://YOUR-RESOURCE.openai.azure.com |
| AZURE_OPENAI_DEPLOYMENT | Existing deployed GPT-4.1-mini ka EXACT deployment name |
| SCM_DO_BUILD_DURING_DEPLOYMENT | true |

`https://YOUR-RESOURCE.services.ai.azure.com` resource endpoint bhi supported hai. Foundry project URL (`.../api/projects/...`) use na karein. Endpoint aur key same resource se hon. Key frontend files mein na dalein.

This app uses Azure's stable `/openai/v1/chat/completions` REST API with the `api-key` header. It does not require an API version setting. The deployment name, not a guessed model ID, is sent as `model`.

6. Settings > Configuration > General settings (or Stack settings) mein Startup Command set karein:

```text
gunicorn --bind 0.0.0.0:8000 --workers 2 --threads 4 --timeout 120 app:app
```

7. Save/Apply karein. Azure Portal mein Cloud Shell kholein, Bash choose karein. Upload file button se **Hamzah_RD_AI_Chatbot.zip** upload karein. ZIP ko extract karne ki zaroorat nahi. Cloud Shell storage create karne ka option aaye to us ka cost check karein; existing setup ya local Azure CLI bhi use kar sakte hain.
8. Neeche placeholders ko apne Web App ke details se replace kar ke run karein (resource group WEB APP ka hai; zaroori nahi AI resource wala ho):

```bash
az account set --subscription "Azure for Students"
az webapp deploy --resource-group YOUR-WEBAPP-RESOURCE-GROUP --name YOUR-WEBAPP-NAME --src-path Hamzah_RD_AI_Chatbot.zip --type zip
```

9. Deployment complete hone par Web App > Overview > Default domain/Browse kholein. Health check: append `/health` to the app URL.
10. Agar startup fail ho: App Service > Log stream dekhein. Build automation setting `true` ho aur ZIP root par `app.py` aur `requirements.txt` hon. `WEBSITE_RUN_FROM_PACKAGE` enable na karein for this Python source build workflow.

## Access

The app has no built-in login. For your own use, configure App Service > Authentication with Microsoft before sharing the URL. Otherwise anyone who can access the app can make model requests using your backend. API keys remain server-side. This is a small demo, not a multi-user production service with application rate limiting or durable storage.

## Optional local Windows PowerShell run

Extract the ZIP and open PowerShell in the extracted folder containing app.py:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
notepad .env
.\.venv\Scripts\python.exe app.py
```

Enter your real values in `.env` and visit http://127.0.0.1:8000. Never upload `.env` or `.venv` in deployment archives.

## Errors

- Missing configuration: add the three Azure settings, then save/restart.
- 401: key and resource endpoint do not match or key is invalid.
- 403: review resource access/network rules; the web app needs access to the AI endpoint.
- 404: verify exact deployment name and resource endpoint.
- 429: model quota/rate limit; credit balance alone does not supply quota.
- Timeout: retry later; check Azure connectivity.

## Sources

https://learn.microsoft.com/en-us/azure/app-service/quickstart-python
https://learn.microsoft.com/en-us/azure/app-service/configure-language-python
https://learn.microsoft.com/en-us/azure/foundry/openai/api-version-lifecycle
https://learn.microsoft.com/en-us/azure/foundry/openai/latest

## Verification

Backend checked locally with Flask's test client and mocked Azure responses. No live Azure request was made without your credentials. Markdown/code in replies is displayed safely as plain text.


## Push this project to GitHub (Windows)

1. Create a new **empty** repository on GitHub, for example `hamzah-rd-ai-chatbot`. Do not add a README or `.gitignore` there if you already have these files locally.
2. Extract `Hamzah_RD_AI_Chatbot.zip` into a folder such as `C:\\Users\\YOUR-WINDOWS-USER\\Projects\\Hamzah_RD_AI_Chatbot`.
3. Open that extracted folder in VS Code, then open **Terminal > New Terminal**.
4. Confirm `.env` is not present in the files you are about to upload. Keep your real Azure key only in a local `.env` file or deployment environment variables. The `.gitignore` already excludes `.env` and `.venv/`.
5. Run these commands, replacing the URL with your own GitHub repository URL:

```powershell
git init
git add .
git status
git commit -m "Initial commit: Hamzah RD AI chatbot"
git branch -M main
git remote add origin https://github.com/YOUR-GITHUB-USERNAME/hamzah-rd-ai-chatbot.git
git push -u origin main
```

If Git asks you to sign in, complete the GitHub authentication prompt. If `git` is not recognized, install Git for Windows first: https://git-scm.com/download/win

**Important:** Never commit your real Azure API key. If a key was accidentally pushed, revoke/rotate it in Azure immediately; deleting it from the latest commit alone may not remove it from Git history.
