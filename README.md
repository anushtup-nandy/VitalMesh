# VitalMesh

Currently has 2 agents 
1. coral medical triage agent
2. coral voice agent

## Run:
```bash
# clone 
git clone git@github.com:anushtup-nandy/VitalMesh.git

#give access
chmod +x ./start.sh

#run
./start.sh
```
- Before doing this, update the API keys (basically createa a `.env` inside your agent's repo and follow the instructions inside the coral docs)
- this should open up 2 terminals and you should be able to speak to your agent!

Coral docs: https://github.com/Coral-Protocol/Coral-MedicalOfficeTriage-Agent

## Issues:
1. Medical triage agent does not work in multi-agent scenarios
2. Voice Interface agent needs openai, does not run with anything else