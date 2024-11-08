#!/bin/bash -u

# while :; do sleep 10; done
export WORKDIR_ROOT=private/cfd-python
export WORK_DIR=integration_test
export WORKDIR_PATH=/${WORKDIR_ROOT}/${WORK_DIR}

cd /${WORKDIR_ROOT}
if [ ! -d ${WORK_DIR} ]; then
  mkdir ${WORK_DIR}
fi

uname -a
uname -m

cd ${WORKDIR_PATH}
rm -rf bitcoind_datadir
rm -rf elementsd_datadir

mkdir bitcoind_datadir
chmod 777 bitcoind_datadir
# cp /root/.bitcoin/bitcoin.conf bitcoind_datadir/
cp ./bitcoin.conf bitcoind_datadir/
mkdir elementsd_datadir
chmod 777 elementsd_datadir
# cp /root/.elements/elements.conf elementsd_datadir/
cp ./elements.conf elementsd_datadir/

# boot daemon
bitcoind --regtest -datadir=${WORKDIR_PATH}/bitcoind_datadir
bitcoin-cli --regtest -datadir=${WORKDIR_PATH}/bitcoind_datadir ping > /dev/null 2>&1
while [ $? -ne 0 ]
do
  bitcoin-cli --regtest -datadir=${WORKDIR_PATH}/bitcoind_datadir ping > /dev/null 2>&1
done
echo "start bitcoin node"

elementsd -chain=liquidregtest -datadir=${WORKDIR_PATH}/elementsd_datadir
elements-cli -chain=liquidregtest -datadir=${WORKDIR_PATH}/elementsd_datadir ping > /dev/null 2>&1
while [ $? -ne 0 ]
do
  elements-cli -chain=liquidregtest -datadir=${WORKDIR_PATH}/elementsd_datadir ping > /dev/null 2>&1
done
echo "start elements node"

# load or create wallet
bitcoin-cli --regtest -datadir=${WORKDIR_PATH}/bitcoind_datadir createwallet wallet false false "" false false
elements-cli -chain=liquidregtest -datadir=${WORKDIR_PATH}/elementsd_datadir createwallet wallet false false "" false false
elements-cli -chain=liquidregtest -datadir=${WORKDIR_PATH}/elementsd_datadir createwallet tr_wallet true false "" false true

set -e

python3 --version

pip3 install *.whl
pip3 install python-bitcoinrpc

# cd integration_test

python3 tests/test_bitcoin.py -v
if [ $? -gt 0 ]; then
  cd ../..
  exit 1
fi

python3 tests/test_elements.py -v
elements-cli -chain=liquidregtest -datadir=${WORKDIR_PATH}/elementsd_datadir getblockchaininfo
elements-cli -chain=liquidregtest -datadir=${WORKDIR_PATH}/elementsd_datadir getsidechaininfo
if [ $? -gt 0 ]; then
  cd ../..
  exit 1
fi
