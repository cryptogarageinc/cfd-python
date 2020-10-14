# -*- coding: utf-8 -*-
##
# @file key.py
# @brief key function implements file.
# @note Copyright 2020 CryptoGarage
from .util import get_util, CfdError, to_hex_string, CfdErrorCode, JobHandle
import hashlib
from enum import Enum


##
# @class Network
# @brief Network Type
class Network(Enum):
    ##
    # Network: Bitcoin Mainnet
    MAINNET = 0
    ##
    # Network: Bitcoin Testnet
    TESTNET = 1
    ##
    # Network: Bitcoin Regtest
    REGTEST = 2
    ##
    # Network: Liquid LiquidV1
    LIQUID_V1 = 10
    ##
    # Network: Liquid ElementsRegtest
    ELEMENTS_REGTEST = 11
    ##
    # Network: Liquid custom chain
    CUSTOM_CHAIN = 12

    ##
    # @brief get string.
    # @return name.
    def __str__(self):
        return self.name.lower().replace('_', '')

    ##
    # @brief get string.
    # @return name.
    def as_str(self):
        return self.name.lower().replace('_', '')

    ##
    # @brief get object.
    # @param[in] network    network
    # @return object.
    @classmethod
    def get(cls, network):
        if (isinstance(network, Network)):
            return network
        elif (isinstance(network, int)):
            _num = int(network)
            for net in Network:
                if _num == net.value:
                    return net
        else:
            _network = str(network).lower()
            for net in Network:
                if _network == net.name.lower():
                    return net
            if _network == 'liquidv1':
                return Network.LIQUID_V1
            elif _network in {'elementsregtest', 'liquidregtest'}:
                return Network.ELEMENTS_REGTEST
        raise CfdError(
            error_code=1,
            message='Error: Invalid network type.')

    ##
    # @brief get mainchain object.
    # @param[in] network    network
    # @return object.
    @classmethod
    def get_mainchain(cls, network):
        _network = cls.get(network)
        if _network == Network.LIQUID_V1:
            _network = Network.MAINNET
        elif _network in {Network.ELEMENTS_REGTEST, Network.CUSTOM_CHAIN}:
            _network = Network.TESTNET
        return _network


##
# @class SigHashType
# @brief Signature hash type
class SigHashType(Enum):
    ##
    # SigHashType: all
    ALL = 1
    ##
    # SigHashType: none
    NONE = 2
    ##
    # SigHashType: single
    SINGLE = 3
    ##
    # SigHashType: all+anyoneCanPay
    ALL_PLUS_ANYONE_CAN_PAY = 0x81
    ##
    # SigHashType: none+anyoneCanPay
    NONE_PLUS_ANYONE_CAN_PAY = 0x82
    ##
    # SigHashType: single+anyoneCanPay
    SINGLE_PLUS_ANYONE_CAN_PAY = 0x83

    ##
    # @brief get string.
    # @return name.
    def __str__(self):
        return self.name.lower().replace('_', '')

    ##
    # @brief get string.
    # @return name.
    def as_str(self):
        return self.name.lower().replace('_', '')

    ##
    # @brief get type value.
    # @return value.
    def get_type(self):
        return self.value & 0x0f

    ##
    # @brief get anyone can pay flag.
    # @retval True      anyone can pay is true.
    # @retval False     anyone can pay is false.
    def anyone_can_pay(self):
        return self.value >= 0x80

    ##
    # @brief get type object.
    # @return object.
    def get_type_object(self):
        return self.get(self.get_type())

    ##
    # @brief get object.
    # @param[in] sighashtype        sighash type
    # @param[in] anyone_can_pay     anyone can pay flag
    # @return object.
    @classmethod
    def get(cls, sighashtype, anyone_can_pay=False):
        if (isinstance(sighashtype, SigHashType)):
            if anyone_can_pay is True:
                return cls.get(sighashtype.value | 0x80)
            else:
                return sighashtype
        elif (isinstance(sighashtype, int)):
            _num = int(sighashtype)
            if anyone_can_pay is True:
                _num |= 0x80
            for hash_type in SigHashType:
                if _num == hash_type.value:
                    return hash_type
        else:
            _hash_type = str(sighashtype).lower()
            if (anyone_can_pay is True) and (
                    _hash_type.find('_plus_anyone_can_pay') == -1):
                _hash_type += '_plus_anyone_can_pay'
            for hash_type in SigHashType:
                if _hash_type == hash_type.name.lower():
                    return hash_type
        raise CfdError(
            error_code=1,
            message='Error: Invalid sighash type.')


