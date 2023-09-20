# SpotilistCLI

## To run
```commandline
python -m venv .venv
source ./venv/bin/activate
pip install -r requirements.txt
python3 app.py <command> <subcommand>
```

## To Do for v1.0.0:
- [ ] Get liked songs
  - https://spotipy.readthedocs.io/en/2.19.0/#spotipy.client.Spotify.current_user_saved_tracks
- [ ] Decompose even further for easier testing
- [ ] Run tests
- [ ] Pipeline to run tests