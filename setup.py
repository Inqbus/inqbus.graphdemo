from setuptools import setup, find_packages

version = '0.1'

setup(name='inqbus.graphdemo',
      version=version,
      description="Demo using flask and bokeh",
      long_description=open("README.txt").read() + "\n" +
                       open("HISTORY.txt").read(),
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Environment :: Plugins",
        "Intended Audience :: System Administrators",
        "License :: Other/Proprietary License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
                  ],
      keywords='',
      author='volker.jaenisch@inqbus.de',
      author_email='volker.jaenisch@inqbus.de',
      url='http://inqbus.de',
      download_url='',
      license='',
      packages=find_packages('src', exclude=['']),
      namespace_packages=['inqbus'],
      package_dir={'': 'src'},
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
                           extra=[
                                  ],
                           docs=[
                                 'z3c.recipe.sphinxdoc',
                                 'sphinxcontrib-requirements',
                                 ],
                           test=[
                                'nose',
                                'coverage',
                                ]
                           ),
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'flask',
          'numpy',
          'bokeh',
          'sqlalchemy',
          'flask-sqlalchemy',
          'flask-security',
          'flask-login>=0.3.0,<0.4',
          'flask_principal',
          'flask_mail',
          'flask_wtf',
          'flask_bootstrap',
          'flask',
          'passlib',
          'pathlib',
          'tables',
          'pandas',
          'flask-menu',
          'flask-bootstrap',
          'scipy'
          # 'Flask-ACL',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """
      )