##
# @class Privkey
# @brief privkey class.
class Privkey:
    ##
    # @var hex
    # privkey hex
    ##
    # @var wif
    # wallet import format
    ##
    # @var network
    # network type.
    ##
    # @var is_compressed
    # pubkey compressed flag
    ##
    # @var wif_first
    # wif set flag.
    ##
    # @var pubkey
    # pubkey

    ##
    # @brief generate key pair.
    # @param[in] is_compressed  pubkey compressed
    # @param[in] network        network type
    # @return private key
    @classmethod
    def generate(cls, is_compressed=True, network=Network.MAINNET):
        _network = Network.get_mainchain(network)
        util = get_util()
        with util.create_handle() as handle:
            _, _, wif = util.call_func(
                'CfdCreateKeyPair', handle.get_handle(),
                is_compressed, _network.value)
            return Privkey(wif=wif)

    ##
    # @brief create privkey from hex string.
    # @param[in] hex            hex string
    # @param[in] network        network type
    # @param[in] is_compressed  pubkey compressed
    # @return private key
    @classmethod
    def from_hex(cls, hex, network=Network.MAINNET, is_compressed=True):
        return Privkey(hex=hex, network=network,
                       is_compressed=is_compressed)

    ##
    # @brief create privkey from hex string.
    # @param[in] wif            wallet import format
    # @return private key
    @classmethod
    def from_wif(cls, wif):
        return Privkey(wif=wif)

    ##
    # @brief constructor.
    # @param[in] wif            wif
    # @param[in] hex            hex
    # @param[in] network        network
    # @param[in] is_compressed  pubkey compressed
    def __init__(
            self,
            wif='',
            hex='',
            network=Network.MAINNET,
            is_compressed=True):
        self.hex = to_hex_string(hex)
        self.wif = wif
        self.network = Network.get_mainchain(network)
        self.is_compressed = is_compressed
        util = get_util()
        with util.create_handle() as handle:
            if len(wif) == 0:
                self.wif_first = False
                self.wif = util.call_func(
                    'CfdGetPrivkeyWif', handle.get_handle(),
                    self.hex, self.network.value, is_compressed)
            else:
                self.wif_first = True
                self.hex, self.network, \
                    self.is_compressed = util.call_func(
                        'CfdParsePrivkeyWif', handle.get_handle(),
                        self.wif)
                self.network = Network.get_mainchain(self.network)
            self.pubkey = util.call_func(
                'CfdGetPubkeyFromPrivkey', handle.get_handle(),
                self.hex, '', self.is_compressed)

    ##
    # @brief get string.
    # @return pubkey hex.
    def __str__(self):
        return self.wif if (self.wif_first) else self.hex

    ##
    # @brief add tweak.
    # @param[in] tweak     tweak bytes. (32 byte)
    # @return tweaked private key
    def add_tweak(self, tweak):
        _tweak = to_hex_string(tweak)
        util = get_util()
        with util.create_handle() as handle:
            _key = util.call_func(
                'CfdPrivkeyTweakAdd', handle.get_handle(),
                self.hex, _tweak)
            return Privkey(
                hex=_key, network=self.network,
                is_compressed=self.is_compressed)

    ##
    # @brief mul tweak.
    # @param[in] tweak     tweak bytes. (32 byte)
    # @return tweaked private key
    def mul_tweak(self, tweak):
        _tweak = to_hex_string(tweak)
        util = get_util()
        with util.create_handle() as handle:
            _key = util.call_func(
                'CfdPrivkeyTweakMul', handle.get_handle(),
                self.hex, _tweak)
            return Privkey(
                hex=_key, network=self.network,
                is_compressed=self.is_compressed)

    ##
    # @brief negate.
    # @return negated private key
    def negate(self):
        util = get_util()
        with util.create_handle() as handle:
            _key = util.call_func(
                'CfdNegatePrivkey', handle.get_handle(), self.hex)
            return Privkey(
                hex=_key, network=self.network,
                is_compressed=self.is_compressed)

    ##
    # @brief calculate ec-signature.
    # @param[in] sighash   sighash
    # @param[in] grind_r   grind-r flag
    # @return signature
    def calculate_ec_signature(self, sighash, grind_r=True):
        _sighash = to_hex_string(sighash)
        util = get_util()
        with util.create_handle() as handle:
            signature = util.call_func(
                'CfdCalculateEcSignature', handle.get_handle(),
                _sighash, self.hex, '', self.network.value, grind_r)
            sign = SignParameter(signature)
            sign.use_der_encode = True
            return sign


