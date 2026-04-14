# LiveKit Assistant

First, create a virtual environment, update pip, and install the required packages:

```
$ python3 -m venv .venv
$ .\.venv\Scripts\Activate.ps1
$ pip install -U pip
$ pip install -r requirements.txt
```

Then set up the following environment variables:

```
LIVEKIT_URL=...
LIVEKIT_API_KEY=...
LIVEKIT_API_SECRET=...
DEEPGRAM_API_KEY=...
GOOGLE_API_KEY=...
```

Notes:
- Do not hardcode secrets in source code.
- This project includes `.env.example` as a template you can copy to `.env`.

PowerShell example:

```powershell
$env:LIVEKIT_URL="wss://your-livekit-host.livekit.cloud"
$env:LIVEKIT_API_KEY="your_livekit_api_key"
$env:LIVEKIT_API_SECRET="your_livekit_api_secret"
$env:DEEPGRAM_API_KEY="your_deepgram_api_key"
$env:GOOGLE_API_KEY="your_google_api_key"
```

Then, run the assistant:

```
$ python3 assistant.py download-files
$ python3 assistant.py start
```

Finally, you can load the [hosted playground](https://agents-playground.livekit.io/) and connect it.