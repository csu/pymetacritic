sudo apt-get update
sudo apt-get install -y git
sudo apt-get install -y python-pip

git clone https://github.com/csu/pymetacritic.git
cd pymetacritic

pip install virtualenv
virtualenv env
source env/bin/activate
pip install -r requirements.txt

screen -S scraper -d -m python scraper.py "$1" "$2"
echo "Scraper started from $1 to $2."