if [[ $VIRTUAL_ENV != "" ]]; then
    echo "deactivate first"
    exit 1
fi

source $(which virtualenvwrapper.sh)
rmvirtualenv sxconsole-lite
mkvirtualenv sxconsole-lite

set -e

echo "Installing python packages"
workon sxconsole
pip install -r dev_requirements.txt

# Setup carbon
echo "Setting up local carbon & whisper"
pip install carbon \
    --install-option="--install-lib=${VIRTUAL_ENV}/lib/python2.7/site-packages" \
    --install-option="--prefix=${VIRTUAL_ENV}"
pip install whisper
cp carbon/config/* "${VIRTUAL_ENV}/conf/"
carbon-cache.py start

echo "Installing npm packages"
npm install

echo "Processing assets"
webpack

echo "All done"
