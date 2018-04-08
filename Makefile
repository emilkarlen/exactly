help:
	echo clean build install uninstall36 upload

clean:
	rm -rf build
	rm -rf dist
	rm -rf src/exactly.egg-info

build:
	python3 setup.py sdist
	python3 setup.py bdist_wheel

install:
	python3 setup.py install

uninstall36:
	test -d /usr/local/lib/python3.6/site-packages/exactly-0.8.8-py3.6.egg && rm -rf  /usr/local/lib/python3.6/site-packages/exactly-0.8.8-py3.6.egg
	test -f /usr/local/bin/exactly && rm -f /usr/local/bin/exactly

upload:
	twine upload dist/*

