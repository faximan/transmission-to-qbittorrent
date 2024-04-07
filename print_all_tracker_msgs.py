#!/usr/bin/python3
import qbittorrentapi
from getpass import getpass

conn_info = dict(
    host="192.168.2.127",
    port=9090
)
qbt_client = qbittorrentapi.Client(**conn_info)
qbt_client.auth_log_in()

torrents = qbt_client.torrents_info()
for idx, torrent in enumerate(torrents):
    print('Processing %{0}d/%d...'.format(len(str(len(torrents)))) % (idx+1, len(torrents)), end="\r")
    for tracker in torrent.trackers:
        if tracker.status == 0:
            continue
        if len(tracker.msg) > 1:
            print(f'{torrent.hash[-6:]}: {torrent.name} ({tracker.msg})')
print("\nDone.")
