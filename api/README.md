# How to build & run flask server
```bash
# Install python modules
pip install -r requirements.txt
# Build cython modules
cd src && python setup.py build_ext --inplace
# Run flask application
flask --app src/index.py run
```