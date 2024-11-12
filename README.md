## Receipt Processor

This repository is a webservice that hosts an API that processes a receipt payload like so:
- Takes in a JSON receipt and returns a JSON object with an ID for the receipt.
- The ID returned can be passed into `/receipts/{id}/points` to get the number of points the receipt was awarded.
  
This project was written in Python and includes a Dockerfile and docker-compose file to run the server in a container. Run `docker compose up --build` fromt the repository folder to start the container.
