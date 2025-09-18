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

# install dependencies
cd agents/medical_agent
conda create --name <env name>
pip install -r requirements.txt

#get to the root and run
./start.sh
```
- Before doing this, update the API keys (basically createa a `.env` inside your agent's repo and follow the instructions inside the coral docs)
- this should open up 2 terminals and you should be able to speak to your agent!

## TODO:
- [ ] Own medical agent
    - [ ] Medical agent should be able to take notes

## Issues:
1. Medical triage agent does not work in multi-agent scenarios
