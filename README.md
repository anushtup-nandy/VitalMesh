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
python setup.py
# to test:
chmod +x ./run.sh
```

```bash
#get to the root and run
./start.sh
```
- Before doing this, update the API keys (basically createa a `.env` inside your agent's repo and follow the instructions inside the coral docs)
- this should open up 2 terminals and you should be able to speak to your agent!

## TODO:
- [X] Own medical agent
    - [X] Medical agent should be able to take notes
    - [X] Improve note taking!
- [ ] EHR agent
- [ ] Pandas / Data analysis agent

## Issues:
1. Medical triage agent does not work in multi-agent scenarios
