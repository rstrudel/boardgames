# Boardgames

## Setup
Go to the root of the repository, then run:
```
pip install .
```

## Play codenames
To play codenames through a facebook chat, run:

```
python -m boardgames.codenames.play --login $EMAIL --thread $THREAD_ID
```

To get a thread id, go to messenger in full screen mode then go to the thread of interest, its id will be written at the end of the url.
