from __future__ import print_function
from pysnmp.entity.rfc3413.oneliner import cmdgen


def snmp_get_oid_v3(snmp_device, snmp_user, oid='.1.3.6.1.2.1.1.1.0', auth_proto='sha',
                    encrypt_proto='aes128', display_errors=True):
    '''
    Retrieve the given OID

    Default OID is MIB2, sysDescr

    snmp_device is a tuple = (hostname_or_IP, snmp_port)
    snmp_user is a tuple = (user_name, auth_key, encrypt_key)

    Defaults to SHA1-AES128 for authentication + encryption

    auth_proto can be 'sha' or 'md5' or 'none'
    encrypt_proto can be 'aes128', 'aes192', 'aes256', '3des', 'des', or 'none'


    From PySNMP manuals:  http://pysnmp.sourceforge.net/docs/current/security-configuration.html

    Optional authProtocol parameter may be used to specify non-default hash function algorithm.
    Possible values include:
    usmHMACMD5AuthProtocol -- MD5-based authentication protocol
    usmHMACSHAAuthProtocol -- SHA-based authentication protocol
    usmNoAuthProtocol -- no authentication to use (default)

    Optional privProtocol parameter may be used to specify non-default ciphering algorithm.
    Possible values include:
    usmDESPrivProtocol -- DES-based encryption protocol
    usmAesCfb128Protocol -- AES128-based encryption protocol (RFC3826)
    usm3DESEDEPrivProtocol -- triple DES-based encryption protocol (Extended Security Options)
    usmAesCfb192Protocol -- AES192-based encryption protocol (Extended Security Options)
    usmAesCfb256Protocol -- AES256-based encryption protocol (Extended Security Options)
    usmNoPrivProtocol -- no encryption to use (default)

    '''

    # unpack snmp_user
    a_user, auth_key, encrypt_key = snmp_user

    auth_proto_map = {
        'sha':  cmdgen.usmHMACSHAAuthProtocol,
        'md5':  cmdgen.usmHMACMD5AuthProtocol,
        'none': cmdgen.usmNoAuthProtocol
    }

    if auth_proto in auth_proto_map.keys():
        auth_protocol = auth_proto_map[auth_proto]
    else:
        raise ValueError("Invalid authentication protocol specified: %s" % auth_proto)

    encrypt_proto_map = {
        'des':      cmdgen.usmDESPrivProtocol,
        '3des':     cmdgen.usm3DESEDEPrivProtocol,
        'aes128':   cmdgen.usmAesCfb128Protocol,
        'aes192':   cmdgen.usmAesCfb192Protocol,
        'aes256':   cmdgen.usmAesCfb256Protocol,
        'none':     cmdgen.usmNoPrivProtocol,
    }

    if encrypt_proto in encrypt_proto_map.keys():
        encrypt_protocol = encrypt_proto_map[encrypt_proto]
    else:
        raise ValueError("Invalid encryption protocol specified: %s" % encrypt_proto)


    # Create a PYSNMP cmdgen object
    cmd_gen = cmdgen.CommandGenerator()

    (error_detected, error_status, error_index, snmp_data) = cmd_gen.getCmd(

        cmdgen.UsmUserData(a_user, auth_key, encrypt_key,
                           authProtocol=auth_protocol,
                           privProtocol=encrypt_protocol, ),
        cmdgen.UdpTransportTarget(snmp_device),
        oid,
        lookupNames=True, lookupValues=True
    )

    if not error_detected:
        return snmp_data
    else:
        if display_errors:
            print('ERROR DETECTED: ')
            print('    %-16s %-60s' % ('error_message', error_detected))
            print('    %-16s %-60s' % ('error_status', error_status))
            print('    %-16s %-60s' % ('error_index', error_index))
        return None


def snmp_get_oid(a_device, oid='.1.3.6.1.2.1.1.1.0', display_errors=False):
    '''
    Retrieve the given OID

    Default OID is MIB2, sysDescr

    a_device is a tuple = (a_host, community_string, snmp_port)
    '''

    a_host, community_string, snmp_port = a_device
    snmp_target = (a_host, snmp_port)

    # Create a PYSNMP cmdgen object
    cmd_gen = cmdgen.CommandGenerator()

    (error_detected, error_status, error_index, snmp_data) = cmd_gen.getCmd(
        cmdgen.CommunityData(community_string),
        cmdgen.UdpTransportTarget(snmp_target),
        oid,
        lookupNames=True, lookupValues=True
    )

    if not error_detected:
        return snmp_data
    else:
        if display_errors:
            print('ERROR DETECTED: ')
            print('    %-16s %-60s' % ('error_message', error_detected))
            print('    %-16s %-60s' % ('error_status', error_status))
            print('    %-16s %-60s' % ('error_index', error_index))
        return None


def snmp_extract(snmp_data):
    '''
    Unwrap the SNMP response data and return in a readable format

    Assumes only a single list element is returned
    '''

    if len(snmp_data) > 1:
        raise ValueError("snmp_extract only allows a single element")

    if len(snmp_data) == 0:
        return None
    else:
        # Unwrap the data which is returned as a tuple wrapped in a list
        return snmp_data[0][1].prettyPrint()
