### Installing and Running

You can clone this repository or download a zip file, build and run the Docker image.

```
$ docker build -t ocr-receiving .
$ docker run -t --device=/dev/video0:/dev/video0 -p 5000:5000 -v ~/ocr-receiving:/app ocr-receiving
```
 
Then open up browser to http://localhost:5000

You can use these images to test it - these are photos of a job posting:
