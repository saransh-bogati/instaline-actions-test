# Instabot RASA Conversational Chatbot

This repo contains [rasa](https://rasa.com/) implementation for the chatbot.

# Setup

0. Prerequisities:
    1. install `python 3.8 (< 3.9), pipenv (for virtual environment)`
    2. Create Virtual Environment. E.g. `pipenv shell --python 3.8`
    3. Install Dependencies from Pipfile (Also includes a spacy trained english model). `pipenv install`
1. Train a Rasa model (step required for first time and will create files under models directory): `rasa train`
2. Start Rasa action server for custom actions. `rasa actions`
3. Start Rasa. **Either One of following**
    1. Rasa Shell for terminal interaction: `rasa shell`
    2. Rasa Server for server interaction: `rasa run`

# References

https://rasa.com/docs/rasa/installation

https://rasa.com/docs/rasa/command-line-interface

https://rasa.com/docs/action-server


