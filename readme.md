# Trovo Webscraper for kdoje.live

Webscraper that saves information about current czech trovo streams to json file.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install foobar.

```bash
pip install selenium
pip install selectolax
```

## Usage

```python
python3 main.py
```

## Raspberry Pi 
### Run script on system start

```
chmod +x main.py
cd /lib/systemd/system
sudo touch trovo_webscraper.service
sudo nano trovo_webscraper.service
```
Paste this to the file
```
[Unit]
Description=Trovo Webscraper
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 <repo-path>/kdojelive-trovo/main.py

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl daemon-reload
sudo systemctl enable trovo_webscraper.service
```

Now you should see:
```
Created symlink /etc/systemd/system/multi-user.target.wants/trovo_webscraper.service → /lib/systemd/system/trovo_webscraper.service.
```
