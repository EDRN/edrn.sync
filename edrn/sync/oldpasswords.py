# encoding: utf-8

u'''Secure old "changeme" passwords'''

from .utils import generatePassword
import argparse, logging, sys, getpass, ldap, re, hashlib

logging.basicConfig(level=logging.INFO, format='%(levelname)-8s %(message)s')

_ldapURL = u'ldaps://edrn.jpl.nasa.gov'
_ldapManager = u'uid=admin,ou=system'
_query = u'(objectClass=edrnPerson)'
_scope = u'one'
_base = u'dc=edrn,dc=jpl,dc=nasa,dc=gov'
_algorithmMatcher = re.compile(ur'\{([^}]+)\}(.+)')
_badPasswd = 'changeme'

_unsaltedBadSHA1Digest = hashlib.sha1(_badPasswd).digest()
_unsaltedBadMD5Digest = hashlib.md5(_badPasswd).digest()

_scopes = {
    u'base': ldap.SCOPE_BASE,
    u'one': ldap.SCOPE_ONELEVEL,
    u'sub': ldap.SCOPE_SUBTREE,
}


_argParser = argparse.ArgumentParser(description=u'Change old "changeme" passwords')
_argParser.add_argument('-D', '--manager-dn', default=_ldapManager, help=u'LDAP manager DN; default %(default)s')
_argParser.add_argument('-w', '--ldap-password', help=u"LDAP server manager password; if not given, you'll be prompted")
_argParser.add_argument('-H', '--url', default=_ldapURL, help=u'URL to LDAP server; default %(default)s')
_argParser.add_argument('-b', '--base', default=_base, help=u'Base DN for search; default %(default)s')
_argParser.add_argument('-q', '--query', default=_query, help=u'User query; default %(default)s')
_argParser.add_argument('-s', '--scope', default=_scope, help=u'Search scope; default %(default)s')


def fixPassword(connection, dn):
    logging.info(u'Fixing bad password for "%s"', dn)
    modlist = [(ldap.MOD_DELETE, 'userPassword', None), (ldap.MOD_ADD, 'userPassword', [generatePassword()])]
    connection.modify_s(dn, modlist)


def fixPasswords(managerDN, managerPassword, ldapURL, query, scope, base):
    connection = ldap.initialize(ldapURL)
    connection.bind_s(managerDN, managerPassword)
    results = connection.search_s(base, scope, query)
    for dn, attrs in results:
        potentiallySaltedHashWithAlg = attrs.get('userPassword')
        potentiallySaltedHashWithAlg = potentiallySaltedHashWithAlg[0] if potentiallySaltedHashWithAlg else None
        if not potentiallySaltedHashWithAlg:
            logging.warn(u'No password for %s', dn)
            continue
        match = _algorithmMatcher.match(potentiallySaltedHashWithAlg)
        alg, potentiallySaltedHash = match.group(1), match.group(2)
        if alg == 'MD5':
            if _unsaltedBadMD5Digest == potentiallySaltedHash.decode('base64'):
                fixPassword(connection, dn)
        elif alg == 'SHA':
            if _unsaltedBadSHA1Digest == potentiallySaltedHash.decode('base64'):
                fixPassword(connection, dn)
        elif alg == 'SSHA':
            digest, salt = potentiallySaltedHash.decode('base64')[:20], potentiallySaltedHash.decode('base64')[20:]
            sha1 = hashlib.sha1(_badPasswd)
            sha1.update(salt)
            if sha1.digest() == digest:
                fixPassword(connection, dn)
        else:
            logging.info(u'Skipping dn "%s" due to algorithm %s', dn, alg)
    connection.unbind_s()


def main():
    args = _argParser.parse_args()
    password = args.ldap_password if args.ldap_password else getpass.getpass(u'LDAP manager password: ')
    fixPasswords(args.manager_dn, password, args.url, args.query, _scopes[args.scope], args.base)
    return True


if __name__ == '__main__':
    sys.exit(0 if main() else -1)
