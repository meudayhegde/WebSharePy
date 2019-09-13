# WebSharePy
<b>Flask</b> based web-server  for managing storage over a web-browser through network.

#### Requirements
- Python3 <a href='https://www.python.org/downloads/'>Download latest</a>
- pip3


#### Basic Usage
```
python3 websharepy.py
```
#### Optional
```
python3 websharepy.py [--dir/-d] <directory_to_serve> [--port/-p] <port> [--host/-H] <client_address_to_accept_from>
```
#### Default values
```
--dir $HOME --port 8080 --host 0.0.0.0
```

use ```--host ::``` to run server with IPv6
to access through IPv6, ```http://[IPv6_addrhere]:PORT``` example: ```http://[ffff:4f32:86dc:0000:912a:d4b6:0fe4:1a02]:8080```
to use IPv4 with IPv6 address, ```http://[::ffff:IPv4Addr]:PORT``` example:```http://[::ffff:127.0.0.1]:8080```


#### Features
- Browse the storage from web-browser
- Download files
- Upload files
- Create/Delete folders

#### TODO
- Implement https and Login features for security
- Download folders
- Video/Audio Streaming