##
# @class Pubkey
# @brief pubkey class.
class Pubkey:
    ##
    # @var _hex
    # pubkey hex

    ##
    # @brief combine pubkey.
    # @param[in] pubkey_list   pubkey list
    # @return combined pubkey
    @classmethod
    def combine(cls, pubkey_list):
        if (isinstance(pubkey_list, list) is False) or (
                len(pubkey_list) <= 1):
            raise CfdError(
                error_code=1,
                message='Error: Invalid pubkey list.')
        util = get_util()
        with util.create_handle() as handle:
            word_handle = util.call_func(
                'CfdInitializeCombinePubkey', handle.get_handle())
            with JobHandle(handle, word_handle,
                           'CfdFreeCombinePubkeyHandle') as key_handle:
                for pubkey in pubkey_list:
                    util.call_func(
                        'CfdAddCombinePubkey',
                        handle.get_handle(), key_handle.get_handle(),
                        to_hex_string(pubkey))

                _key = util.call_func(
                    'CfdFinalizeCombinePubkey',
                    handle.get_handle(), key_handle.get_handle())
                return Pubkey(_key)

    ##
    # @brief constructor.
    # @param[in] pubkey     pubkey
    def __init__(self, pubkey):
        self._hex = to_hex_string(pubkey)
        # validate
        util = get_util()
        with util.create_handle() as handle:
            util.call_func(
                'CfdCompressPubkey', handle.get_handle(), self._hex)

    ##
    # @brief get string.
    # @return pubkey hex.
    def __str__(self):
        return self._hex

    ##
    # @brief compress pubkey.
    # @return compressed pubkey.
    def compress(self):
        util = get_util()
        with util.create_handle() as handle:
            _pubkey = util.call_func(
                'CfdCompressPubkey', handle.get_handle(), self._hex)
        return Pubkey(_pubkey)

    ##
    # @brief uncompress pubkey.
    # @return uncompressed pubkey.
    def uncompress(self):
        util = get_util()
        with util.create_handle() as handle:
            _pubkey = util.call_func(
                'CfdUncompressPubkey', handle.get_handle(), self._hex)
        return Pubkey(_pubkey)

    ##
    # @brief add tweak.
    # @param[in] tweak     tweak bytes. (32 byte)
    # @return tweaked public key
    def add_tweak(self, tweak):
        _tweak = to_hex_string(tweak)
        util = get_util()
        with util.create_handle() as handle:
            _pubkey = util.call_func(
                'CfdPubkeyTweakAdd', handle.get_handle(),
                self._hex, _tweak)
            return Pubkey(_pubkey)

    ##
    # @brief mul tweak.
    # @param[in] tweak     tweak bytes. (32 byte)
    # @return tweaked public key
    def mul_tweak(self, tweak):
        _tweak = to_hex_string(tweak)
        util = get_util()
        with util.create_handle() as handle:
            _pubkey = util.call_func(
                'CfdPubkeyTweakMul', handle.get_handle(),
                self._hex, _tweak)
            return Pubkey(_pubkey)

    ##
    # @brief negate.
    # @return negated public key
    def negate(self):
        util = get_util()
        with util.create_handle() as handle:
            _pubkey = util.call_func(
                'CfdNegatePubkey', handle.get_handle(), self._hex)
            return Pubkey(_pubkey)

    ##
    # @brief verify ec-signature.
    # @param[in] sighash    sighash
    # @param[in] signature  signature
    # @retval True      Verify success.
    # @retval False     Verify fail.
    def verify_ec_signature(self, sighash, signature):
        try:
            util = get_util()
            with util.create_handle() as handle:
                util.call_func(
                    'CfdVerifyEcSignature', handle.get_handle(),
                    sighash, self._hex, signature)
            return True
        except CfdError as err:
            if err.error_code == CfdErrorCode.SIGN_VERIFICATION.value:
                return False
            else:
                raise err


