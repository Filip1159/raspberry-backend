# MediaMTX

Download the MediaMTX v1.15.3. The config file format may differ between versions, so let's stick to this one. All commands should be ran at `/`

```bash
sudo wget https://github.com/bluenviron/mediamtx/releases/download/v1.15.3/mediamtx_v1.15.3_linux_armv7.tar.gz
```

Extract files to `/mediamtx` directory

```bash
sudo tar xzvf mediamtx_v1.2.1_linux_armv7.tar.gz
```

Update the `mediamtx.yml` config file.

Run `./mediamtx`. Make sure that there are no warnings in the logs


# Nginx

Install the Nginx v1.22.1 using `apt`

```bash
sudo apt install nginx
```

Update the `/etc/nginx/sites-available/default` file contents.

Make Nginx run on boot

```bash
sudo systemctl enable nginx
```

# Ngrok

[[Raspberry Pi installation guide]](https://ngrok.com/docs/guides/device-gateway/raspberry-pi)
