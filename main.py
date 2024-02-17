import json
import os
import time
from pathlib import Path
from typing import Literal
from urllib.parse import urlparse

import qbittorrentapi
import transmission_rpc
from qbittorrentapi import TorrentDictionary, TorrentFile

# Get config from config.json.
config: dict = json.load(open('./config.json', 'r'))


def get_qbit():
    # qBittorrent settings.
    qb_host: str = config['qbittorrent']['host']
    qb_port: int = config['qbittorrent']['port']
    qb_username: str | None = config['qbittorrent']['username'] or None
    qb_password: str | None = config['qbittorrent']['password'] or None

    # Connect qBittorrent.
    client = qbittorrentapi.Client(
        host=qb_host,
        port=qb_port,
        username=qb_username,
        password=qb_password
    )

    # Check if login is successful.
    client.auth_log_in()
    print(f"Connected to qBittorrent {client.app.version}, {client.app.webapiVersion}.")

    return client


def get_transmission():
    # Transmission settings.
    tr_protocol: Literal['http', 'https'] = config['transmission']['protocol']
    tr_host: str = config['transmission']['host']
    tr_port: int = config['transmission']['port']
    tr_path: str = config['transmission']['path']
    tr_username: str | None = config['transmission']['username'] or None
    tr_password: str | None = config['transmission']['password'] or None

    # Connect Transmission.
    client = transmission_rpc.Client(
        protocol=tr_protocol,
        username=tr_username,
        password=tr_password,
        host=tr_host,
        port=tr_port,
        path=tr_path
    )

    # Check if login is successful.
    print(f"Connected to Transmission {client.server_version}, {client.protocol_version}.")

    return client


qb_client = get_qbit()
tr_client = get_transmission()


def main():
    # Skip check or not.
    skip_check: bool = config['skip_check']

    # Get all hashes of torrents in qBittorrent.
    qb_torrents = qb_client.torrents_info()
    qb_torrent_hashes: list[str] = [torrent.hash for torrent in qb_torrents]
    print(f"Found {len(qb_torrent_hashes)} torrents in qBittorrent.")

    # Get all torrents in Transmission.
    tr_torrents = tr_client.get_torrents()
    print(f"Fetched {len(tr_torrents)} torrents in Transmission. Transfer them to qBittorrent...")

    for tr_torrent in tr_torrents:
        # Pause the torrent in Transmission.
        tr_client.stop_torrent(tr_torrent.id)

        # Skip torrents that already exist in qBittorrent.
        if tr_torrent.hashString in qb_torrent_hashes:
            print(f"Torrent {tr_torrent.name} already exists in qBittorrent, skipping.")
            continue

        category: str = Path(tr_torrent.download_dir).name

        filepath = config['transmission']['torrent_dir'] + os.path.basename(tr_torrent.torrent_file)

        # Add torrent to qBittorrent.
        qb_client.torrents_add(
            torrent_files=open(filepath, 'rb'),
            save_path=tr_torrent.download_dir,
            rename=tr_torrent.name,
            category=category,
            tags=tr_torrent.labels,
            is_skip_checking=skip_check,
            is_paused=True
        )

        tr_torrent_tracker_domain = urlparse(tr_torrent.trackers[0].announce).netloc
        print(f"Torrent: {tr_torrent.name} Path: {tr_torrent.download_dir} Tracker: {tr_torrent_tracker_domain}")

        time.sleep(1)

# Transmission doesn't differ between torrent and (single) file name. QBittorrent does.
# This can be used to rename the files in Qbit to make it find the files on disk.
# Use with caution, also it does not work well for torrents with a single folder containing
# a single file.
def fix_renamed():
    torrent: TorrentDictionary
    for torrent in qb_client.torrents.info():
        # Set in QBT to avoid messing with good torrents.
        if torrent.tags == "broken":
            files = torrent.files
            if len(files) == 1:
                file: TorrentFile = torrent.files[0]
                torrent.rename_file(file.id, torrent.info.name)
                print(torrent.info.name)


if __name__ == "__main__":
    main()
    # fix_renamed()
