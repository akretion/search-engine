import setuptools

setuptools.setup(
    setup_requires=['setuptools-odoo'],
    odoo_addon={
        'external_dependencies_override': {
            'python': {
                'algoliasearch': 'algoliasearch>=2.0,<3.0',
            }
        }
    }
)