##
# @class SignParameter
# @brief sign parameter container.
class SignParameter:
    ##
    # @var hex
    # hex data
    ##
    # @var related_pubkey
    # related pubkey for multisig
    ##
    # @var sighashtype
    # sighash type
    ##
    # @var use_der_encode
    # use der encode.

    ##
    # @brief encode signature to der.
    # @param[in] signature      signature
    # @param[in] sighashtype    sighash type
    # @return der encoded signature
    @classmethod
    def encode_by_der(cls, signature, sighashtype=SigHashType.ALL):
        _signature = to_hex_string(signature)
        _sighashtype = SigHashType.get(sighashtype)
        util = get_util()
        with util.create_handle() as handle:
            der_signature = util.call_func(
                'CfdEncodeSignatureByDer', handle.get_handle(),
                _signature, _sighashtype.get_type(),
                _sighashtype.anyone_can_pay())
        return SignParameter(der_signature, '', _sighashtype)

    ##
    # @brief decode signature from der.
    # @param[in] signature      signature
    # @return der decoded signature
    @classmethod
    def decode_from_der(cls, signature):
        der_signature = to_hex_string(signature)
        util = get_util()
        with util.create_handle() as handle:
            _signature, sighashtype, anyone_can_pay = util.call_func(
                'CfdDecodeSignatureFromDer', handle.get_handle(),
                der_signature)
            _sighashtype = SigHashType.get(sighashtype, anyone_can_pay)
        return SignParameter(_signature, '', _sighashtype)

    ##
    # @brief normalize signature.
    # @param[in] signature      signature
    # @return normalized signature
    @classmethod
    def normalize(cls, signature):
        _signature = to_hex_string(signature)
        _sighashtype = SigHashType.ALL
        if isinstance(signature, SignParameter):
            _sighashtype = signature.sighashtype
        util = get_util()
        with util.create_handle() as handle:
            normalize_sig = util.call_func(
                'CfdNormalizeSignature', handle.get_handle(), _signature)
        return SignParameter(normalize_sig, '', _sighashtype)

    ##
    # @brief constructor.
    # @param[in] data               sign data
    # @param[in] related_pubkey     related_pubkey
    # @param[in] sighashtype        sighash type
    # @param[in] use_der_encode     use der encode
    def __init__(self, data, related_pubkey='',
                 sighashtype=SigHashType.ALL, use_der_encode=False):
        self.hex = to_hex_string(data)
        self.related_pubkey = related_pubkey
        self.sighashtype = SigHashType.get(sighashtype)
        self.use_der_encode = use_der_encode

    ##
    # @brief get string.
    # @return sing data hex.
    def __str__(self):
        return self.hex

    ##
    # @brief set der encode flag.
    # @return void
    def set_der_encode(self):
        self.use_der_encode = True


