all: tools/image-downloader
	docker build -t $^ $^
	docker run -it \
		--volume /mars-data:/mars-data \
		--volume $(shell pwd)/hirise-images.txt:/run/hirise-images.txt \
		$^ python download-hirise.py /run/hirise-images.txt
	ls /mars-data/hirise-images/*_RED.tif > /mars-data/hirise-images/hirise-red.txt

install:
	sudo ln -s $(shell pwd)/bin/mars /usr/local/bin

shell:
	docker run -it \
		--volume /mars-data:/mars-data \
		mars-data-backend bash

server:
	docker run --publish 80:80 --volume /mars-data:/usr/share/nginx/html:ro nginx

list:
	docker run -it --volume /mars-data:/mars-data bash ls -lah /mars-data/hirise-images

vrt: tools/image-downloader
	docker build -t $^ $^
	docker run -it \
		--volume /mars-data:/mars-data \
		$^ python create-vrt.py

mosaic: tools/tile-server
	DOCKER_BUILDKIT=1 docker build -t $^ $^
	docker run -it \
		--volume /mars-data:/mars-data \
		$^ tile-server /mars-data/hirise-images/*_RED.tif /mars-data/hirise-images/hirise-red.mosaic.json

sync:
	git push --recurse-submodules=on-demand