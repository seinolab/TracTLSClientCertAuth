from setuptools import setup

setup(
    name='tracopt-auth-tls-client-certs',
    version='1.0',
    packages=['tlsclientcertauth'],
    entry_points={
        'trac.plugins': [
            'tracopt.auth.tls-client-certs = tlsclientcertauth.clientauth.clientauth',
        ]
    },
)