##
# @class EcdsaAdaptor
# @brief Ecdsa adaptor.
class EcdsaAdaptor:
    ##
    # @brief sign.
    # @param[in] message        message (byte or string)
    # @param[in] secret_key     secret key
    # @param[in] adaptor        adaptor bytes
    # @param[in] is_message_hashed      message is hashed byte.
    # @retval result[0]   adaptor signature
    # @retval result[1]   adaptor proof
    @classmethod
    def sign(cls, message, secret_key, adaptor,
             is_message_hashed=True):
        msg = message
        if (not is_message_hashed) and isinstance(message, str):
            m = hashlib.sha256()
            m.update(message.encode('utf-8'))
            msg = m.hexdigest()
        _msg = to_hex_string(msg)
        _sk = to_hex_string(secret_key)
        _adaptor = to_hex_string(adaptor)
        util = get_util()
        with util.create_handle() as handle:
            signature, proof = util.call_func(
                'CfdSignEcdsaAdaptor', handle.get_handle(),
                _msg, _sk, _adaptor)
        return signature, proof

    ##
    # @brief adapt.
    # @param[in] adaptor_signature  adaptor signature
    # @param[in] adaptor_secret     adaptor secret key
    # @return adapted signature
    @classmethod
    def adapt(cls, adaptor_signature, adaptor_secret):
        _sig = to_hex_string(adaptor_signature)
        _sk = to_hex_string(adaptor_secret)
        util = get_util()
        with util.create_handle() as handle:
            signature = util.call_func(
                'CfdAdaptEcdsaAdaptor', handle.get_handle(), _sig, _sk)
        return signature

    ##
    # @brief extract secret.
    # @param[in] adaptor_signature      adaptor signature
    # @param[in] signature              signature
    # @param[in] adaptor                adaptor bytes
    # @return adaptor secret key
    @classmethod
    def extract_secret(cls, adaptor_signature, signature, adaptor):
        _adaptor_signature = to_hex_string(adaptor_signature)
        _signature = to_hex_string(signature)
        _adaptor = to_hex_string(adaptor)
        util = get_util()
        with util.create_handle() as handle:
            adaptor_secret = util.call_func(
                'CfdExtractEcdsaAdaptorSecret', handle.get_handle(),
                _adaptor_signature, _signature, _adaptor)
        return Privkey(hex=adaptor_secret)

    ##
    # @brief verify.
    # @param[in] adaptor_signature      adaptor signature
    # @param[in] proof                  adaptor proof
    # @param[in] adaptor                adaptor bytes
    # @param[in] message                message (byte or string)
    # @param[in] pubkey                 public key
    # @param[in] is_message_hashed      message is hashed byte.
    # @retval True      Verify success.
    # @retval False     Verify fail.
    @classmethod
    def verify(cls, adaptor_signature, proof, adaptor, message, pubkey,
               is_message_hashed=True):
        msg = message
        if (not is_message_hashed) and isinstance(message, str):
            m = hashlib.sha256()
            m.update(message.encode('utf-8'))
            msg = m.hexdigest()
        _msg = to_hex_string(msg)
        _adaptor_signature = to_hex_string(adaptor_signature)
        _proof = to_hex_string(proof)
        _adaptor = to_hex_string(adaptor)
        _pk = to_hex_string(pubkey)
        util = get_util()
        with util.create_handle() as handle:
            try:
                util.call_func(
                    'CfdVerifyEcdsaAdaptor', handle.get_handle(),
                    _adaptor_signature, _proof, _adaptor, _msg, _pk)
                return True
            except CfdError as err:
                if err.error_code == CfdErrorCode.SIGN_VERIFICATION.value:
                    return False
                else:
                    raise err


##
# @class SchnorrPubkey
# @brief Schnorr public key.
class SchnorrPubkey:
    ##
    # @var hex
    # hex data

    ##
    # @brief create SchnorrPubkey from privkey.
    # @param[in] privkey      private key
    # @return SchnorrPubkey
    @classmethod
    def from_privkey(cls, privkey):
        if isinstance(privkey, Privkey):
            _privkey = privkey.hex
        elif isinstance(privkey, str) and (len(privkey) != 64):
            _sk = Privkey(wif=privkey)
            _privkey = _sk.hex
        else:
            _privkey = to_hex_string(privkey)
        util = get_util()
        with util.create_handle() as handle:
            pubkey = util.call_func(
                'CfdGetSchnorrPubkeyFromPrivkey', handle.get_handle(),
                _privkey)
            return SchnorrPubkey(pubkey)

    ##
    # @brief constructor.
    # @param[in] data      pubkey data
    def __init__(self, data):
        self.hex = to_hex_string(data)
        if len(self.hex) != 64:
            raise CfdError(
                error_code=1, message='Error: Invalid schnorr pubkey.')

    ##
    # @brief get string.
    # @return pubkey hex.
    def __str__(self):
        return self.hex


