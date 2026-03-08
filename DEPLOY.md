# Local

cd siedmiodniowe-cele \
flask run

# VPS

## Initial setup

### Update
sudo apt update && sudo apt upgrade -y

### Prerequisites
sudo apt install python3 python3-pip python3-venv nginx git ufw -y

### Clone repo
cd /var/www \
sudo git clone https://github.com/wojciech-szyba/siedmiodniowe-cele

### Init virtual environment
python3 -m venv venv \
source venv/bin/activate

### Python prerequisites
pip install --upgrade pip \
pip install -r requirements.txt

### Test
gunicorn --bind 0.0.0.0:20259 "siedmiodniowe_cele.app:create_app()

## User settings
sudo chown -R webapp:www-data /var/www/siedmiodniowe-cele/ \
chmod -R 755 /var/www/siedmiodniowe-cele/ \
chmod 700 /var/www/siedmiodniowe-cele//venv

## Service setup (gunicorn)
nano /etc/systemd/system/siedmiodniowe.service \
sudo systemctl daemon-reload && sudo systemctl restart wall-stash
