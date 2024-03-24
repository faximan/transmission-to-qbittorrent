# Script to mass replace a tracker URL in all applicable torrents.

from datetime import datetime
import qbittorrentapi

_OLD = "<fill>"
_NEW = "<fill>"

def change_trackers(qbt_client, old, new):
    for torrent in qbt_client.torrents_info():
        for tracker in torrent.trackers:
            if tracker.url == old:
                # Comment out the following for dry run
                torrent.remove_trackers(urls=[tracker.url])
                torrent.add_trackers(urls=[new])

                print(f"Renamed {old} to {new} for {torrent.name}")

# See example with credentials at https://github.com/rmartin16/qbittorrent-api/blob/main/README.md
conn_info = dict(
    host="192.168.2.127",
    port=9090
)
qbt_client = qbittorrentapi.Client(**conn_info)
qbt_client.auth_log_in()

change_trackers(qbt_client, _OLD, _NEW)