##
# @class SchnorrSignature
# @brief Schnorr signature.
class SchnorrSignature:
    ##
    # @var signature
    # signature data
    ##
    # @var nonce
    # nonce data
    ##
    # @var key
    # key data

    ##
    # @brief constructor.
    # @param[in] signature      signature
    def __init__(self, signature):
        self.signature = to_hex_string(signature)
        util = get_util()
        with util.create_handle() as handle:
            self.nonce, self.key = util.call_func(
                'CfdSplitSchnorrSignature', handle.get_handle(),
                self.signature)
            self.nonce = SchnorrPubkey(self.nonce)
            self.key = Privkey(hex=self.key)

    ##
    # @brief get string.
    # @return signature hex.
    def __str__(self):
        return self.signature


##
# @class SchnorrUtil
# @brief Schnorr utility.
class SchnorrUtil:
    ##
    # @brief sign.
    # @param[in] message            message (byte or string)
    # @param[in] secret_key         secret key
    # @param[in] aux_rand           random bytes
    # @param[in] nonce              nonce bytes
    # @param[in] is_message_hashed  message is hashed byte.
    # @return signature
    @classmethod
    def sign(cls, message, secret_key, aux_rand='', nonce='',
             is_message_hashed=True):
        msg = message
        if (not is_message_hashed) and isinstance(message, str):
            m = hashlib.sha256()
            m.update(message.encode('utf-8'))
            msg = m.hexdigest()
        _msg = to_hex_string(msg)
        _sk = to_hex_string(secret_key)
        _rand = to_hex_string(aux_rand)
        _nonce = to_hex_string(nonce)
        util = get_util()
        with util.create_handle() as handle:
            if _nonce != '':
                signature = util.call_func(
                    'CfdSignSchnorrWithNonce', handle.get_handle(),
                    _msg, _sk, _nonce)
            else:
                signature = util.call_func(
                    'CfdSignSchnorr', handle.get_handle(), _msg, _sk, _rand)
        return SchnorrSignature(signature)

    ##
    # @brief compute sigpoint.
    # @param[in] message            message (byte or string)
    # @param[in] nonce              nonce bytes
    # @param[in] pubkey             public key
    # @param[in] is_message_hashed  message is hashed byte.
    # @return signature
    @classmethod
    def compute_sig_point(cls, message, nonce, pubkey,
                          is_message_hashed=True):
        msg = message
        if (not is_message_hashed) and isinstance(message, str):
            m = hashlib.sha256()
            m.update(message.encode('utf-8'))
            msg = m.hexdigest()
        _msg = to_hex_string(msg)
        _nonce = to_hex_string(nonce)
        _pubkey = to_hex_string(pubkey)
        util = get_util()
        with util.create_handle() as handle:
            sig_point = util.call_func(
                'CfdComputeSchnorrSigPoint', handle.get_handle(),
                _msg, _nonce, _pubkey)
        return Pubkey(sig_point)

    ##
    # @brief verify.
    # @param[in] signature          signature
    # @param[in] message            message (byte or string)
    # @param[in] pubkey             public key
    # @param[in] is_message_hashed  message is hashed byte.
    # @retval True      Verify success.
    # @retval False     Verify fail.
    @classmethod
    def verify(cls, signature, message, pubkey,
               is_message_hashed=True):
        msg = message
        if (not is_message_hashed) and isinstance(message, str):
            m = hashlib.sha256()
            m.update(message.encode('utf-8'))
            msg = m.hexdigest()
        _msg = to_hex_string(msg)
        _signature = to_hex_string(signature)
        _pk = to_hex_string(pubkey)
        util = get_util()
        with util.create_handle() as handle:
            try:
                util.call_func(
                    'CfdVerifySchnorr', handle.get_handle(),
                    _signature, _msg, _pk)
                return True
            except CfdError as err:
                if err.error_code == CfdErrorCode.SIGN_VERIFICATION.value:
                    return False
                else:
                    raise err


##
# All import target.
__all__ = [
    'Network',
    'SigHashType',
    'Privkey',
    'Pubkey',
    'SignParameter',
    'EcdsaAdaptor',
    'SchnorrPubkey',
    'SchnorrSignature',
    'SchnorrUtil'
]
