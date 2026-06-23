import datetime, os, pathlib

msg_file = pathlib.Path(".commit_msg")
if msg_file.exists():
    print(msg_file.read_text().strip())
else:
    print(f"chore: daily update {datetime.date.today().isoformat()}")
