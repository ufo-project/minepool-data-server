# minepool-data-server
Data server for mining pool


# Install requirement

```
sudo apt install python3 python3-venv virtualenv git

git clone https://github.com/ufo-project/minepool-data-server.git
cd minepool-data-server

virtualenv -p /usr/bin/python3 env-py3
cd env-py3
source bin/activate

pip install -r requirements.txt
```

# Run data server

```
cd ..
python server_main.py
```
